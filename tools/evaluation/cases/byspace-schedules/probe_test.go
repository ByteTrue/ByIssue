package byevaluation

import (
	"bytes"
	"context"
	"encoding/json"
	"net"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/ByteTrue/byspace/internal/cadence"
	"github.com/ByteTrue/byspace/internal/cli"
	"github.com/ByteTrue/byspace/internal/schedule"
	"github.com/ByteTrue/byspace/internal/server"
)

func ptr[T any](v T) *T { return &v }

func TestIndependentCalendar(t *testing.T) {
	for _, c := range []struct{ expression, zone, after, want string }{
		{"*/15 * * * *", "UTC", "2026-11-14T10:15:00Z", "2026-11-14T10:30:00Z"},
		{"0 9 1 * 1", "UTC", "2026-11-02T00:00:00Z", "2027-02-01T09:00:00Z"},
		{"30 2 * * *", "America/New_York", "2026-03-08T05:00:00Z", "2026-03-09T06:30:00Z"},
		{"30 1 * * *", "America/New_York", "2026-11-01T05:30:00Z", "2026-11-01T06:30:00Z"},
	} {
		t.Run(c.expression+"/"+c.after, func(t *testing.T) {
			after, _ := time.Parse(time.RFC3339, c.after)
			next, err := schedule.ComputeNextRunAt(schedule.Cadence{Type: "cron", Expression: c.expression, Timezone: c.zone}, after)
			if err != nil || next.UTC().Format(time.RFC3339) != c.want {
				t.Fatalf("next=%v err=%v, want %s", next, err, c.want)
			}
		})
	}
	for _, value := range []string{"15", "15m"} {
		d, err := cadence.ParseDuration(value)
		if err != nil || d != 15*time.Minute {
			t.Fatalf("duration %q: %v %v", value, d, err)
		}
	}
	for _, ms := range []int64{7 * 60_000, 30_000} {
		if _, err := cadence.EveryMsToFiveFieldCron(ms); err == nil {
			t.Fatalf("accepted unrepresentable interval %d", ms)
		}
	}
}

func TestIndependentPersistenceAndPatch(t *testing.T) {
	home := t.TempDir()
	now := time.Date(2026, 11, 14, 10, 0, 0, 0, time.UTC)
	svc := schedule.NewService(home, schedule.Hooks{Now: func() time.Time { return now }})
	created, err := svc.Create(schedule.CreateInput{
		Name: ptr("nightly"), Prompt: "check builds", Cadence: schedule.Cadence{Type: "cron", Expression: "0 12 * * *", Timezone: "UTC"},
		Target:  schedule.Target{Type: "new-agent", Config: &schedule.TargetConfig{Provider: "mock", Cwd: t.TempDir(), Model: "model-a", ModeID: "mode-a", ArchiveOnFinish: ptr(false)}},
		MaxRuns: ptr(3), ExpiresAt: ptr("2026-12-01T00:00:00Z"),
	})
	if err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(home, "schedules", created.ID+".json")
	before, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := svc.Update(schedule.UpdateInput{ID: created.ID, Prompt: ptr(" "), Name: schedule.Present(ptr("lost"))}); err == nil {
		t.Fatal("invalid patch succeeded")
	}
	after, err := os.ReadFile(path)
	if err != nil || !bytes.Equal(before, after) {
		t.Fatalf("failed patch changed record: %v", err)
	}
	_, err = svc.Update(schedule.UpdateInput{ID: created.ID, Name: schedule.Present[string](nil), MaxRuns: schedule.Present[int](nil),
		NewAgentConfig: &schedule.NewAgentConfigPatch{Model: schedule.Present[string](nil)}})
	if err != nil {
		t.Fatal(err)
	}
	reopened := schedule.NewService(home, schedule.Hooks{})
	got, err := reopened.Inspect(created.ID)
	if err != nil {
		t.Fatal(err)
	}
	if got.Name != nil || got.MaxRuns != nil || got.ExpiresAt == nil || got.Target.Config.Model != "" || got.Target.Config.ModeID != "mode-a" || got.Target.Config.ArchiveOnFinish == nil || *got.Target.Config.ArchiveOnFinish {
		t.Fatalf("patch/reopen lost tri-state values: %+v %+v", got, got.Target.Config)
	}
	if err := os.WriteFile(filepath.Join(home, "schedules", "broken.json"), []byte("{"), 0o600); err != nil {
		t.Fatal(err)
	}
	all, err := reopened.List()
	if err != nil || len(all) != 1 {
		t.Fatalf("corrupt sibling poisoned list: %v %v", all, err)
	}
	if err := reopened.Delete(created.ID); err != nil {
		t.Fatal(err)
	}
	if _, err := reopened.Inspect(created.ID); err == nil {
		t.Fatal("deleted record survived")
	}
}

func TestIndependentRunAndRecovery(t *testing.T) {
	home := t.TempDir()
	now := time.Date(2026, 11, 14, 10, 0, 0, 0, time.UTC)
	started, release := make(chan struct{}, 2), make(chan struct{})
	svc := schedule.NewService(home, schedule.Hooks{Now: func() time.Time { return now }, Execute: func(ctx context.Context, s schedule.StoredSchedule, r schedule.RunHandle) (schedule.ExecutionResult, error) {
		r.RecordWorkspace("run-workspace", ptr("agent-run"))
		started <- struct{}{}
		<-release
		return schedule.ExecutionResult{AgentID: ptr("agent-run"), Output: ptr("checked")}, nil
	}})
	created, err := svc.Create(schedule.CreateInput{Prompt: "check", Cadence: schedule.Cadence{Type: "cron", Expression: "0 12 * * *"}, Target: schedule.Target{Type: "new-agent", Config: &schedule.TargetConfig{Provider: "mock", Cwd: t.TempDir()}}})
	if err != nil {
		t.Fatal(err)
	}
	done := make(chan error, 1)
	go func() { _, err := svc.RunOnce(context.Background(), created.ID); done <- err }()
	select {
	case <-started:
	case <-time.After(5 * time.Second):
		t.Fatal("run never started")
	}
	running, err := svc.Inspect(created.ID)
	if err != nil || len(running.Runs) != 1 || running.Runs[0].WorkspaceID == nil || *running.Runs[0].WorkspaceID != "run-workspace" {
		t.Fatalf("workspace not persisted while running: %+v %v", running, err)
	}
	if _, err := svc.RunOnce(context.Background(), created.ID); err == nil {
		t.Fatal("overlapping run accepted")
	}
	close(release)
	if err := <-done; err != nil {
		t.Fatal(err)
	}
	finished, err := svc.Inspect(created.ID)
	if err != nil {
		t.Fatal(err)
	}
	if len(finished.Runs) != 1 || finished.Runs[0].Status != "succeeded" || finished.Runs[0].Output == nil || *finished.Runs[0].Output != "checked" || *finished.NextRunAt != *created.NextRunAt {
		t.Fatalf("manual run moved cadence or lost output: %+v", finished)
	}
	// A persisted running record is the public restart input, not an internal service field.
	running.NextRunAt = ptr("2026-11-13T12:00:00.000Z")
	raw, err := json.Marshal(running)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(home, "schedules", created.ID+".json"), raw, 0o600); err != nil {
		t.Fatal(err)
	}
	archived := make(chan string, 1)
	recovered := schedule.NewService(home, schedule.Hooks{Now: func() time.Time { return now }, ArchiveWorkspace: func(id string) error { archived <- id; return nil }})
	recovered.Start()
	defer recovered.Stop()
	got, err := recovered.Inspect(created.ID)
	if err != nil {
		t.Fatal(err)
	}
	if got.Runs[0].Status != "failed" || got.Runs[0].Error == nil || !strings.Contains(strings.ToLower(*got.Runs[0].Error), "restart") || *got.NextRunAt != "2026-11-14T12:00:00.000Z" {
		t.Fatalf("restart did not settle interrupted run: %+v", got)
	}
	select {
	case id := <-archived:
		if id != "run-workspace" {
			t.Fatal(id)
		}
	case <-time.After(time.Second):
		t.Fatal("interrupted workspace not archived")
	}
}

func TestIndependentCLIAndRPC(t *testing.T) {
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	addr := listener.Addr().String()
	srv, err := server.New(server.Options{HomeDir: t.TempDir(), Version: "evaluation", ListenAddr: addr})
	if err != nil {
		listener.Close()
		t.Fatal(err)
	}
	defer srv.Close()
	ts := httptest.NewUnstartedServer(srv)
	ts.Listener = listener
	ts.Start()
	defer ts.Close()
	invoke := func(t *testing.T, args ...string) map[string]any {
		t.Helper()
		var out, errors bytes.Buffer
		if code := cli.Main("evaluation", args, &out, &errors); code != 0 {
			t.Fatalf("%v: %d %s", args, code, errors.String())
		}
		var value map[string]any
		if err := json.Unmarshal(out.Bytes(), &value); err != nil {
			t.Fatalf("%v: %v: %s", args, err, out.String())
		}
		return value
	}
	created := invoke(t, "schedule", "create", "--addr", addr, "--every", "15m", "--provider", "pi/example-model", "--cwd", t.TempDir(), "--max-runs", "4", "--expires-in", "1d", "--json", "check CI")
	id, ok := created["id"].(string)
	if !ok || id == "" {
		t.Fatalf("missing schedule ID: %v", created)
	}
	target := created["target"].(map[string]any)["config"].(map[string]any)
	if target["provider"] != "pi" || target["model"] != "example-model" || created["maxRuns"] != float64(4) {
		t.Fatalf("provider/limit lost: %v", created)
	}
	t.Run("update-clears-fields", func(t *testing.T) {
		response := invoke(t, "schedule", "update", "--addr", addr, "--no-max-runs", "--no-expires-in", "--json", id, "updated prompt")
		updated, ok := response["schedule"].(map[string]any)
		if !ok || updated["prompt"] != "updated prompt" || updated["maxRuns"] != nil || updated["expiresAt"] != nil {
			t.Fatalf("clear fields failed: %v", updated)
		}
		stored, ok := invoke(t, "schedule", "inspect", "--addr", addr, id)["schedule"].(map[string]any)
		if !ok || stored["prompt"] != "updated prompt" || stored["maxRuns"] != nil || stored["expiresAt"] != nil {
			t.Fatalf("cleared fields were not persisted: %v", stored)
		}
	})
	for _, step := range []struct{ command, status string }{{"pause", "paused"}, {"resume", "active"}, {"inspect", "active"}} {
		t.Run(step.command, func(t *testing.T) {
			response := invoke(t, "schedule", step.command, "--addr", addr, id)
			got, ok := response["schedule"].(map[string]any)
			if !ok || got["status"] != step.status {
				t.Fatalf("%s: %v", step.command, response)
			}
		})
	}
	var out, errors bytes.Buffer
	if code := cli.Main("evaluation", []string{"schedule", "create", "--addr", "127.0.0.1:1", "--every", "7m", "--provider", "pi", "check"}, &out, &errors); code == 0 || !strings.Contains(errors.String(), "cron") || strings.Contains(errors.String(), "connection refused") {
		t.Fatalf("invalid interval reached network: %d %s", code, errors.String())
	}
	if code := cli.Main("evaluation", []string{"schedule", "delete", "--addr", addr, id}, &out, &errors); code != 0 {
		t.Fatal(errors.String())
	}
	out.Reset()
	errors.Reset()
	if code := cli.Main("evaluation", []string{"schedule", "inspect", "--addr", addr, id}, &out, &errors); code == 0 {
		t.Fatal("deleted schedule still inspectable")
	}
}
