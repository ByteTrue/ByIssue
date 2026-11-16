# bi 效果评测

用真实安装的技能、pi 新会话和独立验收检查行为。代码通过、工作流通过、效率变化分别报告。最初的账单评测与失败证据见[历史记录](../../bywork/work/v2-readiness/evaluation/README.md)。

## 运行一次

需要 Python 3.10+、pi、Node.js、Git，以及已配置的模型访问。运行目录必须是仓库外的新路径；失败目录保留，下一次另起目录。

```bash
python3 tools/evaluation/run.py \
  --output "$TMPDIR/bi-ledger-run-01" \
  --model bytetrueapi/deepseek/deepseek-flash
```

默认测试当前仓库的 `skills/bw/`，使用 ledger 两阶段场景、medium thinking。`--source` 可指定包含 `skills/bw/` 的本地旧版快照；`--config` 指定 pi 配置目录，只使用其中的 `auth.json` 与 `models.json`。模型必须写完整 provider/model，运行结果会核对实际模型。

Memory 筛选还有独立的正向场景：

```bash
python3 tools/evaluation/run.py \
  --case tools/evaluation/cases/memory-selection \
  --output "$TMPDIR/bi-memory-run-01" \
  --model bytetrueapi/deepseek/deepseek-flash
```

### 自动步骤

1. 在空项目中用 `npx skills add` 安装指定来源，逐文件比较 SHA-256，记录 pi 版本、模型、thinking、技能与用例摘要。
2. 只复制业务夹具到项目。每个阶段使用新的 pi 进程与会话目录，关闭其他技能、扩展、MCP、上下文文件和提示模板的自动加载。临时目录独立，两个版本使用相同的目录边界提示。
3. 每阶段结束后保存项目快照和工具记录，核对模型、会话 ID、安装副本、验收材料和原始业务输入。验收由父进程运行，程序和标准答案不传入被测 Agent。
4. 保存业务结果、耗时、工具次数和 pi 返回的 token 用量。失败或超时保留已有证据并非零退出，重跑使用新目录。

这是会话与配置隔离，不是操作系统沙箱。工具记录还需确认 Agent 没有读取项目外的验收材料；发生串扰时，该运行判为无效。

对照默认顺序运行。实测中，即使设置了 TMPDIR，Agent 仍可能写固定 `/tmp` 文件；严格并发隔离需要宿主提供文件系统沙箱。

## 读结果并判定

| 文件 | 用途 |
|---|---|
| `report.json` | 安装、来源摘要、模型与版本、各阶段退出码、业务验收、时间和用量 |
| `review.md` | 工作流结论，初始均为无法判定，审查后逐行回填 |
| `phase-N/trace.jsonl` | 工具参数、结果和助手可见回复，去除逐 token 流与思考内容 |
| `phase-N/project/` | 阶段结束时的业务、work、scope 和 Memory 快照 |
| `phase-N/acceptance.log` 及 `.stderr` | 独立验收输出 |
| `phase-N/raw.jsonl`、`phase-N/sessions/` | 本地原始证据，保留在运行目录 |

运行器退出 0 只表示采集和业务验收通过。**工作流结论由 `review.md` 决定**。审查先看工具成功结果、写入内容和先后顺序，再看阶段快照；收尾文件齐全不能证明过程正确，口头计划不能替代写入。

跨会话场景还要将暂停时的待做契约逐项对照原始用户要求。即使后续实现、测试和 work 彼此一致，漏掉用户规定的输出格式仍是失败。

- [ledger](cases/ledger/workflow-rubric.md)：迁移、范围覆盖、按要求暂停、新会话追加约束、报表、Memory 边界与证据准确性。业务提示和 CSV 沿用首次评测。
- [memory-selection](cases/memory-selection/workflow-rubric.md)：明确长期决定与理由应保留；配置数值和本轮交接信息留在事实源或 work。避免把“从不写 Memory”误判为修复成功。
- [webhook-inbox](cases/webhook-inbox/workflow-rubric.md)：新业务任务，通过真实签名 HTTP、并发重试、重启和 CLI 查询/导出检查通用工作流；完整业务接口在用例的 `project/contracts.md`。原子替换与常量时间比较另需代码审查，不能仅由自动验收的成功路径推定。

逐行写通过、未通过或无法判定，并引用 trace 行号或快照内容。有未通过项就报告具体失败；证据缺失、会话中断或外部条件未走到时写无法判定。保留首次结果，新结果不能覆盖它。

## 比较两个版本

先保存旧技能，再改规则。以下例子从 Git 提取旧包；`BASELINE` 是选定提交，`OLD` 是仓库外的空目录：

```bash
git archive "$BASELINE" skills/bw | tar -x -C "$OLD"
python3 tools/evaluation/run.py --source "$OLD" \
  --output "$TMPDIR/bi-old-01" --model bytetrueapi/deepseek/deepseek-flash
python3 tools/evaluation/run.py \
  --output "$TMPDIR/bi-new-01" --model bytetrueapi/deepseek/deepseek-flash
```

同一对照使用相同用例摘要、pi 版本、模型、thinking、环境提示与验收。每个版本独立安装，两个阶段之间只共享本版本的项目文件。新旧版本都跑相关场景，避免把模型随机波动误认为修改效果。

一次对照只回答本次样例是否出现目标行为。要报告“更快、更省”，两边交替运行至少三次，报告中位数和范围、正确性与工作流结果；范围重叠时报无可测差异。并发耗时只作观察，不用于速度优劣结论。缓存读取、非缓存输入、输出分别列出，不将累计 token 当作单次上下文或实际账单。

最终报告包括版本与来源摘要、业务结果、工作流逐项结论、时间与用量、失败样例及未覆盖范围。真实压缩、多轮长期任务和大型仓库需要对应场景证据。

## 大型仓库的成熟功能重建

[BySpace 计划任务场景](cases/byspace-schedules/task.txt)从固定提交删除调度引擎、CLI/RPC 和前端实现，保留协议、调用方、公开文档与回归测试。原版留在被测项目外。删减副本创建只有一个基线提交的独立分支，并整体移除 v1 `bywork/`。

```bash
python3 tools/evaluation/freeze_repository.py \
  --repo /path/to/byspace \
  --revision 708ec9f2508978a71b80f2cae3ecf3a7d66e8eca \
  --output /path/to/evaluation/corpus
python3 tools/evaluation/prepare_rebuild.py \
  --corpus /path/to/evaluation/corpus \
  --output /path/to/evaluation/rebuild-01 \
  --dependencies-from /path/to/byspace
python3 tools/evaluation/run_repository.py \
  --run /path/to/evaluation/rebuild-01 \
  --model bytetrueapi/deepseek/deepseek-flash
```

依赖复制使用 macOS `cp -cR`，要求来源 lockfile 与固定源码一致。启动前先在独立原版副本和删减基线上标定验收：

```bash
python3 tools/evaluation/cases/byspace-schedules/acceptance.py \
  --project /path/to/project-copy \
  --output /path/to/new-acceptance-evidence --browser
```

验收通过 Go overlay 注入外部公开 API/CLI 探针，不依赖旧实现的私有字段；另外运行原有定向回归、构建、类型检查和两个 schedules Playwright spec。兼容探针覆盖重启归档、agent 环境目标、CLI 输出/空参数、旧周期网格及半小时 DST；浏览器兼容检查覆盖列表分组与 heartbeat 操作。外部浏览器文件只在验收期间注入，结束后移除。浏览器使用独立测试宿主和动态端口，有本机 Chrome 时直接复用。保留原版失败项并查明原因：恢复质量依据需求和原版实际行为分别报告，不能为了让原版全绿而删掉有效断言。

长任务运行器只给一次完整需求，在一个 pi 会话里持续执行。默认原生自动压缩阈值 400k、最近上下文 20k，模型窗口保持配置值；`reserveTokens = contextWindow - compact-at`。通过 `--compact-at` 显式改变阈值，实际设置写入报告。宿主根据上下文增长自动触发，不规定压缩次数或阶段，不做压缩/不压缩对照。默认整项任务超时为四小时，可用 `--timeout` 调整。

与短场景一样，运行器核对实际安装的技能、模型、独立验收及原测试完整性。运行级 home、临时目录和 GitHub 配置隔离；继承的生产 daemon/E2E 配置被清除，Go 子进程移除过期 GOROOT。文件系统仍依靠目录约定，最终需审查越界读取。

长任务证据存放在运行根目录：

| 文件 | 用途 |
|---|---|
| `seed.json` | 原提交、删减基线提交、删除清单与源码摘要 |
| `prompt.txt`、`report.json` | 完整输入、技能/验收摘要、设置、实际用量和结果 |
| `raw.jsonl`、`sessions/`、`trace.jsonl` | 原始流、持久会话与可读工具记录 |
| `compactions.json` | 原生事件和持久摘要逐项对应、次数、压缩用量与上下文峰值 |
| `project/`、`changes.diff` | 重建产物；未跟踪的新文件也在 project 中保留 |
| `acceptance/`、`review.md` | 独立验收日志/浏览器证据，以及人工功能和工作流审查 |

压缩事件必须对应持久会话里的原生摘要，失败或未完成尝试保留。没有触发压缩时计数为零，接续质量保持无法判定。运行时长、累计 token 和压缩次数都不能单独证明实现质量。

首轮完整样例见[大型重建评审](../../bywork/work/large-repo-compaction/review.md)：原版标定、自然压缩、首次验收、补充公开 API/CLI 与浏览器探针、25 项来源对账都已留存。补充探针在模型结束后同时对原版与重建版运行，单独保存为 review 证据，不覆盖首次验收。动作顺序和文件访问回到完整工具记录判断，压缩摘要附带的文件清单可能漏掉 bash 内的读写。

当前任务明确列出精确兼容接口，且验收已经包含首轮补测。它与首轮输入不同；比较技能版本时须同时使用当前冻结任务，不能直接将首轮数值当成同条件基线。当前持续优化的交付判据及每轮依据见[交付验证 work](../../bywork/work/v2-delivery/index.md)。

独立探针的每条精确期望都要能在被测项目可见要求中找到依据。原版行为只能证明兼容差异；缺少公开依据时补任务契约并冻结新输入，先前结果单列输入缺口。调度任务明确区分普通延迟 tick 与重启恢复的跳槽规则，CLI 明确位置提示词形状。

浏览器探针按可见操作判定：页签名称可附带数量，行操作可为行内按钮或菜单。检查仍需实际切换列表，并确认 heartbeat 的编辑/删除可用、计划任务专属操作不可用。控件定位失败先核对截图和可访问性快照，区分功能缺失与探针假设过窄。

## 工作流价值的 A/B 通过率协议

大型重建的单次全绿不是合适的交付门：同一技能在同一任务上的失败点会随运行随机移动（模型方差），逐轮按失败加规则会把技能重新养胖。工作流的价值用对照通过率回答：同一任务、同一模型与 thinking、同一验收，A 臂不安装任何技能（`run_repository.py --no-skill`，任务文本去掉工作流措辞，其余逐字节一致），B 臂安装被测技能。两臂交替顺序各跑至少三次，报告业务通过率和范围；范围重叠时报无可测差异，不宣称工作流收益。

`--no-skill` 运行器不安装技能，并在验收前核对项目内没有意外的 `.agents/skills/bw`（对照被污染即判失败）；报告记录 `arm` 字段。工作流结论仍按 B 臂 trace 和最终 work 的结果判据审查，与业务通过率分开报告。

```bash
bash tools/evaluation/ab_driver.sh   # 交替跑 ab-nobi-01..03 与 ab-bi-01..03
```

## 维护用例和运行器

短场景用例目录包含：

- `project/`：只读业务输入；需要修改的目标文件让 Agent 创建。运行器会核对输入未变。
- 连续编号的 `phase-1.txt`、`phase-2.txt` 等：用户任务，不包含实现答案或评分提示。
- `acceptance.py`：接收项目目录和阶段编号，从真实入口检查需求，失败非零退出。期望值来自需求或手算。
- `workflow-rubric.md`：执行过程和长期记录的审查判据。

仓库重建场景使用 `rebuild.json` 和一份 `task.txt`，其验收接收 `--project`、`--output` 与可选的 `--browser`。新增自然长任务场景先冻结原版和删减版证据，再运行模型。

新增验收要先在已知错误或故意做坏的产物上看到失败。用例、验收或环境提示变化后重跑两组，不能直接和旧指标拼成一次对照。新增场景优先覆盖已暴露的失败与相邻正向行为。

运行器的离线检查已接入发布检查，也可以单独运行：

```bash
python3 -m unittest discover -s tools/evaluation -p test_runner.py -v
```

离线检查使用首次正确产物 `bywork/work/v2-readiness/evaluation/ledger-result.py` 和真实格式错误产物 `bywork/work/eval-standardization/evaluation/revision-2-ledger/phase-2/project/ledger.py`。这两个历史文件也是回归夹具，整理记录时保留或同步迁移其测试引用。

长期判定原则见[评测依据](../../bywork/memory/evaluation.md)。
