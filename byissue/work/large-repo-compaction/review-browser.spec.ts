import { expect, test } from "../support/fixtures";
import { seedWorkspace } from "../support/helpers/seed-client";
import { buildSchedulesRoute } from "../../src/core/utils/host-routes";
import type { DaemonClient } from "@bytetrue/client/internal/daemon-client";

test("keeps active and ended schedules separately browsable", async ({ page }) => {
  const workspace = await seedWorkspace({ repoPrefix: "review-schedule-filter-", git: false });
  const client = workspace.client as unknown as DaemonClient;
  let id: string | undefined;
  try {
    const created = await client.scheduleCreate({
      name: "Review active schedule",
      prompt: "Check the project",
      cadence: { type: "cron", expression: "0 12 * * *" },
      target: { type: "new-agent", config: { provider: "mock", cwd: workspace.repoPath } },
      runOnCreate: false,
    });
    expect(created.error).toBeNull();
    id = created.schedule!.id;
    await page.goto(buildSchedulesRoute());
    const row = page.getByTestId(`schedule-row-${id}`);
    await expect(row).toBeVisible({ timeout: 30_000 });
    await page.getByRole("tab", { name: "Ended", exact: true }).click({ timeout: 5_000 });
    await expect(row).toHaveCount(0);
    await page.getByRole("tab", { name: "Active", exact: true }).click();
    await expect(row).toBeVisible();
  } finally {
    if (id) await client.scheduleDelete({ id });
    await workspace.cleanup();
  }
});

test("heartbeat menu keeps schedule-only execution actions hidden", async ({ page }) => {
  const workspace = await seedWorkspace({ repoPrefix: "review-heartbeat-menu-", git: false });
  const client = workspace.client as unknown as DaemonClient;
  let id: string | undefined;
  try {
    const agent = await workspace.client.createAgent({ provider: "mock", cwd: workspace.repoPath });
    const created = await client.scheduleCreate({
      name: "Review heartbeat",
      prompt: "Continue the conversation",
      cadence: { type: "cron", expression: "0 12 * * *" },
      target: { type: "agent", agentId: agent.id },
      runOnCreate: false,
    });
    expect(created.error).toBeNull();
    id = created.schedule!.id;
    await page.goto(buildSchedulesRoute());
    const row = page.getByTestId(`schedule-row-${id}`);
    await expect(row).toBeVisible({ timeout: 30_000 });
    await row.getByRole("button", { name: /actions/i }).click();
    await expect(page.getByRole("menuitem", { name: /delete/i })).toBeVisible();
    await expect(page.getByRole("menuitem", { name: /run now|pause|resume/i })).toHaveCount(0);
  } finally {
    if (id) await client.scheduleDelete({ id });
    await workspace.cleanup();
  }
});
