---
kind: issue
title: "第一段路由无人守护：description 与姿态表是两套触发词"
type: bug
status: open
created: 2026-09-21
---

# 第一段路由无人守护：description 与姿态表是两套触发词

## 预期与实际

**预期：** 用户说出姿态表里列的触发说法时，`bi` 应该被打开，然后路由到对应姿态。

**实际：** 路由其实有**两段**——第一段决定技能开不开，由宿主注入的 skill `description` 文本决定；第二段才是 `SKILL.md` 的姿态表。两套触发词从来没有对齐过：

- 姿态表里的「小改一下」「别走流程」「顺手」「加个字段」**都不在 description 里**。
- **设计 / 记知识 / 学流程三个姿态在 description 里零覆盖**：`怎么实现、先设计、实现方案`、`记一下坑、写 note`、`我带你跑一遍` 一个都没有。

**证据：** 首次路由评测场景 ⑤「顺手把 tools/ 下的脚本也整理一下吧」，在一个**已经有 `byissue/`** 的仓库里，技能全程没有被打开。详见 `byissue/issues/004-o-posture-routing-regression-tests.md`。

## 第二个缺陷（同一次失败的另一半）

场景 ④「做 XXX 这个 issue，但先别留痕迹」路由到了 `fast.md` + `close.md`，没读 `do.md`。「做这个 issue」是受管理实现的教科书触发词，把它带偏的是「别留痕迹」——因为**无痕迹例外同时写在 `fast.md` 和 `do.md` 两处**。这是契约重复直接造成的路由错误，属于 1.2.0 审计针对的同一类问题，应一并修。

## 方案方向

- description 的触发列表要覆盖姿态表里的高频说法，尤其补上零覆盖的三个姿态。注意 description 有长度与可读性代价，不是简单堆词——要挑真正会被说出口的。
- 修完才能给 `tools/check-skill-repository.py` 加断言：**姿态表的触发词必须在 description 里有覆盖**。现在加会直接红。这条断言是本 issue 的主要长期价值——它让第一段路由第一次有人守。
- 无痕迹例外定唯一归属（倾向 `SKILL.md`，因为它跨 fast 和 do 两个姿态），另一处只链接。

## 验证

重跑评测场景 ①③⑤（触发）与 ④（归属），断言技能被打开且读对必读文件。注意修正评测本身的两个问题（只读工具、8 turns 上限），见 `byissue/issues/004-o-posture-routing-regression-tests.md`。

## 关闭时

- 回写候选：「路由有两段，description 是第一段」属于长期约束，应进 `byissue/spec/index.md` 的统一语言。
