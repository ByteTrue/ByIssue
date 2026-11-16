# 计划任务重建的评审范围

事实源：`tools/evaluation/cases/byspace-schedules/rebuild.json` 与运行目录的 `seed.json`。生成清单入口：`python3 -c 'import json; s=json.load(open("/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-rebuild-01/seed.json")); print(*s["removed_files"], sep="\n"); print(s["removed_functions"])'`。

25 项均已审查。这里的“已覆盖”表示完成来源映射与评审；重建行为仍有失败，见 [review.md](review.md)。下表实现路径相对被测 `project/`，未恢复原文件名而合并到其他文件的项按行为核对。

| 来源项 | 所属行为单元 | 覆盖状态 | 覆盖依据 |
|---|---|---|---|
| internal/cadence/cadence.go | CLI 时长 | 已覆盖 | 同路径重建；时长与拒绝不可表达周期的独立检查、原测试通过 |
| internal/schedule/cron.go | 日历计算 | 已覆盖 | 同路径重建；常见 DST/日历通过，半小时回拨未通过（问题 7） |
| internal/schedule/schedule.go | 调度与持久化 | 已覆盖 | 合入 service.go/types.go；patch、运行、持久化通过，恢复保留与旧周期未通过（问题 1、6） |
| internal/server/schedule_runner.go | agent 与工作区执行 | 已覆盖 | 同路径重建；原 server 定向用例及新增 worktree 用例通过；恢复清理问题归 service |
| internal/cli/commands_extra.go::runHeartbeatCmd | CLI 命令 | 已覆盖 | 拆成命令分派与 runSchedule*；原用例通过，公开 CLI 补测失败（问题 2–5） |
| internal/cli/commands_extra.go::resolveScheduleProvider | provider 解析 | 已覆盖 | 同名 helper；独立 provider/model 创建及原参数拒绝用例通过 |
| internal/server/ws_agent.go::handleScheduleMessage | RPC 路由 | 已覆盖 | 移至 schedule_runner.go，server.go 分派保留；CLI/RPC、浏览器创建/更新实际到达 |
| internal/server/ws_agent.go::parseScheduleUpdate | patch 语义 | 已覆盖 | 由 schedule_runner.go::handleScheduleUpdate 内联解析；null/缺省逐字段审查，浏览器更新通过 |
| internal/server/ws_agent.go::decodeOptional | null 与缺省 | 已覆盖 | decodeNullableString/decodeNullableInt 与配置字段 presence 判断替代；独立 patch 保留/清除通过 |
| internal/server/ws_agent.go::scheduledRunOutput | 运行输出 | 已覆盖 | 同名函数保留在 ws_agent.go；server runner 调用和执行输出定向测试通过 |
| web/src/core/components/schedules/cadence-editor.tsx | cadence 编辑 | 已覆盖 | 内联至 schedule-form-sheet.tsx；预设、表达式、时区输入已读，原浏览器 cadence 用例通过 |
| web/src/core/components/schedules/schedule-form-sheet.tsx | 表单弹层 | 已覆盖 | 同路径重建；7 项浏览器覆盖创建、编辑回填、关闭、移动弹层、归档与隔离设置 |
| web/src/core/components/schedules/schedule-row.tsx | 行与操作 | 已覆盖 | 内联至 schedules-screen.tsx::ScheduleRow；heartbeat 操作边界未通过（问题 9） |
| web/src/core/components/schedules/schedules-table.tsx | 列表展示 | 已覆盖 | 内联至 schedules-screen.tsx；Active/Ended 筛选未恢复（问题 8） |
| web/src/core/hooks/use-schedule-mutations.ts | 写入与反馈 | 已覆盖 | 同路径重建；创建/更新通过真实浏览器；行操作服务端 error 反馈路径仅代码审查，未逐种故障注入 |
| web/src/core/hooks/use-schedules.ts | 数据加载 | 已覆盖 | 同路径重建；主机状态/query key 已读，浏览器加载与刷新可达 |
| web/src/core/schedules/aggregated-schedules.ts | 跨主机汇总 | 已覆盖 | 同路径重建；原聚合单测与非默认主机浏览器用例通过 |
| web/src/core/schedules/schedule-cadence-options.ts | cadence 选项 | 已覆盖 | 同路径重建；原预设及 legacy 显示单测通过 |
| web/src/core/schedules/schedule-derivation.ts | 派生状态 | 已覆盖 | 同路径重建；原失效/完成/目标派生单测通过；页面没有使用 bucket 做筛选 |
| web/src/core/schedules/schedule-form-model.ts | 表单模型 | 已覆盖 | 同路径重建；原模型单测与浏览器 hydration 通过；未宣称所有异步交错均验证 |
| web/src/core/schedules/schedule-project-targets.ts | 主机与项目 | 已覆盖 | 同路径重建，另补 utils/projects.ts 的 projectKind；项目身份与选择用例通过 |
| web/src/core/schedules/use-schedule-form-model.ts | 表单接入 | 已覆盖 | useState 创建单实例，useSyncExternalStore 订阅；原生命周期单测通过 |
| web/src/core/schedules/use-schedule-form-provider-snapshot.ts | provider 异步恢复 | 已覆盖 | 同路径重建，另加 use-schedule-form-inputs.ts；跨主机回填与模型保存的原浏览器用例通过 |
| web/src/core/screens/schedules-screen-state.ts | 页面状态 | 已覆盖 | 同路径重建；原页面状态单测通过 |
| web/src/core/screens/schedules-screen.tsx | 页面入口 | 已覆盖 | 同路径重建；列表/创建/编辑入口可达，筛选和操作边界有实测回归（问题 8、9） |

附带变更已审查：`combobox.tsx`、`select-field.tsx` 增加搜索输入 test ID 传递，`utils/projects.ts` 传递项目类型。协议、客户端、公开文档及原有测试摘要均未变。没有因原文件被合并而直接判为功能缺失。
