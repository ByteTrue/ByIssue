<div align="center">

# ByWork v2

![ByWork](asset/ByWorkCover-v2.png)

**让 Agent 接着做对的事，用真实结果证明完成。**

**中文** · [English](README.en.md)

[快速开始](#快速开始) · [怎么用](#怎么用) · [工作如何保存](#工作如何保存) · [本地验证](#本地验证)

</div>

ByWork 是一个名为 **`bw`** 的 Agent Skill，用于 AI 辅助软件开发。它把目标、约束、下一步和验证证据留在项目中，帮助 Agent 在长任务、上下文压缩和新会话之后继续工作。

你说要做什么，`bw` 根据任务选择澄清、改变、理解与审查，或记忆与方向。小改直接验证；跨会话、多条行为路径和需要完整范围核对的任务建立工作检查点。

## 快速开始

需要支持 Agent Skills 的编码助手，以及 Node.js 22.20+ 和 Git。初始化工作目录使用 Python 3。

### 1. 从 v2 分支安装

在要使用 ByWork 的项目目录运行：

```bash
npx skills add https://github.com/ByteTrue/ByWork/tree/v2 --skill bw
```

按提示选择编码助手。默认安装到当前项目；加 `-g` 可全局安装。更新 v2 或从其他版本切到 v2 时，重新运行同一条命令。

> [!IMPORTANT]
> 安装地址中的 `tree/v2` 指定 v2 分支。仅使用仓库名会安装默认分支的内容。

### 2. 接入项目

在助手中输入：

```text
使用 bw，在这个项目接入 ByWork。
```

Agent 会建立 `bywork/work/` 和 `bywork/memory/`，已有内容保留。随后直接告诉它目标：

```text
使用 bw，把所有旧 CSV 的金额迁移为整数分，保留原始数据，并验证实际导入入口。
```

### 在 pi 中使用

```bash
npx skills add https://github.com/ByteTrue/ByWork/tree/v2 --skill bw -a pi -y
pi
```

在 pi 会话中输入：

```text
/skill:bw 在这个项目接入 ByWork，然后帮我理清这次改动。
```

其他助手按各自的技能调用方式使用 `bw`。

## 怎么用

| 你现在要做什么 | 可以这样说 | 得到什么 |
|---|---|---|
| 澄清目标 | “先聊清楚优惠券叠加的边界，再动代码。” | 确认目标、术语和取舍 |
| 改变软件 | “修复重复导入产生重复账单的问题。” | 实现、真实入口验证，必要时建立 work |
| 理解与审查 | “这条支付链路怎么工作？”“评审这个 diff。” | 有范围、有出处的解释或审查结果 |
| 记忆与方向 | “记住金额始终用整数分。”“整理下一阶段的方向。” | 按主题保存 Memory，按需整理 Vision |

这些请求前加上“使用 bw”即可。遇到只有你能决定的产品边界或取舍，Agent 会提问；能从项目和运行中查明的事实由它自己核对。

### 中途停下，再继续

```text
这轮先完成导入，报表留到下一次。
```

下一次会话：

```text
使用 bw，继续账单迁移。
```

Agent 接续时先读取当前 work 的检查点，再核对实际文件和证据；从压缩摘要接续也一样。存在多个同主题工作时，它会请你选择。

实现时按行为证明表逐行推进：每轮选一个用户行为，保存检查点后实现，从真实公开入口验证，把实际结果回写，再选下一行。验证守住契约：公开 CLI/API 的证明保存真实调用者看到的原始输出；修改共享路径前保存旧行为基线，改后用同一入口复验比较；显式保留/归档等可选策略逐分支验证；持久化、重启和生命周期行为通过新进程或重启入口观察；既有测试和公开夹具保持原文件与原断言，新增回归放新文件。

收尾时逐项核对证明表、scope 和外部验收结果，把每个未通过项写进 `proof_gap`。只有所有证明通过且 `proof_gap` 恰为空字符串时才写 `status: complete`；任何验收失败、缺少原始输出或既有测试被改写，都保持未完成并点名缺口。

运行中的安装技能、评测用例和运行器材料只读；流程记录写入项目的 `bywork/`，技能修改回到技能源仓库。

用户要求的原文或稳定来源、适用条件和例外会一起保留。留到下次的行为也保存已确认的输入输出格式和错误边界，让新会话有完整的实现依据。

## 工作如何保存

```text
bywork/
├── work/
│   └── {slug}/
│       ├── index.md       # 本次目标、检查点和行为证明
│       └── scope.md       # 需要完整范围核对时创建
├── memory/
│   └── {topic}.md         # 长期决定、外部事实、可重跑证明
└── vision/               # 整理长期方向时按需创建
    └── index.md
```

每个 work 的 `index.md` 顶部保存五项检查点：

| 字段 | 回答的问题 |
|---|---|
| `status` | 正在做、被阻塞，还是已完成？ |
| `current_unit` | 当前正在验证哪段行为？ |
| `next_action` | 接下来先做哪一件事？ |
| `must_hold` | 哪些已确认约束必须守住？ |
| `proof_gap` | 还缺什么证据或范围核对？ |

`kind: work` 标识文档类型。代码、配置、测试和 git 保留实现事实；Memory 只记录跨工作仍需要、无法从这些事实直接重建的判断。本轮交接信息留在 work，没有长期内容时 Memory 可以为空。

### 怎样算完成

- **行为证明**：从真实 UI、CLI、API 或其他实际入口操作，观察预期结果和关键副作用，记录证据。
- **范围覆盖**：迁移、重写、移植和“所有 X”任务，从事实源列出范围，逐项对账。

范围全部覆盖仍需行为验证。完成前从原需求逐项找到证明，再核对实际断言是否覆盖每个承诺。无法运行或尚未测到的路径标为“无法判定”，不能靠文件存在或局部测试通过宣布完成。完整契约见 [`skills/bw/SKILL.md`](skills/bw/SKILL.md)。

## 本地验证

维护仓库时，使用 Python 3 和 Bash 运行：

```bash
bash tools/release-check.sh --no-deploy
```

这会检查技能包、引用路径、版本记录、模板和初始化脚本。传入助手实际加载的技能目录，还会逐文件比较安装副本：

```bash
bash tools/release-check.sh /path/to/installed/bw
```

技能规则的真实效果按[标准评测流程](tools/evaluation/README.md)验证：固定输入、空目录安装、独立 pi 会话、业务验收和工作流逐项审查。

仓库只分发 [`skills/bw/`](skills/bw/)。[`tools/`](tools/) 保存维护检查，项目约束在 [`bywork/memory/project.md`](bywork/memory/project.md)，v1 历史材料集中在 [`archive/v1/`](archive/v1/)。首次 pi 实际任务的输入、验收与结果见 [v2 实测记录](bywork/work/v2-readiness/evaluation/README.md)。

---

基于 [CodeStable](https://github.com/liuzhengdongfortest)，由 [ByteTrue](https://github.com/ByteTrue) 维护。了解[为什么做 ByWork](WHY%20BYWORK.md)。
