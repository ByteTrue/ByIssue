---
kind: decision
title: "bi 不为自己的可触发性去写 AGENTS.md"
created: 2026-09-21
superseded-by: ""
---

# bi 不为自己的可触发性去写 AGENTS.md

不在项目的 `AGENTS.md` / `CLAUDE.md` 里写「本项目使用 ByIssue，动手前先读 SKILL.md」这类启动规则，onboard 也不会建议用户这么做。现有契约（`references/onboard.md`：Onboard 不创建或修改 `AGENTS.md` / `CLAUDE.md`）保持不变。

**明确接受的代价：** 不含任何流程词汇的说法——典型如「加个字段就行，很简单」——技能不会被打开，用户得自己说一声 `bi`。这是**接受的边界，不是待修的 bug**，不要再为它开事项。

拒绝的理由是这条路通向的地方：技能要靠往用户项目里注入一行来保证自己被看见，就等于把可触发性从技能自身外包给了宿主文件。那一行谁维护、版本变了谁更新、多个技能都这么干怎么办，全没有答案。而它换来的只是一小类说法的可达性。

**范围限定：** 这条只管「bi 为了自己被触发而写 AGENTS.md」。用户主动要求记一条启动短规则时，`references/note.md` 的路由照旧有效——那是用户的知识，不是技能的自我注入。

## 背景

来自第二轮路由评测：description 补齐后仍有一类说法进不来（见 `byissue/notes/003-skill-description-matching-is-text-only.md`）。当时把 `AGENTS.md` 列为唯一出路并停注待议，用户直接拍板不做。
