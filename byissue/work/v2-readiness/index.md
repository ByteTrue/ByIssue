---
kind: work
status: complete
current_unit: "v2 分支、文档、归档和 pi 实测已完成"
next_action: "无"
must_hold: "中文主文档与英文版同步；安装指定 v2；旧记录完整归档；评测使用实际安装副本和真实 CLI；用户已授权提交推送到 origin/v2；如实保留评测失败项"
proof_gap: "本次交付无待验项；pi 的要求变更先回写与 Memory 边界两项未通过，具体证据保留在 evaluation/README.md"
---

# v2 分支、文档、归档与实测

## 目标与边界

用户要求建立 v2 分支，按 create-readme 重写 README 并从 v2 分支安装，将旧版 bi 产物整体归档，以及在空目录安装技能后用 pi 执行真实任务。

本次评测覆盖安装、非平凡改变、来源完整性核对和新会话接续。用实际产物、CLI 黑盒断言与工具调用记录判断结果。

## 已定方案与约束

- 当前工作树位于 `v2`，跟踪 `origin/v2`。
- 旧记录进入 `archive/v1/`，保持内容与相对结构。当前项目约束放在 `byissue/memory/project.md`，工作放在 `byissue/work/`。
- README 使用 `https://github.com/ByteTrue/ByIssue/tree/v2`，同时提供 pi 的安装和调用方式。
- pi 使用独立配置和会话目录，只安装本次 v2 技能。给它真实业务要求；验证程序放在被测项目外。
- 记录耗时、模型用量、工具次数和实际正确性。单次运行只支持本场景结论，不能证明普遍提效。

## 行为证明

| 行为路径 | 真实入口 | 操作 | 应观察到 | 证据 | 结果 |
|---|---|---|---|---|---|
| 分支 | Git | 创建分支并按用户授权推送 | 当前工作树位于 v2，已有改动保留，远端分支可用 | 主体提交 d5793ae；`git push --set-upstream origin v2` 成功 | 通过 |
| 本地安装 | npx skills | 空目录安装当前技能并比较文件 | pi 加载目录与源技能逐字节一致 | npx 安装成功，release-check 比较实际 .agents/skills/bi 副本通过 | 通过 |
| 远端安装 | GitHub v2 分支 | 从 README URL 安装 | 安装指定分支中的 bi | 空目录安装成功；skills-lock.json 记录 source 为 ByteTrue/ByIssue、ref 为 v2；release-check 比对远端安装副本通过 | 通过 |
| 旧记录隔离 | 文件系统与 checker | 移动后逐文件核对摘要，再执行检查 | 历史内容保留；活动目录仅保留 v2 入口 | scope.md 中的复核命令输出 73 archived files verified | 通过 |
| 文档可用 | README 与 skills CLI | 核对分支、参数、链接和技能调用 | 中英文说明对应实际安装行为 | 分支安装命令成功；pi 的 `/skill:bi` 识别新入口与五字段，并遵守只读要求，见 evaluation/README.md | 通过 |
| pi 实际任务 | 已安装技能与业务 CLI | 分阶段执行迁移和查询，再以新会话继续 | 真实行为正确，未完成时有可接续检查点，范围完整 | evaluation/README.md：独立验收通过，工作流执行缺口单列 | 通过 |
| 维护回归 | release-check | 运行本地检查与安装副本比较 | 全部检查通过 | checker 自测 22/22、初始化测试、本地与远端安装副本比较通过 | 通过 |

## 证据与决定

归档范围见同目录 `scope.md`。pi 的任务、独立验收和结论放在同目录 `evaluation/`。

用户在本轮确认“提交并推送”，授权范围为这批 v2 改动与评测记录，目标为 origin/v2。

评测没有全部证明工作流契约：新要求回写时点和 Memory 边界仍有缺口。业务验收通过与这些规则的执行结果分别记录。

## 完成核对

- 本次交付的行为门通过，包含实际分支安装与 pi 调用。工作流规则的两个未通过项保留在评测结论中。
- 范围门通过，73 个旧文件与基线集合、归档摘要逐项一致，详见 `scope.md`。
- 项目约束与可重跑维护检查保存于 `byissue/memory/project.md`。
- 普遍提效、多轮真实压缩和大型代码库效果无法判定，本次没有对应对照或运行证据。
