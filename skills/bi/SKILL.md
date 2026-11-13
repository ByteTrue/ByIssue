---
name: bi
description: >
  ByIssue：用 work/{slug}/、memory/{topic}.md 与按需的 vision/ 管理软件演化；按用户当前行动推进澄清、改变、理解与审查、记忆与方向。
  触发：bi、ByIssue、初始化 bi、接入 ByIssue；聊聊、先理清、想清楚再做、帮我规划一下、拷问我、多轮问清楚；怎么实现、先设计、实现方案、快速、快改、小改一下、顺手改一下、直接开干、别走流程、做这个、推进、修这个 bug、穿刺、先打通；怎么工作的、这条链路、影响范围、review、评审、看看这 diff/PR；整理 vision、维护 spec、当前真相、记一下坑、写 note、我带你跑一遍、教 AI 做某流程。
---

# ByIssue

ByIssue 是一套帮助人和 Agent 推进软件变化的方法。它把当前工作、可观察证据和长期判断放在项目里，让下一轮工作能从事实继续，而不是从上一轮对话猜测。

调用 `bi` 先判断用户此刻的行动，再读取该行动需要的最小规则。它不要求每次请求都生成完整文档，也不把一次小改扩成固定流水线。

## 共同规则

### 先给结论，再给证据

先用用户的词说明结论和下一步。说改动效果、根因、影响或验证时，在同一句里注明来源：

- **实测**：本轮实际运行并看到结果，给出命令与输出，或日志、截图位置。
- **推断**：由代码或材料得出，尚未运行；代码位置仍然只是推断出处。

验证结果只有 `通过`、`未通过`、`无法判定`。检查没有走到本次改动真正生效的入口时，写 `无法判定`。完成汇报或阶段性收工时，把推断和无法判定集中列在「需要你看的」；没有就写「无」。

### 提问带推荐

问题按序编号，每条给推荐答案和一句理由。能从代码、配置、测试或运行中得到的事实先自己查。真正属于用户的目标、边界、阈值、兼容策略和取舍才交给用户；提问后停在这一轮，等用户回答。

需要用户决定的事项也用候选清单表达，推荐要保留的项和理由。用户要求一次只问一个时，按用户节奏执行。

### 证据要能挡住错误

新检查的期望值来自用户要求、规格或手算，不从被测代码的输出倒推。要说检查挡住了某个错误，先在改动前、真实旧错或故意做坏的副本上看到它失败。性能和节省时间的结论用同一命令交替测改动前后，各至少三次，报告中位数和范围；范围重叠时写无可测差异，并说明计时区间确实做了目标工作。

### 节省上下文

首次加载本文件和行动的必读 reference 时完整读取。并行读取时，业务材料可以采样，规则文件不采样。同一会话里已经完整读取、内容仍在上下文且没有变化的文件直接复用；用户要求重读、文件发生变化或需要核对局部时，再补读最小范围。

第一次写 `byissue/` 文档、commit message 或完成汇报前，读取 [writing](references/writing.md)。

## 四种行动

从用户原话中选一个主行动。选定后继续推进到完成或真实阻塞；一次被授权的落盘动作不会自动改变主行动，新的用户意图才会改变它。

| 主行动 | 用户常这样说 | 必读 | 按需读取 | 默认出口 |
|---|---|---|---|---|
| **澄清** | 聊聊、先理清、想清楚再做、帮我规划一下、拷问我、多轮问清楚 | [clarify](references/clarify.md) | [grilling](references/grilling.md)、[domain-modeling](references/domain-modeling.md)、[ui-spec](references/ui-spec.md) | 形成用户确认的目标、边界或取舍；需要跨会话时创建澄清型 work |
| **改变** | 怎么实现、先设计、实现方案、快速、快改、小改一下、顺手改一下、直接开干、别走流程、做这个、推进、修这个 bug、穿刺、先打通 | [change](references/change.md)、[prove](references/prove.md) | [quality](references/quality.md)、[economy](references/economy.md)、[ui-spec](references/ui-spec.md) | 小改直接验证；复杂或跨会话变化进入 `work/{slug}/` |
| **理解与审查** | 怎么工作的、这条链路、影响范围、review、评审、看看这 diff/PR | [understand-review](references/understand-review.md) | [quality](references/quality.md)、[economy](references/economy.md)、[ui-spec](references/ui-spec.md) | 给出有范围、有证据的解释或审查结果；用户没有授权时不改代码 |
| **记忆与方向** | 整理 vision、维护 spec、当前真相、记一下坑、写 note、我带你跑一遍、教 AI 做某流程、初始化 bi、接入 ByIssue | [memory-direction](references/memory-direction.md) | [onboard](references/onboard.md)、[grilling](references/grilling.md)、[domain-modeling](references/domain-modeling.md) | 更新 `memory/` 或按需的 `vision/`；接入时只初始化新入口 |

行动的深度由目标和风险决定：模糊目标先澄清，现状不明先理解，明确的小改变直接做，跨会话或需要完整性证明的改变建立 work。改变代码本身不是建立 work 的唯一条件。

## 当前工作与项目入口

### 新入口

需要管理、跨会话继续或证明完整性的内容进入 `byissue/`：

```text
byissue/
├── work/
│   └── {slug}/
│       ├── index.md       # 当前工作唯一入口与检查点
│       └── scope.md       # 需要机械范围覆盖时才有
├── memory/
│   └── {topic}.md         # 长期判断，一个主题一份
└── vision/                # 用户整理长期方向时按需创建
    └── index.md
```

新工作区从 `work/`、`memory/` 和按需的 `vision/` 取当前内容。项目里已有的其他 `byissue/` 目录按用户点名的范围读取；它们不自动成为新工作的入口。

### 当前工作是什么

`work/{slug}/index.md` 保存一次变化的目标、边界、已定方案、行为证明、当前状态和下一动作。它是继续同一工作的唯一权威入口；实现、测试、运行产物和 git 记录是已经发生什么的事实来源。

入口顶部的结构化元数据是唯一检查点：

```yaml
---
kind: work
status: in_progress
current_unit: "当前正在处理的可验证行为"
next_action: "接下来唯一的第一件事"
must_hold: "用户已确认且不能自行改变的约束"
proof_gap: "行为门或范围门还缺什么"
---
```

`status` 取 `in_progress`、`blocked`、`complete`。正文不重复这五项状态。`current_unit` 按可验证行为切分，不按会话数量切分；一个会话可以跨越多轮压缩。

### 找到当前工作

用户说“继续”、会话从压缩摘要接续，或新会话进入一个已有主题时：

1. 浏览 `byissue/work/*/index.md` 的 `status`、主题和当前代码变化。
2. 找到一个与用户主题和当前改动相符的 `in_progress` 或 `blocked` work，就读取它的 frontmatter 和被当前动作引用的正文。
3. 找到多个候选时，把候选路径和差异交给用户选择。
4. 找不到时，按小改处理或创建新的 work；不从上一轮摘要猜路径。

项目不维护全局 `current.md` 指针。并行工作各自拥有自己的入口。

## 检查点协议

从压缩摘要继续、开始一个行为单元、单元完成、用户改变目标或约束、执行外部副作用，以及宣布完成之前，先重读当前 work 的检查点，并核对代码、git 和真实证据。

核对按三层分开：

1. 用户最新明确要求决定目标与边界。
2. 代码、配置、git 和真实运行决定已经发生什么。
3. `work/index.md` 保存已选方案、当前单元和证据状态。

如果三层不一致，先更新 work 或停下澄清。摘要中的“已完成”、文件存在、commit 存在和局部测试通过都不能单独成为当前状态。接续后的第一件真正动作必须来自 `next_action`，核对后若它已不成立，先改检查点。

每个可验证行为单元结束时回写 `current_unit`、`next_action`、`proof_gap` 和证明表。完成一项并不等于完成整个 work。

## 改变的完成门

非平凡改变先写行为证明契约：真实入口 → 操作 → 可观察结果。契约和结果使用 `index.md` 中同一张表，形状见 [prove](references/prove.md)。没有能驱动真实行为的入口时，先搭最小入口并跑通一次；仍然跑不了就写 `无法判定`。

需要逐项确认来源完整性的迁移、重写、移植、对齐和“所有 X”任务，按 [prove](references/prove.md) 增加 `scope.md`。范围覆盖与纵向行为证明分开：scope 全部覆盖不能替代真实行为通过。

只有行为门和范围门都通过，work 才能标为 `complete`。完成后原路径保留，下一次新目标或新增范围创建新的 work；已有证据推翻完成结论时，直接把原 work 改回 `in_progress` 或 `blocked` 并更新证明。

小而低风险、一次可完成的改变可以不创建 work。仍要从真实入口验证；中途出现跨会话、多个行为路径、完整性核对或显著风险时，把当前目标、证明契约和已发生事实补入 work，再继续。

## 记忆与方向

长期内容进入 `memory/{topic}.md`：用户长期决定、已确认的外部事实、值得复跑的证明。每条记录写适用边界、依据类型、证据或复核方式和重访条件。代码、配置、测试和 git 已经能回答的事实不复制。

Memory 默认一个主题一份文件，不设全局索引。开始工作时按主题检索命中的 Memory；用户新决定或当前证据与旧记录冲突时，先停下判断并更新记录。

Vision 只在用户整理长期方向或明确要求方向约束时使用。它描述目标世界、旅程和候选方向，不承担当前实现状态。稳定的当前事实、约束和取舍按用户需要写入 Memory。

## 汇报与 Git

完成或阶段性收工时说明：目标与范围、当前状态、行为证明结果、范围覆盖结果、写入的 Memory、推断和无法判定项。没有需要用户看的内容时写「需要你看的：无」。

默认不自动 commit、push、开 PR、合并或发布。用户明确要求其中一个动作时，先完成当前 work 的检查点回写、行为/范围门核对和必要的 Memory 记录，再在同一动作链中执行。外部副作用前再次读取检查点；不要用会话开头的记忆代替它。

## 按需材料

- 质量目标与承诺：[quality](references/quality.md)
- 实现经济性：[economy](references/economy.md)
- UI 关系与状态：[ui-spec](references/ui-spec.md)
- 写作：[writing](references/writing.md)
- 项目接入：[onboard](references/onboard.md)

模板位于：[`templates/work.md`](templates/work.md)、[`templates/scope.md`](templates/scope.md)、[`templates/memory.md`](templates/memory.md)、[`templates/vision.md`](templates/vision.md)。初始化脚本位于 [`scripts/init_byissue.py`](scripts/init_byissue.py)。许可证和上游归属见 [NOTICE.md](NOTICE.md)。
