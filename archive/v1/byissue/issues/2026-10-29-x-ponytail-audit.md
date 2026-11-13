---
kind: issue
title: "全仓 Ponytail Audit（1.10.1 基线）"
type: chore
created: 2026-10-29
---

# 全仓 Ponytail Audit（1.10.1 基线）

## 目标与范围

对 `ByIssue` 仓库（`1.10.1` 基线）执行一轮完整 `ponytail-audit`。由于本项目「散文就是逻辑」（`byissue/spec/index.md`），审计范围同时覆盖：
- 包含：分发技能包 `skills/bi/`（`SKILL.md`、20 篇 `references/*.md`、12 份 `templates/entities/*.md`、`agents/openai.yaml`、2 个 Python 脚本）、仓库校验与评测工具 `tools/`、制度记忆 `byissue/`、根目录入口文档（`AGENTS.md`、`CLAUDE.md`、`README.md`、`README.en.md`、`WHY BYISSUE.md`）。
- 不包含：新增姿态或改变现有四层世界模型。

假设负载：单开发者或多并行 git worktree / 多子代理会话同时在目标项目与本仓库中调用 `bi` 技能及配套脚本。

## 审计发现（按严重度排序，编号 1–9）

### Must fix（契约冲突 Bug / 校验失明）

1. **根目录 `CLAUDE.md` 仍指示模型直接改写 `AGENTS.md` / `CLAUDE.md`**（`CLAUDE.md:L1-16`）
   - **这是什么：** 仓库根目录供 Claude Code 启动时自动注入的指令文件。
   - **问题：** 第 2 行仍写「几乎每次启动都必须知道的短规则直接写入项目已有 `AGENTS.md` 或 `CLAUDE.md`」，与 `byissue/decisions/008-bi-never-writes-agents-md.md` 及 `skills/bi/SKILL.md:L194`（「bi 只写 `byissue/` 之内，不碰 `AGENTS.md` / `CLAUDE.md`」）正面冲突，且漏掉 `AGENTS.md` 后补的三条核心维护规则。
   - **修法：** 删除 `CLAUDE.md`（或改为单行 `@AGENTS.md`；净减 15–16 行）。
   - **不修的后果：** 在 Claude Code 下跑本仓库时，注入的系统指令会直接命令模型去改写 `AGENTS.md` / `CLAUDE.md`，并缺失渐进式披露、禁写演变史与粉色大象判据。

2. **`maketools.md` 与 `note.md` 残留写「Agent 指令」的旧分支**（`skills/bi/references/maketools.md:L21,37`、`skills/bi/references/note.md:L15,17`）
   - **这是什么：** 「学流程」与「记知识」两个姿态的行动指南、原则与收尾汇报。
   - **问题：** `decisions/008` 规定删除指向 Agent 指令文件的写入分支，但 `maketools.md:L21` 仍写「准备写 Agent 指令、notes 或 tools 前必须确认目标文件的当前版本」，第 37 行仍要求汇报「是否增加了 Agent 指令引用」；`note.md:L15,17` 仍保留「Agent 指令不是知识库：只放短规则……拿不准时默认写 notes，不要污染 Agent 指令」（暗示拿得准时写短规则进 Agent 指令）。
   - **修法：** `maketools.md:L21` 删去「Agent 指令、」，第 37 行改为「是否建议用户自行添加启动规则索引」；`note.md:L15-17` 删去关于「Agent 指令只放短规则」的两句话（净减 4 行）。
   - **不修的后果：** 进入「学流程」或「记知识」姿态时，模型仍可能按字面指示修改用户仓库的 `AGENTS.md` / `CLAUDE.md`。

3. **`SKILL.md` 毕业方向残留与 `close.md` 相反的旧规则「将稳定结论的具体内容合并进 Project Spec」**（`skills/bi/SKILL.md:L229-237`）
   - **这是什么：** `SKILL.md`「完成、关闭与 Git」下方的「毕业方向」列表，常驻在所有会话上下文中。
   - **问题：** `SKILL.md:L233` 仍写 `Epic 关闭 → 将稳定结论的**具体内容**合并进 Project Spec`，而 `byissue/decisions/004-project-spec-drops-implementation-description.md` 与 `skills/bi/references/close.md:L23,88` 早已规定「毕业是筛选，不是搬运……能从代码重建的不写」（`002` 当年只改了 `close.md`，漏改 `SKILL.md` 副本）。该列表还与上方仅隔 15 行的 `### 什么内容可以写到哪一层`（`SKILL.md:L198-209`）重复。
   - **修法：** 删除 `SKILL.md:L229-237` 的「毕业方向」重复列表，在 `### 什么内容可以写到哪一层` 的 `Project Spec` 行补半句准入提示并指向 `close.md` / `spec.md`（净减 8 行）。
   - **不修的后果：** 关闭 Epic 时，常驻上下文中的 `SKILL.md:L233` 会诱导模型把整段能力与实现描述搬进 `Project Spec`，导致规格腐化。

4. **`tools/check-skill-repository.py` 的 `check_byissue_references` 完全漏检日期前缀事项（`YYYY-MM-DD-`）与放弃态（`-w-`）**（`tools/check-skill-repository.py:L14,157-181`）
   - **这是什么：** 校验本仓库 `byissue/` 内部事项引用是否因关闭改名而悬挂的守门函数。
   - **问题：** `ITEM_REF_RE` 仍硬编码为 `\b(\d{3}-[oxd]-[A-Za-z0-9_-]+(?:\.md)?)\b`，且只按 3 位数字前缀过滤。自 `1.9.0`（日期前缀 `YYYY-MM-DD-`）和 `1.10.0`（放弃字母 `-w-`）以来，所有新事项的引用一旦在关闭改名后悬挂，脚本都会静默放行并报通过。
   - **修法：** 将正则扩为匹配 `(?:\d{4}-\d{2}-\d{2}|\d{3})-[oxdw]-[A-Za-z0-9_-]+(?:\.md)?`，并用去掉状态字母后的 `(prefix, slug)` 键识别本仓事项（既能抓出本仓日期事项的 `-o-`/`-x-`/`-w-` 引用未更新，又不误报文中虚构示例）。
   - **不修的后果：** 本仓库关闭任何日期前缀的 issue / epic 时若漏改引用，校验脚本永远报绿。

### Should fix（缺自动化校验 / 环境兼容 / 常驻上下文瘦身）

5. **两项纯确定性的发布审查规则未写进 `tools/check-skill-repository.py`**（`tools/check-skill-repository.py:L42-133`、`tools/prompt-review.md:L55,62`）
   - **这是什么：** `prompt-review.md` 第 5 类（技能自足性：禁引仓库专属文件、模板禁带技能内部路径）与第 7 类（frontmatter `description` 触发词反向认领）。
   - **问题：** 这两项均是 100% 确定性的集合差检查，目前却只写在 `prompt-review.md` 里靠每次发版起 LLM 子代理手写临时 bash 脚本检查。
   - **修法：** 在 `tools/check-skill-repository.py` 增加约 18 行断言覆盖这两项，并精简 `tools/prompt-review.md` 第 7 类说明。
   - **不修的后果：** 单独跑 `check-skill-repository.py` 抓不到模板泄漏技能内部路径或 `description` 孤儿触发词，每次发版还要多烧子代理轮次。

6. **`onboard.md` 使用 `python` 而非 `python3`，且 `check_open_issues.py` 调用处未写明从技能目录解析**（`skills/bi/references/onboard.md:L20`、`skills/bi/SKILL.md:L225`）
   - **这是什么：** 供模型执行的初始化脚本与提交前检查脚本命令。
   - **问题：** `onboard.md:L20` 写 `python <bi-skill>/scripts/init_byissue.py --project .`，在无 `python` 别名（仅有 `python3`）的 macOS / Linux 环境会报 `command not found`；`SKILL.md:L225` 写 `先跑 scripts/check_open_issues.py` 时未像 `onboard.md` 那样提醒从 `bi` 技能目录解析路径，模型在有同名 `scripts/` 目录的用户仓库里易找错位置。
   - **修法：** `onboard.md:L20` 改为 `python3`；`SKILL.md:L225` 注明技能目录下的 `scripts/check_open_issues.py`。
   - **不修的后果：** 在标准 macOS 环境首次执行 onboard 命令会失败；在用户仓库执行提交前门禁时可能报找不到 `scripts/check_open_issues.py`。

7. **`SKILL.md` 尾部「4. 授权边界」与「5. 按需读取的原则文件」同前文姿态表、提交表重复，且含一处错误诱因**（`skills/bi/SKILL.md:L261-286`）
   - **这是什么：** `SKILL.md` 末尾的两节汇总（26 行）。
   - **问题：** 「4. 授权边界」5 条中有 4 条重复了前文姿态表与提交表（「完成不等于关闭；关闭后文件留在原树原位」在单文件内出现 4 次）；「5. 按需读取的原则文件」完整重复了姿态表「按需读」列的 6 个链接，且第 280 行写「关闭时发现可以进行有界简化」与 `close.md:L33`（关闭只核对既有有界简化是否仍成立，不在关闭时临时降级）矛盾。
   - **修法：** 将「4. 授权边界」唯一增量的第 1 条（执行类姿态持续推进、讨论不适用）并入第 1 节判断列表，删去其余重复项与第 5 节重複表，保留末段模板与脚本入口说明（净减约 22 行）。
   - **不修的后果：** 每次会话常驻上下文多载入 20 余行重复文本，且第 280 行会诱导模型在关闭阶段把未完成需求包装成有界简化。

### Nice to have（历史档案一致性）

8. **`byissue/decisions/007` 的 `superseded-by` 填了裸编号 `"008"` 而非文件名**（`byissue/decisions/007-bi-does-not-write-itself-into-agents-md.md:L5`）
   - **这是什么：** 决策记录 `007` 的 frontmatter。
   - **问题：** `templates/entities/decision.md:L11` 要求 `superseded-by` 填新决策的文件名，而 `007` 只填了 `"008"`。
   - **修法：** 改为 `superseded-by: "008-bi-never-writes-agents-md"`。
   - **不修的后果：** 与决策模板契约不一致。

9. **早期 `byissue/` 文档有 7 处路径引用写成了不含 slug 的截断前缀**（`byissue/issues/001,002,003,004,011`、`byissue/notes/002`、`byissue/talks/001`）
   - **这是什么：** 早期事项/笔记中形如 `byissue/decisions/004`、`byissue/talks/001`、`byissue/issues/007` 的路径写法。
   - **问题：** 这些路径缺了文件名后半段 slug，直接传给 `read` 工具会报文件不存在。
   - **修法：** 补全这 7 处路径为真实完整文件名。
   - **不修的后果：** Agent 顺着历史文档路径直读时会触发一次 `ENOENT` 再退回 `ls`。

## 执行记录与验证

按审计报告将 1–9 项全部落地：

1. **删除根目录 `CLAUDE.md`**：`git rm CLAUDE.md`，消除与 `AGENTS.md` 及 `decisions/008` 冲突的双份指令文件（-16 行）。
2. **清理 `maketools.md` 与 `note.md` 残留的 `Agent 指令` 分支**：`skills/bi/references/maketools.md` 删去「准备写 Agent 指令」并将汇报改为「是否建议用户自行添加启动规则索引」；`skills/bi/references/note.md` 删去关于「Agent 指令只放短规则」的两段重复/冲突叙述（-4 行）。
3. **删除 `SKILL.md` 漂移的「毕业方向」重复列表**：删去含旧措辞「将稳定结论的具体内容合并进 Project Spec」的重复列表，在 `### 什么内容可以写到哪一层` 的 `Project Spec` 行补入筛选判据提示并链接 `close.md` 与 `spec.md`（-8 行）。
4. **修复 `tools/check-skill-repository.py` 的 `check_byissue_references`**：支持 `YYYY-MM-DD-` 日期前缀与 `-w-` 放弃字母，通过本仓 `(prefix, slug)` 集合检测事项状态字母漂移而不误报虚构示例。
5. **将自足性与反向触发词检查收归 `tools/check-skill-repository.py`**：机械断言 `skills/bi/` 不引用本仓库专属文件、`templates/` 不含技能包内部路径、frontmatter `description` 触发词均被姿态表认领，并同步精简 `tools/prompt-review.md` 第 7 类说明。
6. **修正脚本调用说明**：`skills/bi/references/onboard.md` 的 `python` 改为 `python3`；`SKILL.md`、`do.md`、`fast.md` 注明 `scripts/check_open_issues.py` 从 `bi` 技能目录解析。
7. **精简 `SKILL.md` 尾部重复章节**：将「4. 授权边界」中唯一不重复的执行类姿态持续推进规则并入「1. 先选姿态」第 10 条，删除其余 4 条重复边界与「5. 按需读取的原则文件」重复表（含与 `close.md` 冲突的「关闭时发现可以进行有界简化」）（-28 行）。
8. **补全 `decisions/007` 的 `superseded-by` 文件名**：改为 `"008-bi-never-writes-agents-md"`。
9. **补全 7 处历史截断路径引用**：将 `byissue/issues/{001,002,004,011}`、`byissue/notes/002`、`byissue/talks/001` 中的半截路径补全为真实完整文件名。

### 验证与沉淀结论

- `python3 tools/check-skill-repository.py`：通过，且注入 `2026-10-29-x-ponytail-audit` 悬挂引用自测确认可精准拦截日期前缀事项的状态漂移。
- `tools/prompt-review.md` 对抗性审查：子代理（`sub_52e7065f7e09`）七类必查全部 `0` 发现（`Merge verdict: OK / 可以分发`）。
- 沉淀收割：已查重 `byissue/notes/` 与 `byissue/spec/index.md`；本次发现的重复漂移已由 `byissue/spec/index.md` 既有「重述过的契约一定漂移」覆盖，无新增独立 note 或 spec 条目。
