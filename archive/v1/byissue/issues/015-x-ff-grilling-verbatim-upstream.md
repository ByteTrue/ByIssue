---
kind: issue
title: "Grilling 正文完全照抄上游英文原文"
type: ff
status: closed
created: 2026-10-11
---

# Grilling 正文完全照抄上游英文原文

> **读者：** 以后搜到这条时——「为什么 grilling.md 是全英文、且和 mattpocock/skills 逐字节一致」。用户实测（加载了契约但没执行动词、问题难用）后拍板：不再自行翻译和扩展 grilling，直接照抄上游；翻译过程失真，LLM 英文亲和。

- 改动：`skills/bi/references/grilling.md` + `~/.pi/agent/skills/bi/references/grilling.md`（装机副本）——整体替换为上游 `mattpocock/skills` 的 `skills/productivity/grilling/SKILL.md` 当前正文（含 2026-10-07 合入的「Word each question so "yes" accepts your recommended answer」）；废除 1.7.0 的中文翻译+扩展版。仅保留仓库惯例的英文标题 `# Grilling`；上游 frontmatter 不复制（reference 非独立技能）。
- 验证：`curl` 上游 raw 与本地正文 diff，唯一差异为上游 frontmatter 四行（刻意不抄）；两副本互 diff 一致；`python3 tools/check-skill-repository.py` 绿。
- byissue：无 spec 漂移——`spec/index.md` 的 Grilling 词条（多轮访谈 primitive、前沿为空+用户确认、对应上游 grilling+grill-with-docs 拆分）对纯上游版仍然成立。已知取舍：中文版超出上游的内容随替换移除（domain-modeling 四反射、假信号表、谈不出来去原型、一次只问一个逃生口、46 问/4 轮校准）；它们在上游的归属是 domain-modeling 与 grill-me 文档，不在 grilling 本体。VERSION/CHANGELOG/README 按用户限定未动，本 ff 即变更记录。

顺手发现：装机副本整体落后仓库一版——`~/.pi/agent/skills/bi/` 的 SKILL.md 缺「直接要求提交/推送」行、do.md 缺收尾扩句（1.8.0 内容），仅 grilling 本次被带到最新。不在本次范围。
