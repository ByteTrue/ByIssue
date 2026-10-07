---
kind: issue
title: "授权推送时 issue 未关：跳跃路径无规则、检查未绑定动作"
type: bug
status: closed
created: 2026-10-07
---

# 授权推送时 issue 未关：跳跃路径无规则、检查未绑定动作

## 预期与实际

**预期：** 用户授权提交 / 推送 / 开 PR / 发布时，相关常规 issue 先关闭（`-o-` → `-x-`）并完成毕业回写，改名与回写随代码进同一笔 commit，只跑一趟 CI（[010](byissue/issues/010-x-close-before-commit-contract-timing.md) 契约，1.6.1）。

**实际：** byspace 会话（pi session `01a10fb2`，1242 行、6 次上下文压缩）中，用户说「发一版，同时提交改动、开PR」时两个常规 issue（epic 004 的 001、根树 002-o-pi-subagent-inline-tool-card）仍开着；agent 直接 commit + push + 开 PR #20，把关闭留到合入之后，收尾汇报与沉淀收割整拍被跳过。被质问时 agent 自己说出正确时序——「在你授权开 PR 的同时一并请求关闭授权、关闭完再推」——这条规则当时不在任何文件里。

## 根因

1. **契约不在执行点在场。** 全会话从未加载 `do.md` / `close.md`（以讨论姿态开场，滑到实现与推送，靠 `SKILL.md` 开头的压缩摘要运行）；1.6.1 修复的正向时序写在 `do.md`，推送那一刻不在上下文。
2. **跳跃路径未定义。** 010 修的是「实现完成 → 收尾汇报 → 授权」的正常节拍。用户直接下令提交+PR 时没有收尾汇报这一拍，「授权了 push 但未授权关闭」处于未定义状态，模型把「关闭要授权」读成推迟关闭的理由，动量选择先推后问。`fast.md` 第 70 行早有快改通道同款规则（「在提交前一并给出关闭建议并随同次提交关闭」），受管理通道与 `SKILL.md` 层缺失。
3. **注意力衰减。** 6 次压缩后，会话开头读入的 `SKILL.md` 摘要距推送决策 1100+ 行。措辞修不了位置问题——需要绑定到 git 动作本身的机械检查，而非依赖回忆。

## 修复方案

- `skills/bi/references/do.md`「收尾与提交」补跳跃路径：未经收尾汇报直接要求提交 / 推送 / 开 PR / 发布时，同轮补上关闭建议并请求授权，关闭完成后合并提交再推送；先推后关会把改名与回写拆成第二笔提交、多跑一轮 CI。
- `skills/bi/SKILL.md` Git 默认行为表加一行同款压缩规则（`SKILL.md` 是所有姿态都在场的唯一文件，与 1.7.1 宿主记忆段同一归属推理）。
- 新增 `skills/bi/scripts/check_open_issues.py`：提交 / 推送 / 开 PR / 发布前跑，列出根树与各 Epic issues 树中仍开着的常规 issue（open `ff` 仅提醒，open Epic 不列——那是进行中的正常状态），存在关闭门槛时退出码 1。检查绑定动作而非姿态，不依赖回忆，抗上下文压缩。
- 不要求用户改 `AGENTS.md`；想接 pre-push hook 的用户可自行接入（可选附加项，非必要条件，与 decisions/007、008 一致）。

## 验证

- 脚本实测：夹具（open 常规 + open ff + open Explore 目录 + open Epic issue + closed/d 各态）分类全部正确，退出码符合预期；本仓库 013 落盘前退 0、落盘后退 1；byspace worktree 退 1 并完整列出其 open 常规 issue；无 `byissue/` 的目录退 0。
- `python3 tools/check-skill-repository.py` 通过（脚本已被 `SKILL.md` 反引号全路径引用；姿态表未动，无需行为评测）。

## 执行记录

- 2026-10-07：落地上述三项改动；`VERSION` → 1.7.2，`CHANGELOG.md` 同名小节；`close.md` / `fast.md` / README 未动（前者「代码先行提交时关闭单独成笔」是恢复路径不是许可，fast 通道已有同款规则，README 从未承载过时序契约）；清理会话分析的临时脚本。发版提交按新契约将本 issue 改名 `-x-` 随代码单次 commit。

## 关闭结论

1. **判断成立**：跳跃路径（授权提交而 issue 未关、无收尾汇报）确实无规则，且契约存放位置与执行点脱节是主因——被质问时 agent 能复述正确时序，证明不是措辞问题而是位置问题。
2. **回写位置**：契约本体落在 `skills/bi/SKILL.md`（Git 默认行为表）与 `skills/bi/references/do.md`（收尾与提交），`spec/index.md` 已声明 `skills/bi/SKILL.md` 为唯一权威入口，不另写一份；未立 decision（一段规则补全不满足「难以逆转」门槛）。证据与取舍记录在 `CHANGELOG.md` 1.7.2 小节。
3. **遗留**：① 行为回归评测仍缺位（issue 004 追踪）；② 剩余风险——上下文烂掉的会话若根本不记得跑检查脚本，纯提示层无法兜底，用户侧 pre-push hook 是可选加固而非必要条件，已在 CHANGELOG 记录。
