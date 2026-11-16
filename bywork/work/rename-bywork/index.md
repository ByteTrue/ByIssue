---
kind: work
status: complete
current_unit: "ByIssue → ByWork 改名完成：独立仓库 ByteTrue/ByWork 已发布，两仓已推送"
next_action: "无；byspace 全新会话 bw 触发冒烟留待用户下次实际使用时自然验证（本仓宿主已热加载 bw，init 幂等已实测）"
must_hold: "历史文档与冻结评测快照保留旧名不改；byspace 的 .gitignore/Makefile 用户在途改动不碰；archive/v1 冻结；ByIssue 仓库保留作研发档案不改名"
proof_gap: ""
---

# ByIssue → ByWork 改名

## 目标与边界

用户于 2026-11-17 拍板改名 ByWork：名字词源已死（by=bytetrue ID、issue=v1 单元），只有 byspace 一个消费者，现在是迁移成本最低点；评测结论证明方法论，路径字面量改名不使其失效。完整命名决定、触及面实测、实施顺序与风险见同目录 [rename-checklist.md](rename-checklist.md)。

边界：只改当前契约与活引用；历史文档（CHANGELOG 旧节、已完成 work、台账、memory 依据条）与冻结评测快照保留旧名。不重跑大型评测（字面契约变更，无行为规则改动）。

## 已定方案与约束

- 技能 ID `bi`→`bw`，description 触发列表保留「bi、ByIssue」旧称别名；目录 `skills/bi/`→`skills/bw/`、`byissue/`→`bywork/`、`init_byissue.py`→`init_bywork.py`；VERSION 3.0.0。
- 历史 work 中的 `byissue/...` 路径引用统一改道为 `bywork/...` 保链接可达，文字叙述中的产品旧名 ByIssue 保留；checker 实跑确认无断链。
- GitHub 拓扑（m03388 改定）：新建独立仓库 ByteTrue/ByWork，main 即当前 v2 全量快照（skills/bw + tools + 完整 bywork/ + 文档，链接全 intact）；ByIssue 原地保留作研发档案，不改名。理由：就地改名会让 ByWork 仓库默认分支仍是 v1，需更大的分支操作才自洽；新仓库 main 直接名实相符，git 开发史本就留 ByIssue 不丢。随提交推送一并请求授权。
- 备选：推迟到首次对外分发再改名——被否，最强理由是改名破坏已有安装；否决依据：当前仅一个消费者且可同批改道，拖到多消费者时迁移成本单调上升。

## 行为证明

| 行为路径 | 真实入口 | 操作 | 应观察到 | 证据 | 结果 |
|---|---|---|---|---|---|
| 分发包改名后结构一致 | release-check --no-deploy | 改名后全量维护检查 | checker、反例自测、脚本夹具、运行器测试全绿 | checker passed、22/22 反例、21 脚本夹具、14 运行器测试，release check passed | 通过 |
| 本仓工作目录迁移 | check_work.py --project . | git mv byissue bywork 后校验 | 全部 work 一致，无断链 | check_work 5/5 consistent；checker 无断链报告 | 通过 |
| byspace 迁移守卫不回退 | byspace 守卫命令 | git mv + 活引用改道后复跑 | docs-links/audit:ledger/parity/typecheck/lint/format/go test 与迁移基线一致（MISSING 0） | docs-links 2 pass 0 fail；audit:ledger 512 文件 MISSING 0；parity-surface 4 pass；go hostsync 15 passed；typecheck 无 error；oxlint 0 warnings 0 errors（2134 文件）；format:check 全过；i18n vitest 7 files 135 tests；check_work 2/2 | 通过 |
| 新触发词冒烟 | 本仓宿主 skill 加载 + init_bywork.py | 改名后宿主重载技能并跑 init | 加载 skills/bw，bywork/ 已存在时幂等保留 | 本仓 system-update 推送 bw 新技能（description 含旧称别名）；byspace 跑 init_bywork.py 输出 work/memory 均 kept。byspace 全新会话 bw 触发未单独跑，留待用户实际使用自然验证 | 通过 |
| 用户在途改动隔离 | git status | 提交前核对 | byspace 的 .gitignore/Makefile 保持未 staged 未修改 | git diff --cached 无 .gitignore/Makefile；工作树与索引一致、无未跟踪残留；byspace 提交 79faeb91b 仅含改名 + i18n 产物 | 通过 |
| 新仓库发布与两仓推送 | gh repo create + git push | 新建 ByteTrue/ByWork、指向 remote、提交推送 | ByWork main 即 v2 全量；byspace main 含迁移+i18n；ByIssue 保留 | gh 建 public 仓 https://github.com/ByteTrue/ByWork；ByWork 提交 8b93823（243 文件）推 main，branch.main.merge 残留 v2 已清；byspace 提交 79faeb91b（362 文件）推 main（8c5007087..79faeb91b），lefthook format/lint/typecheck 通过；ByIssue 仓库未改名 | 通过 |

## 证据与决定

- 本 work 的建立本身是一次规则修正：改名清单最初误挂在已 complete 的 v2-delivery 下，被用户指出后挪出。复盘产物挂原 work、带待办和验收的新目标建自己的 work；该归属规则已写入 memory-direction.md，并由 check_work.py 的 complete-work 引用检查机械咬合。
- byspace 原计划分两提交（先 i18n 再改名），实测发现 `byissue/→bywork/` 的 323 条 rename 在更早迁移会话就已暂存，与 i18n 内容改动缠在同一索引；硬拆需撤出全部 rename 再逐文件分 hunk，风险高、收益仅历史好看。改为一个提交涵盖两部分，message 写清边界。这是按真实 git 状态调整方案，非降低验证标准。
- 盲替教训：含旧称别名/历史对照的行（SKILL.md description 触发列表、清单「旧→新」表）不能进批量替换，本次两处误伤均核对修回。