# 从 pstack 吸收什么

> 2026-11-09。用户给出 `/Users/zijie/workspace/reference/pstack-claude`，原话：「这个是最近比较火的工作流，看看我们能从中学到什么，吸收什么到我们的工作流中」。按讨论推进的顺序写。

---

## 1. 先定位：两边方向几乎相反

读的范围：路由技能 `poteto-mode`、24 条 principle、主要 playbook（bug-fix、feature、prototype、refactoring、eval、autonomous-run、pause-safely、session-pickup、multi-phase-plan），以及 how、why、reflect、correct、architect、interrogate、blast-radius、show-me-your-work。没细读的：PR 生命周期类 playbook、形式化验证、statechart、各宿主适配代码。

pstack-claude 是 Lauren Tan 的 pstack 的移植版：67 个技能目录（43 个公开技能 + 24 条 principle，见其 `docs/reference.md`），多模型 panel、按角色配模型、PR 流水线、夜间自治。bi 是单入口、制度记忆、压认知负荷，并且明说不是 Agent 编排器。

**结论：** 大部分不该搬。值得拿的是它的两条纪律：让结论带上证据，把反复出现的教训变成会报错的检查。这正好对上 bi 自己认下的三个缺口：retro 的 A 族「写了但不执行」、retro 里没采纳的「回归钉」、`WHY BYISSUE.md` 里「AI 的产出要我审计」。

bi 已经独立做到、不用动的：拷问循环（覆盖了 pstack 对分叉分类的一半）；重要接口设计两遍（= architect 的 design it twice）；现状说明按层展开（≈ how 的输出结构）；修完用同一观察确认（= verify on the same surface）；economy 阶梯（≈ Laziness 与 Subtract Before You Add）；姿态评测「判据是调用序列，不是它自己的说法」（= grade from transcripts, not self-report）；note 的六个月测试（≈ reflect 的 durability 判据）。

## 2. 建议吸收的清单

随技能分发（`skills/bi/`）：

1. **结论带出处。** 来自 poteto-mode 的 Writing the reply、show-me-your-work 的 Attention 段、figure-it-out 的 INCONCLUSIVE。bi 的 `docs.md`「量化判断必须附出处」只管写进 `byissue/` 的数字，对话汇报里没有对应规矩。
2. **同一个坑踩第二次，就变成检查。** 来自 `correct` 与 principle-encode-lessons-in-structure：规则已经写了却没人强制，再犯就是复发，应在最高可行层级修（架构 > 类型 > lint > 测试 > 文档）。bi 的沉淀去向原本全是文字。
3. **修 bug 三条。** 撤回没生效的试修（bug-fix playbook：「might help 的保险代码是假设不是修复，证据推翻假设就回滚它引出的改动」）；共享同一前提的修复连续失败就先验前提（attack-the-premise）；失败检查要红在预测的偏差上（prove-it-works 的「Red is a colour, not a measurement」）。`debug.md` 背景里点名了「猜测残留物」，却没有一句叫 agent 去清理。
4. **跑一下就能看到结果的分叉，自己跑。** 来自 poteto-mode 对分叉的分类与 prototype 的「No decision means no prototype」。bi 的「事实自己先查」只覆盖查得到的事实。
5. **动结构之前先固定现有行为。** 来自 refactoring playbook 第 1 步：编译和 lint 通过不算固定住了。
6. **按下一个 agent 设计。** 来自 architect 的 `design-red-flags.md` 与 `correct`：下一个改代码的 agent 只看得见自己打开的文件、照抄最近的例子，所以从一个文件看起来对的改动，对全仓也要对。

次一档：用户拍板保留原话和适用范围（why 的 epistemics「Claims about human decisions」）；暂不关闭时写接续点（pause-safely）；Review 发现附运行证据，并找出改动安全所依赖的那一个事实（interrogate、blast-radius）。

维护侧（不分发）：评测盲化（pstack 的 Eval playbook：被测 agent 看得见的目录、文件、提示里不出现 eval、test、judge 之类的词）；checker 自测（pstack 用故意做坏的样例目录证明每条检查都会报错）；真实会话复盘的固定做法（reflect 的三视角 + 合成筛子）；规则和强制机制对照表（correct 的规则表）。

## 3. 不吸收的，与理由

- **多模型 panel**（arena、swarm、interrogate、architect 的多 runner）与**按角色配模型**（setup-pstack、`models.json`）：bi 不是 Agent 编排器，多一套配置就多一份认知负担。
- **PR 生命周期**（babysit、shipping、autopilot、orchestrate、fix-ci）：绑定特定宿主和代码托管平台，而 bi 默认不 commit、不 push。
- **「Never block on the human」加频繁 commit**：bi 有意把 commit、push、关闭留给用户；执行类姿态持续推进到完成，`SKILL.md` 姿态判断第 10 条已经写了。
- **每个任务把 playbook 步骤逐字抄进 todolist 并写 `skip:`**：对快改是纯仪式；bi 在关键环节已经要求显式写「无」。
- **把 24 条 principle 拆成独立技能**：内容和 economy、code-design、debug、domain-modeling 大面积重叠，拆开违背单入口。（「大面积重叠」是类别结论，没有逐条核对。逐条裁定见 `byissue/epics/2026-11-09-x-pstack-item-verdicts/`。）
- **unslop、deslop、no-comments**：英文文风规则；代码精简已有 ponytail。（同日续谈推翻了这条：bi 不能假设 ponytail 已安装，这条理由违反 `byissue/spec/index.md` 的形态约束。三项在 1.12.0 吸收进 `skills/bi/references/economy.md`「交付前清理自己的 diff」和 `skills/bi/references/writing.md`，以那次为准，见 `byissue/talks/2026-11-09-bi-v2-rejected-what-carries-over.md` 第 6 节。）
- **TSV 决策日志 + transcript 审计 + 异模型复核**：issue 的执行记录已经起这个作用；只取 Attention 段的思路，并入第 1 条。
- **SessionStart 路由 hook、项目级 playbook 扩展**：bi 经 `npx skills` 分发，没有 hook 机制，也不写 `AGENTS.md`；项目定制本来就由 `AGENTS.md` 优先。

## 4. 用户裁决

**已确认：** 用户全选。随技能分发的四组：1–2 证据与审计、3 修 bug 纪律、4–5 自己跑与先固定行为、6 与次一档。维护侧四项：评测盲化、checker 自测、真实会话复盘、规则和强制机制对照表。推进方式选「直接改，打成一个版本」（选项原文：改完跑 checker 和对抗审查，提交前停下给你看；这份对照顺带存成 talk）。

## 5. 落地时多出来的发现

- **第 2 条不是 1.9.2 否掉的「回归钉台账」。** 当时的否决理由是它和技能零依赖冲突。这次不建台账、不往技能里加任何东西，只把「同一个坑踩第二次」的沉淀候选首选去向改成项目自己的测试、类型、lint 或脚本；项目没有检查入口就退回文字。触发条件挂在每次都会做的查重上，问的是事实问题（以前记过吗），不是判断题。
- **`tools/fixtures/state-letter-probe.sh` 的臂目录名会泄露答案。** 被测 agent 的工作目录就是 `w-violation/`、`o-control/` 这类名字，等于提示它「这里有违规」「这是对照组」。这是推断，没查历史日志确认它是否被利用过。已改成中性的 `host-a` 到 `host-e`，脚本把对应关系打印给父会话。
- **checker 的「本仓专属文件」名单是手工维护的。** 新增 tools 文件就会过期，正是第 6 条说的「要手工同步的清单」。已改为从 `tools/` 派生，并用自测里的一个用例证明新文件不改 checker 也会被覆盖。
- **发布链路和 `tools/posture-scenarios.md` 对「何时跑姿态评测」说法不一。** 而且链路里 rsync 排在评测之后，可评测加载的是部署副本。已统一并调整顺序。

## 6. 出口

**已执行：** 1.11.0，改动清单见 `CHANGELOG.md` 同名小节。

**对抗审查：** 一轮，判定「修掉发现后可以分发」。三条 P1 都是新句子的契约缺口：撤回试修会连用户没提交的改动一起撤掉；「按下一个 agent 设计」没有绑在本次改动上；「实测」和「推断」的定义重叠。另有三条 P2，以及盲化副本里留着往轮的答案表。全部按审查给的修法改了，细节见 `CHANGELOG.md` 1.11.0。

**行为探针（实测，夹具在 `/tmp/ledger-svc`、`/tmp/notes-app`、`/tmp/shop-cart`）：**

- **审 diff**（说法「bi 看看这个 diff 有没有问题」）：读了 `SKILL.md` → `code-design.md`，没读 do、fast。发现都标了实测，探针脚本写在项目外，结束时工作区没变。
- **快改文案**：不带 bi 的对照组没跑测试，而且明说了「没有运行测试」。带 bi 的跑了测试，标了「验证（实测）」，末尾写了「需要你看的：无」，也留了 ff 记录。
- **修 bug，同文件里有用户没提交的草稿**：用户的草稿逐字保留。修前修后用同一条命令对照，结果从 10000 变成 9000。新测试放到旧代码上跑会失败，它也引用了失败内容（`10000 != 9000`）。对照组同样保留了草稿（它做的是局部编辑）。「撤回试修」这条路径这次没走到，因为第一次修复就生效了。
- **路由**：本机的 bi 经 magpie 索引加载，要绕一层。只有一句话时子 agent 没有一次打开 bi（0/3）；句首加上「bi」后打开了 1/3，有一次它把「bi」当成了打字错误。后两组探针是在 task 里直接给出 bi 的 `SKILL.md` 路径才跑成的。环境事实与对策见 `byissue/notes/2026-11-09-bi-behind-magpie-index-is-rarely-opened.md`。

**仍开放：** 姿态场景表没有整表重跑，要先解决上面的路由环境问题。「撤回试修」「先验证共同前提」「先钉住行为」「跑得出来的问题自己跑」这几条还没有行为证据。新规则里「模型默认会这样做」的判断（叠加试修、把推断说成实测、拿编译通过当行为不变、跑得出来的问题拿去问用户）都是推断，没有行为评测。要拿到证据，需要搭会诱发这些默认的夹具：一个第一次合理试修不生效的 bug；一个只跑相邻测试就容易报「已修复」的改动。

**暂不纳入：** 见第 3 节。
