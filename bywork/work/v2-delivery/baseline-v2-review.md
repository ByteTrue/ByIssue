# 补全需求后的旧技能基线

## 结论

业务验收与工作流均未通过。模型恢复了主体功能，所有原有定向回归和浏览器检查通过；外部探针仍有两处失败。它把 work 标为 complete 时，自己的 RPC 证明行甚至仍写着「待跑 / 未验证」。

该运行使用旧技能、补全后的 v2 任务。与首次长任务相比输入已经变化，结果差异不能归因于技能优化。候选一正在使用同版任务独立运行。

## 运行证据

根目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-baseline-v2-01/`。

- 模型 `bytetrueapi/deepseek/deepseek-flash`，medium，pi 1.5.2，持续单会话。
- pi 正常结束，用时 2,094.89 秒；163 条助手消息，197 次工具调用。
- 原生压缩 0 次，上下文峰值 382,498，未达到 400k 阈值。接续能力无法从本轮判定。
- `acceptance/results.json` 的 12 组自动检查中，独立 Go 探针失败，其余 11 组通过。浏览器包含原有 7 项与外部 2 项检查。
- `integrity.json` 确认 1,087 份原测试和 179 份协议、客户端与公开文档原样保留；安装技能与冻结用例摘要一致，corpus 未变，分支仍只有一个基线提交且无 remote。审查没有改变业务产物。
- 完整事件在 `trace.jsonl`。`trace-index.md` 索引全部调用，长命令与去重后的工具输出保存在 `tool-calls/`；关键工作流片段另存 `workflow-evidence.json`。

## 独立验收失败

### 1. 重启时无视显式保留工作区

`TestReviewRestartKeepsExplicitlyRetainedWorkspace` 失败。已写入 agent 的运行记录具有 `archiveOnFinish=false`，重启仍调用了工作区归档 hook。

实现位置为 `project/internal/schedule/schedule.go:1029–1031`：发现运行工作区就加入归档列表，没有采用正常结束时的保留条件。此次任务已经明确重启也遵守正常归档约定，固定原版对同一检查通过。这是有充分输入依据的功能缺陷。

### 2. CLI 忽略位置参数中的新提示词

`TestIndependentCLIAndRPC/update-clears-fields` 失败。命令清除了 maxRuns 和 expiresAt，但 `schedule update ... <id> "updated prompt"` 返回的 prompt 仍为旧值。

代码在 `project/internal/cli/commands_extra.go:881–886` 只从 `--prompt` 填充更新请求，没有取 id 后的位置参数。固定原版接受该位置参数，但其另一个已知旧错是发送嵌套 patch，导致更新内容整体未保存；不能将相同的表面失败都算作重建新增回归。

这项还有评测输入缺口：保留的公开文档只展示了更新 cadence/限制，v2 任务补充了清除 flags 与输出外层，却没有明确位置提示词。该检查记录了真实兼容差异，但不足以单独证明模型遗漏了可见的精确要求。后续冻结输入要补明这一形状；本轮原始验收保留。

## 工作流审查

以下行号是 `trace.jsonl` 行号。

| 判据 | 结果 | 证据 |
|---|---|---|
| 业务写入前建立 work | 通过 | 82–83 首建 work；84–85 保存 scope；94–95 才写首个业务文件 |
| 保存精确契约与来源 | 未通过 | `initial-work.md:36–46` 主要按测试包组织，多个操作挤在同一行；CLI 的已知 JSON 外层没有保存，重启保留条件没有展开。第 51 行直接认定「现有测试保留完整契约」 |
| 来源逐项对账 | 未通过 | scope 列的是测试文件和粗粒度文档分类。392 将全部项改为已覆盖，394 才重新 find 实现文件；没有把操作与实际断言逐项对应 |
| 单元切换前保存检查点 | 未通过 | 106 在 server 实现前更新；152 写 CLI 前没有 CLI 单元检查点。162 写「前端列表」，200–250 跨数据、表单与屏幕，264 才改为表单单元；354 新增 CLI 更新检查，366 才集中回写 |
| 接续先读检查点 | 无法判定 | 未发生压缩；本次没有新会话接续 |
| 原测试完整性与有效新检查 | 通过 | 1,087 份原测试摘要未变。新增 CLI 检查在 357 报「nothing to update」，修复后 361 通过，确实挡住过真实错误 |
| 独立业务验收 | 未通过 | 重启保留探针与 CLI 更新探针失败，见上述输入边界 |
| 完成声明与自身证据一致 | 未通过 | 392 标 complete；最终 work 第 40 行仍是 RPC「待跑 / 未验证」，第 55 行却写行为门通过。396 最终回复称真实入口验证通过，遗漏外部探针中的保留失败 |
| Memory 筛选 | 通过 | 只创建当前 work，没有将实现摘要或临时状态写入 Memory |
| 目录及生产服务边界 | 通过（工具记录范围） | 全部调用索引与参数未发现读取外部答案、写原项目或调用生产 daemon 控制；临时服务使用测试宿主和 TMPDIR。目录约定仍不等于系统调用级沙箱 |

模型多次用 shell 管道截取测试输出，工具本身返回 0 不能证明测试通过。此次确实读取并修复了多项失败；上述判定已回到实际输出，不依据 shell 退出码代替测试结论。

## 其他边界与后续判断

- 模型本轮确实遇到 `TestRelayTerminalStopsAfterLastClientWithoutStoppingLocal` 的 `websocket: message too big`，证据在 trace 322–323；最后排除此测试后 server 通过。它是否与重建有关仍未做本轮同条件原版标定，模型将其称为「无关」属于推断。
- 后续同条件定向标定已完成：`preflight/relay-comparison-v2-01/` 对独立原版和基线运行相同的 `go test ./internal/server -run '^TestRelayTerminalStopsAfterLastClientWithoutStoppingLocal$' -count=1 -timeout=90s -v`，均通过。原失败本次未复现；这不足以确认它是原版旧错，也不能抹去首次失败。
- 本次定向审查足以否定完成结论，未把代码恢复的所有边界重新审计一遍；两个自动失败不是缺陷总数上限。
- 单元前写入和完成逐行核对仍是候选一需要证明的核心。此次零压缩不能用来判断其恢复行为，也不能为下一次运行人为安排压缩。
