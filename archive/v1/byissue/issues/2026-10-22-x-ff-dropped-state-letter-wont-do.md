---
kind: issue
title: "放弃态字母改 w，避开 d 被读成 draft"
type: ff
created: 2026-10-22
---

# 放弃态字母改 w，避开 d 被读成 draft

> **读者：** 以后搜到这条时——「改了啥、怎么信、动没动制度记忆」。

真实误读触发：一个只有 `d` 的 Epic 目录被读成「draft，还没定」，进而判成未完成。`d` 在状态字母位同时被 draft / date / default 占着先验，紧贴日期又没有消歧信息，而它在 22 个样本里出现 0 次——没人有机会靠使用经验校准。改成 `w`（`wontfix` 的缩写，该状态在 issue 追踪器里的既有术语）。

- 改动：`skills/bi/SKILL.md`、`references/{close,complain,do,explore,fast}.md`、`templates/entities/issue.md`、两份 README — `-d-` / `o|x|d` / 裸字母 `d` 全部改为 `w`，共 39 处；路径表 `w=won't do 放弃关闭` 给出字母锚。
- 验证：`tools/check-skill-repository.py` 通过；`grep -rn -- '-d-' skills/ README*.md tools/` 无命中；python 全文扫「独立字母 d」只剩 `check_open_issues.py` 的 `\d` 正则误报；路径表各行列数与表头一致（`\|` 转义补齐）。仓库内不存在 `-w-`/`-d-` 存量路径，无迁移。
- 行为评测：`tools/fixtures/state-letter-probe.sh` 五臂全过（`w-clean` / `w-settled` / `w-violation` / `o-control` / `x-control`），无一处把 `w` 读成 `wip`、进行中或 draft；`w-violation` 臂同时验到「读对字母」与「指出子 issue 违反关闭前置条件」。评测设计见 `tools/posture-scenarios.md`「状态字母读法探针」。
- 评测过程修掉一处夹具错误：初版 `w-child` 臂用「Epic `-w-` + 子 issue `-o-`」去测「子 issue 不覆盖 Epic 状态」，而 `close.md` 要求关闭 Epic 时内部事项已关或明确废弃/移出——那是契约不允许的状态，子 agent 正确地把它报成矛盾。改为 `w-settled`（子 issue `-x-`，合法）+ `w-violation`（`-o-`，反向断言必须指出违反）。
- byissue：新增 `decisions/2026-10-22-wont-do-letter-replaces-draft-ambiguous-d.md`（含两个否决方案：并入 `-x-` 与直接删除放弃项）；`byissue/` 内历史 issue/talk 与旧 CHANGELOG 条目的 `d` 保留为档案。

顺手发现：`close.md` 的「dropped issue」小标题与 `SKILL.md` 的「won't do」是同一状态的两种英文写法，已统一为 won't-do。
