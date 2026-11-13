

更新 `bi` 的核心结构或行动模式时，同步检查相关 references、templates、scripts 和 README，避免同一契约出现两套表述。


单个 skill 或 `byissue/` 工作文档应当适当精简，但不设统一行数上限。优先完整说明会影响理解和判断的背景、结构、原则与契约；当细节只在特定场景需要、偏离主线或已经妨碍阅读时，再按渐进式披露抽到同 skill 或同实体目录下的 references/templates/scripts/相邻子文档，并在入口文件里清楚指过去。不要为了缩短文件硬压缩或拆散核心叙事。

工作流文档只写给现在用它的人（`skills/bi/` 与 `byissue/`）：规则只陈述当前成立的契约。演变原因、证据与取舍留在对应的 work，长期结论写入同主题 Memory。

- 否定式表述要挣得它的注意力成本：一条「不要 X」只在 X 是模型的强默认行为时才写。项目约束见 `byissue/memory/project.md`。

当前工作从 `byissue/work/` 的检查点继续，长期决定按主题检索 `byissue/memory/`。技能契约读取本仓库 `skills/bi/SKILL.md`。

`archive/v1/` 是历史快照，仅在用户要求追溯历史时读取；不要把其中的旧工作流规则用于 v2 任务。

