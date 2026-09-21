---
kind: issue
title: "按第二轮评测附带的 review 清理 checker"
type: ff
status: closed
created: 2026-09-21
---

# 按第二轮评测附带的 review 清理 checker

又一次「顺手」产出：路由评测场景 ⑤ 第二轮（「顺手把 tools/ 下的脚本也整理一下吧」）交回 9 条缺陷清单。其中 2 条在我修悬挂引用时已经顺带解决，1 条是历史记录不必动，其余照做。

- **改动：**
  - `byissue/spec/index.md` — 发布链路第二步还让人跑 `tools/check-posture-routing.py`，**那个脚本早已删除**。这是真·活缺陷：文档指向一个不存在的命令。改成「动过姿态表则起 subagent 按 `tools/posture-scenarios.md` 跑一轮行为评测」，与「主跑法是 subagent 不是脚本」保持一致。
  - `tools/check-skill-repository.py` — `LINK_RE` 的 `[^)#]+` 让带锚点的链接（`](references/foo.md#节)`）**整条匹配失败**，既不校验也不报错，是个静默漏检。改为允许锚点、只取 `#` 前的路径。负向测试：`[fast](nonexistent.md#x)` 现在如期报 `points at missing path`。
  - 同文件 — 拆出 `check_scenarios(report, postures)`：原来 `check_posture_table` 跨 `SKILL.md` 和场景表干两件事，docstring 只描述前半段。
  - 同文件 — 模块 docstring 补上后来折进来的姿态表与场景表检查，并写明两件**刻意不检查**的事（契约文字、语义路由）。
  - 同文件 — `report` 从带 `# noqa: E731` 的 lambda 改成嵌套 `def`。
  - `tools/check-skill-repository.py`、`skills/bi/scripts/init_byissue.py` — 有 shebang 却没有执行位，加上。
- **已在别处解决：** 场景表里 `005-o-` 的失效引用、以及「`tools/*.md` 里的 `byissue/` 路径无人校验」——`check_byissue_references` 已经覆盖（见 `byissue/issues/008-o-closing-renames-break-full-name-references.md`）。
- **未采纳：** `byissue/issues/007-x-description-and-posture-table-are-two-trigger-sets.md` 正文里「该断言现在加会直接红」是写作当时的事实，属于已关闭事项的历史记录，不回改。review 自己也主动跳过了 `len(postures) < 5`，因为 `byissue/issues/006-x-ff-checker-self-review-fixes.md` 判过一次保留——**它记得上一轮的结论，没重开已决问题**。
- **验证：** `python3 tools/check-skill-repository.py` 通过；锚点链接负向测试如期变红后恢复。
- **byissue：** 已同步 `byissue/spec/index.md` 的发布链路（原表述已失效）。
