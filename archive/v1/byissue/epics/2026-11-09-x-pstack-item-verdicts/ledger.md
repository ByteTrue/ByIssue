# 台账：pstack 逐项裁定

接着做或改这张表之前，先读同目录 [spec.md](spec.md) 的「已定方案与必须守住」和「结论的判据」。

接续点：五个单元都已裁定（118 行）。候选去重后在 [candidates.md](candidates.md)，用户已裁决吸收 9 条，落地是单元 L（119–127 行），1.14.0 已全部落地；第 120 行行为证据无法判定，用户已确认接受。53 行「已有／已有·部分」已逐行复核（4 行降级，1 行证据更新，5 行注明缺口不吸收的依据是用户对 candidates.md 的裁决；复核记在各 verdicts 行末「复核：」），复核翻出的一条新缺口用户同意吸收，落地是第 128 行（1.14.1）；它落地后关 Epic。verdicts 里 bi 的行号是裁定当时（1.13.3）的，1.14.x 加句后会漂几行，按原句 grep 定位。引用由 `check_quotes.py` 机械核对，脚本报的不一致逐条人工看过：都是建议新文或转述放进了引号，或标点不同。

## 列举来源

在 `/Users/zijie/workspace/reference/pstack-claude/plugins/pstack`（HEAD `91ab921`）下跑，可以重跑：

```sh
ls skills                                   # 67 个技能目录，含 24 条 principle-*
ls skills/poteto-mode/playbooks             # 23 个 playbook
ls agents                                   # 4 个子代理定义
ls hooks                                    # 22 个 hook 文件
ls hooks.json models.json                   # 插件根的 hook 注册与按角色配模型（U5 子代理发现，补进来）
```

## 结论取值

「结论」列取 `large.md` 的五个值：`做了` 表示这一行已有带证据的裁定，`不做` 只用于用户明确不要裁定的项。裁定本身写在「证据」列开头：

- `[已有]` bi 的 `文件:行` 和原句，说明同一时点同一动作。
- `[候选]` 它改变 agent 在哪个时点的什么动作，会落到 bi 哪个文件。
- `[不吸收]` 违反哪条形态约束，或与哪条现有契约冲突（引 `文件:行`），或只服务 pstack 自身机制。

| # | 项 | 单元 | 结论 | 证据 |
|---|---|---|---|---|
| 1 | playbook `authoring-a-skill` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 2 | playbook `autonomous-run` | U1 | 做了 | [已有·部分] 见 [verdicts/U1.md](verdicts/U1.md) |
| 3 | playbook `autopilot-full` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 4 | playbook `autopilot-stack` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 5 | playbook `babysit` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 6 | playbook `bug-fix` | U1 | 做了 | [已有·部分] 见 [verdicts/U1.md](verdicts/U1.md) |
| 7 | playbook `eval` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 8 | playbook `feature` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 9 | playbook `hillclimb` | U1 | 做了 | [已有·部分] 见 [verdicts/U1.md](verdicts/U1.md) |
| 10 | playbook `investigation` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 11 | playbook `multi-phase-plan` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 12 | playbook `opening-a-pr` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 13 | playbook `orchestrate` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 14 | playbook `pause-safely` | U1 | 做了 | [已有·部分] 见 [verdicts/U1.md](verdicts/U1.md) |
| 15 | playbook `perf-issue` | U1 | 做了 | [候选] 见 [verdicts/U1.md](verdicts/U1.md) |
| 16 | playbook `prototype` | U1 | 做了 | [已有·部分] 见 [verdicts/U1.md](verdicts/U1.md) |
| 17 | playbook `refactoring` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 18 | playbook `runtime-forensics` | U1 | 做了 | [候选] 见 [verdicts/U1.md](verdicts/U1.md) |
| 19 | playbook `session-pickup` | U1 | 做了 | [已有] 见 [verdicts/U1.md](verdicts/U1.md) |
| 20 | playbook `shipping` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 21 | playbook `trace-forensics` | U1 | 做了 | [候选] 见 [verdicts/U1.md](verdicts/U1.md) |
| 22 | playbook `visual-parity` | U1 | 做了 | [候选] 见 [verdicts/U1.md](verdicts/U1.md) |
| 23 | playbook `worktree-cleanup` | U1 | 做了 | [不吸收] 见 [verdicts/U1.md](verdicts/U1.md) |
| 24 | skill `principle-attack-the-premise` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 25 | skill `principle-boundary-discipline` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 26 | skill `principle-build-the-lever` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 27 | skill `principle-encode-lessons-in-structure` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 28 | skill `principle-exhaust-the-design-space` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 29 | skill `principle-experience-first` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 30 | skill `principle-explain-the-number` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 31 | skill `principle-fix-root-causes` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 32 | skill `principle-foundational-thinking` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 33 | skill `principle-guard-the-context-window` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 34 | skill `principle-laziness-protocol` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 35 | skill `principle-make-operations-idempotent` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 36 | skill `principle-migrate-callers-then-delete-legacy-apis` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 37 | skill `principle-minimize-reader-load` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 38 | skill `principle-model-the-domain` | U2 | 做了 | [候选] 见 [verdicts/U2.md](verdicts/U2.md) |
| 39 | skill `principle-never-block-on-the-human` | U2 | 做了 | [不吸收] 见 [verdicts/U2.md](verdicts/U2.md) |
| 40 | skill `principle-outcome-oriented-execution` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 41 | skill `principle-prove-it-works` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 42 | skill `principle-redesign-from-first-principles` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 43 | skill `principle-separate-before-serializing-shared-state` | U2 | 做了 | [已有] 见 [verdicts/U2.md](verdicts/U2.md) |
| 44 | skill `principle-sequence-verifiable-units` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 45 | skill `principle-subtract-before-you-add` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 46 | skill `principle-test-behavior-not-implementation` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 47 | skill `principle-type-system-discipline` | U2 | 做了 | [已有·部分] 见 [verdicts/U2.md](verdicts/U2.md) |
| 48 | skill `architect` | U3 | 做了 | [已有·部分] 见 [verdicts/U3.md](verdicts/U3.md) |
| 49 | skill `arena` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 50 | skill `automate-me` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 51 | skill `babysit` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 52 | skill `benchmark-checklist` | U3 | 做了 | [候选] 见 [verdicts/U3.md](verdicts/U3.md) |
| 53 | skill `blast-radius` | U3 | 做了 | [已有] 见 [verdicts/U3.md](verdicts/U3.md) |
| 54 | skill `bro` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 55 | skill `correct` | U3 | 做了 | [已有·部分] 见 [verdicts/U3.md](verdicts/U3.md) |
| 56 | skill `create-formal-verification-skill` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 57 | skill `create-verification-skill` | U3 | 做了 | [候选] 见 [verdicts/U3.md](verdicts/U3.md) |
| 58 | skill `deslop` | U3 | 做了 | [已有] 见 [verdicts/U3.md](verdicts/U3.md) |
| 59 | skill `figure-it-out` | U3 | 做了 | [已有·部分] 见 [verdicts/U3.md](verdicts/U3.md) |
| 60 | skill `fix-ci` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 61 | skill `fix-merge-conflicts` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 62 | skill `get-pr-comments` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 63 | skill `how` | U3 | 做了 | [已有] 见 [verdicts/U3.md](verdicts/U3.md) |
| 64 | skill `in-your-own-words` | U3 | 做了 | [已有] 见 [verdicts/U3.md](verdicts/U3.md) |
| 65 | skill `interrogate` | U3 | 做了 | [已有·部分] 见 [verdicts/U3.md](verdicts/U3.md) |
| 66 | skill `ketchup-video` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 67 | skill `ketchup` | U3 | 做了 | [已有·部分] 见 [verdicts/U3.md](verdicts/U3.md) |
| 68 | skill `maintain-formal-verification-skill` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 69 | skill `maintain-verification-skill` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 70 | skill `make-pr-easy-to-review` | U3 | 做了 | [不吸收] 见 [verdicts/U3.md](verdicts/U3.md) |
| 71 | skill `no-comments` | U4 | 做了 | [已有] 见 [verdicts/U4.md](verdicts/U4.md) |
| 72 | skill `poteto-help` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 73 | skill `poteto-mode` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 74 | skill `recall` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 75 | skill `reflect` | U4 | 做了 | [已有] 见 [verdicts/U4.md](verdicts/U4.md) |
| 76 | skill `setup-pstack` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 77 | skill `sharpen` | U4 | 做了 | [候选] 见 [verdicts/U4.md](verdicts/U4.md) |
| 78 | skill `show-me-your-work` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 79 | skill `statechart` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 80 | skill `swarm` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 81 | skill `tdd` | U4 | 做了 | [已有·部分] 见 [verdicts/U4.md](verdicts/U4.md) |
| 82 | skill `teach` | U4 | 做了 | [已有] 见 [verdicts/U4.md](verdicts/U4.md) |
| 83 | skill `technical-writing` | U4 | 做了 | [已有·部分] 见 [verdicts/U4.md](verdicts/U4.md) |
| 84 | skill `thermo-nuclear-code-quality-review` | U4 | 做了 | [已有·部分] 见 [verdicts/U4.md](verdicts/U4.md) |
| 85 | skill `thermo-nuclear-review` | U4 | 做了 | [已有·部分] 见 [verdicts/U4.md](verdicts/U4.md) |
| 86 | skill `thermos` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 87 | skill `typescript-best-practices` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 88 | skill `unslop` | U4 | 做了 | [已有] 见 [verdicts/U4.md](verdicts/U4.md) |
| 89 | skill `what-did-i-get-done` | U4 | 做了 | [不吸收] 见 [verdicts/U4.md](verdicts/U4.md) |
| 90 | skill `why` | U4 | 做了 | [已有·部分] 见 [verdicts/U4.md](verdicts/U4.md) |
| 91 | agent `comment-sicko` | U5 | 做了 | [已有·部分] 见 [verdicts/U5.md](verdicts/U5.md) |
| 92 | agent `poteto-agent` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 93 | agent `thermo-nuclear-code-quality-review-subagent` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 94 | agent `thermo-nuclear-review-subagent` | U5 | 做了 | [已有·部分] 见 [verdicts/U5.md](verdicts/U5.md) |
| 95 | hook `agy-context.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 96 | hook `codex-hooks.json` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 97 | hook `copilot-context.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 98 | hook `copilot-hooks.json` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 99 | hook `hooks.json` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 100 | hook `json.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 101 | hook `kimi-instructions.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 102 | hook `muse-context.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 103 | hook `pre-tool-use.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 104 | hook `pre-tool-use.sh` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 105 | hook `script-contracts.awk` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 106 | hook `session-start-agy.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 107 | hook `session-start-context.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 108 | hook `session-start-copilot-setup.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 109 | hook `session-start-copilot-sheet.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 110 | hook `session-start-copilot.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 111 | hook `session-start-minimax.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 112 | hook `session-start-muse-sheet.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 113 | hook `session-start-muse.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 114 | hook `session-start-opencode.md` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 115 | hook `session-start.ps1` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 116 | hook `session-start.sh` | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 117 | hooks.json（插件根） | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 118 | models.json | U5 | 做了 | [不吸收] 见 [verdicts/U5.md](verdicts/U5.md) |
| 119 | 落地 1：性能数字要量对（SKILL.md「证据本身要可信」） | L | 做了 | 复测 P1：读了 SKILL.md、fast.md；计时脚本在一个循环里交替跑改前改后各三次、三种查询，工具输出带三个值与中位数（5219→3.0ms），点名瓶颈；最终汇报只给了中位数没给范围，范围重叠分支没被触发（两边差三个数量级）。首轮 P1 跑在加强前：读了 SKILL.md；改前用同一脚本跑 3 次报「median 313.1 range 271.1-378.9」，改后同法 1.2ms，点名瓶颈是循环里重建 sku 列表 |
| 120 | 落地 2：卡死、泄漏、变慢先取现场（debug.md「升级」第 1 步） | L | 做了 | 行为无法判定：两次 P2（规则在 complain 快路径时一次、移到 debug「升级」后一次）都在读完源码后直接看出 audit() 的二重循环，再按请求数递增计时证实平方增长；复测只读了 complain.md、没进升级、没读 debug.md。夹具源码太小，读代码就能定位，不会逼出升级路径。要验证需要读代码定位不了的夹具。用户 2026-11-09 在「接受，不再补测」上确认：两次行为都对，与接受 debug.md 很少被读同理 |
| 121 | 落地 3：没有驱动真实行为的入口就先搭一个（do.md） | L | 做了 | P3：bash 读了 do.md；测试在随机端口起真实 server 发 HTTP 走「加商品→查总价」，入口用法写进夹具的 notes/2026-11-09-http-endpoint-test-shape.md |
| 122 | 落地 4：界面重写的对齐靠截图对比（large.md） | L | 做了 | P4：读了 large.md；写新代码之前用 headless Chrome 截了旧页 full/empty 两张基线，新页同尺寸截图对比 sha256 相同 |
| 123 | 落地 5：新写的检查先看它红一次（SKILL.md「证据本身要可信」） | L | 做了 | P5 新测试先在改前代码上跑见 99 元用例失败（期望 0 实际 10）；P3 同一测试放到 git archive HEAD 副本上跑，两个用例 404 失败 |
| 124 | 落地 6：两条设计红旗（code-design.md） | L | 做了 | P6：读了 code-design.md；发现第 2 条「同一份行格式写在三处」，建议 orders-store 独占格式、导出 readOrders()；P8（时序分解）：读了 code-design.md，指出 load/validate/save 三处各写一遍同一组规则且互相矛盾，建议只留一个拥有该格式的模块（它引的是「存储或报文格式散在多处」那条，没点名「按执行先后切」） |
| 125 | 落地 7：改状态的操作要能重跑（fast.md 红线、do.md「实现与验证」） | L | 做了 | 首轮 P7 只读了 fast.md、writing.md，规则当时在 code-design.md，没读到；脚本自带「全整数就拒跑」与先写 .bak，是模型自己的默认。审查 F3 后整条移进 fast.md，复测 P7：读了 fast.md；脚本改成先写 *.tmp 再 rename（首轮是原地覆盖），汇报写明「中途崩掉原文件不变」「全是整数时报错退出，避免误跑两次」；还把守卫删掉的副本上跑过测试看它失败；P7D（受管理 issue 走 do 路径）：读了 do.md，脚本默认预演、--write 走 .tmp+rename，重跑打印「已转换过，未改动」 |
| 126 | 落地 8：测试的期望值来自需求（SKILL.md「证据本身要可信」） | L | 做了 | P5 期望值来自 spec「含 99 元」；P3「期望值按需求手算（10×2 加 20）」；P7「期望值手算得出」 |
| 127 | 落地 9：先独立审完再看别人的评审（code-design.md Review） | L | 做了 | P9：读了 code-design.md；独立找出删掉 Math.max 致负金额（实测 -30），再判同事两条：一条方向对没到位、一条不成立 |
| 128 | 落地 10：算得出来的值不另存一份（code-design.md、fast.md） | L | 做了 | P10F 快改路径：读了 fast.md，新增 count() 遍历 items 现算，没有另存同步字段，测试期望值手算；P10 审查重跑（审查修法后的措辞）：必须处理第一条就点名「能算出来的值另存一份」，建议换 getter。P10S（状态放得比用途宽）：读了 code-design.md，点名「状态放得比用途宽」，实测 lastAdded 让实例多一个键，建议删字段还原成用 sku。首轮 P10：读了 code-design.md；第一条就指出 itemCount「是从 items 算得出来的值，却又被单独存了一份」，用探针实测清空 items 后 itemCount 仍为 5，建议改成计算属性 |
