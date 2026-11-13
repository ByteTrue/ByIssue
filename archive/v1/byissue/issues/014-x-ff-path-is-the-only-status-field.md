---
kind: issue
title: "路径是唯一的状态字段"
type: ff
created: 2026-10-10
---

# 路径是唯一的状态字段

下游仓库 byspace 的两个真实会话事故同根：issue 的状态被文件名和 frontmatter `status` 字段双重表达，两处写入必有中间态和先后顺序，两边不一致就没有任何机制能发现。ff 072 会话里 agent 创建 `-x-` 文件名却照模板默认抄 `status: open`，合并后才想起补正，又违规直推 main 多出一笔提交；issue 073 会话里 agent 从未读到 `o|x|d` 的语义（见下）而照抄目录主流给新 issue 命名 `073-x-`。修复：删掉 status 字段，路径成为状态唯一出处，同时在创建动作现场补上状态字母公式。

- 改动：`skills/bi/` 八处——`SKILL.md` 关闭契约改为「状态由路径唯一表达，不设 frontmatter 状态字段」；`references/close.md`、`references/fast.md` 删「把 status 改为 closed」表述；四个模板（issue / ff-issue / explore-index / epic-spec）删 frontmatter `status` 行；`references/do.md` 补「新开一律 `-o-`，关闭时才改 `-x-`/`-d-`」。`epic-spec.md` 的 `status: draft` 一并删（全套文档无一处定义其流转，属死字段）。
- 采样修复（第二段因果，073 会话取证）：`SKILL.md`「节省上下文」节补「姿态必读必须完整读入；批量并行读取时业务文件可以采样，规则文件采样即静默丢失」；`do.md` 状态公式即其对照修复——`fast.md` 历来带全公式，ff 从未出过状态字母错误，缺公式处才出错。已确认非 codemode 工具层问题（codemode 溢出全量落盘可恢复，截断是 agent 显式 `slice(0, 6000)` 采样规则文件所致）。
- 验证：`grep -rn status` 全技能目录零残留（`git status` 除外）；`python3 tools/check-skill-repository.py` 通过；`rsync -a --dry-run --itemize-changes` 校验 `~/.agents/skills/bi/` 与源仓库一致。
- byissue：无 spec 漂移。`spec/index.md` 未定义 status 契约（路径即状态的规则本体在 `SKILL.md`，该文件即权威出处，无需同步）。归档的旧 ff（001–012）保留旧 frontmatter，以路径为准，不做任何迁移。

顺手发现：模板默认值是个系统性陷阱——模板默认 `status: open` 与「按交付判定写 `-x-`」组合起来必产生矛盾，本次模板已根治；历史归档不受影响。
