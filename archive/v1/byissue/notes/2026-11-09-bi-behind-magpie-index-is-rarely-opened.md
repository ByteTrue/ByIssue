# 经 magpie 索引安装时，bi 很少被打开

> **读者：** 在本机跑姿态评测或行为探针的人。

**这是用户有意的安装方式，不需要修。** 用户 2026-11-09 原话：「索引间接安装，这个事情可以不用管，是我刻意的……我要用的话，我会主动说 BI」。适用范围：长期。下面的事实只影响本机怎么跑评测。

**结论：** 本机 bi 经 magpie 安装，宿主实际加载的是 `~/.config/magpie/library/skills/bi/`。`~/.agents/skills/bi/` 不存在。系统提示里列出的技能只有 `magpie-skills` 一个索引，bi 的名字只出现在索引的长清单里，它的 `description` 根本没进系统提示。所以 `byissue/notes/003-skill-description-matching-is-text-only.md` 讲的文本匹配在这里用不上：要打开 bi 得先读索引，再读 bi，多绕一层。

**证据（2026-11-09，子 agent 默认工具，`cwd` 为带 `byissue/` 的临时 git 项目，统计依据是会话日志里有没有读 `skills/bi/SKILL.md`）：**

| 说法 | 打开 bi |
|---|---|
| 只有需求句（审 diff、快改文案、修 bug 各一条） | 0/3。审 diff 那条打开的是直接列在系统提示里的 `ponytail-review` |
| 句首加 `bi` | 1/3。修 bug 那条在回复里说「你说的 "bi" 我当成打字错误处理了」 |
| task 里写明 `SKILL.md` 路径 | 2/2 |

日志都在 `~/.pi/agent/sessions/--private-tmp-{notes-app,ledger-svc,shop-cart}--/` 下，每个目录里的日志按时间排序，依次对应表中各行（ledger-svc 没有跑第三行）。复现：`grep -c 'skills/bi/SKILL.md' <日志>`，结果为 0 就是没打开。

**怎么办：**

- **评测前先找出宿主实际加载的副本**，同步到那里，再用 `diff -rq` 确认和仓库 `skills/bi/` 一致。本机找法：`readlink -f ~/.pi/agent/skills/magpie-skills/.skills/bi`。
- **magpie 会从 GitHub 拉回这份副本，盖掉本地 rsync 的内容。** `~/.config/magpie/library.json` 里 bi 的来源是 `github`、`Bytetrue/ByIssue`、`skills/bi`。2026-11-10 10:57 它把副本换回了当时远端的 `0d7e5f6`（1.13.3），而本地已经 rsync 过 1.14.0–1.14.2，`diff -rq` 对 0d7e5f6 的归档为 0 处差异。所以没 push 的改动在这台机器上只能临时测：rsync 之后马上跑探针，跑前跑后各 `diff -rq` 一次；中间隔得久，先重新 rsync。push 之后它会拉到新版本。
- **在本机测 bi 内部规则的探针**，task 里写明 bi 的 `SKILL.md` 路径，再接用户那句话。这样测的是「打开之后怎么做」，测不了路由。
- **路由评测**（`tools/posture-scenarios.md` 的场景表）在这种安装方式下测的是「索引会不会被打开」，不是 bi 的姿态路由。要测姿态路由，得换一个 bi 直接列在系统提示里的环境。
