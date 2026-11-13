# 台账：pstack 维护侧逐项裁定

列举命令（在 `/Users/zijie/workspace/reference/pstack-claude`，HEAD `91ab921`）：

```sh
grep '^## ' CHANGES.md                                   # M1：按 10 个版本一行
ls CONTRIBUTING.md CONTEXT.md README.md SECURITY.md NOTICE*.md VERSION .gitattributes .gitignore .markdownlint-cli2.jsonc .pre-commit-config.yaml bunfig.toml package.json bun.lock kimi.plugin.json LICENSE*
find .agents .claude-plugin .github docs -type f | sort  # M2 的其余
find tools lean tla -type f | sort                       # M3
find tests -maxdepth 1 -type f | sort                    # M4
find tests/pi -type f | sort                             # M5
cd plugins/pstack/skills && find . -path '*/scripts/*' -type f ! -name '*.test.*' ! -name '*.json' ! -name '*.lock' ! -name '.prettier*' | grep -v -e watch-pr -e statechart | sort   # M6
```

不在范围：`plugins/pstack/` 下的技能、agent、hook、`hooks.json`、`models.json`（上一个 Epic `byissue/epics/2026-11-09-x-pstack-item-verdicts/` 已逐项裁定），以及 `plugins/pstack/` 下的宿主适配目录（`pi/`、`omp/`、`opencode/`、`grok/`、各 `.*-plugin/`），它们只服务 pstack 的多宿主分发。

结论取值：`[已有]`、`[已有·部分]`、`[候选]`、`[不吸收]`，判据见同目录 spec.md「结论的判据」。状态：`没做`、`做了`。

接着做或改这张表之前，先读同目录 spec.md 的已定方案与必须守住。

接续点：五个单元都已裁定（138 行），每个单元的引用由父会话核对，记在各 `verdicts/M<n>.md` 末尾。候选去重后在 [candidates.md](candidates.md)，用户已裁决学 8 条并补 LICENSE，落地是单元 L（139–147 行），随 1.14.2 发布。维护侧审查（3 P1、11 P2）与合并复审（5 P2）已全修；selftest 32 条，换回 HEAD 的 checker 放过其中 14 条。收尾前还有两步（见 spec「收尾前补的两步」）：已有类逐行复核已做（表格里实为 30 行，维持 29、翻为不吸收 1；5 处证据过时或残余未处置已就地标「复核：」，其中三处顺手修进 checker 与 selftest）；M6 技能自带脚本 13 行已判（唯一候选用户定为暂不学）。Epic 已关闭。

| # | 项 | 单元 | 状态 | 结论与证据 |
|---|---|---|---|---|
| 1 | CHANGES.md 0.9.133 至 0.9.124（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 2 | CHANGES.md 0.9.123 至 0.9.114（10 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 3 | CHANGES.md 0.9.113 至 0.9.104（10 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 4 | CHANGES.md 0.9.103 至 0.9.94（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 5 | CHANGES.md 0.9.93 至 0.9.84（10 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 6 | CHANGES.md 0.9.83 至 0.9.74（10 个版本） | M1 | 做了 | [候选] 见 [verdicts/M1.md](verdicts/M1.md) |
| 7 | CHANGES.md 0.9.73 至 0.9.64（10 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 8 | CHANGES.md 0.9.63 至 0.9.54（10 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 9 | CHANGES.md 0.9.53 至 0.9.44（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 10 | CHANGES.md 0.9.43 至 0.9.34（10 个版本） | M1 | 做了 | [不吸收] 见 [verdicts/M1.md](verdicts/M1.md) |
| 11 | CHANGES.md 0.9.33 至 0.9.24（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 12 | CHANGES.md 0.9.23 至 0.9.14（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 13 | CHANGES.md 0.9.13 至 0.9.5（10 个版本） | M1 | 做了 | [已有·部分] 见 [verdicts/M1.md](verdicts/M1.md) |
| 14 | CHANGES.md 0.9.4 至 0.9.2（3 个版本） | M1 | 做了 | [已有] 见 [verdicts/M1.md](verdicts/M1.md) |
| 15 | CONTRIBUTING.md | M2 | 做了 | [已有·部分] 见 [verdicts/M2.md](verdicts/M2.md) |
| 16 | CONTEXT.md | M2 | 做了 | [已有] 见 [verdicts/M2.md](verdicts/M2.md) |
| 17 | README.md | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 18 | SECURITY.md | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 19 | NOTICE.md | M2 | 做了 | [候选] 见 [verdicts/M2.md](verdicts/M2.md) |
| 20 | NOTICE-skills.md | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 21 | VERSION | M2 | 做了 | [已有] 见 [verdicts/M2.md](verdicts/M2.md) |
| 22 | .gitattributes | M2 | 做了 | [候选] 见 [verdicts/M2.md](verdicts/M2.md) |
| 23 | .gitignore | M2 | 做了 | [已有] 见 [verdicts/M2.md](verdicts/M2.md) |
| 24 | .markdownlint-cli2.jsonc | M2 | 做了 | [候选] 见 [verdicts/M2.md](verdicts/M2.md) |
| 25 | .pre-commit-config.yaml | M2 | 做了 | [候选] 见 [verdicts/M2.md](verdicts/M2.md) |
| 26 | bunfig.toml | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 27 | package.json | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 28 | bun.lock | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 29 | kimi.plugin.json | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 30 | LICENSE | M2 | 做了 | [候选] 见 [verdicts/M2.md](verdicts/M2.md) |
| 31 | LICENSE-cursor-team-kit | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 32 | LICENSE-thermos | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 33 | .agents/plugins/marketplace.json | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 34 | .claude-plugin/marketplace.json | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 35 | .github/dependabot.yml | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 36 | .github/FUNDING.yml | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 37 | .github/ISSUE_TEMPLATE/bug_report.yml | M2 | 做了 | [已有·部分] 见 [verdicts/M2.md](verdicts/M2.md) |
| 38 | .github/ISSUE_TEMPLATE/config.yml | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 39 | .github/ISSUE_TEMPLATE/feature_request.yml | M2 | 做了 | [已有·部分] 见 [verdicts/M2.md](verdicts/M2.md) |
| 40 | .github/pull_request_template.md | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 41 | .github/scripts/statechart-watchdog.sh | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 42 | .github/workflows/ci.yml | M2 | 做了 | [已有·部分] 见 [verdicts/M2.md](verdicts/M2.md) |
| 43 | .github/workflows/security.yml | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 44 | docs/pi-equivalence.md | M2 | 做了 | [已有·部分] 见 [verdicts/M2.md](verdicts/M2.md) |
| 45 | docs/reference.md | M2 | 做了 | [不吸收] 见 [verdicts/M2.md](verdicts/M2.md) |
| 46 | lean/lake-manifest.json | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 47 | lean/lakefile.toml | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 48 | lean/lean-toolchain | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 49 | lean/Model/WatchPoll.lean | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 50 | lean/Model/WatchPoll.mutations | M3 | 做了 | [已有] 见 [verdicts/M3.md](verdicts/M3.md) |
| 51 | lean/Model/WatchPoll.statements | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 52 | tla/PiScheduler.matrix | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 53 | tla/PiScheduler.mutations | M3 | 做了 | [已有·部分] 见 [verdicts/M3.md](verdicts/M3.md) |
| 54 | tla/PiScheduler.tla | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 55 | tools/forks.json | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 56 | tools/generate.mjs | M3 | 做了 | [已有·部分] 见 [verdicts/M3.md](verdicts/M3.md) |
| 57 | tools/pi-package.mjs | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 58 | tools/plugin.mjs | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 59 | tools/runtimes.mjs | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 60 | tools/substitutions.json | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 61 | tools/sync.mjs | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 62 | tools/typecheck-pi.mjs | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 63 | tools/upstream.json | M3 | 做了 | [不吸收] 见 [verdicts/M3.md](verdicts/M3.md) |
| 64 | tools/validate-skills.mjs | M3 | 做了 | [已有·部分] 见 [verdicts/M3.md](verdicts/M3.md) |
| 65 | tests/agent-roster.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 66 | tests/agent-skills.test.mjs | M4 | 做了 | [已有·部分] 见 [verdicts/M4.md](verdicts/M4.md) |
| 67 | tests/agy.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 68 | tests/check-plan.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 69 | tests/check-playbooks.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 70 | tests/check-sheet.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 71 | tests/ci-forks-step.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 72 | tests/claude-config-dir.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 73 | tests/claude-project-dir.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 74 | tests/codex-session-effort.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 75 | tests/copilot-smoke.sh | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 76 | tests/copilot-tui.py | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 77 | tests/copilot.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 78 | tests/directory-scan.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 79 | tests/find-transcript.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 80 | tests/generate-checkout.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 81 | tests/generate.test.mjs | M4 | 做了 | [已有·部分] 见 [verdicts/M4.md](verdicts/M4.md) |
| 82 | tests/grok-smoke.py | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 83 | tests/grok.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 84 | tests/image-metadata.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 85 | tests/invariants.test.mjs | M4 | 做了 | [已有] 见 [verdicts/M4.md](verdicts/M4.md) |
| 86 | tests/kimi.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 87 | tests/log.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 88 | tests/mapping-coverage.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 89 | tests/minimax-smoke.sh | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 90 | tests/minimax.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 91 | tests/models.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 92 | tests/muse.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 93 | tests/omp.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 94 | tests/opencode.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 95 | tests/pi-equivalence.test.mjs | M4 | 做了 | [已有·部分] 见 [verdicts/M4.md](verdicts/M4.md) |
| 96 | tests/pi-package.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 97 | tests/pre-tool-use.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 98 | tests/readme-facts.test.mjs | M4 | 做了 | [候选] 见 [verdicts/M4.md](verdicts/M4.md) |
| 99 | tests/remove-during.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 100 | tests/resume.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 101 | tests/runtime-packaging.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 102 | tests/session-hook-sheets.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 103 | tests/session-hook-windows.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 104 | tests/session-hook.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 105 | tests/shipping-git.test.mjs | M4 | 做了 | [候选] 见 [verdicts/M4.md](verdicts/M4.md) |
| 106 | tests/skill-collision-repro.sh | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 107 | tests/skill-references.test.mjs | M4 | 做了 | [候选] 见 [verdicts/M4.md](verdicts/M4.md) |
| 108 | tests/skill-rules.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 109 | tests/sync.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 110 | tests/test-discovery.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 111 | tests/worktree-audit.test.mjs | M4 | 做了 | [不吸收] 见 [verdicts/M4.md](verdicts/M4.md) |
| 112 | tests/pi/agent-defaults.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 113 | tests/pi/agent-tools-off.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 114 | tests/pi/agent-transcript-command.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 115 | tests/pi/agents-activity.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 116 | tests/pi/agents-launch.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 117 | tests/pi/agents-messages.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 118 | tests/pi/agents-run.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 119 | tests/pi/agents-session.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 120 | tests/pi/catalog.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 121 | tests/pi/child.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 122 | tests/pi/config.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 123 | tests/pi/fake-pi.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 124 | tests/pi/fake-pi.test.mjs | M5 | 做了 | [已有·部分] 见 [verdicts/M5.md](verdicts/M5.md) |
| 125 | tests/pi/harness.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 126 | tests/pi/host.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 127 | tests/pi/interaction.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 128 | tests/pi/live-harness.mjs | M5 | 做了 | [已有] 见 [verdicts/M5.md](verdicts/M5.md) |
| 129 | tests/pi/live.test.mjs | M5 | 做了 | [已有·部分] 见 [verdicts/M5.md](verdicts/M5.md) |
| 130 | tests/pi/parent-session.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 131 | tests/pi/path-skills.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 132 | tests/pi/prompt.test.mjs | M5 | 做了 | [已有] 见 [verdicts/M5.md](verdicts/M5.md) |
| 133 | tests/pi/runtime.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 134 | tests/pi/slash.test.mjs | M5 | 做了 | [候选] 见 [verdicts/M5.md](verdicts/M5.md) |
| 135 | tests/pi/sleep-wait.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 136 | tests/pi/user-agents.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 137 | tests/pi/worktree-status-config.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 138 | tests/pi/worktree.test.mjs | M5 | 做了 | [不吸收] 见 [verdicts/M5.md](verdicts/M5.md) |
| 139 | 落地 1：全仓路径可达（checker） | L | 做了 | checker 新增 `check_repo_paths`；selftest「current doc names a deleted tool」「current doc links a missing file」在旧 checker 上 FAIL、新 checker 上 ok |
| 140 | 落地 2：修过的静默漏检各钉 selftest 坏样例 | L | 做了 | selftest 文档写明每修一次漏检加一条旧版放过的坏样例并对旧版跑一次；本轮 6 条新 case 中 5 条在 HEAD 的 checker 上 FAIL（带锚点那条 009 已修，旧版也 ok） |
| 141 | 落地 3：CHANGELOG 版本闸门与过期数字 | L | 做了 | checker 版本闸门（最新小节等于 VERSION、版本不重复）与 `check_derived_facts`；第一次跑就报出 spec「20 篇」实际 22 篇，已改；对应 selftest 3 条 |
| 142 | 落地 4：close.md 修引用命令对夹具原样跑 | L | 做了 | `tools/check-close-reference-command.py`：close.md 三处 grep 命令写法一致，对夹具原样跑命中正好 10 行；去掉 --exclude-dir=.git 的变体被判出 |
| 143 | 落地 5：分发脚本的夹具测试 | L | 做了 | `tools/check-skill-scripts.py` 8 个用例全过；换回 1.13.1 之前的 check_open_issues.py，两条重复状态用例 FAIL |
| 144 | 落地 6：行为评测夹具自证前提、判分非零退出 | L | 做了 | posture_table.py 建完夹具先断言 task 里的路径存在与 PRE 表；把 README 的 npm tset 改掉后脚本列出「28 … lacks 'npm tset'」并不写计划；posture_judge.py 对没跑的条目记 NOT RUN 并以 1 退出（实跑确认） |
| 145 | 落地 7：A/B 删句判据（posture-scenarios.md） | L | 做了 | `tools/posture-scenarios.md` 新增「两臂行为相同，就删掉那句」 |
| 146 | 落地 8：发布前检查脚本与部署副本核对 | L | 做了 | `tools/release-check.sh` 串起四项检查与部署副本 diff；对本机部署副本通过，对改过一字节的副本与不存在的目录都失败；spec「谁在挡」rsync 行改为它 |
| 147 | 落地 9：仓库根 LICENSE 与上游镜像 NOTICE | L | 做了 | 仓库根 `LICENSE`（MIT，liuzhengdong 与 ByteTrue），README 两版链到它。审查指出 MIT 要求声明随拷贝走而根 NOTICE 不进分发包，用户 2026-11-10 在「放进分发包，打成 1.14.2」上确认：`skills/bi/NOTICE.md` 含 ByIssue 与上游 mattpocock/skills（GitHub API 核对为 MIT）两份原文，`SKILL.md` 末尾一行指向它，根 `NOTICE.md` 改为指向包内；checker 断言包内 NOTICE 含 LICENSE 原文 |
| 148 | poteto-mode/scripts/bootstrap.ts | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 149 | poteto-mode/scripts/check-plan.mjs | M6 | 做了 | [候选] 见 [verdicts/M6.md](verdicts/M6.md) |
| 150 | poteto-mode/scripts/check-playbooks.mjs | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 151 | poteto-mode/scripts/codex-session-effort.mjs | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 152 | poteto-mode/scripts/resume.mjs | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 153 | poteto-mode/scripts/worktree-audit.mjs | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 154 | reflect/scripts/claude-project-dir.mjs | M6 | 做了 | [已有·部分] 见 [verdicts/M6.md](verdicts/M6.md) |
| 155 | reflect/scripts/find-transcript.mjs | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 156 | setup-pstack/scripts/check-sheet.awk | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 157 | setup-pstack/scripts/check-sheet.sh | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 158 | setup-pstack/scripts/read-sheet.sh | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 159 | setup-pstack/scripts/sheet.awk | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
| 160 | show-me-your-work/scripts/log.sh | M6 | 做了 | [不吸收] 见 [verdicts/M6.md](verdicts/M6.md) |
