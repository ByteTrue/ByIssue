---
kind: issue
title: "将只留在客户端记忆中的沉淀项全量对账并补入 byissue/"
type: ff
created: 2026-10-29
---

# 将只留在客户端记忆中的沉淀项全量对账并补入 byissue/

> **读者：** 以后搜到这条时——「改了啥、怎么信、动没动制度记忆」。  
> **自检（四答即可，可合成短段，勿空标题凑节）：** 做了什么 · 改了哪些文件 · 怎么验证 · 对 `byissue/` 有无影响。

---

逐条对账 `<project-memory>`（17 条）与本仓库真实会话踩坑记录，把此前只写在客户端记忆或上一轮仅更新了记忆、尚未落入 `byissue/` 的 4 项规则与外部事实全部补入仓库跟踪的 `byissue/` 与 `tools/`。

- 改动：
  - `byissue/spec/index.md`：「改这个仓库要守什么」补入两条此前仅在客户端记忆中的项目规则——① 必做环节不写成判断题、触发范围不用窄场景枚举收窄模型判断面；② 路径与状态标记须避开常见词竞争先验并用新上下文冷读探针验首读释义；「发布链路」同步 `tools/check-skill-repository.py` 现行五项守门范围。
  - `tools/prompt-review.md`：第 3 类「路径与命名契约自洽」补入状态标记竞争先验与冷读行为探针核查要求。
  - `byissue/notes/2026-10-29-uv-spawn-cwd-enoent-in-parallel-subagent.md`、`tools/posture-scenarios.md`：沉淀 Node.js / libuv `uv_spawn` 在同轮并行 `rm -rf` 重建 `cwd` 与启动 `subagent` 时报 `spawn <node_path> ENOENT` 的外部运行时坑点与分轮规避方式。
- 验证：`python3 tools/check-skill-repository.py` 与 `python3 skills/bi/scripts/check_open_issues.py --project .` 均通过。
- byissue：如上已完成 `spec/index.md` 与 `notes/` 回写。
