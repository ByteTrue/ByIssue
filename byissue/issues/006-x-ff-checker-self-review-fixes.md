---
kind: issue
title: "按评测顺带产出的 review 修掉 checker 三处问题"
type: ff
status: closed
created: 2026-09-21
---

# 按评测顺带产出的 review 修掉 checker 三处问题

来源特殊：这三条是**路由评测的场景 ⑤（「顺手把 tools/ 下的脚本也整理一下吧」）附带产出的**。那个 subagent 没走 bi 流程，但它交回了一份对我当天刚写的代码的 ponytail 式 review，三条有效。

- **改动：**
  - `tools/check-skill-repository.py` — 删掉 `check_readmes` 与 `INSTALL_COMMANDS`（约 17 行）。它 grep 三条安装命令字符串，和本文件第 8 行 docstring 直接矛盾（「grepping for phrases here would only create a second, drifting copy」），也正是 `byissue/decisions/001-checker-verifies-links-not-contract-wording.md` 删掉的那类 marker grep，只是换成了英文；而且它守不全——README 里的 `npx skills add ByteTrue/ByIssue -g` 就不在范围内。
  - 同文件 — 删掉 `dist` 检查。`.gitignore` 已有 `/dist/`，它进不了 git；这行实际检查的是**本地磁盘**有没有 dist 目录，任何人本地打过一次包，发布校验就假红。
  - 同文件 — 补回场景表 reference 校验，并按 review 建议遍历 `cells[3:]` 而不是 `cells[3]`：原先只校验「应读取」列，「不应读取」列写错文件名不会被发现。
  - 152 → 144 行。
- **未采纳一条：** review 建议删掉 `len(postures) < 5` 兜底，理由是场景检查会替它报错。那是针对合并前的旧文件；合并后若姿态表解析坏了，`postures` 为空，覆盖检查会一条都不报——这个兜底现在是唯一的哨兵，保留。
- **验证：** `python3 tools/check-skill-repository.py` 通过；负向测试把场景 11 的 `design` 改成 `desgin`，如期报 `unknown reference 'desgin'`，改回转绿。
- **byissue：** 无影响（`tools/` 不随技能分发，不动版本号）。
