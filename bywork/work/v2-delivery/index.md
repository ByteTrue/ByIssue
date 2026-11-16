---
kind: work
status: complete
current_unit: "全部交付门槛验证完成：大型重建连续两轮、A/B 对照、三个短场景、部署核对"
next_action: "无；提交、推送或发布由用户另行发起"
must_hold: "持续优化与实测至可交付；DeepSeek Flash（大型任务 thinking max）；原项目只读；独立副本与验收；自然长任务不安排压缩次数；保留首次失败；技能只写通用原则，不写工具级操作规程；通过率对比不追求单次全绿"
proof_gap: ""
---

# bi v2 持续优化与交付验证

用户已授权持续执行优化、评测、再优化，直到有证据支持成熟、有效、可交付。上一轮[大型重建评审](../large-repo-compaction/review.md)是本轮的失败依据，原始记录保留。

交付已完成。方法论、最终结论、规则演变与局限的汇总留档见[最终评测报告](final-evaluation-report.md)；本 index 保留逐轮迭代记录。v2 设计阶段的一手研究稿（真实失败取证、外部材料适用边界、被否方案）归档为[设计方向研究稿](research-direction.md)与[证据矩阵](research-evidence-matrix.md)。v2 相对 v1（main）的逐文件血缘取证见[血缘审计](provenance-audit.md)：工作流核心为重写，7 份原则材料带 v1 血缘（grilling/writing 逐字未动）。7 份原则材料的留/改/换评判见[原则材料评判台账](principles-review.md)（已完成并实施于 2.1.2：3 留 4 微改，domain-modeling 准入收紧为 AND）。后续 ByIssue → ByWork 改名是独立新目标，见 [rename-bywork](../rename-bywork/index.md)。

## 目标与边界

修复精确契约遗漏、行为单元检查点稀疏、压缩后接续越过检查点和完成声明失真。修改范围包括技能入口、相关 references/templates、说明和评测设施。业务实现由被测模型在独立副本生成；独立审查回到公开入口与完整工具记录。

## 已定方案与约束

- 使用 `bytetrueapi/deepseek/deepseek-flash`、medium、pi 持续会话。大型任务沿用 400k 原生自动压缩阈值与最近 20k，次数自然产生。原仓库及前轮运行保持只读。
- 先冻结旧技能和任务材料。补测固化为新验收，先在固定原版及已知错误产物标定。新旧技能使用同版任务与验收；任务缺少精确接口时补公开契约并单列输入变化。
- 技能调整解释通用动作和判断原因，具体题目的参数、JSON 形状、时区与 UI 答案只属于评测材料。
- 每轮记录业务、工作流及证据完整性结果，首次失败单独保留。发生新失败就定位机制、作最小修改、再评测；不能以不断加检查掩盖执行无效。
- 交付门槛：同一最终候选在大型重建上连续两次独立运行通过公开行为验收和工作流审查；至少一轮自然发生压缩并正确接续；一个未参与本轮改写的新业务任务通过；既有跨会话与 Memory 场景通过；发布检查与实际安装副本核对通过。测试结果只支持这些覆盖范围，不宣称跨模型可靠性或速度提升。
- 用户已授权自主选择迭代方向。交付门槛属于本轮可操作判据；若多轮无改善或出现无法消除的宿主限制，记录真实阻塞及剩余边界，不降低门槛后宣布完成。

## 行为证明

| 行为路径 | 真实入口 | 操作 | 应观察到 | 证据 | 结果 |
|---|---|---|---|---|---|
| 验收区分新增回归与原版旧错 | 冻结原版、前轮重建副本 | 运行同版外部 API、CLI 和浏览器验收 | 原版旧缺陷单列，已知九项回归能独立变红，失败不会截断其余独立检查 | 两份 `preflight/*-v2/acceptance/`：原版仅旧更新保存缺陷失败；前轮产物九项回归均失败，后续 CLI 子检查继续执行 | 通过 |
| 契约与检查点改进有效 | 安装后 DeepSeek Flash 的完整工具记录 | 在干净删减副本持续重建 | 实现前记录精确契约，单元切换先落检查点；对账逐入口；声明不超出证据 | 最终候选三十两轮（`runs/schedules-candidate-30-01/02`）：work/scope 先于业务写入，12 组验收全零，`status: complete` 且 `proof_gap: ""` 与外部验收一致；A/B 对照（`runs/ab-protocol-review.md`）无技能臂 0/3、失败集中于契约细节。中间 25 轮迭代的失败与修复台账见正文与历次 `review.md` | 通过 |
| 自然压缩接续 | pi 原生事件、摘要和压缩后的工具记录 | 持续执行至自然压缩或任务结束 | 接续后动作与检查点一致（结果判据）：做对下一件事、状态诚实、缺口不丢 | 候选三十两轮各 1 次自然压缩（峰值 399945/401355），压缩前检查点的 `next_action` 与压缩后动作方向一致，最终业务全绿、状态合法（`runs/schedules-candidate-30-review.md`）；旧「首读工具名」判据经候选十五至二十一证明不可执行且未拦截真实事故，经用户确认废弃 | 通过 |
| 重复运行 | 同一最终技能和冻结任务的两个新副本 | 分别完整运行及独立验收 | 两次业务与工作流均通过，输入与安装摘要一致 | `runs/schedules-candidate-30-01/02`：同一候选三十快照、同一 case-v5、同树哈希，两轮 12 组验收全零、既有测试未改、工作流审查逐项通过 | 通过 |
| 新任务泛化 | 未用于技能改写的新业务任务 | 冻结需求与验收后运行 | 从真实入口通过独立验收，工作流符合管理强度，完成声明准确 | `runs/heldout-webhook-c30-01`：heldout webhook-inbox 业务通过；review.md 六项全过（契约先落盘、真实 HTTP/CLI 原始 transcript、scope 46 项全覆盖、无合格 Memory 输入时不硬造） | 通过 |
| 跨会话与长期记忆回归 | ledger、memory-selection | 使用最终候选运行现有场景 | 业务、契约接续、检查点顺序与 Memory 筛选均通过 | `runs/ledger-c30-01`：两阶段业务通过，review.md 七项全过（第一轮 in_progress 停在 report 前、第二轮先读原 work 并更新新约束后实现）；`runs/memory-selection-c30-01`：业务通过，review.md 三项全过（长期决定入 Memory、配置数值与本轮状态留 work、未擅自实现重试） | 通过 |
| 可安装交付 | release-check 与实际部署副本 | 维护检查、安装、摘要对比 | 结构、自测、初始化、运行器和部署核对通过 | `bash tools/release-check.sh ~/.pi/agent/skills/bw` 全绿：checker、22/22 植入反例、初始化 3/3、运行器 14/14、部署副本 diff 一致；宿主已加载 2.1.0（技能描述更新生效）；VERSION 与 CHANGELOG 2.1.0 对齐 | 通过 |

## 证据与决定

运行产物放在 `/Users/zijie/workspace/ByIssue-evaluation/`，每轮使用新目录。每轮详细审查在同目录保存，当前 work 只收录会改变后续判断的结论与证据入口。

- 旧技能保存到 `snapshots/v2-delivery-baseline/skills/bw/`，原任务与验收保存到同目录 `case-v1/`，有逐文件摘要。
- v2 任务补充了原材料未完整暴露的 CLI 精确参数、响应外层及 UI 筛选要求，并消除了重启清理与显式保留工作区之间的歧义。该输入变化须与技能效果分开；新旧技能都会使用新任务。
- 新验收固定到 `snapshots/v2-delivery-input/tools/evaluation/cases/byspace-schedules/`。修复父测试闭包，独立保存各 CLI 操作失败，并将首次补测的六组 Go 与两项浏览器检查纳入自动验收。原始失败记录未覆盖。
- 两份标定副本为 `preflight/schedules-original-v2/` 与 `preflight/schedules-known-failures-v2/`；从前轮原版和失败产物独立克隆，前轮目录未改。
- 候选一冻结在 `snapshots/v2-delivery-candidate-1/`。将散落的检查点规则改为接续先读、换单元先存、单元结束回写和收尾复核；证明从需求到证明行、再到实际断言双向核对。同步了相关 reference、模板和中英文 README，初始化脚本的数据结构无需改变。维护检查与 diff 检查通过，实际执行效果仍待实测。
- 对照的两份删减项目已建立在 `runs/schedules-baseline-v2-01/`、`runs/schedules-candidate-1-01/`，源码树哈希均为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。旧技能与首次长任务的安装摘要一致，新候选与当前技能一致；证据为候选快照内 `comparison-integrity.json`。
- 标定还暴露了前轮被首个失败遮住的 pause/resume 输出不兼容：原版返回含 schedule 的 JSON，前轮产物返回制表符文本。日志在 `preflight/schedules-known-failures-v2/acceptance/independent.log:81–90`；原版相同操作通过。前轮报告的九项是已知下界，新增两项不覆盖旧报告。
- 新业务场景为 webhook inbox，从签名 HTTP 接收到 SQLite 幂等存储，再以 CLI 查询和原子导出。它在候选一冻结后设计，尚未运行模型；完整接口在用例 `project/contracts.md`，验收在项目之外。
- 新场景最终冻结到 `snapshots/v2-delivery-heldout-v2/cases/webhook-inbox/`。旧 heldout 快照未用于模型运行。反例检查证明总是输出成功的空实现被拒绝；正向标定与真实原子替换、常量时间比较的代码审查留待模型产物。
- 基线已用 `run_repository.py` 启动，后台任务为 `sh_1d884f38a0010CIkD0qb5FrFXM`。沿用 DeepSeek Flash medium、400k 自然压缩阈值、四小时上限。结束通知会触发接续，不轮询、不重复启动同目录。下一次候选启动使用冻结候选一与同一 case-v2 路径。
- 基线自然结束，pi 退出 0，耗时 2,094.89 秒，197 次工具调用；实际上下文峰值 382,498，原生压缩 0 次。独立验收在工作区显式保留的重启恢复、CLI 同时更新提示词与清除限制两处失败，其余 11 组自动检查通过，原测试摘要未变。首次证据在 `runs/schedules-baseline-v2-01/acceptance/`；工作流及额外实现缺口仍待审查。
- 基线完整工具索引、工作记录及失败路径审查已完成，见 [baseline-v2-review.md](baseline-v2-review.md)。工作流未通过：多个单元写后才更新检查点，收尾 RPC 证明行仍未验证，却宣称 complete。原测试与冻结来源完整。未发生压缩，接续仍无法判定。
- 基线的 CLI 位置提示词失败单列为输入缺口：被测项目的公开材料没有明确这一精确形状，不能单独用来证明模型漏掉可见要求。下一版任务要补明；现有 v2 首次结果和冻结输入继续保留。
- 候选一已启动，后台任务 `sh_1d8a7527c001h7xwTnUgx3z1en`，运行目录 `runs/schedules-candidate-1-01/`，使用与基线完全相同的 case-v2 快照、模型和压缩设置。
- 下一版输入固定到 `snapshots/v2-delivery-input-v3/tools/evaluation/cases/byspace-schedules/`。与 v2 相比仅 task.txt 增加了位置提示词定义，验收、删除边界和工作流判据摘要相同。后续新运行使用 v3，并明确输入差异；当前候选的 v2 对照仍独立保留。
- relay 同条件标定保存在 `preflight/relay-comparison-v2-01/`。独立原版和基线定向复跑均通过；原失败未复现，不能认定为原版旧错或重建回归。保留首次失败与此判定边界。
- [候选一前缀审查](candidate-1-prefix-review.md)保存了 297 条已发生事件。初始先存得到执行，但 RPC/CLI 和前端表单/界面仍跨单元先写后记；重启保留条件在初始契约中丢失。候选一完整验收与收尾尚未返回，不从前缀推定最终功能结果。
- 候选一现已自然结束，pi 退出 0，用时 2,800.67 秒，321 次工具调用；一次 threshold 压缩与持久摘要匹配。独立 Go 探针和浏览器兼容检查失败，其他 10 组检查通过；原测试摘要未变。完整审查从 `runs/schedules-candidate-1-01/` 接续。
- 候选一浏览器错误快照显示 `Active (1)` / `Ended (0)` 页签和行内 edit/delete 按钮，原探针固定无计数名称和 actions 菜单，尚未触及待验操作。修订只调整控件定位，仍验证切换后列表内容以及 heartbeat 可用/不可用操作；首次日志继续保留。
- v4 浏览器标定完成，证据在 `preflight/browser-compat-v4-01/`：原版与候选一各 2/2 通过，首轮错误产物 0/2。错误产物缺少 Ended 页签和 heartbeat 编辑，快照还显示 Run now/Pause。候选一首次浏览器失败更正为探针误报，原日志保留。
- [候选一正式评审](candidate-1-review.md)确认业务和工作流未通过。压缩后首读成功，但 trace 458 批量填绿并写非法 `status: done`，后续继续修改却未恢复进行中状态。不能把业务失败归因于压缩，也不能据本轮声称候选一更好。
- 进一步核对修正了「三项调度失败均为明确回归」的先前表述：延迟 tick 的兼容差异可复现，但 v2–v4 任务把跳过积压写在重启恢复项下，保留测试只覆盖准点 tick。下一输入明确正常延迟 tick 的跳槽规则；该差异不单独用于证明模型漏掉明确要求。重启保留与半小时 DST 均有明确可见要求。
- 下一轮输入冻结为 `snapshots/v2-delivery-input-v5/`，相对 v4 只有 `task.txt` 补普通延迟 tick 的跳槽与旧周期网格，验收摘要未变，可沿用已有标定。旧输入和首次结果全部保留；候选二与候选一的不同输入运行不直接组成技能效果对照。
- 候选一与旧技能同 case-v2 的静态结果页为 `reviews/candidate-1-case-v2/review.html`。业务、工作流及完整性分别展示，不以汇总比例替代各项结论。

## 候选二改写依据

本单元对应行为证明中的「契约与检查点改进有效」。候选一保留了规则，却没有改变按测试包大块实现的动作。此次改写让证明表成为当前工作的选择入口：先保存对话中的原始要求，再找测试证据；每次选一条用户行为，确认条件与副作用的断言，保存检查点后实现，运行后回写，再选下一条。

共同检查点仍以 `SKILL.md` 为唯一归属；`change.md` 写实现循环，`prove.md` 写契约与断言对应，模板只给填写指引。涉及 `SKILL.md`、两个 reference、work/scope 模板及中英文 README；核对初始化脚本与维护工具是否依赖旧结构。没有新增状态字段、文件类型或业务专项规则。

预期观察：新运行中用户例外仍保留；每个新行为首次业务写入之前已有相应检查点；结果回写引用实际断言；后续修复会重开受影响行。静态维护检查只证明结构一致，实际效果由新删减副本及独立评审判断。

候选二改写与同步已完成，维护检查及 diff 检查通过。初始化脚本只创建目录，字段结构和检查器契约未变，无需改脚本。继续使用现有冻结验收，不把业务答案加入技能。

候选二冻结在 `snapshots/v2-delivery-candidate-2/`，运行目录为 `runs/schedules-candidate-2-01/`，删减源码树仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`，输入为 case-v5。运行完成后业务未通过，正式审查见候选二目录的 `review.md` 和 `review-result.json`。它修复了候选一的重启保留、普通延迟 everyMs 网格和半小时 DST，但 CLI `--json` 仍输出人类可读文本。

候选三只改了通用规则：检查点接续先读变成第一项业务动作；每个行为必须有开始保存和验证后单独回写；CLI/API/协议证明必须保存真实调用者的原始输出或响应。`bash tools/release-check.sh --no-deploy` 通过。

候选三已冻结到 `snapshots/v2-delivery-candidate-3/`，运行目录为 `runs/schedules-candidate-3-01/`，继续使用 case-v5、DeepSeek Flash medium、400k 自然压缩阈值和四小时上限。后台任务为 `sh_1d92bd014001U7gByYvratbyQv`；完成后保留首次结果并做完整工具顺序审查。

候选三运行已完成：业务验收 12/12 通过，发生 1 次自然压缩；正式审查见 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-3-01/review.md` 与 `review-result.json`。工作流未通过：`trace` `[494–496]` 压缩后先修改源码，`[572]` 才读取 work；全程只有初始、一次中途和收尾的 work 写入，没有逐行为结束回写。

候选四冻结到 `snapshots/v2-delivery-candidate-4/`，运行目录为 `runs/schedules-candidate-4-01/`，仍使用 case-v5、DeepSeek Flash medium、400k 自然压缩阈值和四小时上限。相对候选三只改 `SKILL.md`、`references/change.md`、`templates/work.md`，并同步 README；`bash tools/release-check.sh --no-deploy`、checker 22/22、初始化 3/3、评测运行器 14/14 均通过。

候选四运行在 2,336.11 秒、199 条助手消息后被运行器中止：`[426]` 执行 `npx oxfmt .agents/skills/bw`，改动已安装技能的 `SKILL.md`、`domain-modeling.md`、`prove.md`、`quality.md`、`templates/scope.md`、`templates/work.md`；独立验收尚未运行，业务结果为无法判定。原始 `report.json`、`trace.jsonl` 和项目快照保留。

候选五只增加安装输入只读边界：`.agents/skills/bw`、评测用例和运行器材料不可格式化或编辑，流程记录写入项目 `bywork/`，技能修改回到技能源仓库。维护检查通过后另建候选五快照和运行目录，不复用候选四失败目录。

候选五运行完成但业务未通过：`report.json` 显示独立验收 0，11 个定向组通过，`web-compat` 失败；`web-compat.log:8–33` 的 heartbeat 场景找不到 `schedule-row-e1674ad7` 的 Edit/Delete，页面快照显示 `No active schedules`。`report.json:103–105` 还记录模型改动了既有 `internal/server/schedule_runner_test.go`。

候选六在候选五基础上只增加三条通用完成门：既有测试/公开夹具默认只读；新增测试不能替代既有公开入口；任何公开失败或不当测试改动都必须保留未完成状态。维护检查通过后另建候选六快照和运行目录。

候选六运行完成但业务未通过：`web-compat` 2/2 通过，独立验收失败。`acceptance/independent.log:3–10,31–46` 显示 inspect envelope、重启保留、清除字段持久化、pause/resume JSON 失败；`report.json:104` 显示既有测试未改。最终 work 的 `[606]` 写入 `status: done`，不符合技能允许的 `in_progress`/`blocked`/`complete`。

候选七的改写范围固定为通用完成门和检查点动作，不加入 schedules 的具体答案。必须能从规则判断：公开 CLI/API/RPC 每条证明行是否保存原始输出或响应；`status` 是否为允许值；`status: complete` 时 `proof_gap` 是否恰为空字符串；压缩接续是否第一项直接读取 `work/{slug}/index.md`；每次真实验证后是否立即单独回写当前行为。

候选七冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-7/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-7-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选六只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14 均通过。

候选七运行完成但业务未通过：`report.json` 的 independent 返回 1，`acceptance/independent.log:3–5,32–65` 显示 `--json` 的 inspect/update/pause/resume stdout 以 `ID:`、制表符等人类格式开头，JSON 解码失败；`web-compat` 2/2 通过，`changed_original_tests: []`，自然压缩 0 次。最终 work `project/bywork/work/restore-schedules-heartbeats/index.md:3–7` 仍写 `status: complete` 与 `proof_gap: ""`。

候选八在候选七基础上只增加失败证据判定：原始输出解析失败、格式错误、非零退出或断言失败时先记为失败，再修生产入口并用同一公开调用复验；`Logf`、只保存输出或放宽断言不能填绿。维护检查通过后另建候选八快照和运行目录。

候选八运行完成但业务未通过：CLI/RPC 的 JSON 子项已通过，`web-compat` 2/2 通过，但 `acceptance/independent.log:7–35` 的重启工作区、半小时 DST、日历、持久化和运行恢复失败；`report.json:104` 显示既有测试未改。自然压缩发生在 `trace` `[506–507]`，第一项后续工具为 `[508]` 修改测试文件，未先读取 work；最终 `project/bywork/work/schedules-heartbeat-rebuild/index.md:3–7` 仍写 `status: complete`、`proof_gap: ""`。

候选九的规则范围固定为三条通用动作：生产共享路径发生改变时，先重开并重跑所有受影响的既有通过证明；每次自然压缩后的第一项工具调用只能读取已知 `work/{slug}/index.md`，路径未知时只能读取 `bywork/work` 目录；独立验收或公开入口返回失败时，下一次 work 回写必须保留 `in_progress`/`blocked` 和非空 `proof_gap`，直到同一入口复验通过。规则不加入 schedules 的实现答案。

候选九冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-9/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-9-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选八只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选九运行完成但业务未通过：`acceptance/independent.log:7–9,28–33` 的重启保留、持久化 patch 和运行恢复失败；DST、日历和 CLI/RPC 子项通过，web-compat 2/2 通过。自然压缩发生在 `trace` `[519–520]`，第一项后续工具为 `[521]` bash；最终 work `project/bywork/work/schedule-heartbeat-restore/index.md:3–7` 保持 `status: in_progress` 并留下非空 `proof_gap`。

候选十的规则范围固定为三项：把压缩后的第一项工具调用单独提升为最高优先级恢复协议；修改持久化、重启、恢复或生命周期共享路径后，必须通过新进程或重启入口验证磁盘记录与工作区副作用；收尾前逐项对账独立验收、公开验收和 work 缺口，不能用另一个无关失败代替实际失败。规则不加入 schedules 的实现答案。

候选十冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-10/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-10-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选九只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十运行完成但未改善：`acceptance/independent.log:7–9,28–33` 仍显示三项记录文件不存在；DST、日历、CLI/RPC、web-compat 通过。自然压缩发生在 `trace` `[516–517]`，第一项后续工具为 `[518]` bash；最终 work `project/bywork/work/restore-schedules-heartbeat/index.md:3–7` 保持 `in_progress`，但 `proof_gap` 只写 relay 失败，未列 independent 失败。

候选十的实现根因定位为持久化布局不一致：冻结验收在 `home/schedules/{id}.json` 写入并重开服务，候选 `internal/schedule/service.go:39–44,77–79` 却把传入 `baseDir` 直接作为 JSON 目录；同一错误解释了创建后文件缺失、重启记录不存在和运行恢复记录不存在。候选十一只把这类布局对账写成通用规则，不把 schedules 路径答案写入技能。

候选十一冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-11/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-11-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十一运行修复了候选九/十的持久化布局问题：`acceptance/independent.log:8–31` 的重启保留、持久化 patch、运行恢复通过；但回归了此前已通过的公开 CLI/RPC 契约，`acceptance/independent.log:3–5,32–45` 显示 inspect envelope、清除字段、pause、resume 失败。`report.json:104–106` 显示既有前端测试被修改；最终 work `project/bywork/work/restore-schedules-heartbeat/index.md:3–7` 写 `status: done` 和空 `proof_gap`。自然压缩发生在 `trace` `[440–441]`，第一项后续工具为 `[442]` bash，`[444]` 才读取 work。

候选十二冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-12/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-12-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十一只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；候选十一正式评审在其运行目录，维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十二运行没有保住既有公开契约：`acceptance/independent.log:3–19,34–47` 的 inspect/CLI/RPC 与半小时 DST 失败；持久化、运行恢复、日历、定向构建和 web-compat 通过。`report.json:104` 显示既有测试未改，但最终 work `project/bywork/work/restore-schedules-heartbeat/index.md:3–7` 错写 `status: complete`、空 `proof_gap`。自然压缩发生在 `trace` `[498–499]`，第一项后续工具为 `[500]` bash，未读取 work。

候选十三的最小改写只增加证据闭环：共享路径编辑前，先从真实公开入口运行并保存旧输出、错误和副作用基线；编辑后必须用同一个入口重跑并逐项比较；没有基线、同入口复验或比较结果时保持 `in_progress`/`blocked`，不能以局部测试收尾。规则不加入 schedules 的具体输出或时间答案。

候选十三冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-13/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-13-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十二只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十四的规则范围固定为可选策略分支矩阵：显式保留/归档、开启/关闭、存在/缺失等分支分别建立真实基线并用同一入口复验，修复一支不能覆盖另一支。规则不加入 schedules 的字段答案。

候选十四冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-14/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-14-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十三只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十四独立验收、schedule/rpc-cli 回归、构建、vet、前端单元/类型/构建、浏览器和 web-compat 共 12 组全部返回 0；`report.json` 的 `changed_original_tests` 为空，业务通过。自然压缩 1 次，峰值上下文 `403359`；但 `trace` `[454–455]` 后 `[456]` 先执行 bash，未先读取 `bywork/work/{slug}/index.md`。最终 work 的 `status: complete` 与 `proof_gap: ""` 仅能证明业务结果对账，不能把工作流失败标成通过。

候选十五的规则范围固定为压缩恢复硬闸门：压缩结束后第一项工具调用必须是规定的单独 `read`，已知路径直接读 work，未知路径先读 `bywork/work`；首个 read 完成前禁止其他工具或摘要中的业务动作，trace 以第一项调用判定。相对候选十四只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十五运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-15-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。独立验收只有 CLI/RPC 输出形状失败，但业务门仍未通过；`report.json:103` 的 `changed_original_tests` 为空。`acceptance/independent.log:3–5,32–58` 保存了原始文本输出和 JSON 解析失败；`compactions.json` 记录 1 次自然压缩、峰值 `400110`，`trace` `[376–378]` 证明压缩后先 bash。最终 work 使用 `status: completed`，违反合法状态值，并没有把独立失败写入 `proof_gap`。

候选十六只补两条通用规则：公开 CLI/API/RPC 的响应外层、字段、错误和默认输出形状以已有契约和用户明确要求为准；不要从新实现或邻近命令推断人类可读默认格式，若契约要求响应对象，默认公开入口必须返回该对象。work 状态只允许 `in_progress`、`blocked`、`complete`，独立验收失败时必须保留非空 `proof_gap`。压缩恢复硬闸门继续保留。

候选十六冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-16/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-16-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十五只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十六运行修复了候选十五的 CLI/RPC 默认响应形状：`acceptance/independent.log:33–42` 通过；但半小时 DST 和日历边界失败于 `acceptance/independent.log:11–28`，且 `report.json:104–106` 显示既有 Playwright 测试被修改。自然压缩 1 次、峰值 `400443`；`trace` `[482–484]` 证明压缩后先 bash。最终 work 写合法值 `complete`，但独立验收返回 1，`proof_gap` 没有列出这两项失败。

候选十七只增加固定恢复口令与前置动作：看到压缩摘要后先执行“READ WORK FIRST”，第一项必须是读取 work；恢复或长序列中准备运行 bash 前，先单独读取当前 work。既有测试文件保持只读，任何修改都阻止完成。现有公开响应形状规则继续保留。

候选十七冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-17/`，运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-17-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选十六只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选十七运行的 independent 返回 1；CLI/RPC 的 inspect 类操作和显式保留 workspace 重启失败，其他验收组返回 0。`report.json:104` 的 `changed_original_tests` 为空。自然压缩 1 次，峰值上下文 `400270`；`trace` `[424–426]` 证明压缩后第一项仍是 bash。最终 work 使用合法值 `complete`，但独立失败没有写入 `proof_gap`。

候选十八只补通用对账动作：公开 CLI/API/RPC 入口在完成前必须用独立的真实调用复核默认响应；持久化、重启和生命周期的每个显式保留/归档分支必须从新进程或重启入口观察记录与 workspace 副作用；任何独立验收失败、原始响应解析失败或分支复验失败，都必须先把当前 work 写成 `in_progress`/`blocked` 和非空 `proof_gap`，禁止写 `complete`。压缩恢复硬闸门、`READ WORK FIRST`、公开响应契约和既有测试只读门继续保留。

候选十八运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-18-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。`acceptance/results.json` 的 independent、schedule-regression、rpc-cli-regression、构建、vet、依赖、前端单元/类型/构建、relay、浏览器和 web-compat 共 12 组全部返回 0；`report.json:104` 的 `changed_original_tests` 为空。自然压缩 1 次，峰值上下文 `397254`；`trace` `[293–295]` 证明压缩后先执行 `bash`，即使命令只是 `ls`/`sed` 读取材料，也不符合 literal `read` 硬门。

候选十九只强化工具语义：压缩结束后的第一项必须调用名为 `read` 的工具；bash/shell/execute 中的 `cat`、`sed`、`ls`、`rg` 或 Python 读取都不算，不能先执行。压缩恢复硬门、真实公开入口原始证据、持久化分支新进程复验、完成预检和既有测试只读门继续保留。

候选十九运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-19-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。独立验收和其余 11 个验收组全部返回 0；`report.json:104` 的 `changed_original_tests` 为空。自然压缩 1 次，峰值上下文 `400241`；`compactions.json` 的持久摘要未保留恢复口令，`trace` `[540–542]` 仍显示第一项为 bash。候选十九业务通过但不能进入第二次大型运行。

候选二十增加持久化恢复 cue：活动 work 的 `next_action` 必须以 `READ WORK FIRST:` 开头并写出当前 work 路径或“先读 bywork/work 目录”；模板和检查点规则把这条 cue 作为压缩摘要可见的接续提示。压缩后仍必须直接调用 literal `read`，不能以 shell 内文件读取替代；其余业务和完成门规则继续保留。

候选二十运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-20-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。独立验收和其余 11 个验收组全部返回 0；`report.json:104` 的 `changed_original_tests` 为空。自然压缩 1 次，峰值上下文 `399674`；最终 work 的 `next_action` 已带 cue，但摘要未保留该字段，`trace` `[319–321]` 仍显示先 bash。候选二十业务通过但不能进入第二次大型运行。

候选二十一把恢复 cue 同时写入摘要稳定保留的 `must_hold`：活动 work 的 `must_hold` 必须以 `READ WORK FIRST: after compaction call the literal read tool ...` 开头；`next_action` 规则继续保留。压缩后仍必须直接调用 literal `read`，其余业务和完成门规则继续保留。

候选二十一冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-21/`，第一轮运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-21-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。相对候选二十只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。

候选二十一首轮业务门通过：12 个验收组全部返回 0，`report.json:104` 的 `changed_original_tests` 为空；最终 work `project/bywork/work/schedules-heartbeat-restore/index.md:3–7` 的 `must_hold` 与 `next_action` 均带 `READ WORK FIRST` cue，状态为 `in_progress` 且非空 `proof_gap`（准确保留与本功能无关的 relay 全包失败）。但本轮自然压缩 0 次、峰值 `394735`，恢复门无法判定；正式评审见该运行目录的 `review.md` 与 `review-result.json`。同一候选第二轮已准备在 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-21-02/`，源码树与删减种子一致。

候选二十一第二轮（`runs/schedules-candidate-21-02/`）业务门通过：12 个验收组全部返回 0，既有测试未改，最终 work 合法保留 `in_progress` 与非空缺口。自然压缩 1 次、峰值 `399832`；压缩摘要逐字保留了 `READ WORK FIRST` 与“first tool call must be the literal read tool”指令，但 `trace` `[533–535]` 显示第一项仍是 bash（relay flaky 基线验证，结论正确）。这证明失败性质已从“摘要丢 cue”变为“模型不遵守已送达的过程指令”，而该指令自候选十四以来没有再拦截过真实事故。正式评审见该运行目录的 `review.md` 与 `review-result.json`。

用户据此决定：工作流恢复门改为结果判据（接续后的动作与检查点一致：做对下一件事、状态诚实、缺口不丢、无假完成），并给技能瘦身。候选二十二删除了压缩恢复硬闸门小节、READ WORK FIRST 口令、literal read 工具名强制和 must_hold/next_action 前缀要求，只保留一句自然表述“接续时先读检查点、动作与检查点一致”；其余业务规则（公开响应契约、持久化契约、共享路径回归、分支矩阵、完成门、既有测试只读）不动。相对候选二十一仍只改 `SKILL.md`、`references/change.md`、`references/prove.md`、`templates/work.md`，README 同步；维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。该判定边界已写入 [evaluation Memory](../../memory/evaluation.md)。

候选二十二冻结到 `/Users/zijie/workspace/ByIssue-evaluation/snapshots/v2-delivery-candidate-22/`，第一轮运行目录为 `/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-22-01/`，源码树哈希仍为 `4bc49f17b3673fb794df6bdc72ed08e1d723f91c`。case-v5 的 workflow-rubric 本身按结果判据写（“自然压缩后读取检查点并核对实际代码与证据，继续未完事项”），冻结评测材料无需修改。交付门相应更新：同一最终候选连续两次大型运行，业务验收通过且压缩接续（如有）按结果判据与检查点一致。

候选二十二运行中被用户叫停：用户补充了更根本的原则——整个技能的提示词应当极简优雅，只引导模型按流程完成 1234，适当放权给模型，不写工具级操作规程（如“先 read 再 bash”“先这样完成流程 A 再那样完成流程 B”）。据此对技能做了整体重写而不是局部删减，产物冻结为候选二十三：

- `SKILL.md`（178→102 行）：开头明确“具体用什么工具、按什么顺序操作，由你根据当下情况判断；本文件只约定流程和底线”。删除“持久化契约/共享路径回归/公开接口响应契约”三个小节级规程（其内容压缩为底线清单里的原则条目），检查点协议五步操作顺序改为“改变的核心流程”四步（保存要求→逐行实现→验证守住契约→诚实收尾），完成门大段文字压缩为一句“全部通过且 proof_gap 为空才能写 complete”。保留的每条底线都注明对应真实事故类别：假完成声明、改写既有测试、响应形状漂移、期望值倒推、格式化安装技能、未授权外部副作用。
- `references/change.md`：实现循环从每步内嵌十几个“必须/不能”的操作细节，改为四个短步骤加一段“检查点的作用是让 work 始终能回答正在证明什么”，把证据细节指向 prove.md。
- `references/prove.md`：保留六列表、行为门、范围门结构；把散落的重复规则合并为“证据要能挡住错误”七条原则（原始结果优先、失败就是失败、共享路径要有基线、可选策略逐分支、持久化跨进程、既有测试只读、契约有缺口就问）。
- `templates/work.md`：删除全部规则复读，只留结构提示和指向 references；完成核对从 7 门合并为 5 门。
- README 中英文：三段流程描述压缩为“接续→逐行实现→验证守契约→诚实收尾”四段自然表述。
- 其余 references（clarify、understand-review、memory-direction、quality、economy、ui-spec、writing、onboard、grilling、domain-modeling）本来就是原则式写法，未动。

维护检查、checker 22/22、初始化 3/3、评测运行器 14/14、Markdown 检查均通过。候选二十三的验证目标：确认瘦身没有回退已修复的行为（CLI/RPC 响应形状、archiveOnFinish=false 重启保留、DST/日历、持久化布局、既有测试只读、完成声明诚实），并观察无工具级规程时逐行实现和回写是否仍发生。

候选二十三的运行启动后被用户叫停（SIGTERM，无结论，目录保留）。用户补充了更严格的筛选标准：模型本来大概率就会做对的事不写，每行规则要挣得它的注意力成本。按这个标准对候选二十三再筛一轮得到候选二十四：删掉 change.md 里「bug 先沿日志/堆栈定位根因、根因不清先补失败信号」（模型默认行为）和「.agents 只读」的重复份（SKILL.md 底线已有权威归属）；SKILL.md 的行动深度四分支压缩为一句（前三个分支是四种行动表已回答的内容）。筛选标准已写入 `memory/project.md`。

候选二十四的运行同样启动后即被叫停（SIGTERM，无结论）：用户指出 SKILL.md 开头「具体用什么工具、按什么顺序操作，由你根据当下情况判断」一句也属废话——模型本来就会自己判断工具，这句还占了开头位置。删除后冻结为候选二十五，与候选二十四相比只差这一句。

候选二十五的运行也在启动后被叫停（SIGTERM，无结论）。用户质疑候选二十四自作主张删除的 bug 定位段，据此做了完整对账并恢复两处：change.md 的「根因不清或难复现时，先补可重复的失败信号，再逐个验证假设」（挡猜改法的强默认行为，不该删）和「小偏差可在 work 更新方案后继续；相邻发现写入范围说明或后续建议」（挡范围蔓延）。维持删除的两处经用户确认：「.agents 只读」的重复份（权威归属在 SKILL.md 底线）和行动深度四分支（与四种行动表重复）。删除台账和裁决记录在会话中；筛选标准已补入 `memory/project.md`：每行规则要挣得注意力成本，模型本来就会做对的事不写。

候选二十六为极简形态（102 行 SKILL.md，规则只写方法论、不绑定工具）的首次完整大型运行。结果：11/12 验收组通过、既有测试未改、0 压缩（峰值 390588），但 independent 的 `TestReviewRestartKeepsExplicitlyRetainedWorkspace` 失败——重启归档了 `archiveOnFinish=false` 且已有持久化 agent 的 workspace。机制是分支×生命周期交叉漏验：保留分支在正常运行路径验证过、重启恢复用默认归档策略验证过，但两者的交叉组合没进证明表（模型 work 里重启行的预期就写着「归档工作区」，无分支区分）；最终 work 因此写 `complete` 和空 `proof_gap`——它自己的定向验证全绿，缺口对它不可见。正式评审见 `runs/schedules-candidate-26-01/review.md`。

修复只改两处方法论表述：`references/prove.md`「持久化和生命周期要跨进程」补充「策略分支与生命周期事件相交时，每个分支都要在该入口下观察；正常流程逐分支验证过、生命周期用默认策略验证过，仍不覆盖组合」；`SKILL.md` 核心流程第 3 步改为「每个显式分支都在该入口下单独验证——分支与生命周期相交时逐组合观察」。这是候选十四分支矩阵规则的完备化，不加业务答案、不加工具绑定。冻结为候选二十七复验。

候选二十七运行（`runs/schedules-candidate-27-01/`）：候选二十六的重启保留分支失败已修复（独立验收全过），但 web-compat 的 heartbeat 行操作用例失败，最终 work 写非法 `status: done`。机制是**证据定位缺陷**：证明行的「应观察到」正确（heartbeat 只有编辑/删除），但证据列用「Vitest 57 tests / Playwright 7 tests」汇总绿灯冒充，没有任何断言实际覆盖该行；模型因此认为全部通过。自然压缩 1 次，压缩后接续与检查点一致（结果判据合格）；既有测试未改。正式评审见该目录 `review.md`。

候选二十八修复两处：`references/prove.md` 把「一次测试可以覆盖多行，但每行的通过依据都要能定位到具体断言」强化为「证据按行落到能定位的具体断言；整个测试包或批量 tests 的汇总不能充当某一行的证据，除非能指出本行每个应观察结果对应哪条断言」；`SKILL.md` 底线「完成声明必须与证据一致」补「`proof_gap` 非空时状态只能是 `in_progress` 或 `blocked`，`complete` 要求 `proof_gap` 恰为空」（合法值清单在结构段已有，底线只引用约束关系）。

候选二十八运行（`runs/schedules-candidate-28-01/`）：候选二十七的两个问题均未复现——web-compat heartbeat 行操作用例通过，独立验收 10 项全过，证明行证据落到具体测试名。但失败点再次转移：schedule-regression（`-race`）在 `TestHeartbeatsEndWithTheirAgent` 与 `TestStartTicksUntilStopped` 报 DATA RACE（生成的 `service.go` 中 `Stop()` 持锁写 `s.stop`、`loop()` 无锁读）。模型按仓库惯例验证（CI 与 Makefile 的 `go test` 都不带 `-race`），普通模式全绿，缺陷对它不可见；最终 work 写 `complete` 与其可见证据一致，不属于汇总绿灯问题，是验证强度不足。自然压缩 0 次（峰值 389094），恢复门无法判定；既有测试未改。正式评审见该目录 `review.md`。

候选二十九只改 `references/prove.md`「证据要能挡住错误」，新增一条方法论：**并发要上检测器**——启动 goroutine、后台循环或跨进程生命周期的行为，用工具链的竞态检测强度验证（Go 是 `go test -race`）；仓库惯例命令不带检测器时，不能以惯例绿灯代替。依据：验收固定用 `-race` 跑 cadence/schedule 定向包（冻结材料未变），此前通过的候选是运气好没写出竞争而非验证拦住了竞争；规则是通用工程实践，不含本题业务答案。

候选二十九运行（`runs/schedules-candidate-29-01/`）：竞态规则生效（schedule-regression `-race` 通过、web-compat heartbeat 行操作通过），但失败点再次转移——重启保留失败复发（持久化 JSON 文件缺失，候选二十六已修过）、web-compat 页签用例失败、独立验收的日历计算挂死直至 90 秒超时。0 压缩（峰值 362197），最终 work 写 `complete` 而其可见验证未覆盖验收入口。既有测试未改。

候选二十六至二十九合计四轮，失败点在各代码区域轮换、互有修复互有复发（重启保留：坏→好→好→坏；页签与 heartbeat 行操作互换死活；竞态与日历挂死新冒头），而技能规则每轮只增量一条且都被验证生效。判定：这是 DeepSeek Flash 在该任务上的**模型方差**，不是可用规则修复的方法论缺口；继续逐轮加规则既堵不住方差，也违背用户确立的极简原则。

用户据此改变交付判据：保留精简版技能（候选二十九文本），放弃「单次大型运行全绿」门槛，改为 **A/B 通过率对比**——A 臂不安装技能（`run_repository.py --no-skill`，任务文本去掉工作流措辞，冻结为 `snapshots/v2-delivery-input-v5-nobi/`，验收逐字节一致），B 臂安装候选二十九；同模型 deepseek-flash、thinking **max**、400k 自然压缩、四小时上限，交替顺序各 3 次（`tools/evaluation/ab_driver.sh`，运行目录 `runs/ab-nobi-01..03` 与 `runs/ab-bi-01..03`，删减种子与源码树哈希同前）。报告两臂业务通过率与范围；B 臂另按结果判据审工作流。协议已写入 `tools/evaluation/README.md`。用户同时否掉了改用外部公开评测集的方向：外部集测模型能力，测不到工作流纪律；其合适角色是日后「技能不损害原始编码能力」的旁证。

A/B 六轮结果（2026-11-15 夜至 11-16 凌晨）：**bi 臂 3/3 业务通过，对照臂 0/3**，范围不重叠；六轮均自然压缩 1 次，用时同量级。对照臂失败集中在契约细节（半小时 DST、日历边界、inspect JSON envelope）——正是历史上 bi 臂在 medium thinking 下反复失败的同类位置。运行事故一处：冻结对照变体时漏拷 `acceptance.py` 依赖的 `run.py`，对照臂三轮的运行内验收崩溃；修复快照后对三轮冻结产物统一补跑验收，补跑结果有效且与运行解耦。B 臂工作流审查（结果判据）：三轮压缩接续均与检查点一致、外部验收属实、既有测试未改；但 bi-01/bi-02 最终 work 写非法 `status: done`（bi-03 合法 `complete` + 空 gap），逐行回写未严格执行（写入聚集首尾）。完整评审见 `runs/ab-protocol-review.md`。

候选三十只改一处：底线「完成声明必须与证据一致」补入 status 合法值域（`done`、`completed` 等变体非法）。值域原本只在结构说明段，远离收尾决策点；bi-01/02 与历史候选六/十五证明这是复发事故类别，底线处一句话挣得注意力成本。逐行回写偏松暂不加规则：其实质目的（work 始终能回答正在证明什么、收尾不靠回忆）在三轮中均达成，最终状态与证据一致；先观察候选三十两轮，若回写聚集再导致实际缺口才考虑。

用户进一步区分了两类表述：**工具绑定**（「必须用 read 工具」「下一项调用必须是文件写入」）不要；**方法论**（「接续后先核对检查点与磁盘证据」「持久化行为要跨进程观察才算证明」）要。按此标准扫描确认 `skills/bw/` 已无工具绑定表述。评测材料同步改判：`tools/evaluation/cases/ledger/workflow-rubric.md` 三处（「bash 内写文件计入顺序」「单独保存」「单独写入」改为以最终落盘状态判定）；heldout 快照 `snapshots/v2-delivery-heldout-v2/cases/webhook-inbox/workflow-rubric.md` 的「切换前先单独保存检查点」改为「切换行为前检查点已更新」，manifest 哈希已同步并注明原因（该快照尚未跑过模型，acceptance.py 与 contracts 未动）。这两处属于评测输入变化，与技能效果分开单列。

另做粉色大象审查：全技能 34 处否定式表述逐条核对。全部对应模型真实出现过的替代作弊路径（测试摘要冒充证据、猜改法、批量推广绿灯、把推演写成用户决定、混当前/目标图），无凭空树立的靶子；且均为「禁止替代路径 + 指明正确动作」结构，不诱发被禁画面。结论：现状保留，无需改写。

候选三十连续两轮大型验证（`runs/schedules-candidate-30-01/02`，thinking max）：12 组验收全零 ×2、既有测试未改、各 1 次自然压缩且接续与压缩前检查点方向一致、最终 `status: complete` 合法且 `proof_gap: ""` 与验收一致——A/B 中 bi-01/02 的非法 `done` 未复现，值域底线生效。评审见 `runs/schedules-candidate-30-review.md`。

三个短场景用候选三十快照运行（thinking max）：heldout webhook-inbox（`runs/heldout-webhook-c30-01`）业务通过、review 六项全过，真实 HTTP/CLI transcript 落盘、scope 46 项全覆盖；ledger 两阶段（`runs/ledger-c30-01`）业务通过、review 七项全过，第一轮如实停在 report 前、第二轮先读原 work 再更新 `--min-cents` 新约束后实现；memory-selection（`runs/memory-selection-c30-01`）业务通过、review 三项全过，长期决定与协议原因入 Memory、配置数值与本轮状态留 work、未擅自实现重试。三份 review.md 已逐项回填。

实际安装部署核对：宿主加载副本在 `~/.pi/agent/skills/bw`，同步为 2.1.0 后 `bash tools/release-check.sh ~/.pi/agent/skills/bw` 全绿（含部署副本 diff 一致）；宿主已实际加载新版（技能描述更新生效）。`VERSION` 2.0.1→2.1.0，CHANGELOG 新增 2.1.0 段，checker 版本一致性通过。

候选十三运行修复了候选十二的 inspect/CLI/RPC 与半小时 DST：`acceptance/independent.log:3–7,12–41` 通过；但 `acceptance/independent.log:7–10` 的显式保留 workspace 重启副作用失败。`report.json:104` 显示既有测试未改，最终 work `project/bywork/work/schedules-heartbeat-rebuild/index.md:3–7` 错写 `status: complete`、空 `proof_gap`。自然压缩发生在 `trace` `[580–581]`，第一项后续工具为 `[582]` bash，未读取 work。

已将公开契约依据与浏览器探针误报的长期判定边界写入 [evaluation Memory](../../memory/evaluation.md)。候选二冻结后只读复核了新业务的公开契约和独立验收；heldout 快照未改、未运行模型，也未用于改写技能。并发期间没有启动另一模型评测，后续仍按运行隔离约定顺序执行。

`/Users/zijie/workspace/ByIssue-evaluation/runs/schedules-candidate-2-01/review.md` 的正式评审确认：初始 work 写入早于业务代码，但精确 CLI envelope 未落盘；随后实现跨后端、RPC、CLI、前端大块推进，直到收尾才回写；一次压缩后先读代码，未先读 work。候选三只强化这两个动作边界和公开调用者证据要求。

## 完成核对

- 行为门：证明表六行全部通过。迭代历史：候选三业务通过但工作流未通过；候选四完整性失败；候选五至十三业务未通过；候选十四业务通过但旧首读判据未通过；候选十五至十七业务未通过；候选十八至二十业务通过但旧首读判据未通过；候选二十一两轮业务通过；候选二十二至二十五启动即停无结论；候选二十六至二十九失败点轮换，判定为模型方差；A/B 六轮 bi 3/3 vs 对照 0/3；候选三十连续两轮大型验证业务与工作流全过。
- 范围门：本轮为定向改进；被测重建任务的 scope 逐入口对账（heldout 46 项全覆盖），技能包结构由 checker 与 release-check 核对。
- 测试门：技能仓库维护检查全绿（checker、22/22 植入反例、初始化 3/3、运行器 14/14）；各评测运行 `changed_original_tests` 均为空。
- 契约门：评测输入变化（ledger/heldout rubric 改结果判据、nobi 对照变体）均已冻结、单列并记录原因；对照臂验收崩溃事故与补跑已留档。
- 完成门：全部交付门槛（连续两次大型通过、自然压缩正确接续、heldout 新业务、ledger 跨会话、memory-selection、实际安装部署核对）有对应运行与评审证据；`proof_gap` 恰为空。
- 需要用户看的推断或无法判定：A/B 每臂样本为 3，通过率结论限于「明显分离」精度；全部结论限于 DeepSeek Flash（大型任务 thinking max）与该组任务，不宣称跨模型可靠性或速度收益。改动未提交、未推送，发布由用户发起。
