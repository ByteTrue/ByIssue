---
kind: issue
title: "吸收上游 grill 家族余下文档：domain-modeling 入库 + 接线"
type: ff
status: closed
created: 2026-10-11
---

# 吸收上游 grill 家族余下文档：domain-modeling 入库 + 接线

> **读者：** 以后搜到这条时——「为什么有个英文 domain-modeling.md、grilling 为什么接了它」。用户澄清：当时要拿的本就是 grill-with-docs / grill-me 整套；docs 因格式不同不完全吸收。

- 做了什么：`skills/bi/references/domain-modeling.md` 新建为英文 reference——读侧（顶撞词汇 / 磨模糊词 / 编场景 / 拿代码对照）逐句照抄上游 `skills/engineering/domain-modeling`；写侧按 ByIssue 映射：术语 → `byissue/spec/` 统一语言、过三条件门的决策 → `byissue/decisions/`、其余留对话（Talk 收束进 `byissue/talks/`），**不在 ByIssue 项目创建上游的 GLOSSARY.md / docs/adr/**；grill-me / grill-with-docs 两份 docs 页的承重行为并入（谈不出来去原型、It's working if 判据）。docs 页的路由表与用户侧辅导未吸收（姿态系统与用户手册不在技能职责内）；上游 GLOSSARY-FORMAT / ADR-FORMAT 子文档因写侧映射不再需要。
- 接线：`SKILL.md` 四处——讨论 / 愿景必读表、设计按需读表、提问段指路 + 「一次只问一个」逃生口永久化；`byissue/spec/index.md` 计数 19→20、Grilling 词条加逐字节镜像注记（勿手改）、新增 Domain modeling 词条；`tools/posture-scenarios.md` 场景 1 / 2 / 16 / 25 应读取列补齐（评测与姿态表不矛盾）。
- 验证：`python3 tools/check-skill-repository.py` 绿；`rsync` 后 `diff -rq` 仓库与 `~/.agents/skills/bi/` 全包一致——顺带补上 ff 015 遗留：装机副本此前整体落后 1.8.0 一版，本次整包带到最新。
- byissue：已同步 `byissue/spec/index.md`（见上）。发版三件套（VERSION / CHANGELOG / README）按用户限定未动，ff 015 + 本条即变更记录。
- 修正（2026-10-11，用户指出粉色大象）：初版在 `domain-modeling.md` 写了「Never create GLOSSARY.md / docs/adr/」、在 spec 词条尾句重述了一遍——违反 spec 既有规则「否定式表述要挣得它的注意力成本」（禁令是全文件唯一引入这两个文件名的地方，纯请进注意力），也违反单一归属。改为纯正向映射（三个产出 → 三个 `byissue/` 去向，无缺口可堵），spec 尾句同步删。

