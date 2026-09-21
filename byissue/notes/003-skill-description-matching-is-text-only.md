# 技能 description 的条件式触发是无效的

> **读者：** 要写或改 skill `description` 的人——别在里面写「当项目存在某文件时」这类条件。

**结论：** 宿主用 `description` **纯文本**匹配来决定要不要打开一个技能。它不会去看文件系统、不会检查 git 状态、也不会执行任何判断。所以「或项目已有 `byissue/` 且正在处理愿景、规格、bug……」这种**条件式触发子句等于没写**——它只是给匹配器多了几个无关词。

**何时用：** 写 skill frontmatter 的 `description`、或排查「技能为什么没触发」时。

**证据：** 2026-09-21 的路由评测，场景 ⑤「顺手把 tools/ 下的脚本也整理一下吧」跑在**已经有 `byissue/` 目录**的 ByIssue 仓库里（`cwd` 就是它），子会话系统提示里确实注入了 `bi` 的完整 description，技能仍然全程没被打开。子会话日志：`~/.pi/agent/sessions/--Users-zijie-workspace-projects-ByIssue--/2026-09-21T09-29-54-471Z_sub_0d358810448c.jsonl`。

**怎么办：** 触发条件只能是**用户可能说出口的词**。想表达「这个项目在用 ByIssue」，唯一有效的办法是让用户说出 `bi`／`ByIssue`，或在项目的 `AGENTS.md` 里写一行启动规则（那个是每次都会注入的）。

**相关：** `byissue/issues/007-x-description-and-posture-table-are-two-trigger-sets.md`。

## 补充：有一类说法 description 根本救不了

2026-09-21 第二轮评测：把姿态表的高频触发词补进 description 后，「小改一下，别走流程」和「顺手把 tools/ 整理一下」都恢复了正常路由，但「**加个字段就行，很简单**」仍然迟到——因为这句话里**一个流程词汇都没有**，它是纯需求陈述。

没有任何合理的 description 能覆盖这类说法（穷举需求句式等于把 description 写成词典）。

理论上唯一的出路是往项目 `AGENTS.md` 写一行启动规则——它每次会话都注入，不依赖匹配。**这条路已被明确否决**，见 `byissue/decisions/007-bi-does-not-write-itself-into-agents-md.md`：技能不为自己的可触发性去写用户的宿主文件。

所以这一类说法的实际表现是**开得晚，不是进不来**：两轮评测里技能分别在第 6 和第 9 个调用才被读到，期间 agent 已经自由探索了好几步。真正「从没打开」的是第一轮的「小改一下，别走流程」和「顺手把 tools/ 整理一下」，那两条属于 description 漏词，已修好。

迟到是**接受的边界**：用户想让它早点进来就自己说一声 `bi`。不要再为它开事项，也不要把它记成「技能不会被打开」。
