# Project Spec

> **读者：** 要改 ByIssue 这个技能本身的人——「它现在是什么、改它要守什么、从哪下手、怎么验证、怎么发」。  
> 目标世界不在这里：ByIssue 的愿景写在仓库根的 `WHY BYISSUE.md`，这里只记当前成立的事实。

## 这个项目是什么

一个**单技能仓库**。它分发一个叫 `bi` 的 Agent Skill，产品形态是散文——判断规则、原则和模板，不是可执行代码。用户在自己的项目里调用 `/bi`，技能先判断用户此刻的姿态，再只加载那一个姿态需要的规则，并把跨会话要保留的结论写进该项目的 `byissue/` 工作区。

因此这个仓库有一个反直觉的性质：**散文就是逻辑**。改一句 reference 等于改一次代码路径，而不是改文档。

## 现在有什么

- **`skills/bi/SKILL.md`** —— 唯一入口与权威契约。姿态路由表、世界模型、`byissue/` 工作区地图、路径命名与编号规则、开工协议、授权边界都在这里。其他文件只能链接它，不能重述它。
- **`skills/bi/references/`** —— 18 篇。分两类：**姿态文件**（talk / design / do / fast / complain / close / explore / spec / vision / note / onboard / maketools）回答「这个姿态怎么行动」；**原则文件**（code-design / economy / quality / ui-spec / docs / debug）回答「判断的尺子是什么」，被多个姿态按需加载。
- **`skills/bi/templates/entities/`** —— 13 个。它们是**自检清单**，不是槽位骨架：给读者列出「别漏什么」，不预制空章节。
- **`skills/bi/scripts/init_byissue.py`** —— 在目标项目建 `byissue/` 八个目录，并写入 vision / spec 两个入口骨架。幂等；`--force` 才覆盖那两个入口。
- **`tools/check-skill-repository.py`** —— 发布前校验。见下「发布链路」。
- **`agents/openai.yaml`** —— Codex 宿主的薄适配层，是目前唯一的第二宿主。

## 改这个仓库要守什么

- **源头在 `skills/bi/`，`~/.agents/skills/bi/` 只是部署副本。** 改完必须 rsync 同步，否则当前会话用的还是旧规则。
- **一条规则只能有一个归属。** 新增规则先确定它属于哪个文件，其他文件只能链接过去。重述过的契约一定会漂移——`done/` 在 1.1.0 删除后仍在三处存活，`onboard.md` 手抄的目录清单漏掉了 `decisions/`，都是这条规则被违反的代价。
- **不设行数上限。** 按渐进式披露拆，不按行数砍；核心叙事不许为了短而打散。
- **只分发 `skills/bi/`。** 仓库根的 README、WHY、asset 不进技能包；技能包里也不放没人引用的文件（checker 会报）。
- **零依赖。** 纯 stdlib Python + Markdown。
- **中文为主。** README 有英文版，技能本体目前只有中文——这是当前选择，不是永久约束。

## 发布链路

```text
改 skills/bi/ → python3 tools/check-skill-repository.py → rsync 同步 ~/.agents/skills/bi/
              → 更新 VERSION + CHANGELOG.md 同名小节 → 单个 commit → npx skills 分发
```

checker 校验四件事：VERSION 是合法 semver 且 CHANGELOG 有同名小节；`skills/` 下只有 `bi`；README 两版都写了三条安装命令；以及**链接可达性双向成立**——技能指向的每条路径必须存在，每个打包文件必须被引用到。它刻意**不**检查契约文字：grep 中文短语只能证明字符串还在，还会变成契约的第二份副本，改一次文案就要同步改校验。

副作用：新增 reference 或 template 时，必须在某处用**完整路径**引用它（如 `templates/entities/tool.md`），否则报 `packaged but nothing references it`。入口白名单只有 `SKILL.md`、`agents/openai.yaml`、`scripts/init_byissue.py`。

## 当前没有的东西

- **没有行为回归测试。** 散文是逻辑，但没有任何检查会在姿态路由坏掉时失败。checker 只挡路径漂移，挡不住语义漂移。
- **没有使用信号采集。** 真实分布靠人工统计外部仓库得到，见 `byissue/notes/001-real-world-usage-stats.md`。
- **没有第二个宿主适配**（除 Codex）。

## 想深入时

- 想知道为什么这样设计 → 仓库根 `WHY BYISSUE.md`（动机与立场）、`README.md`（面向用户的解释）
- 想改行动规则 → `skills/bi/SKILL.md` 定位姿态，再改对应 reference
- 想知道某个取舍当时为什么那样拍 → `byissue/decisions/`
- 想知道真实项目怎么用它 → `byissue/notes/001-real-world-usage-stats.md`
