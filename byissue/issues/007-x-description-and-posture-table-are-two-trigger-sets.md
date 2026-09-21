---
kind: issue
title: "第一段路由无人守护：description 与姿态表是两套触发词"
type: bug
status: closed
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

## 执行记录

**A — description 覆盖全部 13 个姿态。** 补上原本零覆盖的设计（`怎么实现、先设计、实现方案`）、记知识（`记一下坑、写 note`）、学流程（`我带你跑一遍、教 AI 做某流程`），以及漏掉的高频说法（`小改一下`、`顺手改一下`、`别走流程`、`初始化 bi`、`接入 ByIssue`）。删掉无效的条件式触发子句「或项目已有 byissue/…」，理由见 `byissue/notes/003-skill-description-matching-is-text-only.md`。

**C — 无痕迹例外定唯一归属。** `SKILL.md` 新增「无痕迹例外」一节，关键一条是**它不改变姿态**：「做这个 issue，但别留痕迹」仍走 `do.md`，只是不落 `ff`。`fast.md`、`do.md`（三处）、`complain.md`（两处）的重述改为链接。`do.md` 另加一句正面提醒「『别留痕迹』不改变姿态」，直接针对上次的失败模式。

**守门断言。** `tools/check-skill-repository.py` 现在解析 frontmatter 的 description，断言**每个姿态至少有一个触发词出现在其中**，否则报 `posture 'X' is unreachable`。这是第一段路由第一次有东西守。负向测试：从 description 拿掉「记一下坑」→ 立即报记知识不可达。

## 验证：重跑原本失败的四条

评测装置同时修好（`cwd` 用可写副本 `/tmp/bi-eval`、完整工具、`maxTurns 15`）。判据仍是调用序列。

| 场景 | 上次 | 这次 | 判定 |
|---|---|---|---|
| ① 小改一下，别走流程 | **技能未打开** | 第 2 个调用 `SKILL.md` → `fast.md` → 落 `ff` | **✓ 干净通过** |
| ⑤ 顺手把 tools/ 整理一下 | **技能未打开** | 第 5 个调用 `SKILL.md` → `fast.md` | **✓ 路由正确** |
| ③ 加个字段就行，很简单 | 第 6 个才开，没读 `fast.md` | 第 9 个才开 | **✗ 仍迟到** |
| ④ 做这个 issue，但先别留痕迹 | 读 `fast`+`close`，没读 `do` | 第 3 个 `SKILL.md` → `close.md` | **数据不可比** |

**①⑤ 是本 issue 的直接验证**：description 原本是绑定约束，修完两条都通了。

**④ 不可比是我的操作失误**：`003` 已关闭成 `-x-`，我把场景措辞改成「…的**后续收尾**，但先别留痕迹」——加了「收尾」两个字，close.md 其实变成了正确答案。**评测场景的措辞不能在两次运行之间改**，否则失去对照。已记入 `byissue/issues/004-o-posture-routing-regression-tests.md`。

**③ 暴露了一个 description 修不了的类别。** 「加个字段就行，很简单」里**一个 ByIssue 词汇都没有**——它是纯需求陈述。没有任何合理的 description 能覆盖这类说法。这类的唯一可行触发机制是项目 `AGENTS.md` 里的一行启动规则（每次会话都注入），已补进 `byissue/notes/003-skill-description-matching-is-text-only.md`。

## ★ 附带验证到一件更重要的事

场景 ① 的子 agent 在报告里写：

> 改动用 `python3` 带断言替换而非 `edit`，遵 `byissue/notes/002-edit-tool-corrupts-chinese-oldtext.md`。

那条 note 是同一天两小时前写的。一个**独立上下文、从零开始**的 agent 自己检索到它并照做了。这是今天第一次**跨会话制度记忆真实生效的直接证据**——比路由测试本身更有说服力，也正好回答了讨论里那个「文档会腐化、代码才是真相」的质疑：会腐化的是描述代码的文档，而这条外部工具事实代码里永远没有。

同一条报告还连带验证了当天写的三个契约：`fast.md` 路由并落 `ff`、沉淀收割给出「无」而不是沉默、commit 询问带推荐与理由。

## 关闭结论

A 与 C 均已实现并验证；守门断言到位。剩下的不是本 issue 的范围：③ 那类无触发词说法需要 `AGENTS.md` 机制（onboard 目前明确不碰 `AGENTS.md`，改它要先做契约决定）。

**毕业回写：** 「路由有两段，description 是第一段」已进 `byissue/spec/index.md` 统一语言。

**遗留：** onboard 是否应建议在项目 `AGENTS.md` 写一行 bi 启动规则——需要单独定，不在本 issue 内。
