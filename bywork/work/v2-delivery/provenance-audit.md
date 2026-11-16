# v2 技能文件血缘审计

回答一个问题：v2 是不是 v1 随便改改？结论：**工作流核心是重写，7 份原则材料带 v1 血缘（2 份逐字未动）。** 以下全部 git 实测。

## 取证基线

- v1 = `main` HEAD `471cd65`（docs(byissue): magpie pulls bi back from GitHub…）。
- v2 = `v2` HEAD `2a5883a`（chore: v2.1.1 收尾…）。
- `git merge-base main HEAD` = `471cd65`，即 v2 从 main HEAD 直接长出，无分叉。
- 行数/改动幅度用 `git diff --numstat main HEAD -- <path>` 与 `git show main:<path> | wc -l`。

## 结构层：v1 骨架整体拆除（重写证据）

| 维度 | v1 | v2 |
|---|---|---|
| SKILL.md | 281 行，姿态模型（讨论/设计/快改/受管理实现/修bug/收尾…） | 102 行，四种行动 + 改变核心流程 + 底线（+63/−242） |
| references | 23 份 | 12 份 |
| 模板 | 13 个 `templates/entities/`（issue/epic-spec/decision/talk/note/vision-index…） | 4 个（work/memory/scope/vision），entities 目录已不存在 |
| 实体模型 | Vision / Project Spec / Epic / Issue | 单一 work + Memory + 按需 vision |

v1 的 15 份核心 references 在 v2 全部删除（`git cat-file -e HEAD:<path>` 均失败）：
`close code-design complain debug design do docs explore fast large maketools note spec talk vision`。

v2 的五份核心 references 在 main 上不存在（`git cat-file -e main:<path>` 均失败），为新建：
`change clarify prove memory-direction understand-review`。

v2 新造、v1 无对应物的机制：检查点五字段（status/current_unit/next_action/must_hold/proof_gap）、证明表六列、scope 机械范围门、完成四门（行为/范围/契约/完成）、`scripts/check_work.py`。

## 继承层：7 份同名原则材料

| 文件 | v1→v2 numstat | v1→v2 行数 | 性质与来源 |
|---|---|---|---|
| `grilling.md` | 0/0（逐字节同） | 27→27 | 外部件。v1 时期 `bc6821b`「grilling mirrors upstream verbatim」镜像 Matt Pocock `skills/productivity/grilling/SKILL.md`；v2 延续。非 v1 原创 |
| `writing.md` | 0/0（逐字节同） | 42→42 | **v1 原创**，1.12.0 `49d4c64` 引入、1.13.2 `69851bb` 修订；v2 原样照搬 |
| `domain-modeling.md` | +11/−13 | 46→44 | 外部件（Matt `skills/engineering/domain-modeling/SKILL.md`）吸收改写，落点换成 bywork/memory，加 Grillable/ungrillable 段 |
| `economy.md` | +28/−79 | 106→55 | v1 原创压缩。6 个原则标题里 5 个逐字保留（先理解再最小化/从不新增开始/在正确责任边界修一次/不为想象中的未来付费/留下最小有用反馈/交付前清理自己的 diff），删背景、应用场景及 3 节 |
| `quality.md` | +20/−45 | 71→46 | v1 原创重组。保留「九项产品质量特征」（ISO/IEC 25010）框架；「质量承诺链」改写为「选中即承诺/质量目标如何进入 work/必须保留的工程护栏」 |
| `ui-spec.md` | +18/−75 | 99→42 | v1 原创大幅压缩 |
| `onboard.md` | +14/−26 | 39→27 | v1 原创改写，接入脚本保留 |

`scripts/init_bywork.py` +7/−17，v1 脚本改写。`scripts/check_work.py` 为 v2 新建。

## 外部来源核对（grilling / domain-modeling）

- 参考副本 `~/workspace/reference/ai-workflows/matt-skills/`，remote `github.com/mattpocock/skills`。
- 副本 HEAD `5863806`（2026-11-12），`git ls-remote origin HEAD` 同为 `5863806`，即当前上游最新。
- `grilling.md` 与上游 SKILL.md 正文逐行 diff 仅 1 行措辞漂移：上游 `dispatch a sub-agent with a fresh context window to find it`，bi 少 `with a fresh context window`。核心机制（design tree/frontier/rounds/❓➡️ 格式/事实与决策分离/确认门）一致。
- `domain-modeling.md` 是吸收件非镜像，按 bi 契约判断，不存在逐字同步问题。

## 判断

- 方法论核心（怎么干活）= 重写，v1 无对应物，已验证（A/B 3/3 vs 0/3、候选三十连续两轮、三短场景）。
- 通用原则（怎么算好代码/好文字/好访谈）= 继承。economy/quality/ui-spec/onboard 是 v1 原创压缩重组，writing 是 v1 原创逐字搬，grilling/domain-modeling 本就是外部吸收件。
- 「v2 完全从头设计」对工作流架构成立，对全部文字不成立。原则材料稳定继承本身合理（不重复造轮子），但是否「优秀到没有优化空间」需另行调研评判，不在本审计范围。

## 边界

- 未逐行核对 economy/quality 压缩后是否丢失 v1 某条有效原则（只比标题骨架与行数）。
- 未审计 v1 `bywork/` 制度记忆内容是否被 v2 沿用（属归档，byspace 侧已处理）。
- 本记录是静态血缘取证，不替代对每份原则材料的质量评判。