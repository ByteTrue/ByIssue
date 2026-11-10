---
kind: epic
title: "pstack 维护侧逐项裁定：它怎么测自己、怎么记变更、怎么强制规则"
created: 2026-11-10
---

# pstack 维护侧逐项裁定：它怎么测自己、怎么记变更、怎么强制规则

> **读者：** 接着做这次裁定的 agent，以及以后想知道「ByIssue 维护侧的某个检查为什么这样做、pstack 的某个做法为什么没学」的人。

## 要改变什么

ByIssue 的维护侧（`tools/`、发布链路、`CHANGELOG.md`）比较薄。`byissue/spec/index.md`「谁在挡这些规则」里有四行强制者是「无」：改完 `skills/bi/` 跑对抗审查、动过姿态表或必读文件后跑姿态评测、rsync 同步部署副本、零依赖。行为评测靠手工起子代理、手工读会话日志判分。pstack 仓库在技能之外有一整套维护设施：`tests/` 下 70 多个测试、`tools/generate.mjs --check` 挂在 pre-commit 和 CI 上、`CHANGES.md` 133 个版本每条写明改了什么和为什么、`tla/` `lean/` 的形式化模型带变异测试。这个 Epic 让 pstack 维护侧的每一项都有一条带证据的结论，把值得学的列给用户定，再逐项落到 ByIssue 的维护侧。

## 已定方案与必须守住

- **这是上一个 Epic 定下的下一个议题。** 用户 2026-11-09 原话：「我觉得可以学习呀，我感觉就是我们这边比较薄弱的地方，我觉得可以专门开个事项或者课题去做。等这次做完之后，下一步就做这个吧」。适用范围：本议题。
- **不 fork pstack，按条吸收。** 用户 2026-11-09 原话：「pstack 并没有实现我想要的效果，所以我这边的结论是否定做 v2 版本。继续只吸收优化我们的」。适用范围：长期。
- **做法沿用上一个 Epic。** 机械列举进台账，读文件和初判交给 DeepSeek 子代理分单元做，父会话核对引用是否真实、「已有」是否同一时点同一检查，候选攒成一次交给用户裁决，再逐项落地。
- **形态约束**，出处 `byissue/spec/index.md`「改这个仓库要守什么」：零依赖（标准库 Python 加 Markdown）、只分发 `skills/bi/`、技能自足、中文为主。零依赖是对 ByIssue 整个仓库说的，维护侧工具也是标准库 Python 加 shell。
- **用低价模型。** 审查和行为评测用 DeepSeek，出处 `byissue/spec/index.md`「这个项目是什么」。

## 结论的判据

- **已有**：引出 ByIssue 里（`tools/`、`byissue/spec/index.md` 发布链路、`CHANGELOG.md` 写法、`tools/fixtures/`）的 `文件:行` 和原句，说明它在**同一个时点**做**同一项检查或同一种记录**。「也有测试」「也有 changelog」不算。
- **候选**：说明它在 ByIssue 能挡住哪一类具体失败，最好指到 ByIssue 历史上真发生过的一次（`CHANGELOG.md` 某版本、`byissue/issues/`、`byissue/notes/`、`byissue/decisions/` 里的记录，引 `文件:行`），以及会落到哪个文件；用到第三方工具（bun、node、lean、TLA+、markdownlint、pre-commit 框架）的，写明换成标准库 Python 或 shell 的做法，或判不吸收。
- **不吸收**：理由必须是形态约束之一、与 ByIssue 现有契约的具体冲突（引 `文件:行`），或只服务 pstack 自己的机制（多宿主适配、上游同步与 fork 管理、PR 与发布流水线、运行时代码的单元测试）。
- **M1（CHANGES.md）的判法不同**：每行是 10 个版本。要找的是两类东西：一是它怎么写变更记录（格式、写不写原因与证据）；二是**改技能散文的教训**，即某条规则改动后靠什么证据判断它起没起作用（例如「Live sessions showed that it changed nothing」这类）。每个教训对照 ByIssue 有没有同样的认识（引 `byissue/` 或 `tools/` 的 `文件:行`），没有的列为候选。

## 当前方案

台账 [ledger.md](ledger.md) 按类型切成五个单元：M1 `CHANGES.md`（按 10 个版本一行），M2 根目录文档与配置、`.github/`、`docs/`，M3 `tools/` 与 `lean/` `tla/`，M4 `tests/` 顶层，M5 `tests/pi/`。每个单元交给一个 DeepSeek 子代理逐行给结论与证据，写到 `/tmp/pstack-M<n>.md`；父会话核对后用上一个 Epic 的 `merge_unit.py` 并回台账（单元名换成 M<n>）。

## 用户裁决

2026-11-10，用户在「按推荐学这 8 条」上确认，选项原文：「按依赖顺序做（先 checker 与自测，最后串成发布前脚本），每条用一个会变红的坏样例证明它真能拦；不动 skills/bi 就不升 VERSION」。同时在「补，版权人写原作者 liuzhengdong 与 fork 维护者 ByteTrue」上确认补仓库根 LICENSE，选项原文：「照 README 末尾那句归属写 MIT LICENSE；上游镜像归属放仓库根 NOTICE，不进分发包；开写前核一遍上游许可证」。清单见 [candidates.md](candidates.md)。

## 收尾前补的两步

用户 2026-11-10 在「先提交 1.14.2，再并行做复核和脚本单元，之后关 Epic」上确认：

- 逐行复核 33 行「已有／已有·部分」是否同一时点同一检查（关闭条件本来就要求）。
- 补单元 M6：pstack 技能自带的 13 个脚本（`plugins/pstack/skills/*/scripts/`，不含 `watch-pr/`、`statechart/` 的 PR 与图生成代码）。上一个 Epic 只按 SKILL.md 判了技能，这些脚本跟着 PR 流水线一笔带过；其中 `check-plan.mjs` 机械校验计划里每个单元有没有证据框，和 `large.md` 的台账对得上。

## 未确认问题

- 候选落地后算不算 `skills/bi/` 的发布：只改 `tools/` 和 `byissue/` 时不动 `VERSION`，发布链路里的提示词审查只在动了 `skills/bi/` 时跑。裁决后按候选逐个定。

## 关闭条件

台账全部行是 `做了` 并带结论与证据；「已有」类逐行复核过同一时点同一检查；候选已交用户裁决；裁决为吸收的项已落地并有检查跑通的证据，或经用户确认推迟。

## 关闭

2026-11-10 关闭。138 项加补单元 M6 的 13 项都有结论与证据；已有类逐行复核（表格里 30 行：维持 29、翻为不吸收 1，过时证据就地标「复核：」）；用户批准的 8 条与 LICENSE 随 1.14.2 落地，复核时顺手修的三处检查随本次提交；M6 唯一候选用户定为等台账在真实项目里用过再看。毕业到 Project Spec 的：「谁在挡这些规则」表新增的几行与发布链路改写（随 1.14.2）、「许可证随包走」一条、「当前没有的东西」里台账检查那一句。
