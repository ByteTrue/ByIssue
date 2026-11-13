---
kind: issue
title: "引用事项必须给完整文件名或目录名"
type: feature
status: closed
created: 2026-09-21
---

# 引用事项必须给完整文件名或目录名

## 做成以后是什么样

`SKILL.md` 里「引用 Epic Issue 时必须给完整路径」扩展成通用规则：**任何地方引用事项都要写完整文件名或目录名**，不允许裸编号（`Issue 087`、`byissue/issues/018`）。编号方案本身不动。

**范围：** 一处规则扩写，可能顺带在 `close.md`／`fast.md` 的回写段落各补半句。存量的裸引用不回改。

## 为什么现在做

决策见 `byissue/decisions/005-accept-number-collisions-require-full-name-references.md`。实测：14% 的编号被共用，但真正歧义的引用只有个位数——疼的是「裸编号 + 碰撞」的组合，不是碰撞本身。修引用一行就够，修编号要换方案。

## 验证

改完在 AGCopilot 跑一次快改，断言产出的 `ff` 里引用其他事项时写了完整文件名。

## 关闭时

- 这是 `ff` 量级的改动，不必走完整受管理流程；建立事项只是为了挂住 `decisions/005` 的论证。

## 执行记录

`SKILL.md` 里「Issue 编号不是全局身份」那句改写：点明同一棵树也会撞号（并行会话各取「最大序号 + 1」）、这是**已接受的代价**，然后把「必须给完整路径」从只约束 Epic Issue 扩展为**引用任何事项都必须给完整文件名或目录名**，并给了正反例（`issues/018-x-feishu-first-class-entry/` vs `Issue 018`）。

编号方案未动，符合 `byissue/decisions/005-accept-number-collisions-require-full-name-references.md`。

## 验证

`python3 tools/check-skill-repository.py` 通过。真实快改场景的断言并入 `byissue/issues/004-x-posture-routing-regression-tests.md`。

## 关闭结论

`SKILL.md` 一处改写完成，编号方案未动。论证在 `byissue/decisions/005-accept-number-collisions-require-full-name-references.md`。

**遗留：** 存量裸引用不回改（个位数，上下文可读）。
