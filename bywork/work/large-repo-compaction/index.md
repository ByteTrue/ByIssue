---
kind: work
status: complete
current_unit: "大型仓库自然长任务评测与独立评审已完成"
next_action: "无；后续业务修复、技能调整或复评另建 work"
must_hold: "DeepSeek Flash；原项目只读；副本独立分支；删除副本中的 v1 产物；持续完成真实大需求；压缩次数由运行决定；原版实现与独立验收留在项目之外"
proof_gap: ""
---

# 大型项目与真实上下文压缩评测

评测完成。被测功能和 bi v2 工作流执行均未通过；1 次真实自然压缩已证实。完整结论、9 项新增问题与修复建议见 [review.md](review.md)。

## 目标与边界

用户主要使用 DeepSeek，希望从现有项目中选择一个大型仓库，建立专用评测副本，并构造能验证真实上下文压缩的任务。沿用当前标准评测的独立验收与证据保留方式。

## 已定方案与约束

- 候选选择 BySpace。固定提交有 3,498 个跟踪文件，2,941 个源码文件约 572,136 行；完整源码导出到仓库外的专用目录，每次运行从固定副本重新复制。
- 主模型沿用 `bytetrueapi/deepseek/deepseek-flash`，thinking medium。此次不扩展模型矩阵。
- 在副本建立专用评测分支，删除一个成熟功能的实现，给出完整需求，让 pi 用 v2 工作流持续恢复。功能应跨多个行为单元，最终由独立验收和代码评审判断效果。
- 副本中的 v1 `bywork/` 产物全部移除。原版实现留在被测项目之外；评测分支从删减后的快照建立，不提供可直接还原答案的 Git 历史。
- 同一 pi 会话持续执行，宿主按实际上下文用量自然压缩。次数由运行决定；只观察原生事件、摘要与接续动作，不人为安排压缩次数，不做压缩/不压缩对照。
- 本轮将 pi 原生自动压缩阈值设为 400k，保留最近 20k；模型窗口仍为 1M，通过 reserveTokens=600000 配置。阈值沿用本机扩展的 400k 策略，但原生机制可在连续工具轮次间检查。记录该运行级设置，保持全局配置不变。
- 独立验收通过公开 Go API、真实 CLI/RPC 测试宿主及现有前端/浏览器入口验证。新增验收文件留在被测项目外；已有测试完整性单独核对。原版已有缺陷与重建回归分开报告。
- 原项目不修改，不启动或连接现有 BySpace daemon；评测使用独立 home 与临时目录。所有产物保留在评测副本，主仓库只保留任务、验收、运行入口与必要证据。

## 评测交付的行为证明

本 work 收尾的是任务构造、连续运行与独立评审。被测功能和工作流的失败结论保存在证据列及评审报告中。

| 行为路径 | 真实入口 | 操作 | 应观察到 | 证据 | 结果 |
|---|---|---|---|---|---|
| 固定大型副本 | 本地 Git 提交导出 | 创建 corpus，再复制运行目录并核对来源变化 | 提交、文件清单、摘要与规模可复核，原项目同期变化单列 | manifest.json 与 integrity.json：固定源码摘要一致；原仓库同期 3 个提交单列 | 通过 |
| 评测分支 | 独立副本的 Git | 删除目标实现与 v1 产物，提交删减基线 | 分支有真实缺口，旧版工作记录和答案历史不可直接读取 | runs/schedules-rebuild-01/seed.json；分支 eval/rebuild-schedules，单提交 6d58be4，无 remote，工作区干净；byissue 已移除 | 通过 |
| 功能恢复评测 | 副本中的真实入口 | 给出完整任务，持续运行后执行独立验收 | 标定原版与删减版，判定重建业务和兼容性，保留首次失败 | acceptance、review-01、review-browser-01：业务未通过，9 项新增问题已复现并与原版核对 | 通过 |
| 真实压缩 | pi 自动压缩事件 | 持续执行长任务 | 有压缩时保存次数、原因、用量与摘要；未触发时如实记录 | compactions.json：1 次 threshold、1 份匹配的持久摘要，无错误；报告上下文峰值 401,333，压缩前投影 401,807 token | 通过 |
| 压缩后接续评审 | 压缩后的业务工具调用 | 按 trace 核对检查点读取与实际修改顺序 | 能判定是否按 v2 从检查点接续，缺口有逐动作证据 | workflow-evidence.json：接续未通过，先执行 30 次工具调用且修改代码，才读取 work | 通过 |
| 最终评审 | 独立验收、实现 diff 与工具记录 | 检查恢复范围、关键副作用和工作流 | 分开报告业务问题、工作流缺口与压缩证据；失败保留 | [review.md](review.md)、[scope.md](scope.md) 25 项来源对账及运行目录 review-result.json | 通过 |
| 维护回归 | 离线检查与 release-check | 检查新增运行器及现有场景 | 错误、截断、伪压缩不能误记成功；已有检查通过 | [release-check-final.log](release-check-final.log)：checker、自测 22/22、初始化、运行器 13/13、实际评测安装副本比对全部通过；早期一轮输出留 `release-check.log` | 通过 |

## 证据与决定

本机 pi 配置列出的 DeepSeek Flash context window 为 1M。安装的 pi 文档提供 RPC `compact`、`get_state`、`get_messages` 与 `get_session_stats`，可以在不伪造摘要的情况下直接验证真实压缩。

本机 Go 启动受过期 GOROOT 环境变量影响；仅在评测子进程清除 GOROOT 后，`go version` 返回 go1.27.3 darwin/arm64。

用户进一步明确：采用成熟功能删除后重建的长任务，不预设两次压缩，也不采用压缩/不压缩对照。此前的离线配置新功能与固定两次压缩方案停止，已写但未运行的场景和控制逻辑移除。已冻结的完整 BySpace 副本与构建证据继续复用。

准备结果：删除 19 个实现文件、6 个 Go 函数，共 6,422 行；移除 303 份 v1 工作文档。已有协议、调用方、公开文档和测试保留。依赖副本可解析 Vitest 与 Playwright。运行根为 `/Users/zijie/workspace/ByIssue-evaluation/`，原版 corpus、删减分支和验收证据分别存放。

原版首次预检 `preflight/schedules-original/acceptance-01/`：日历/DST、持久化 patch、运行与恢复三组独立检查通过，定向 Go 回归、构建、vet、51 项前端单测和类型检查通过。独立 CLI 检查发现原版 update 发送嵌套 patch，而服务端读取顶层字段，导致返回成功但不更新。保留该验收与失败，按原版既有缺陷单列。浏览器首次失败来自缺少 relay 的 dist，补齐构建后复验。

第二次原版定向预检 `acceptance-02/`：relay 构建通过，7 项浏览器检查全部通过；独立验收只剩 `TestIndependentCLIAndRPC/update-clears-fields` 既有失败。删减基线 `runs/schedules-rebuild-01/baseline/` 的公开探针、Go 构建/回归和前端相关检查均因实现缺失而失败，依赖构建成功。最终验收任务摘要已保存为 `preflight.json`，原项目跟踪文件摘要保存为 `original-before.json`。

恢复范围按 `seed.json` 的删除清单在 [scope.md](scope.md) 逐项审查。最终结论不能把原版既有失败当成重建新增缺陷，也不能沿用原版通过结果代替重建验证。

已执行 `run_repository.py --run /Users/zijie/workspace/ByIssue-evaluation/runs/schedules-rebuild-01 --model bytetrueapi/deepseek/deepseek-flash --thinking medium --compact-at 400000 --timeout 14400`。后台 shell `sh_1d824e9eb001pPIlib1ou9L74b` 已结束。pi 耗时 2,005.72 秒，172 条助手消息，211 次工具调用；独立验收耗时 101.71 秒。原测试未修改，模型与技能摘要一致。pi 宣布恢复完成并将自己的 work 标为 complete，外部验收判为未通过。

Memory 更新了大型长任务采用真实功能重建、自然压缩、原版标定及 DeepSeek Flash 优先的评测边界，并记录 pi 压缩元数据可能漏掉 bash 文件读写的外部事实。本轮没有改变技能包。

补充复测 `review-01/`：相同 [review_test.go](review_test.go) 通过 Go overlay 分别驱动原版和重建版公开 API/CLI，6 组在原版通过，在重建版失败。确认 heartbeat 创建拒绝已设置的 agent ID、inspect JSON 外层丢失、空到期参数 panic、重启忽略保留工作区设置、逾期 every 周期漂移，以及 Lord Howe 半小时回拨漏掉第一次 01:45。外部日志和探针摘要保留，重建实现未改。

浏览器补测 `review-browser-01/` 的两项在原版通过、重建失败，确认 Active/Ended 筛选缺失、heartbeat 菜单出现计划任务专属操作。探针为 [review-browser.spec.ts](review-browser.spec.ts)，临时测试文件已从两份副本移除，截图与 Playwright trace 留在各自证据目录。

工具记录：首次 work 写入 98–99，早于业务写入 116；此后跨多个单元直到 240 才更新。压缩 340–341 后先执行 30 次工具调用，350/360 已改业务代码，402 才重读 work。418 标 complete，最终完成声明超过独立验证所支持的范围。

完整性核对 `integrity.json`：冻结 corpus、1,087 份原测试、199 份协议/客户端/公开文档及技能、验收摘要均匹配。原仓库同期从 f3aa7bd 前进至 05f8205，共 3 个提交、7 个文件变化，前后 SHA 均匹配相应已提交版本，Git 状态不变；见 `original-concurrent-changes.log`。工具记录未见读取外部答案或写原仓库，但多次将日志写到固定 `/tmp`，违反临时路径约定。

pi 所称“原有 relay 失败”另用同一单测在原版与重建版定向标定，两者本次均通过。保留 pi 当时的失败，原因无法判定，不列入已确认新增回归。

完成核对：25/25 来源项已评审，正式报告与补充探针可复核；原冻结用例另存于运行目录 `case-snapshot/`，摘要匹配首次运行。维护检查通过，版本仍为 2.0.1；本轮主仓库改动未提交、未推送。需要你看的：原 relay 失败原因、严格文件系统隔离和跨运行可靠性仍无法判定；没有性能或实际成本提升结论。
