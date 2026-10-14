

更新 `bi` 的核心结构或行动模式时，同步检查相关 references、templates、scripts 和 README，避免同一契约出现两套表述。


单个 skill 或 `byissue/` 工作文档应当适当精简，但不设统一行数上限。优先完整说明会影响理解和判断的背景、结构、原则与契约；当细节只在特定场景需要、偏离主线或已经妨碍阅读时，再按渐进式披露抽到同 skill 或同实体目录下的 references/templates/scripts/相邻子文档，并在入口文件里清楚指过去。不要为了缩短文件硬压缩或拆散核心叙事。

工作流文档只写给现在用它的人（`skills/bi/` 与 `byissue/`）：规则只陈述当前成立的契约，不解释它取代了什么、哪次改的、为什么改。演变原因、证据与取舍留在 `byissue/decisions/`。

- 否定式表述要挣得它的注意力成本：一条「不要 X」只在 X 是模型的强默认行为时才写。给已不在上下文里的旧版本清痕迹（「不再」「以前是」「已经删掉」）也是同一回事——那是把旧东西重新送进注意力。判据见 `byissue/spec/index.md`，清理记录见 `byissue/decisions/010-negative-statements-must-earn-their-attention-cost.md`。


