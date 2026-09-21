# Onboard：接入 ByIssue

## 背景

Onboard 模式负责把 ByIssue 的本地工作区放进项目：创建 `byissue/`、基础实体目录，以及 vision / project spec 的主文档骨架。

它只做初始化和补齐。已有内容默认保留，不迁移旧文档，不替用户整理需求，不创建 issue。

## 原则

onboard 可以观察项目，但不能编项目。能从代码、README、配置、测试和 git 历史推断的，只能作为候选事实或下一步建议；业务目标、路线图、明确不做什么、用户故事和长期取舍，除非已有文档证据或用户确认，否则不要写进 `byissue/`。

默认不覆盖已有文件。只有用户明确要求重置 `byissue/vision/index.md` 与 `byissue/spec/index.md` 时，才使用 `--force`，并在执行前再次确认覆盖这两个入口。

## 行动指南

优先运行技能包内的初始化脚本。脚本路径要从 `bi` skill 根目录解析，不要假设目标项目本身存在 `scripts/`：

```bash
python <bi-skill>/scripts/init_byissue.py --project .
```

初始化后确认 `byissue/vision/index.md` 与 `byissue/spec/index.md` 存在，并确认基础实体目录已创建或保留。Vision 骨架只是空地图，不推断用户的目标应用。Onboard 不创建或修改 `AGENTS.md` / `CLAUDE.md`。

如果项目已有旧文档，只说明之后可以通过讨论、规格维护、知识记录、流程学习或关闭模式逐步沉淀，不在 onboard 里强迁移。

## 产物契约

脚本会创建基础实体目录，以及 `byissue/vision/index.md` 和 `byissue/spec/index.md`；具体创建或保留了哪些路径以脚本输出为准，不在本文重抄一份清单。工作区地图见 `SKILL.md`。Epic 的 `issues/` 在该 Epic 首次建立所属 Issue 时再创建。

`byissue/vision/index.md` 只是目标应用地图骨架，`byissue/spec/index.md` 只是当前项目真相骨架。Onboard 不替用户填写愿景或真实需求，不创建 issue、epic、note 或 tool 正文，不覆盖已有内容。已有项目缺少 Vision 时，重新运行脚本可以增量补齐，不影响原有 `byissue/` 内容。

## 收尾汇报

告诉用户创建或补齐了哪些目录和文件、哪些已存在所以保留，以及下一步最适合进入哪种模式：讨论、规格维护、知识记录或未知流程学习。

## 应用场景

第一次使用 bi、项目还没有 `byissue/`、用户说接入 ByIssue/初始化 bi/搭好 bi 基础结构/重跑 onboard 同步缺失骨架时使用。
