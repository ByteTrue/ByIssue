# 项目约束与发布依据

适用范围：维护 ByIssue 技能仓库。工作流契约以 `skills/bi/SKILL.md` 及其 reference 为准。

## 这个项目是什么

ByIssue 是一个单技能仓库，分发 `skills/bi/` 下名为 `bi` 的 Agent Skill。产品形态是散文、模板和一个初始化脚本。散文就是逻辑，改一条规则等于改变一条行动路径。

技能包内的每个文件都必须从入口、模板或另一个已达文件被引用。

代码、测试、配置、git 和真实运行结果是实现事实。项目文档保存不能由这些事实直接重建的目标、长期决定、外部观察和可重跑证明。

## 改这个仓库要守什么

- 一条规则只有一个权威归属。其他文件只通过链接或短指针进入它。
- 核心入口先判断行动，再读取该行动的最小必读规则。
- 当前工作从检查点继续，摘要、文件存在、commit 存在和局部测试通过都要回到真实代码和证据核对。
- 行为证明必须走到本次变化真正生效的入口。没有走到真实路径的检查标记为 `无法判定`。
- 范围覆盖由事实源机械生成，不能用一张全量清单替代真实行为证明。
- 技能包只分发 `skills/bi/`，技能内部路径必须自足。
- `skills/bi/NOTICE.md` 随包携带根 `LICENSE` 和上游归属。`references/grilling.md` 使用上游材料，`domain-modeling.md` 保留其阅读侧材料。
- 仓库使用标准库 Python、Markdown 和 shell。技能本体以中文为主。
- 工作流文档只陈述当前成立的契约。演变原因、证据和取舍放在历史记录中。
- 否定式规则只在它阻止模型的强默认行为时保留；其他情况直接陈述正确动作。
- 当前 `byissue/` 只使用 `work/`、`memory/` 和按需的 `vision/`。`archive/v1/` 仅用于用户明确要求的历史追溯。

## 检查与发布

维护侧检查各自负责一件事：

| 规则 | 检查 |
|---|---|
| 版本号与发布记录一致 | `tools/check-skill-repository.py` |
| 技能包入口、许可证、路径可达且没有本仓专属路径 | `tools/check-skill-repository.py` |
| 当前工作区与归档隔离 | `tools/check-skill-repository.py` |
| work 模板保留唯一检查点字段 | `tools/check-skill-repository.py` |
| checker 的每项检查可以变红 | `tools/check-skill-repository-selftest.py` |
| 初始化脚本在用户项目创建并保留 `work/`、`memory/` | `tools/check-skill-scripts.py` |
| 宿主加载的部署副本与源代码一致 | `tools/release-check.sh` |

发布顺序是：修改 `skills/bi/`，运行 `bash tools/release-check.sh --no-deploy`，更新 `VERSION` 和 `CHANGELOG.md`，同步宿主实际加载的部署副本，再运行 `bash tools/release-check.sh <部署副本目录>`，最后按用户要求提交或分发。

`tools/release-check.sh` 不猜部署目录。没有给出目录或 `BI_DEPLOYED` 时，发布检查会失败；编辑后的本地检查使用 `--no-deploy`。

## 当前边界

ByIssue 保存项目中的当前工作和长期判断，不替宿主记录会话，也不把模型编排、工作树管理或多代理调度加入技能契约。语义是否适合某个具体项目，要通过真实项目中的行动、行为证明和用户反馈校准。

## 依据与重访

- 用户决定：本轮要求 v2 分支安装、旧版产物整体归档，以及 pi 实际任务评测；原要求和证据保存在 `byissue/work/v2-readiness/index.md`。
- 可重跑证明：上表的维护命令验证结构和安装副本，具体行为效果以实际任务记录为准。
- 当分发形态、工作区模型或用户的发布授权改变时，重新核对本记录。
