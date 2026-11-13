---
kind: issue
title: "宿主记忆层不是沉淀去处"
type: ff
status: closed
created: 2026-09-28
---

# 宿主记忆层不是沉淀去处

沉淀收割时「记一下这个坑」被宿主自带的记忆层吸走，`byissue/` 拿不到东西。根因是注入层级：宿主的记忆 guidance 常驻系统提示并明写「值得留的事实进 memory」，而 bi 的去处规则在按需加载的技能文件里——常驻的赢。在 `SKILL.md` 既有的写入边界契约里追加一段，把宿主记忆层也排除出去。

- 改动：`skills/bi/SKILL.md` — 在「bi 只写 `byissue/` 之内，不碰 `AGENTS.md` / `CLAUDE.md`」之后追加「宿主自带的记忆层同样不是去处」，措辞宿主无关（不点名任何扩展或工具名）；`VERSION` 1.7.0 → 1.7.1；`CHANGELOG.md` 新增 1.7.1 小节；已 rsync 同步 `~/.agents/skills/bi/`，`diff -rq` 确认一致。
- 仓库外改动：`~/.config/cortexkit/magic-context.jsonc` 加 `memory.enabled: false`、`memory.auto_search.enabled: false`、`dreamer.disable: true`，备份 `magic-context.jsonc.bak-20260928-173123`。属用户本机配置，不进版本库。
- 验证：`python3 tools/check-skill-repository.py` 通过（姿态表与 description 未动，两段路由不受影响，无需跑行为评测）。配置侧以 `json.loads` 确认可解析，并与上游 schema 的键名逐一核对（`memory.enabled` / `memory.auto_search.enabled` / `dreamer.disable`）；生效需重启 Pi。
- byissue：无 spec 漂移。契约本体落在 `SKILL.md`，`spec/index.md` 已声明它是唯一权威入口，不再另写一份。未立 `decisions/`——一段追加不满足「难以逆转」门槛。

顺手发现：`byissue/notes/001-real-world-usage-stats.md` 记录的「产品本身不采集任何使用信号」在本次得到侧面印证——判断记忆是否被误用只能靠人工读宿主的本地数据库，byissue 侧没有任何信号。不在本次范围。
