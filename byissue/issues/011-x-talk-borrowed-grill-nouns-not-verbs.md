---
kind: issue
title: "Talk 借了 grill 的名词没借动词：拷问循环退化成一轮选项"
type: bug
status: closed
created: 2026-09-23
---

# Talk 借了 grill 的名词没借动词：拷问循环退化成一轮选项

## 预期与实际

**预期：** Talk 姿态像上游 `mattpocock/skills` 的 `grill-with-docs` 那样多轮拷问，直到把模糊点尽可能梳理完才收。

**实际：** 用到 Talk 时基本不拷问——LLM 自己象征性给几个选项，一轮就搞定。用户长期体感如此，非个例。

**最小场景：** 任何模糊需求进 Talk，模型给「三个选项 + 一句推荐」，用户挑一个，会话即收束。

## 根因

不是「模型不够努力」，是规则写漏了。`talk.md` 只借了 grilling 的**结论名词**（「前沿清空，即对齐完成」），没借**产生结论的动词**：

- 没有**设计树**（每个决策分叉出挂在其下的决策）。
- 没有**前沿的定义**（前置已定的决策集合），只有一个弱化到单数的「当前最关键分叉」。
- 没有**「每轮重算前沿」**这个动作。
- 终止条件是「真问题一句话且用户确认 / 做什么有轮廓 / 最大未知已标出」——**三条都不需要用户开口**，模型第一轮就能自我宣告满足。
- 「最多三到五轮深挖」是全场唯一带数值的指令，被当成**目标**而非上限。

这是 spec/index.md 那条「描述句 vs 祈使句」老坑的一个变体：**借了名词没借动词**。对照 grill 原文，「前沿」是一串祈使句的产物（Map the tree → Ask the whole frontier → Wait → Recompute → Done when empty），talk 里对应位置只剩一句修辞。

同病的其他现场：`vision.md`「提出最能改变地图结构的**一个**问题」（硬限成一个、且无树）；`design.md`「接口未清时**标待确认**」（标出 ≠ 问出，把成本推给实现阶段）。

## 方案

按上游 `grilling`（primitive）+ `grill-with-docs`（落盘 wrapper）的拆分来：

1. **新建 `skills/bi/references/grilling.md`** —— 纯访谈循环，本体不写任何文件。祈使句写全：建设计树（不落盘，避免第二个真相源）、每轮问整个前沿、事实自己查决策等用户、前沿为空且用户确认才停、不设轮数/问题数上限（校准：46 问落 4 轮是普通会话）、四条假信号表、谈不出来的问题去原型。
2. **`talk.md` 降级为 wrapper** —— 提问循环全部指向 grilling，只保留 Talk 增量：「前沿为空且用户确认前不给施工方案、不落盘」。删掉重复的收住条件细节和「三到五轮」上限。
3. **修 vision.md / design.md 两处同病** —— vision 的「一个问题」改为一轮问完整层前沿；design 的「标待确认」改为问用户。
4. **SKILL.md** —— 姿态表讨论/愿景/设计的「按需读」加 grilling；「提问必须带建议」加一段指向它；原则文件表加一行；description + 姿态表加触发词「拷问我」（两段路由都要有，见 issue 007）。
5. **同步契约** —— README 中英版的 Talk 停止条件（原来正是「已能说清最大未知」这条假信号）、spec/index.md 的 references 计数 18→19 + 新增统一语言「Grilling」+ 描述句坑补「借名词没借动词」变体、posture-scenarios.md 加场景 25。

**决策树不落盘**是刻意取舍：grill 自己承认前沿是判断不是计算图，落盘会造第二个真相源要维护两份。

## 验证

- `python3 tools/check-skill-repository.py` 绿（新文件被 talk/vision/design/SKILL 多处引用，满足「打包文件必须被引用」）。
- 新增姿态触发词「拷问我」同时进了 description 和姿态表，checker 的「触发词须出现在 description」断言通过。
- **行为验证是已知缺口（见遗留）**：是否真的多轮拷问，需要多轮 subagent 评测才能证伪，而当前装置是单轮 `task`。

## 关闭时

- 毕业回写：spec/index.md 统一语言加「Grilling」、references 计数、描述句坑的变体 —— 已随本 issue 一并写入。
- 相关：`byissue/talks/001` 第 7 节（首次发现 ByIssue 抄了 grill 但差在语气）、`byissue/issues/005-x-posture-stability-across-authorized-actions.md`（同一根因「描述句不触发」）、`byissue/issues/004-x-posture-routing-regression-tests.md`（多轮评测缺口）。

## 遗留

**多轮行为评测能力缺口**：验证「grilling 是否真的多轮拷问」必须多轮评测。issue 004 的遗留早已写明「场景 21、23 需要多轮设置，当前单轮 `task` 跑不了，这是评测能力的缺口」。本次新增的场景 25 同样受此限。补跑法（`subagent` 的 `resume` + 原 cwd）等真需要验证 grilling 有效性时再做，不在本 issue 范围内强行扩。


## 修正：只抄了一半（用户纠正）

用户要求「提示词效果上确认和 Matt 那边一致」。逐句对照上游全文（`grilling` + `domain-modeling` + 三份 docs + 三个 changeset）后，第一版漏了八处承重指令。

| 上游 | 第一版 |
|---|---|
| `relentlessly` | 无强度词 |
| 轮次格式模板（标题 / 正文 / `➡️` 推荐各占一行，问题间 `---` 分隔） | 只说「编号 + 推荐答案」 |
| `dispatch a sub-agent to find it` | 只写「去查」 |
| 前沿是判断不是计算图；发现同轮依赖后**在下一轮重开那个分支** | 无 |
| 「另一个技能在 resolve-this-ticket 框架里跑 grilling」是替用户答题的主因 | 无 |
| 「不是一次问一个，也不是一次问全部」 | 只说了后半 |
| 用户要求「一次只问一个」的逃生口 | 无 |
| **domain-modeling 全部四条**：与词汇表顶撞、磨模糊词、编具体场景压边界、拿代码对照 | **全无** |

`grill-with-docs` = `grilling` + `domain-modeling`，第一版只做了前半。

### 三条架构级修正

1. **grilling 从姿态表「按需读」提到「必读」**（讨论、愿景两行）。上游 doc 记录的头号故障正是「技能跑了但没加载 `grilling`，于是模型即兴访谈、一次性倒出所有问题、不带推荐」——与本 issue 的用户症状逐字吻合。放在「按需读」等于复刻同一个故障模式。
2. **补 domain-modeling 的读取侧**：访谈中当场顶撞术语、编场景压边界、拿代码对照用户陈述。**写入侧不复制**——统一语言归 `spec.md`、立碑三条件归 `SKILL.md` 与 `templates/entities/decision.md`，grilling 只留「当场接住，别攒到最后」这个反射加指针。理由是单一归属：复制写入契约必然漂移。
3. **补轮次格式模板**，含标题行与 `---` 分隔。上游为分隔符单独发过一个 changeset，且 doc 明说这个格式「是一轮能按编号回答的原因」；标题还迫使每条问题落在一个决策上，而不是一句闲话。

### 验收

31 项承重行为逐条对照通过（`relentlessly` / 树 / 前沿定义 / 整轮问完 / 编号加推荐 / 等待 / 格式模板 / 分隔符 / 重算 / 依赖推后 / subagent / 不阻塞 / 决策归用户 / 替答即坏 / 前沿为空 / 无静默假设 / 确认门 / 判断非计算图 / 重开分支 / 不是一问一答也不是全倒 / 一次一问逃生口 / 不设上限 / 谈不出来去原型 / 任务框架误读 / primitive 非步骤 / 顶撞词汇 / 磨词 / 编场景 / 对代码 / 当场捕获 / 立碑三条件）。上游 `grilling` 291 词 → 本文件 198 词。

连带同步：`tools/posture-scenarios.md` 场景 1、2、16 的「应读取」列补 `grilling`（否则评测与姿态表互相矛盾）；`SKILL.md` 原则文件表删掉 grilling 行（已进姿态表必读，同一契约不留两处表述）。
