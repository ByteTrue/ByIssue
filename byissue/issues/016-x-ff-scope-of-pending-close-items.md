---
kind: issue
title: "待关闭事项的范围定义"
type: ff
created: 2026-10-11
---

# 待关闭事项的范围定义

下游仓库的盘点 agent 给 talk 标「（状态 open）」并建议收成 closed：`SKILL.md` 里「待关闭事项」一词只出现一次、无范围定义，agent 把 talks/ 扫进清单，又在无状态概念可依据处借用 issue 的 open/closed 即兴发明——与 1.8.0 同类失效（契约沉默处，模型借用相邻概念）。机械层本来就对（`check_open_issues.py` 只扫 issues 树），这次补的是散文层。

- 改动：`skills/bi/SKILL.md` — 「提问必须带建议」段尾补一句：待关闭事项只来自路径带 `-o-` 的 issue、epic、ff 与 Explore；talk、note、decision 无状态，不进待关闭清单。初稿曾带「talk 是否完结看其出口节」尾巴，落盘前删去——出口节契约本体在 talk.md 与模板，排除规则本身已断事故链，且 note/decision 无「完结」维度，只给 talk 配判据不对称。VERSION → 1.8.1，CHANGELOG 同步。
- 验证：`python3 tools/check-skill-repository.py` 通过；rsync 校验部署副本与源一致。
- byissue：无影响（规则本体在 `SKILL.md`，`spec/index.md` 不设 status 契约，与 014 先例一致）。

顺手发现：无。
