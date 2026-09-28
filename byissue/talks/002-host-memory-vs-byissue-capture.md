# 宿主记忆层与 `byissue/` 谁是沉淀去处 talk

> **写法：** 按当时讨论推进的顺序写，每一节 = 一轮推进或一次关键纠正，节标题用议题语言。

---

## 1. 开场：经验进了记忆，没进 bi 的沉淀流程

用户原话是：开发中遇到坑，LLM 只把经验存进 magic context 的记忆里，而不是走 bi 的沉淀流程；换一台机器记忆不迁移，之前的经验就都没了。问了三件事——怎么看、记忆功能能否配置禁用、要不要卸载扩展防冲突。

**已确认：** 这是真问题，不是洁癖。查到的证据比用户描述的更严重（见第 2、3 节）。

## 2. 冲突不在「两个系统都想存」，而在注入层级

先查了 Magic Context 的 guidance 文本（`dist/` 里实际编译产物，不是文档）：它每轮都注入系统提示，明写 `A fact worth keeping is memory` 和 `Durable project facts belong in ctx_memory, not notes.`。而 bi 的 `note.md` 说「去处只有一个：`byissue/notes/`」——那是**按需加载**的技能文件。

**已确认：** 系统提示常驻、技能文件按需，常驻的那条一定赢。这不是模型偷懒，是优先级设计如此。所以「防止冲突」靠劝模型是没用的，得从注入源头或契约归属下手。

## 3. 实测：记忆已经在重抄仓库，而且早于换机器就丢了

三组只读查询（`~/.local/share/cortexkit/magic-context/context.db`）：

**（1）ByIssue 项目 6 条 memory，5 条是仓库文件的副本。** #1841 源头/部署副本、#1842 checker 五件事、#1843 两段路由、#1923 grilling 归属 → 全在 `spec/index.md` 里；#1845 不写 AGENTS.md → `decisions/008`。只有 #1844（edit 损坏中文）在 `notes/002` 有真身。

这正是本项目自己那条「重述过的契约一定漂移」被违反的现场：第二个真相源，而且 dreamer 每天还要花 token 去 verify 它。

**（2）不可迁移比「换机器」更早发生。** byspace 的记忆池裂成两半：`git:bed137d6…` 下 1411 条，`git:31713d42…` 下 143 条。而 byspace 现在的 root commit 是 `31713d42`——`bed137d6` 在本机任何仓库里都找不到了（全 home 扫过，含 worktrees）。项目身份按 git root commit hash 算，历史一重写，1411 条当场变孤儿。用户说的「换机器就丢」，实际是「改一次 git 历史就丢」。

**（3）绝大多数记忆不经过判断。** 全库 1932 条：1702 条 source_type=historian（压缩过程自动 promote），149 条 agent，81 条 dreamer。「只把经验存到记忆里」这件事有一大半根本不经过任何人的筛选。

**已确认：** 用户「现在的记忆可以抛弃」的判断有数据支撑。

## 4. 配置禁用可行且干净，卸载不可取

`memory.enabled: false`（用户级，需重启 Pi）。代码路径确认它做四件事：`ctx_memory` 工具被 `setActiveTools` 摘掉（模型物理上没法再写）、不再注入 `<project-memory>`、guidance 里的 MEMORY_GUIDANCE 段直接消失、historian/`ctx-recomp` 不再 promote。

卸载会连带砍掉压缩那一半（historian / 打标 / `ctx_reduce` / `ctx_search` / `ctx_expand`），那部分 bi 没有替代物，而它不是冲突源。

**已确认的取舍：** `<user-profile>` 会一起空掉（`state.memoryEnabled === false ? [] : …`，没有单独开关）。现存 11 条 user memory 是关于用户本人的，`byissue/` 天然装不下。用户明确选择接受，不导出。

**已确认：** 走三行配置，不走 `prompt_surface.guidance_override_path` 覆写文案。后者能保住 user-profile，但等于手写一份要跟着上游 guidance 版本走的散文，正好撞上「一条规则只能有一个归属」。

## 5. 关键纠正：改 `note.md` 是无效落点

原建议改 `note.md`，落笔前核对姿态加载表发现它只在**记知识**姿态加载。而实际发生沉淀的是**收尾**（`close.md` 的「沉淀收割」）和**快改**（`ff` 收尾）——那两个姿态下 `note.md` 不在场，reference 之间不能假定对方在场。

**已确认：** 改 `SKILL.md` 那段既有的写入边界契约（「bi 只写 `byissue/` 之内，不碰 `AGENTS.md` / `CLAUDE.md`」）之后追加一段。`SKILL.md` 永远在上下文里，一处覆盖三个姿态，不新增第二份表述。

措辞刻意写成宿主无关（不点名 Magic Context / `ctx_memory`）：技能要能分发给用别的宿主的用户，且不能依赖对方装了什么扩展。

## 6. 出口

**已执行：**
- `~/.config/cortexkit/magic-context.jsonc`：`memory.enabled: false`、`memory.auto_search.enabled: false`、`dreamer.disable: true`（保留原有 dreamer/historian 模型选择，重新打开只需翻一个键）。备份 `magic-context.jsonc.bak-20260928-173123`。
- `skills/bi/SKILL.md` 新增一段写入边界契约；rsync 同步 `~/.agents/skills/bi/`；VERSION 1.7.0 → 1.7.1；CHANGELOG 同名小节。
- `python3 tools/check-skill-repository.py` 通过。
- 落 `byissue/issues/012-x-ff-host-memory-is-not-a-sediment-destination.md`。

**暂不纳入：**
- 记忆导出 / 分流。用户明确「现在的记忆可以抛弃」。
- `decisions/` 立碑。一段追加不满足「难以逆转」门槛，理由记在 CHANGELOG。
- `spec/index.md` 新增条目。契约本体在 `SKILL.md`，spec 已声明 `SKILL.md` 是唯一权威入口，再写一遍就是第二个归属。
- 卸载扩展。压缩那一半没有替代品，且不是冲突源。
- 行为评测。本次没动姿态表和 frontmatter description，两段路由都没变，`tools/posture-scenarios.md` 无需新增场景。
