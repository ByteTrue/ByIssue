# pi 实际任务评测

## 任务与判据

给空项目安装本地 v2 技能后，提供三份含嵌套路径、中文客户、整数及小数金额的 CSV。第一轮实现迁移并按用户要求暂停；第二轮使用全新 pi 会话继续报表，并加入最小金额过滤。

- 业务正确性由 `acceptance.py` 从真实 CLI 独立检查；期望金额来自手算，验收程序保留在被测项目之外。
- 工作流正确性由工具调用记录和磁盘产物判断：读取安装的技能、先写检查点、按来源建立范围、暂停保留缺口、新会话读取检查点、完成前验证真实入口。
- 记录时长、模型用量和工具调用数。单个样例不支持与其他工作流的效率比较。

## 输入与独立验收

- 第一轮：`phase-1.txt`
- 第二轮：`phase-2.txt`
- 原始数据：`legacy/`
- 独立验收：`acceptance.py`

```bash
python3 byissue/work/v2-readiness/evaluation/acceptance.py <被测项目目录> migrate
python3 byissue/work/v2-readiness/evaluation/acceptance.py <被测项目目录>
```

在空项目、尚无 ledger.py 时运行独立验收，已观察到失败，证明缺少实际入口无法通过。

## 运行结果

业务验收通过；工作流执行未全部通过。两轮是不同的 pi 会话，第二轮没有传入第一轮对话，仅保留项目文件。

环境：pi 1.5.2，`bytetrueapi/deepseek/deepseek-flash`，thinking 为 medium。技能由 `npx skills add <本地 v2 仓库> --skill bi --agent pi --copy --yes` 安装到 `.agents/skills/bi`，运行前逐文件比较与源技能一致。配置和会话目录隔离，显式加载该副本，关闭其他技能、扩展、MCP、上下文文件及提示模板的自动加载。

| 指标 | 第一轮：迁移 | 第二轮：新会话接续与报表 |
|---|---:|---:|
| 进程耗时 | 123.80 秒 | 133.70 秒 |
| 模型回复数 | 21 | 18 |
| 工具调用数 | 27 | 29 |
| 输入 token（不含缓存读取） | 43,622 | 55,570 |
| 缓存读取 token | 348,928 | 411,776 |
| 输出 token | 19,155 | 21,160 |

以上为 pi 返回的累计用量，包含多轮重复上下文；不把累计 token 当作单次上下文大小，也不据此推算实际账单。总进程耗时为 257.50 秒，没有无技能对照组。

### 独立验证

`acceptance.py` 的两次验收均退出 0：

- 三份 CSV 递归迁移，7 条记录、金额合计 101570 分，整数转换和排序符合手算期望。
- 同一输入重复运行字节一致，原始数据保留。
- 10 类非法输入非零退出，stderr 有错误，已有目标文件不被覆盖。
- 7 条报表路径通过，覆盖默认汇总、客户精确匹配、阈值边界及组合过滤。
- 3 个非法阈值非零退出。

pi 另外编写了 18 个 CLI 回归测试，并实际在改坏的副本上验证部分检查会失败。独立验收程序从未提供给 pi。

### 工作流观察

| 判据 | 结果 | 可复查证据 |
|---|---|---|
| 从安装副本读取 v2 与所需 reference | 通过 | 两份 trace 的开头工具调用 |
| 写业务代码前建立 work 和证明契约 | 通过 | phase-1-trace 中 work 写入先于 ledger.py |
| 从事实源列出全部迁移范围 | 通过 | find 命令列出 3 份 CSV，scope 逐文件覆盖 |
| 按用户要求暂停并留下可继续的状态 | 通过 | 第一轮 work 为 in_progress，next_action 指向 report，缺口明确 |
| 新会话根据检查点接续 | 通过 | 第二轮第 3 个工具调用读取既有 work，随后核对代码和测试 |
| 新要求先进入检查点再实现 | 未通过 | 第二轮先编辑 ledger.py，实现和测试完成后才更新 work；--min-cents 没有先进入检查点与证明契约 |
| Memory 只保留长期必要内容 | 未通过 | 第一轮 Memory 包含“本轮只做 migrate”、3 份 CSV/7 行等临时事实，并复述 CLI 形状和原子写入实现；第二轮继续扩写 |
| 真实入口验证后再完成 | 通过 | 两轮均运行 CLI；第二轮在测试通过后标记 complete，随后再次复验 |

另有一处证据标注错误：首轮实际运行的是默认 `shasum`（SHA-1），work 却写成 SHA-256。第二轮使用 `shasum -a 256` 并修正了记录。原数据字节未变化，问题在记录的算法名称。

这次证明了该样例能完成迁移、跨会话继续并交付正确行为，也暴露了规则写在文件里仍可能未按时执行。没有测试多轮真实压缩、大型代码库、其他模型或长期效率提升。上述未通过项保留为 v2 后续修改依据，本轮未通过追加提示或改写产物来抹掉失败。

## 证据文件

- [metrics.json](metrics.json)：用量与技能包各文件 SHA-256。
- [phase-1-trace.jsonl](phase-1-trace.jsonl)、[phase-2-trace.jsonl](phase-2-trace.jsonl)：保留工具参数、结果和最终文字，去除逐 token 流与思考内容；临时根目录统一记作 `<run-root>`。
- `phase-1-artifacts/`、`phase-2-artifacts/`：work、scope 与 Memory 原始快照，使用 `.txt` 后缀以区别于本仓库的活动工作记录。
- [ledger-result.py](ledger-result.py)：pi 交付的实现；`test_migrate.py.txt`、`test_report.py.txt` 是其回归测试快照。

## 重跑方法

从空目录安装技能，复制 `legacy/`，再依次把 `phase-1.txt` 和 `phase-2.txt` 的内容交给两个新 pi 会话。每轮使用相同模型、安装副本和以下启动参数；第二轮不加 `--continue` 或 `--resume`：

```bash
pi --model bytetrueapi/deepseek/deepseek-flash --thinking medium \
  --mode json --print --approve \
  --no-extensions --no-mcp --no-context-files --no-prompt-templates \
  --no-skills --skill "$RUN/project/.agents/skills/bi" \
  --session-dir "$RUN/sessions" "$(cat "$EVAL/phase-1.txt")"
```

`RUN` 是临时根目录，`EVAL` 是本目录的绝对路径；在 `$RUN/project` 中运行。`PI_CODING_AGENT_DIR` 指向只含模型与授权配置的独立目录。第二轮替换为 phase-2.txt。每轮结束后从本仓库运行上面的独立验收命令。
