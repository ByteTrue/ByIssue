# 候选：五个单元的 [候选] 与 [已有·部分] 缺的那块，去重后

> **读者：** 要裁决「学哪几条」的用户，以及落地时的 agent。每条的 pstack 原文和 ByIssue 证据的 `文件:行` 在 `verdicts/M<n>.md` 的「候选汇总」与「父会话核对」里，这里只写结论和推荐。

推荐的取舍标准：能不能指到 ByIssue 真发生过的一次失败；落地是标准库 Python 或 shell 的几十行，还是要引入新东西；和现有契约有没有冲突。全部落在维护侧（`tools/`、`byissue/spec/index.md`），不动 `skills/bi/` 的就不升 `VERSION`。

## 推荐学（8 条）

| # | 内容 | 来源 | 落点 | 挡住的真实失败 |
|---|---|---|---|---|
| 1 | **全仓路径可达。** checker 把链接与反引号路径的检查从 `skills/bi/` 和 `byissue/` 五类目录扩到全仓 Markdown（`tools/…`、`byissue/spec/…`、README、AGENTS、CHANGELOG），指向不存在的文件就报错 | validate-skills.mjs、ci.yml links 与 markdownlint job | `check-skill-repository.py` + selftest | 发布链路曾让人去跑一个早已删掉的脚本，checker 全绿（issue 009:14）；本次实跑又找到两条解析不到的链接 |
| 2 | **修过的静默漏检各钉一个 selftest 坏样例。** 以后 checker 每修一次漏检，同时在 selftest 加一条会让旧版漏掉的坏样例；先补 009 的带锚点链接 | WatchPoll / PiScheduler 的 mutations | `check-skill-repository-selftest.py` | `LINK_RE` 让带锚点的链接整条不校验也不报错（issue 009:15）；`retro-failure-modes.md:99` 记着这类教训只落成了文档 |
| 3 | **CHANGELOG 版本闸门，顺手修过期数字。** 第一个版本标题必须等于 `VERSION`，同一版本号不能出现两节；`spec/index.md` 里「references 下 20 篇」改成实际数 | generate.mjs release gate、readme-facts.test | checker + `spec/index.md` | 「20 篇」实际 22 篇，没人发现；版本闸门本身是预防性的，和这条一起做只多十行 |
| 4 | **文档里的命令原样跑。** 从 `close.md` 抽出改名修引用的那条命令，不经模型直接对 `close-reference-repair.sh` 夹具跑，断言命中的正好是该改的那几处 | shipping-git.test（从 merge-safety.md 抽 sh 块执行） | 新 `tools/` 自测脚本，复用现有夹具 | 这条命令重写九轮才稳住，三次写出不存在的路径（`CHANGELOG.md:120-121`）；现在改它没有任何东西会红 |
| 5 | **分发的技能脚本有夹具测试。** `check_open_issues.py`、`init_byissue.py` 各有一个造好的 `byissue/` 夹具和期望输出 | check-plan / check-sheet / check-playbooks 等技能脚本单测 | 新 `tools/` 自测脚本 | 重复状态字母缺陷到用户项目里才暴露，列出 7 条假待办（`CHANGELOG.md:49`） |
| 6 | **行为评测夹具先自证前提，判分不让「没跑」冒充「通过」。** `posture_table.py` 建完每个夹具先断言它真造出了要测的东西；`posture_judge.py` 有失败就非零退出，没有会话日志记「未跑」 | fake-pi.test、live.test 的 `PSTACK_PI_REQUIRE_*` | `tools/fixtures/` | 夹具缺目标物让两批评测作废（`posture-scenarios.md:14`，DeepSeek 笔记场景 30）；judge 现在永远退出 0 |
| 7 | **A/B 删句判据。** 改了一句会改变动作的话，用同一低价模型两臂各跑几次；两臂行为相同就删掉这句，跑不到生效路径的标「未验证」 | CHANGES.md 0.9.128 等（10 个真实会话行为全同，删句） | `tools/posture-scenarios.md` | 已在 1.13.2 做过一次（删 B1），但判据没写下来；`retro-failure-modes.md` 的 A 族「写了但不执行」占比最高 |
| 8 | **一条发布前检查脚本。** 依次跑 checker、selftest、新增的 #4 #5 自测，再 `diff -rq` 源头和部署副本，任何一步失败就非零退出；把 `spec/index.md`「谁在挡这些规则」里 rsync 那行的「无」换成它 | .pre-commit-config.yaml、ci.yml skills-only job | 新 `tools/release-check.sh` + `spec/index.md` | 装机副本落后仓库一版发生过两次（issue 015:17、016:15） |

## 需要你定（1 条）

| 内容 | 来源 | 说明 |
|---|---|---|
| 仓库根补 `LICENSE`，给分发包里的上游镜像写归属 | NOTICE.md、LICENSE | README 写 MIT（`README.md:14,218`），仓库根却没有 LICENSE 文件；`grilling.md` 是 `mattpocock/skills` 的逐字节镜像，归属只写在维护者文档里。版权人怎么写（原作者 CodeStable 与 fork 维护者）只有你能定 |

## 补单元 M6 后追加

| 内容 | 来源 | 结论 |
|---|---|---|
| 台账形态检查脚本（表头、状态取值、「做了」行带证据、没做完时有接续点） | `check-plan.mjs` | 用户 2026-11-10 在「不学，等台账在真实项目里用过再看」上确认：台账还没在用户项目里用过，本仓两份台账形态漂了但没判错过一行，它也挡不住假的「做了」。记在 `byissue/spec/index.md`「当前没有的东西」 |

## 推荐不学（4 条）

| 内容 | 来源 | 理由 |
|---|---|---|
| 给上游逐字节镜像钉哈希 | slash.test | 预防性，没有出过手改镜像的事故；且拿不到上游，只能挡手改 |
| `.gitattributes` 统一换行 | .gitattributes | 没有 Windows 贡献者，也没有 CRLF 事故 |
| 文档里裸写的文件名必须对上包内文件 | skill-references.test | 今天跑零命中；挡不住历史上那次 `done/` 残留（那是目录名） |
| 版本标题与 frontmatter 声明值逐项一致（name 等于目录名、description 长度） | generate.mjs | 没有历史失败；版本闸门已并入第 3 条 |
