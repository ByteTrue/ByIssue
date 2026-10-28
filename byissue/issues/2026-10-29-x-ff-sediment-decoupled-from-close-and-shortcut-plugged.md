---
kind: issue
title: "封堵改名捷径并将沉淀收割解耦至每次阶段性收工与提交"
type: ff
created: 2026-10-29
---

# 封堵改名捷径并将沉淀收割解耦至每次阶段性收工与提交

> **读者：** 以后搜到这条时——「改了啥、怎么信、动没动制度记忆」。  
> **自检（四答即可，可合成短段，勿空标题凑节）：** 做了什么 · 改了哪些文件 · 怎么验证 · 对 `byissue/` 有无影响。

---

复盘真实长会话（6895 行 JSONL）中「规则写明沉淀收割，模型却连续 5 次改名关 issue 不读 `close.md`、且在事项因配额阻塞保持 `-o-` 先行提交时漏掉外部事实沉淀」的根因，从入口阅读完整性、改名捷径门禁、跨姿态常驻自检与 `-o-` 阶段性提交四个切面收紧契约。

- 改动：
  - `skills/bi/SKILL.md`：「节省上下文」首句明确 `SKILL.md` 全文与所选姿态必读首次加载必须完整读入，仅在已完整读过且需核对局部细节时补读；「路径与命名」写明 `-o-` → `-x-`/`-w-` 是 `close.md` 的最后一步，动手改名前必须先读并执行 `close.md`；「经验沉淀以落入 `byissue/` 为准」收归全过程盘点、外部事实自检问题与 `notes/`、`spec/` 查重动作，并绑定每次完成汇报、阶段性收工与提交（含事项暂留 `-o-`）；「什么内容可以写到哪一层」补入 `Note` 行并扩写 `Project Spec` 时机；「完成、关闭与 Git」表合并受管理实现、修 bug（受管理）与“做完/修好”，同步 `-o-` 阶段性收工的沉淀裁决与单次 commit 规则。
  - `skills/bi/templates/entities/issue.md`：删去顶部注释里孤立的「关闭时：路径 `-o-` 改为 `-x-` 或 `-w-`」，消除创建模板提前剧透改名公式与单一归属重复。
  - `skills/bi/references/close.md`：「先确认可以关闭」明确暂不满足关闭条件时保持 `-o-` 不改名但照常执行沉淀收割；行动指南按「读取关闭上下文 → 核对关闭条件 → 沉淀收割与毕业回写（提交前必做，区分无论是否关闭均沉淀的经验与仅 `-x-` 交付关闭的事项毕业回写） → 修引用并改名关闭 issue」正序重排。
  - `skills/bi/references/complain.md`：清理与回写、产物契约、收尾汇报补齐读取 `fast.md` / `close.md` 的显式祈使句，并引用 `SKILL.md` 在汇报中列出沉淀候选与关闭建议。
  - `skills/bi/references/do.md`、`skills/bi/references/fast.md`、`skills/bi/scripts/check_open_issues.py`：产物契约「关闭候选」改为「沉淀与毕业候选」，收尾与提交涵盖因外部阻塞暂留 `-o-` 的阶段性收工提交，统一引用 `SKILL.md` 沉淀与提交契约并保留 `check_open_issues.py` 门禁。
- 验证：
  - `python3 tools/check-skill-repository.py` 通过。
  - 两轮 `reviewer` 子代理按 `tools/prompt-review.md` 七类必查对抗性审查：第一轮检出 3 项 P1（`close.md` 条件核对与两类回写分层、未加载 `close.md` 时的沉淀自检可达性、提交契约跨文件重述），当轮修复后第二轮复审 0 发现（Merge verdict: OK）。
  - 独立子代理冷读行为探针（模拟因免费配额耗尽暂留 `-o-` 的 bug 事项要求阶段性收尾提交）：自动运行 `scripts/check_open_issues.py`，给出保持 `-o-` 不改名建议，查重 `byissue/notes/` 与 `spec/` 后完整列出外部平台事实与长期约束沉淀候选，并在单次 commit 前请求裁决。
- byissue：已同步 `byissue/spec/index.md`「描述句 / 祈使句」条目（补充第四种变体：入口剧透机械末步截断加载 + 动作绑死终态关闭）。
