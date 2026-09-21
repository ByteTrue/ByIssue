# Project Spec

> **读者：** 要改 ByIssue 这个技能本身的人——「这些词指什么、改它要守什么、哪些方案已经排除过」。  
> 准入判据：**只写代码和目录里重建不出来的东西**。所以这里没有「各文件都做什么」——`ls` 加读文件头就有。目标世界在仓库根 `WHY BYISSUE.md`。

## 这个项目是什么

一个**单技能仓库**，分发一个叫 `bi` 的 Agent Skill。产品形态是**散文**：判断规则、原则和模板，不是可执行代码。

这带来一个反直觉的性质，也是本项目最重要的一条约定：**散文就是逻辑**。改一句 reference 等于改一次代码路径，而不是改文档。所有工程直觉（回归测试、单一归属、发布校验）都按这个前提套用。

## 统一语言

- **姿态（posture）**：用户此刻在做的那类事（讨论 / 快改 / 受管理实现 / 修 bug / 收尾…）。`bi` 先判断姿态，再只加载那个姿态需要的规则。姿态是**动作级**的：一次被授权的落盘动作不改变当前姿态。
- **姿态文件 / 原则文件**：`references/` 下的 18 篇分成两类——姿态文件回答「这个姿态怎么行动」，原则文件是被多个姿态按需加载的尺子。**这个分类在文件系统里看不出来**，18 个 `.md` 平铺在一个目录里。
- **源头与部署副本**：`skills/bi/` 是源头，`~/.agents/skills/bi/` 是 rsync 出去的副本。改副本无效。
- **描述句 / 祈使句**：写规则的两种语气。描述句规范产物归属（「坑点 → notes」），祈使句指挥会话中的动作（「必须在收尾汇报中列出并询问」）。**只有祈使句会被执行**，这是本项目反复踩到的坑。

## 改这个仓库要守什么

- **一条规则只能有一个归属。** 新增规则先定归属，其他文件只能链接。重述过的契约一定漂移——`done/` 在 1.1.0 删除后仍在三处存活、`onboard.md` 手抄的目录清单漏掉 `decisions/`，都是这条被违反的代价。
- **不设行数上限。** 按渐进式披露拆，不按行数砍；核心叙事不许为了短而打散。
- **只分发 `skills/bi/`。** 仓库根的 README、WHY、asset 不进技能包；技能包里也不放没人引用的文件。
- **技能必须自足。** 不引用只存在于本仓库的文件——用户装到自己项目里时那些路径不存在。
- **零依赖、中文为主。** 纯 stdlib Python + Markdown；README 有英文版，技能本体目前只有中文，这是当前选择不是永久约束。

## 发布链路

```text
改 skills/bi/ → python3 tools/check-skill-repository.py
              → 动过姿态表则 python3 tools/check-posture-routing.py
              → rsync 同步 ~/.agents/skills/bi/
              → 更新 VERSION + CHANGELOG.md 同名小节 → 单个 commit → npx skills 分发
```

rsync 那一步没有任何代码强制，忘了就等于没改。checker 的取舍见 `byissue/decisions/001-checker-verifies-links-not-contract-wording.md`；它带来一条硬约束：**新增 reference 或 template 必须在某处用完整路径被引用**，否则报 `packaged but nothing references it`。

## 当前没有的东西

- 行为回归测试（`byissue/issues/004-o-posture-routing-regression-tests.md`）。checker 只挡路径漂移，挡不住语义漂移。
- 使用信号采集。真实分布靠人工统计外部仓库，见 `byissue/notes/001-real-world-usage-stats.md`。
- 除 Codex 外的第二宿主适配。

## 想深入时

- 为什么要有这个项目 → 仓库根 `WHY BYISSUE.md`
- 某个取舍当时为什么那样拍 → `byissue/decisions/`
- 真实项目怎么用它 → `byissue/notes/001-real-world-usage-stats.md`
- 各文件做什么 → 直接读 `skills/bi/SKILL.md`，它是唯一入口和权威契约
