---
kind: issue
title: "定义什么不该进 Project Spec，并把毕业改成筛选"
type: feature
status: open
created: 2026-09-21
---

# 定义什么不该进 Project Spec，并把毕业改成筛选

## 做成以后是什么样

`spec.md`、`close.md` 和 Project Spec 模板给出一条可执行的判据：**进 spec 的只有代码里重建不出来的东西**（统一语言、边界与被排除方案、长期质量约束、做/不做）；能力如何运作、架构地图、数据流叙述不进。Epic 关闭时的毕业动作从「合并稳定结论的具体内容」改成「筛出代码里没有的那部分」。

**范围：** 包含 `spec.md` 行动指南与产物契约、`close.md` 毕业规则、`templates/entities/project-spec-index.md`、`docs.md` 里相关表述的归属对齐。不包含存量 spec 的批量重写（见下），不包含 Epic Spec（它描述还不存在的东西，不腐，不动）。

## 为什么现在做

决策与完整论证见 `byissue/decisions/004-project-spec-drops-implementation-description.md`。要点：Project Spec 结构性必腐——它描述已经存在的东西，天生是代码的第二份表述。而现行 `close.md` 明写「不能只写『见某 Epic』，要合并具体内容」，等于在催 agent 写最容易腐烂的那类文字。

现状证据：三个真实仓库的 spec 共约 1400 行，其中 AGCopilot 的 311 行里「能力地图」「架构地图」正是腐化第一现场，而同一文件里的「统一语言」「状态与数据边界」不会腐——差别就在可重建性。

`docs.md` 其实早有一句「代码路径只作为证据索引或落点」，原则是对的，是 `spec.md` 的落地契约背叛了原则。

## 方案方向

- 判据写成一句可执行的：**代码里重建不出来的，或能被机器校验的，才进 spec。**
- 存量不批量重写（那是另一次 audit）。改成下次 close 回写到某一节时，顺手按新尺子处理那一节——与 `001` 共用「收割而不另起一件事」这条原则。
- 注意副作用：这条落地后，spec 分层压力会自然消失（AGCopilot 那 311 行按尺子过一遍大概掉到一百来行），**不要再单独做一个分层触发器机制**。

## 验证

拿 AGCopilot 现有 `spec/index.md` 做一次干跑：按新判据逐节标记「留 / 删 / 降为落点」，确认删掉的确实都是 `ls` 加读文件头能重建的，留下的确实都重建不出来。

## 关闭时

- 回写候选：判据本身属于长期约束，应进 ByIssue 自己的 `byissue/spec/index.md`。
- 相关：`byissue/talks/001-...` 第 4–5 节；`byissue/decisions/004-...`。
