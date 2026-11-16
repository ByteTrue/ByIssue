---
name: bi
description: >
  ByIssue：用 work/{slug}/、memory/{topic}.md 与按需的 vision/ 管理软件演化；按用户当前行动推进澄清、改变、理解与审查、记忆与方向。
  触发：bi、ByIssue、初始化 bi、接入 ByIssue；聊聊、先理清、想清楚再做、帮我规划一下、拷问我、多轮问清楚；怎么实现、先设计、实现方案、快速、快改、小改一下、顺手改一下、直接开干、别走流程、做这个、推进、修这个 bug、穿刺、先打通；怎么工作的、这条链路、影响范围、review、评审、看看这 diff/PR；整理 vision、维护 spec、当前真相、记一下坑、写 note、我带你跑一遍、教 AI 做某流程。
---

# ByIssue

ByIssue 把当前工作、可观察证据和长期判断放在项目里，让下一轮工作从事实继续，而不是从上一轮对话猜测。

调用 `bi` 先判断用户此刻的行动，再读取该行动需要的最小规则。不要求每次请求都生成完整文档，也不把一次小改扩成固定流水线。

## 四种行动

从用户原话中选一个主行动，推进到完成或真实阻塞：

| 主行动 | 用户常这样说 | 必读 | 按需读取 | 默认出口 |
|---|---|---|---|---|
| **澄清** | 聊聊、先理清、想清楚再做、帮我规划一下、拷问我、多轮问清楚 | [clarify](references/clarify.md) | [grilling](references/grilling.md)、[domain-modeling](references/domain-modeling.md)、[ui-spec](references/ui-spec.md) | 形成用户确认的目标、边界或取舍；需要跨会话时创建澄清型 work |
| **改变** | 怎么实现、先设计、实现方案、快速、快改、小改一下、顺手改一下、直接开干、别走流程、做这个、推进、修这个 bug、穿刺、先打通 | [change](references/change.md)、[prove](references/prove.md) | [quality](references/quality.md)、[economy](references/economy.md)、[ui-spec](references/ui-spec.md) | 小改直接验证；复杂或跨会话变化进入 `work/{slug}/` |
| **理解与审查** | 怎么工作的、这条链路、影响范围、review、评审、看看这 diff/PR | [understand-review](references/understand-review.md) | [quality](references/quality.md)、[economy](references/economy.md)、[ui-spec](references/ui-spec.md) | 给出有范围、有证据的解释或审查结果；用户没有授权时不改代码 |
| **记忆与方向** | 整理 vision、维护 spec、当前真相、记一下坑、写 note、我带你跑一遍、教 AI 做某流程、初始化 bi、接入 ByIssue | [memory-direction](references/memory-direction.md) | [onboard](references/onboard.md)、[grilling](references/grilling.md)、[domain-modeling](references/domain-modeling.md) | 更新 `memory/` 或按需的 `vision/`；接入时只初始化新入口 |

跨会话或需要完整性证明的改变建立 work；其余直接做。

## 项目结构

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

`work/{slug}/index.md` 是继续同一工作的唯一权威入口，顶部的结构化元数据是唯一检查点：

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

`status` 只能取 `in_progress`、`blocked`、`complete`。`proof_gap` 只在没有任何缺口时为空字符串。

用户说“继续”或会话从压缩摘要接续时：先读取匹配的 work 检查点（不确定是哪个就看 `byissue/work/` 下的 `status` 和主题；多个候选让用户选），核对它与代码、git 和已有证据，再继续。摘要和记忆不能替代这次读取；接续后的动作要与检查点一致。

## 改变的核心流程

非平凡改变按四步推进，细节见 [change](references/change.md) 和 [prove](references/prove.md)：

1. **保存要求。** 把用户要求原文、条件和例外落盘到 work，再写行为证明表：每行一个用户行为，注明真实入口、操作、应观察到什么。
2. **逐行实现。** 每轮只选一行：先把这行写入检查点，再实现，再从真实入口验证，然后把实际结果回写这一行，才选下一行。不要批量实现后集中补写。
3. **验证守住契约。** 从真实公开入口验证，保留调用者看到的原始输出。改动共享路径前先保存旧行为的基线，改后用同一入口复验比较。持久化、重启和生命周期行为用新进程或重启入口观察，每个显式分支（保留/归档、开/关、存在/缺失）都在该入口下单独验证——分支与生命周期相交时逐组合观察。
4. **诚实收尾。** 完成前逐项核对证明表、scope 和外部验收结果，把每个未通过项写进 `proof_gap`。全部通过且 `proof_gap` 为空才能写 `complete`；任何失败都保持 `in_progress`/`blocked`。

## 底线

这些规则每一条都挡住过真实事故，不可协商：

- **完成声明必须与证据一致。** 外部验收失败、原始输出解析失败、任何未验证项存在时，不能写 `complete`，缺口逐项写进 `proof_gap`；`proof_gap` 非空时状态只能是 `in_progress` 或 `blocked`，`complete` 要求 `proof_gap` 恰为空。`status` 合法值只有这三个，`done`、`completed` 等变体非法。局部测试全绿不能覆盖独立验收失败。
- **既有测试和公开验收夹具是只读证据。** 新增回归放新文件；为适应实现而改写既有测试，不能进入 `complete`。
- **公开接口的响应形状是契约。** CLI/API/RPC 的输出外层、字段、错误和默认格式以用户要求、公开文档和既有调用方为准，不从新实现或邻近命令推断。契约要求响应对象时，默认入口必须返回该对象。
- **证据要能挡住错误。** 期望值来自需求、规格或手算，不从被测代码的输出倒推；没有真实入口的原始结果时，结论只能是 `无法判定`。
- **安装输入只读。** 项目内的 `.agents/skills/bi/`、评测用例和运行器材料是输入；流程记录只写项目的 `byissue/`，技能修改回到技能源仓库。
- **外部副作用先收尾。** 用户授权 commit、push 或发布时，先完成检查点回写和完成门核对再执行。

## 共同规则

- **先给结论，再给证据。** 说效果、根因或验证结果时注明来源是实测（给出命令与输出位置）还是推断。验证结果只有 `通过`、`未通过`、`无法判定`；没走到本次改动真正生效的入口就是 `无法判定`。收工时把推断和无法判定集中列在「需要你看的」，没有就写「无」。
- **提问带推荐。** 问题按序编号，每条给推荐答案和一句理由。能自己查到的事实先查；只有目标、边界、阈值、兼容策略和取舍才交给用户，提问后等回答。
- **节省上下文。** 首次加载本文件和行动必读的 reference 时完整读取；已读且未变的文件直接复用。第一次写 `byissue/` 文档、commit message 或完成汇报前，读取 [writing](references/writing.md)。

## 记忆与方向

长期内容进入 `memory/{topic}.md`，一个主题一份，不设全局索引。写入前按 [memory-direction](references/memory-direction.md#memory) 判断跨工作用途与不可重建性；当前工作的接续信息留在 work。开始工作时按主题检索命中的 Memory；新决定或新证据与旧记录冲突时，先更新记录再继续。

Vision 只在用户整理长期方向时使用，描述目标世界与候选方向，不承担当前实现状态。

## 汇报

完成或阶段性收工时说明：目标与范围、当前状态、证明结果、写入的 Memory、推断和无法判定项。没有需要用户看的内容时写「需要你看的：无」。

## 按需材料

- 质量目标与承诺：[quality](references/quality.md)
- 实现经济性：[economy](references/economy.md)
- UI 关系与状态：[ui-spec](references/ui-spec.md)
- 写作：[writing](references/writing.md)
- 项目接入：[onboard](references/onboard.md)

模板位于：[`templates/work.md`](templates/work.md)、[`templates/scope.md`](templates/scope.md)、[`templates/memory.md`](templates/memory.md)、[`templates/vision.md`](templates/vision.md)。初始化脚本位于 [`scripts/init_byissue.py`](scripts/init_byissue.py)。许可证和上游归属见 [NOTICE.md](NOTICE.md)。
