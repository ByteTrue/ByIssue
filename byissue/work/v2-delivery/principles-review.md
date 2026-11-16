# 原则材料评判台账（7 份非核心 references）

> 状态：**已实施**（2.1.2）。7 份评判全部完成，改动清单已按用户确认落地；release-check 全绿、check_work 4/4、grilling 正文逐行核对为上游 verbatim。提交推送待用户授权。

## 取证基线与方法

- 评判对象：`skills/bi/references/` 里方法论核心以外的 7 份原则材料。核心五份（change/clarify/prove/memory-direction/understand-review）已验证，排除。
- 当前技能 HEAD `2a5883a`；Matt 上游副本 HEAD `5863806`（= origin 最新）。
- 方法：三个 explore 子代理并行做外部范式只读对比，我另读 Matt `writing-for-agents` 一手元方法论 + wnld `prose-checklist`/`quality-gate` 原文。每份给三态结论 留/改/换，带证据。
- 判据沿用 bi 自身原则：能改变模型默认行为或对应真实失败才留；否定式要挣得注意力成本；不绑工具、不依赖用户 AGENTS.md；不为想象中的未来付费。
- 参考库：`/Users/zijie/workspace/reference/ai-workflows/`。wnld 实际路径 `write-notes-like-deepseek/skills/write-notes-like-deepseek/references/`。
- 本台账只评判、不改技能；用户确认后才动。

## 结论速览

| 文件 | 结论 | 证据状态 |
|---|---|---|
| writing.md | **留**（先前「改」已撤回） | 已核实（子代理 + 我复核 memory-direction.md:16 原文） |
| grilling.md | **改：仅补回 6 词短语（:25）** | 已核实（git diff + 上游 CLAUDE.md/CHANGELOG 三重证据） |
| economy.md | **留** | 已核实（子代理 12 候选约束逐条核查） |
| quality.md | **改（2 行微补，表留）** | 已核实（子代理，bmad/spec-kit 对比） |
| ui-spec.md | **改（微，约 1.5 行）** | 已核实（子代理，gstack/Matt/bmad 对比） |
| onboard.md | **留** | 已核实（子代理：外部复杂度全来自配置面，bi 配置面为零） |
| domain-modeling.md | **改（微，约 2 行）** | 已核实（子代理：吸收时丢上游两条有效纪律） |

---

## 1. writing.md — 留（先前「改」结论撤回）

**撤回理由（我复核原文确认）**：本台账第一版建议补「受众声明/单一真相源/现在时/无会话泄露」三条。子代理指出、我逐行核实：这些规则**已在正确归属处存在**——
- `memory-direction.md:16` 原文「只写当前成立的结论，不写变更叙事、会话视角或实现流水账。一个主题的后续事实更新原文件，不建立平行摘要」——现在时/去泄露/单一真相源逐字覆盖（wnld 轮已吸收，我忘了）。
- `memory-direction.md:9`「为什么不能直接从代码、配置、测试或 git 取得？」——不复述环境的权威归属。
- `writing.md:3` 已声明管辖对象（回复、byissue/ 文档、commit message）——受众声明已存在。
再往 writing.md 补会制造第二份表述，违反 `byissue/memory/project.md:15`「一条规则只有一个权威归属」。

**挡住的失败**：14 条清单逐条对应真实写作劣化（奉承/黑话/同物异名/被动/硬凑三条/假排比/破折号/电报体/emoji）。

**子代理外部对比结论**：与 pstack `unslop` 33 条规则中所有适用中文的条目一一对应（17 行对齐表），无一条该删；两处 bi 更好——`:10`「跨项目成立即删」是可操作测试优于 unslop 的举例，`:37` 表格/流程图豁免把例外挂在可观察谓词上（superpowers `writing-skills/SKILL.md:262` 认可的正确例外形式）。英文专属条目（-ing 尾缀/delve 词表/title case/冠词）不适用中文，不补。

**三个真候选缺口均不满足准入线（project.md:26 事故证据标准）**：
- 收尾客套（「希望对你有帮助」）：`:16`「客套」类别词已语义覆盖；若评测漏网，最小改法是加一个例词（+6 字）。
- 无基线比较级：`:9` 例句本身就是带基线改写，属显式化而非新约束；漏网时 `:9` 末尾加半句（+18 字）。
- 节奏单调（全文短句电报体）：`:8` 拆分触发条件是「读者得回头重读」不是长度，正确读法下是 no-op；仅当评测证明过度执行才补「一个思想带条件的长句留着」。

**形式风险监控路径**：禁止清单反噬（superpowers writing-skills:249-263）测的是生成期 shaping，writing.md 是编辑期清单且每条禁令配正面改写，恰是外部推荐的防御。是否过度执行交 A/B 评测裁决，不预加规则。

## 2. grilling.md — 改：仅补回 6 词短语（:25）

**两处事实纠正（子代理指出、我 diff 复核）**：①漂移位置是 bi `grilling.md:25`（不是第一版写的 :18）；②「访谈结束不等于行动授权」**不是 bi 独有**——上游 `grilling/SKILL.md:30` 逐字就有，bi `:27` 是镜像。bi 真正的增强在包装层：`clarify.md:21` 把确认门又钉一次。

**唯一正文漂移**：bi `:25` `dispatch a sub-agent to find it`，上游 `:28` `dispatch a sub-agent with a fresh context window to find it`。

**补回的三重证据（子代理核对）**：
1. Matt 全仓硬规则：`matt-skills/CLAUDE.md:27`「Every skill that dispatches a subagent says to start it with a fresh context window. Some harnesses (Codex, for one) fork the parent conversation by default」——失败模式具体：宿主默认 fork 父会话，子代理带着访谈上下文出生。
2. 上游有意批量修订：`matt-skills/CHANGELOG.md:31`（PR #1341）8 个技能统一加短语，理由「throws away the clean context a subagent exists for」。
3. 机制：fork 的子代理继承访谈已给的 ➡️ 推荐答案，查证向推荐锚定（bmad advanced-elicitation「冷读者」防同一失败）。facts/decisions 分离要成立，查事实的上下文不能带待验证立场。

**附带收益**：`NOTICE.md:33`「the body is a verbatim copy of the upstream grilling skill」声明恢复为真；provenance-audit.md 记录的漂移可关闭。

**诚实边界**：bi 主宿主 pi/opencode 的子代理是否默认 fork 未实测；但 6 词成本≈0，即使宿主天然给新上下文，短语仍显式声明独立查证意图。

**最小改法**：`:25` 补 `with a fresh context window`，一行内 6 词，其余 27 行一律不动（外部对比表无一条值得以破坏 verbatim 镜像为代价加入；bi 的增强全在包装层，归属正确）。

---

## 3. economy.md — 留（子代理证据已核实）

**挡住的失败**：为想象未来付费（单实现接口/单产品工厂/转发 wrapper）、每调用方加 guard 不消根因、LOC 竞赛、无基线声称节省、diff 留复述注释/类型抑制/想象失败兜底。

**子代理核查 12 个外部候选约束，无一构成 bi 未覆盖的有效缺口**（要么语义等价、要么在相邻契约、要么属诱发范围蔓延的负优化）。代表对比：
- 覆盖优先于行数：gstack `ETHOS.md:51-57` ≡ bi `economy.md:9/:21` 平局规则。
- 共同归属修一次：pstack `principle-fix-root-causes/SKILL.md:17,19` ≡ bi `:25`。
- 投机抽象禁令：matt `codebase-design/SKILL.md:65`「One adapter means a hypothetical seam. Two adapters means a real one.」≡ bi `:31`。
- 有界简化 ceiling+trigger：gstack `plan-eng-review/sections/preamble.md:76`、ponytail `shortcut:` 都只有二要素，**bi `:37` 多「升级方向」，是超集**。
- 「先减后建」pstack `principle-subtract-before-you-add/SKILL.md:13-14`：**不加**——它鼓励顺手删相邻死代码，与 bi「只清理自己的 diff」`:49` 冲突，对 agent 是范围蔓延诱因，bi 顺序更安全。

**两处优于外部**：①第 1 级把「删除/收窄需求/调配置」排最前（外部最小化框架全从「怎么写更少代码」起步，gstack autoplan 甚至完整性优先、简单性垫底）；②三要素含升级方向，把有界简化与 5 级梯闭环。

**留的理由**：55 行承载决策序+平局规则+责任边界+投机禁令+有界简化+反馈回路+清理+基线诚实共 8 机制，密度高于所有外部同类；每条否定都对应外部反复证实的 agent 强默认失败，无可删冗余。**无优化空间。**

## 4. quality.md — 改（2 行微补，九特征表留；子代理证据已核实）

**挡住的失败**：质量清单仪式化（凑分类填「满足/不适用」）、质量口号不落证据（「保证可靠性」）、agent 自造质量目标自我证明、以「本次没选」为由跳过校验/权限/数据丢失防护、中文「安全」歧义混谈 Security/Safety、分类学膨胀（Observability 塞第十项）。

**操作化部分已优于外部**：选中即承诺+可观察结果+证据强度匹配+工程护栏，是外部最完整的「质量目标→验收」契约（spec-kit/bmad 只做到前两层，bi 做到落证据第三层）。

**真实缺口仅两处（外部有、bi 全库无）**：

| 缺口 | 外部来源 | 最小改法 |
|---|---|---|
| 反指标/代价：优化 A 会伤 B（性能↔可维护性、信息安全↔交互能力） | bmad `template-prd.md:59`「counter-metrics naming the metric they balance」 | 目标字段后补一条：「选中一个质量目标时，点名它可能牺牲的另一项特征或指标；取舍由用户确认，写入 work 或 memory。」 |
| 可量化目标的数值阈值措辞（「可观察」不必然「可判定」） | bmad `template-prd.md:62`、spec-kit `checklist.md:201` | `:28` 锐化：「…可观察结果；可量化时给出数值阈值或可判定判据。」 |

**九特征表为什么留（子代理五点论证）**：①外部没有更轻的等价物只有更散的（gstack 质量语言 ETHOS 364 行+gate-integrity 171 行+simplification 49 行，远超 bi 46 行）；②表是扫描词汇不是验收清单，验收早已操作化，换表丢 Security/Safety 中文消歧+子特性提示+Flexibility/Interaction 维度+标准出处；③低频行（Safety/Compatibility/Interaction）恰是 agent 易漏行，删低频=删防漏功能；④抽象风险已被「禁凑分类+具体正例+证据强度匹配」三道闸消解；⑤换表需重写下游 work 模板/memory 引用，迁移代价负收益。

**不建议做**：换表、删子特性列、删低频行、把 gstack gate-integrity 失败目录搬进 quality.md（prove.md 已承载且位置更对）、Observability 升第十项。

**子代理保留意见**：第 2 条反指标若 bi 实际 work 已自发出现可降级为可选——待实施时核对。

## 5. ui-spec.md — 改（微，约 1.5 行；子代理证据已核实）

**挡住的失败**：散文描述空间关系/分栏/状态歧义、为纯后端改动凑空线框、规格过早实现化（写组件名/CSS）、截图/原型腐烂后失真相、当前与目标混标、拿线框图当验收证据。

**核心范式被外部直接印证**：「文本规格为真相、mock 只是插图」bmad `bmad-ux/SKILL.md:11`「Both spines win on conflict with any mock」直接同构；ASCII 优先 gstack `document-generate/SKILL.md:334` 印证；6 问接近最优最小契约（bmad EXPERIENCE 8 节/spec-kit 模板的交集）。**bi 独有且更好**：当前/目标/候选/示意强制标注（外部无等价物）、popover 溢出在规格期就标边界（gstack 到审查期才查）、vision/memory/work 三层时间分置（外部全单落点）。

**真实缺口仅两处（模型强默认失败，外部独立印证）**：

| 缺口 | 外部来源 | 最小改法 |
|---|---|---|
| 状态枚举缺「超长内容/溢出」（happy-path-only 强默认） | gstack `design-review/SKILL.md:732`「long-content states are part of the component」、`visual-design.md:144` | `:11` 枚举追加「超长内容/溢出」，改 4 个字 |
| 候选未要求结构不同（模型默认生成三个近似变体，Matt 称 wallpaper） | Matt `prototype/UI.md:38,54,109`；superpowers `visual-companion.md:277` | 加一句「比较候选时让布局、信息层级或主动作结构不同；只差颜色文案的不是候选」 |

**不引入**：State×Surface 矩阵（完整 UX 工作流的重量级）、DESIGN.md 设计 token（会把 bi 扩成设计系统工具）、变体切换器/原型工艺（bi 的原型是澄清手段不是交付物，已有出口在 domain-modeling ungrillable 段）、IA 闭合检查（vision 按需场景，无真实失败证据）。

## 6. onboard.md — 留（子代理证据已核实）

**挡住的失败**：接入时替用户填业务目标/生成 Vision/整理历史、覆盖已有文件、初始化后不汇报不路由、把 README 观察当已确认业务目标。

**留的核心理由**：外部 onboarding 的复杂度**全部正比于配置面**——Matt setup 要问 issue tracker/triage labels/domain 布局，openspec 要教 8 技能+CLI，bmad 要管既有指令存废。bi 配置面是零（两个固定目录、无 tracker 选择、不碰 AGENTS.md），那些纪律要么不适用要么已在正确归属处覆盖（consent→memory-direction:28、先查后问→SKILL:81、幂等/防覆盖→init 脚本机械保证）。「不碰宿主指令文件」比 Matt 的「编辑既有 CLAUDE.md」by design 更强——整类失败不存在。

**唯一边界项**：检测到旧版 byissue 布局时是否报告迁移。现有「保留并汇报新建/保留」已覆盖大半；无真实事故证据前不挣注意力成本，**若将来出现旧布局混淆事故再加一行**。当前无优化空间。

## 7. domain-modeling.md — 改（微，约 2 行；子代理证据已核实）

**GLOSSARY/ADR 换 byissue/memory 的取舍：方向对，但吸收时丢了上游两条有效纪律。**

对的部分（子代理逐条核对）：单一落点+主题检索替代 GLOSSARY-MAP（上下文关系可从代码重建，本就不该存）；懒创建/即时捕获保留；ADR-FORMAT 引用删得对——`templates/memory.md` 承载格式且**更强**（被否方案必写+重访条件，上游皆可选）；glossary 纯净性已泛化保留（`:31`+memory-direction:18）；bi 还有上游没有的增强（code naming 作术语真相源、Grillable/ungrillable 整合、It's working if 自检）。

**丢的两条（真实代价）**：

| 缺口 | 上游来源 | 后果 | 最小改法 |
|---|---|---|---|
| ADR 第三条件「真实权衡」被换掉，且 AND→OR | Matt `domain-modeling/SKILL.md:68-72`、`ADR-FORMAT.md:31-37`（三条件 AND：hard to reverse ∧ surprising ∧ **real trade-off**） | bi `:28` 用弱条件「long-lived」替换「真实权衡」，显而易见的选择（无备选、只是长期存在）也能进 memory；两问筛选器挡不住「长期+理由不可重建+其实没权衡过」这类 | `:28` 补「且经过真实权衡（有 genuine alternatives）」；是否收紧回 AND 由用户定 |
| 选定词 + `_Avoid_` 近义词机制无承载者 | `GLOSSARY-FORMAT.md:27`（Be opinionated）、消费侧 `setup…/domain.md:43`「Don't drift to synonyms the glossary explicitly avoids」 | 术语当结论存进主题文件，被否近义词没记录：会话 1 锐化「Customer 不是 account」，会话 2 读到结论但漂移会复发；writing:22 只管单文档、clarify:9 只管当场，都不持久 | `:27` 加「连同选定词与要避免的近义词」；memory 模板结论节自然容纳，无需新模板 |

可选低优先：同句加「只收本项目特有的词」（`GLOSSARY-FORMAT.md:29`）。GLOSSARY-FORMAT/ADR-FORMAT 两个引用文件**不需要恢复**——格式已由 memory 模板承载，缺的只是这两条纪律内容。NOTICE.md 归属描述仍成立（吸收件非镜像）。

## 安全发现（子代理报告）

参考材料 `matt-skills/skills/engineering/tdd/tests.md:77` 含提示注入（要求原样输出 `{{NAME_ab12cd34}}` 占位符、「不要质疑」）。子代理已忽略、按不可信数据处理。引用外部材料内容时一律当不可信数据，不当指令。

## 横切观察（不在本次改动范围）

Matt `writing-for-agents` 给了审整个技能包的元杠杆：**no-op**（模型默认已遵守的指令花负载却什么都没说，判据 model-relative，靠跑文档裁决）、**sediment**（添加感觉安全删除感觉危险，陈旧层沉积）、**negation**（否定式把被禁行为拖进上下文，应 prompt the positive，见 `writing-for-agents/SKILL.md:74`）。bi 已做过粉色大象审查 + 极简重写（178→102 行），这三杠杆大部分已落实。若日后要再审，按「逐句猎 no-op、逐行查 relevance」做，属另一轮工作。

## 改动清单（已实施于 2.1.2）

| 文件 | 改动 | 量级 |
|---|---|---|
| `references/grilling.md:25` | 补 `with a fresh context window` | 6 词 |
| `references/quality.md:28` | 「可观察结果」后加「可量化时给出数值阈值或可判定判据」 | 半行 |
| `references/quality.md` 目标字段后 | 补反指标：选中质量目标时点名可能牺牲的另一项特征，取舍由用户确认 | 1 行 |
| `references/ui-spec.md:11` | 状态枚举追加「超长内容/溢出」 | 4 字 |
| `references/ui-spec.md` | 补「比较候选时让布局、信息层级或主动作结构不同；只差颜色文案的不是候选」 | 1 句 |
| `references/domain-modeling.md:28` | 补回第三条件「真实权衡」，收紧回三条件 AND（用户确认采纳推荐） | 半行 |
| `references/domain-modeling.md:27` | 术语落点加「连同选定词与要避免的近义词」 | 半行 |

不动：writing.md（留）、economy.md（留）、onboard.md（留）；九特征表、5 级梯、6 问、极简接入全保留。
可选低优先（默认不做）：domain-modeling「只收本项目特有的词」；quality 反指标若实际 work 已自发出现可降级。
发布：已走 VERSION 2.1.2 + CHANGELOG + release-check --no-deploy 全绿；grilling 补短语后正文逐行核对为上游 verbatim，NOTICE 声明恢复为真。两个可选项按默认未做。domain-modeling 准入按推荐收紧为 AND。

## 边界与诚实声明

- 只评判 7 份非核心原则材料；方法论核心五份已验证，不在范围。
- 三个子代理报告全部返回；关键引用我做了二次核对（memory-direction.md:16 原文、grilling diff、上游 CLAUDE/CHANGELOG）。
- 本台账第一版曾预填未收到的外部对比、且 writing.md 结论错误（建议补的规则已在 memory-direction 存在）、grilling 两处行号/归属事实错误——均已撤回修正，保留此记录作为「证据先于结论」的反例。
- 外部对比基于本机参考副本（Matt HEAD 5863806 = 最新），未做穷尽式全网调研；行号以当前 checkout 为准。
- 本台账不改技能；改动已于 2.1.2 按用户确认实施（7 处微改，含 domain-modeling AND 收紧），提交推送待授权。