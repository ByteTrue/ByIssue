---
kind: issue
title: "引用事项必须给完整文件名或目录名"
type: feature
status: open
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
