# DeepSeek Flash 大型功能重建评审

## 结论

评测已完成，重建功能与 bi v2 工作流执行均未通过。DeepSeek 恢复了可构建、可运行的主体功能，原有定向回归全部通过；独立验收和补充复测确认 9 项新增兼容性或行为问题。当前实现不宜交付。

自然长任务发生了 1 次真实原生压缩。压缩后仍能继续读代码、修改和测试，但没有先读取 work 检查点。此次证明了“大仓库连续执行并自然压缩”可运行，没有证明压缩后的 v2 接续契约已被可靠执行。

以下代码位置相对被测项目 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-rebuild-01/project/`。审查按个人开发环境中的单 daemon、多个任务及多主机客户端判断；没有高并发性能结论。

## 运行与证据

证据根目录为 `/Users/zijie/workspace/ByIssue-evaluation/`：

- `corpora/byspace-708ec9f25/`：固定提交 `708ec9f2508978a71b80f2cae3ecf3a7d66e8eca`，3,498 个文件，约 572,136 行源码。
- `preflight/schedules-original/`：原版预检、补充 Go/浏览器复测及 relay 定向标定。
- `runs/schedules-rebuild-01/`：下文简称运行目录，保存模型会话、首次验收、重建产物及独立评审。

删减基线移除了 19 个实现文件、6 个函数，共 6,422 行，以及 303 份 v1 工作文档。分支 `eval/rebuild-schedules` 只有基线提交 `6d58be4`，没有 remote 或原实现历史。[25 项来源对账](scope.md)已完成；原文件合并进新文件按行为映射判断。

| 项目 | 实测值 |
|---|---|
| 模型与宿主 | `bytetrueapi/deepseek/deepseek-flash`，medium，pi 1.5.2 |
| 执行 | 一份完整需求，一个持续会话，pi 退出 0，耗时 2,005.72 秒（约 33 分 26 秒） |
| 消息与工具 | 172 条助手消息，211 次工具调用，其中 bash 208、read 3 |
| 原生压缩 | 1 次 `threshold`；事件与持久摘要匹配，未中止、无错误 |
| 上下文 | 模型窗口 1M；阈值 400k；保留最近 20k；报告峰值 401,333；压缩前投影 401,807；压缩后估计 23,939 token |
| 普通轮次用量 | input 806,172；output 147,775；cacheRead 33,482,880；totalTokens 34,436,827 |
| 摘要另计 | input 148,861；output 3,756；totalTokens 152,617 |

用量是宿主报告的累计值，不能当成上下文峰值、实际账单或效率提升。全局 pi 配置未被运行器更改；本轮设置见运行目录 `report.json`。

## 功能验证

| 检查 | 原版 | 删减基线 | 重建版 |
|---|---|---|---|
| 独立日历、patch 持久化、执行与恢复三组 | 通过 | 实现缺失，未通过 | 通过 |
| 独立 CLI 更新/清除限制 | 未通过：返回成功但未保存 | 实现缺失，未通过 | 未通过：不识别原参数 |
| cadence/schedule 定向回归与 race | 通过 | 未通过 | 通过 |
| server/CLI 定向回归、Go 构建、vet | 通过 | 未通过 | 通过 |
| 前端 51 项单测、类型检查、构建 | 通过 | 未通过 | 通过 |
| 原有 7 项浏览器检查 | 补齐 relay 构建后通过 | 构建未通过，未运行 | 通过 |
| 补充 6 组公开 Go API/CLI 检查 | 通过 | 不适用 | 6 组均未通过 |
| 补充 2 项真实浏览器检查 | 通过 | 不适用 | 2 项均未通过 |

首次证据保存在 `acceptance/`，没有用补测替换。补充检查保存在两份副本各自的 `review-01/` 和 `review-browser-01/`，后者含失败截图与 Playwright trace。

原版已存在的 CLI 缺陷是 `commands_extra.go:332–333` 发送嵌套 `patch`，服务端读取顶层字段，导致更新无效。重建版新增的问题是丢失原来的清除参数；不能把原版已有的更新失效也算作新增。

### 必须修复

1. **重启归档了明确要求保留的运行工作区** — `internal/schedule/service.go:1023–1035`。
   - 场景与影响：新 agent 已写入运行记录，`archiveOnFinish=false`，daemon 在运行中重启。恢复应标记失败并保留工作区。
   - 实测：`TestReviewRestartKeepsExplicitlyRetainedWorkspace` 在原版通过，重建版调用了归档 hook；保留设置失效。
   - 最小修复：恢复分支采用正常结束时同样的归档条件。agent 已创建且显式 false 时保留，尚未成功创建 agent 时清理。

2. **正常 agent 环境无法创建 heartbeat** — `internal/cli/commands_extra.go:667–698`。
   - 场景与影响：已有真实 agent 记录，环境设置 `BYSPACE_AGENT_ID`，执行 `heartbeat create --cron ...`。这是 agent 创建自身 heartbeat 的正常入口。
   - 实测：`TestReviewHeartbeatCreateFromAgent` 原版通过，重建版却报 `BYSPACE_AGENT_ID is not set`。代码先从环境取得目标，再错误地要求原始 `--target` 非空。
   - 最小修复：移除对原始 flag 的重复判断，以已经解析的目标 ID 为准。

3. **原有清除参数不再被接受** — `internal/cli/commands_extra.go:913–935`。
   - 场景与影响：执行 `schedule update --no-max-runs --no-expires-in --json <id> ...`。已有脚本无法按原接口清除限制。
   - 实测：首次独立验收报 `flag provided but not defined: -no-max-runs`；原版接受这些参数，但另有上述保存缺陷。
   - 最小修复：恢复两个 flag，并将显式清除映射到顶层 `maxRuns: null`、`expiresAt: null`。用相同 CLI 命令验证实际存储结果。

4. **空到期参数使 CLI 崩溃** — `internal/cli/commands_extra.go:989–997`。
   - 场景与影响：执行 `schedule update --expires-in= --json <id>`。空参数应按明确规则拒绝或处理，不能崩溃。
   - 实测：`TestReviewCLIEmptyExpiryDoesNotPanic` 原版通过，重建版 nil 解引用；解析器返回 `(nil, nil)`，调用方直接解引用。
   - 最小修复：在更新入口先验证空值，再解引用解析结果。

5. **inspect 的 JSON 输出丢失原有外层字段** — `internal/cli/commands_extra.go:860–867`。
   - 场景与影响：`schedule inspect <id>` 的调用方读取 `result.schedule.id`。重建版直接输出 schedule 对象，破坏已有解析代码。
   - 实测：`TestReviewCLIInspectEnvelope` 原版通过，重建版没有 `schedule` 外层。
   - 最小修复：按该命令原有约定输出完整响应；逐命令核对输出形状，不把 create 的形状推广到 inspect。

6. **延迟执行改变旧 everyMs 记录的时间网格** — `internal/schedule/service.go:743–759`。
   - 场景与影响：10:00 开始的十分钟周期，延迟至 10:25 才 tick；下一槽应是 10:30。
   - 实测：`TestReviewLateIntervalKeepsOriginalGrid` 原版得到 10:30，重建版得到 10:35，周期逐次偏移。
   - 最小修复：跳过积压槽时，按原计划时刻加整倍数周期，不能改从当前时刻重新计时。

7. **半小时夏令时回拨漏跑一次** — `internal/schedule/cron.go:228–239`。
   - 场景与影响：`Australia/Lord_Howe` 的 `45 1 * * *`，在 `2026-04-04T14:30:00Z` 后查下一次，应得到 `14:45Z`。
   - 实测：`TestReviewHalfHourDST` 原版正确，重建版直接返回 `15:15Z`；漏掉第一次 01:45。该组另一个“第一次之后找第二次”子检查通过。
   - 最小修复：按实际时区偏移变化求重复时刻，不能假定所有回拨都是一小时。

8. **列表失去 Active/Ended 筛选** — `web/src/core/screens/schedules-screen.tsx:99–112,208–250`。
   - 场景与影响：用户已有活动计划任务，切到 Ended 查看结束记录，再切回 Active。重建版将两类任务混列，缺少该入口。
   - 实测：浏览器补测第一项原版通过，重建版找不到 Ended tab。代码只保留主机筛选。
   - 最小修复：恢复按已存在的派生 bucket 切换列表，并验证两个方向的切换。

9. **heartbeat 菜单暴露计划任务专属操作** — `web/src/core/screens/schedules-screen.tsx:286,325–339`。
   - 场景与影响：打开 heartbeat 的操作菜单，重建版显示“Run now”和“Pause”；与保留的公开产品边界及原 UI 不一致。
   - 实测：浏览器补测第二项原版为 0 个相关菜单项，重建版为 2 个。
   - 最小修复：恢复 `target.type === "new-agent"` 的操作可见性条件，保留 heartbeat 已有的编辑与删除入口。

## 工作流与接续

证据来自完整 `trace.jsonl` 及成功工具结果，关键片段另存为 `workflow-evidence.json`。行号均为 trace 行号。

| 判据 | 结果 | 证据与判断 |
|---|---|---|
| 业务写入前建立 work | 通过 | 98 写 work/scope，99 成功；116 才开始业务写入 |
| 保存足够精确的兼容契约 | 未通过 | work 将 CLI 概括为 JSON、清除参数、目标选择，未逐项保留原参数、输出外层与目标操作边界；完成时仍靠局部用例概括全部契约 |
| 从事实源机械枚举并逐项对账 | 未通过 | 有 `rg/find` 检索和粗粒度能力表，未把实际来源逐项映射；最终 UI 能力丢失，scope 仍全写已覆盖 |
| 行为单元前后更新检查点 | 未通过 | 116 后已跨调度、CLI、前端等单元，直到 240 才集中更新；收尾 418 才再次更新 |
| 自然压缩后先读取检查点 | 未通过 | 340–341 压缩；342 起直接读代码，350/360 修改业务；402 才重读 work，此前已有 30 次工具调用 |
| 原测试完整性 | 通过 | 1,087 份原测试摘要不变；新增 worktree/DST 测试通过，但未覆盖本次补测边界 |
| 外部行为验收 | 未通过 | 首次 CLI 验收失败，补测确认另外 8 项问题 |
| 完成声明与证据相符 | 未通过 | 418 标记 complete；最终称全部行为门通过，与外部结果不符 |
| Memory 内容边界 | 通过 | 没有写入临时实现摘要或未确认承诺；被测项目只创建 work |
| 项目与临时路径约定 | 未通过 | 未观察到外部答案读取、原仓库写入或生产 daemon 命令，但 252、260、266、274、292、310 等将日志写入固定 `/tmp` |

压缩摘要保留了任务大范围、关键契约和待复核事项，模型也继续核对了协议与实现。错误不能简单归因于压缩：CLI 参数和 JSON 形状等问题已存在于压缩前的 152，列表实现写于 218；归档问题在 360 只补了 heartbeat 排除条件，仍遗漏 false 设置。

这一轮更明确的失败机制是：以已有测试集合代替完整契约对账，工作记录回写稀疏，最终把“所跑检查通过”扩大成“全部行为通过”。这些是本轮证据支持的判断，不能由单次样例推出模型或技能的普遍可靠性。

## 完整性与证明边界

- `integrity.json` 确认冻结 corpus、原测试、199 份协议/客户端/公开文档，以及安装技能与验收摘要一致。基线分支仍是单提交、无 remote。审查没有改写重建业务实现。
- 原项目的 Git 状态前后相同，但 HEAD 从 `f3aa7bd` 前进至 `05f8205`，期间 3 个提交涉及 7 个 CI/E2E 文件。变化文件的前后 SHA 分别匹配对应提交；见 `original-before.json`、`original-after.json`、`original-concurrent-changes.log`。因此不声称共享原仓库在整段时间内完全未变；固定评测输入没有受这些提交影响。
- 工具审查未发现读取外部答案或操作原仓库、生产服务。目录提示不是文件系统沙箱，无法据此证明所有子进程的系统调用级隔离。pi 的压缩元数据 `modifiedFiles` 为空，但 bash 实际写入了业务文件；文件访问审查必须回到工具参数与结果。
- 首次独立 CLI 探针的子测试闭包捕获父 `t`，未知 flag 后又出现 `FailNow on a parent test`。未知 flag 的失败仍成立，但该次后续 CLI 检查没有走完。补充探针显式传递当前 `t`，各项失败独立留存。
- pi 曾把 relay 单测失败称为既有问题。本次在原版与重建版单独重跑该测试，两者均通过；当时失败原因无法判定，未计入 9 项新增问题。
- 覆盖本任务定向链路及上述边界；未运行全仓库测试、真实外部模型提供方、原生移动端宿主或性能/成本对照。9 项是已证实的问题，不是缺陷总数上限。

## 复核入口与后续

- 首次运行与自动验收入口：[标准评测流程](../../../tools/evaluation/README.md#大型仓库的成熟功能重建)。输入与判据在 `tools/evaluation/cases/byspace-schedules/`。
- 补充 Go 探针：[review_test.go](review_test.go)。两份 `review-01/result.json` 保存相同探针摘要与命令；复跑时创建空的 `internal/byevaluation/`，通过保存的 overlay 注入，结束后移除空目录。
- 浏览器探针：[review-browser.spec.ts](review-browser.spec.ts)。临时复制到副本 `web/e2e/browser/evaluation-review.spec.ts`，按 `review-browser-01/result.json` 的命令在新的输出目录运行，结束后移除临时测试文件。环境沿用运行器的 `repository_env`。
- 运行目录的 `review.md` 保存逐项工作流结论，`review-result.json` 保存机器可读摘要。原首次失败、补测失败及模型完成声明均保留。

后续优先修复上述业务缺陷，并把精确兼容项纳入下一版冻结验收；评估技能调整时另起新运行。工作流改进优先针对单元前检查点和真实入口对账，本轮没有修改技能规则来覆盖已发生的执行结果。

评审结论：先修复 1–9，再重新验收。需要你看的：relay 当时失败原因、严格文件系统隔离和跨运行可靠性仍无法判定。
