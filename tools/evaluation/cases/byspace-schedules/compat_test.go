package byevaluation

import (
	"bytes"
	"context"
	"encoding/json"
	"net"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"

	"github.com/ByteTrue/byspace/internal/cli"
	"github.com/ByteTrue/byspace/internal/schedule"
	"github.com/ByteTrue/byspace/internal/server"
	"github.com/ByteTrue/byspace/internal/store"
)

func reviewCLI(t *testing.T) (string, string) {
	t.Helper()
	home := t.TempDir()
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	addr := listener.Addr().String()
	srv, err := server.New(server.Options{HomeDir: home, Version: "review", ListenAddr: addr})
	if err != nil {
		listener.Close()
		t.Fatal(err)
	}
	t.Cleanup(func() { srv.Close() })
	ts := httptest.NewUnstartedServer(srv)
	ts.Listener = listener
	ts.Start()
	t.Cleanup(ts.Close)
	return addr, home
}

func reviewInvoke(t *testing.T, args ...string) map[string]any {
	t.Helper()
	var out, errOut bytes.Buffer
	if code := cli.Main("review", args, &out, &errOut); code != 0 {
		t.Fatalf("CLI %v: exit %d: %s", args, code, errOut.String())
	}
	var result map[string]any
	if err := json.Unmarshal(out.Bytes(), &result); err != nil {
		t.Fatalf("JSON output %q: %v", out.String(), err)
	}
	return result
}

func TestReviewHeartbeatCreateFromAgent(t *testing.T) {
	addr, home := reviewCLI(t)
	st := store.New(home)
	_, ws, err := st.EnsureWorkspaceForCwd(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	id := "11111111-1111-4111-8111-111111111111"
	now := time.Now().UTC().Format(time.RFC3339)
	if err := st.UpsertAgent(store.AgentRecord{ID: id, Provider: "pi", Cwd: ws.Cwd, WorkspaceID: ws.WorkspaceID, CreatedAt: now, UpdatedAt: now, LastStatus: "idle"}); err != nil {
		t.Fatal(err)
	}
	t.Setenv("BYSPACE_AGENT_ID", id)
	created := reviewInvoke(t, "heartbeat", "create", "--addr", addr, "--cron", "0 12 * * *", "--json", "continue the existing conversation")
	target, _ := created["target"].(map[string]any)
	if target["type"] != "agent" || target["agentId"] != id {
		t.Fatalf("wrong heartbeat target: %v", created)
	}
}

func TestReviewCLIInspectEnvelope(t *testing.T) {
	addr, _ := reviewCLI(t)
	created := reviewInvoke(t, "schedule", "create", "--addr", addr, "--cron", "0 12 * * *", "--provider", "pi", "--cwd", t.TempDir(), "--json", "check")
	id, _ := created["id"].(string)
	got := reviewInvoke(t, "schedule", "inspect", "--addr", addr, id)
	if value, ok := got["schedule"].(map[string]any); !ok || value["id"] != id {
		t.Fatalf("existing inspect JSON envelope removed: %v", got)
	}
}

func TestReviewCLIEmptyExpiryDoesNotPanic(t *testing.T) {
	defer func() {
		if r := recover(); r != nil {
			t.Fatalf("CLI panicked for --expires-in='': %v", r)
		}
	}()
	addr, _ := reviewCLI(t)
	created := reviewInvoke(t, "schedule", "create", "--addr", addr, "--cron", "0 12 * * *", "--provider", "pi", "--cwd", t.TempDir(), "--json", "check")
	id, _ := created["id"].(string)
	var out, errOut bytes.Buffer
	cli.Main("review", []string{"schedule", "update", "--addr", addr, "--expires-in=", "--json", id}, &out, &errOut)
}

func TestReviewRestartKeepsExplicitlyRetainedWorkspace(t *testing.T) {
	home := t.TempDir()
	now := time.Date(2026, 11, 14, 10, 0, 0, 0, time.UTC)
	svc := schedule.NewService(home, schedule.Hooks{Now: func() time.Time { return now }})
	created, err := svc.Create(schedule.CreateInput{Prompt: "check", Cadence: schedule.Cadence{Type: "cron", Expression: "0 12 * * *"}, Target: schedule.Target{Type: "new-agent", Config: &schedule.TargetConfig{Provider: "pi", Cwd: t.TempDir(), ArchiveOnFinish: ptr(false)}}})
	if err != nil {
		t.Fatal(err)
	}
	created.Runs = []schedule.Run{{ID: "interrupted", Status: "running", StartedAt: "2026-11-14T09:00:00.000Z", ScheduledFor: "2026-11-14T09:00:00.000Z", AgentID: ptr("agent-created"), WorkspaceID: ptr("kept-workspace")}}
	raw, err := json.Marshal(created)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(home, "schedules", created.ID+".json"), raw, 0o600); err != nil {
		t.Fatal(err)
	}
	var archived atomic.Int32
	reopened := schedule.NewService(home, schedule.Hooks{Now: func() time.Time { return now }, ArchiveWorkspace: func(string) error { archived.Add(1); return nil }})
	reopened.Start()
	defer reopened.Stop()
	got, err := reopened.Inspect(created.ID)
	if err != nil || got.Runs[0].Status != "failed" {
		t.Fatalf("interrupted run not recovered: %v %v", got, err)
	}
	if archived.Load() != 0 {
		t.Fatal("restart archived a workspace despite archiveOnFinish=false and a persisted agent")
	}
}

func TestReviewLateIntervalKeepsOriginalGrid(t *testing.T) {
	start := time.Date(2026, 11, 14, 10, 0, 0, 0, time.UTC)
	var now atomic.Int64
	now.Store(start.UnixNano())
	svc := schedule.NewService(t.TempDir(), schedule.Hooks{Now: func() time.Time { return time.Unix(0, now.Load()) }, Execute: func(context.Context, schedule.StoredSchedule, schedule.RunHandle) (schedule.ExecutionResult, error) {
		return schedule.ExecutionResult{}, nil
	}})
	created, err := svc.Create(schedule.CreateInput{Prompt: "check", Cadence: schedule.Cadence{Type: "every", EveryMs: 10 * 60_000}, Target: schedule.Target{Type: "new-agent", Config: &schedule.TargetConfig{Provider: "pi", Cwd: t.TempDir()}}})
	if err != nil {
		t.Fatal(err)
	}
	now.Store(start.Add(25 * time.Minute).UnixNano())
	svc.Tick()
	deadline := time.Now().Add(3 * time.Second)
	for time.Now().Before(deadline) {
		got, err := svc.Inspect(created.ID)
		if err != nil {
			t.Fatal(err)
		}
		if len(got.Runs) > 0 && got.Runs[0].Status != "running" {
			if got.NextRunAt == nil {
				t.Fatal("late interval lost nextRunAt")
			}
			if *got.NextRunAt != "2026-11-14T10:30:00.000Z" {
				t.Fatalf("10-minute grid starting 10:00, delayed to 10:25: next=%s, want 10:30", *got.NextRunAt)
			}
			return
		}
		time.Sleep(time.Millisecond)
	}
	t.Fatal("run did not finish")
}

func TestReviewHalfHourDST(t *testing.T) {
	for _, c := range []struct{ after, want string }{
		{"2026-04-04T14:30:00Z", "2026-04-04T14:45:00Z"},
		{"2026-04-04T14:45:00Z", "2026-04-04T15:15:00Z"},
	} {
		t.Run(c.after, func(t *testing.T) {
			after, _ := time.Parse(time.RFC3339, c.after)
			next, err := schedule.ComputeNextRunAt(schedule.Cadence{Type: "cron", Expression: "45 1 * * *", Timezone: "Australia/Lord_Howe"}, after)
			if err != nil || next.UTC().Format(time.RFC3339) != c.want {
				t.Fatalf("next=%v err=%v, want %s", next, err, c.want)
			}
		})
	}
}
