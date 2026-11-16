# ByIssue → ByWork 改名清单

状态：实施中（新仓库方案）。决定：用户于 2026-11-17 拍板 ByWork（m03010）；理由：只有 byspace 一个消费者，现在是迁移成本最低点；评测结论证明方法论，路径字面量改名不使其失效。随后（m03385/m03388）改为新建独立仓库 ByteTrue/ByWork，main 即当前 v2 全量；ByIssue 原地保留作研发档案（v1+v2 历史与评测证据），不改名、不回退工作树。内容层改名（skills/bw、bywork/、checker、文档）两种方案复用，已完成并全绿。

## 命名决定

| 项 | 旧 | 新 |
|---|---|---|
| 产品全名 | ByIssue | ByWork |
| 技能 ID / 触发词 | `bi` | `bw`（description 触发列表保留「bi、ByIssue」作旧称别名） |
| 分发包目录 | `skills/bi/` | `skills/bw/` |
| 用户项目工作目录 | `byissue/` | `bywork/` |
| 初始化脚本 | `scripts/init_byissue.py` | `scripts/init_bywork.py` |
| 自举软链接 | `.agents/skills/bi → ../../skills/bi` | `.agents/skills/bw → ../../skills/bw` |
| 版本 | 2.2.0 | 3.0.0（路径是公开契约，破坏性变更） |
| GitHub 仓库 | ByteTrue/ByIssue（保留作研发档案） | 新建独立 ByteTrue/ByWork，main 即当前 v2 全量；旧仓不改名 |

历史文档（CHANGELOG 旧节、已完成 work、台账、memory 依据条）中的 ByIssue/byissue 字样**保留不改**——它们是历史事实记录。只改当前契约与活引用。

## 触及面（已实测）

### ByIssue 仓库

1. **分发包**（10 文件 41 处）：SKILL.md 10、onboard.md 4、memory-direction.md 4、init_bywork.py 4、check_work.py 4、domain-modeling.md 3、change.md 2、agents/openai.yaml 2、quality.md 1、writing.md 1。`git mv skills/bi skills/bw` + `git mv` 脚本 + 字面替换；SKILL.md `name: bi`→`bw`，description 加旧称别名。
2. **维护侧 checker**：check-skill-repository.py（SKILL 路径、ENTRY_FILES、`found != ["bi"]`、REPO_PREFIX `bywork/(work|memory|vision)`、隐藏目录注释）、check-skill-scripts.py（SCRIPT 路径 + 夹具断言）、release-check.sh（如有字面）。
3. **评测**：prepare_rebuild.py:52-53（删 `bywork/`）、test_runner.py:127,139,175-176,188（历史路径引用与 v1 目录夹具）、cases/memory-selection/acceptance.py:7-8、tools/evaluation/README.md。**冻结快照（v2-delivery-input-v5/v6、nobi、heldout-v2、candidate-*）不改**——历史运行按当时契约判定，重跑旧快照需旧技能，属预期。
4. **仓库文档**：README.md 13、README.en.md 12、AGENTS.md 4；CHANGELOG 只加 3.0.0 新节，旧节 47 处保留。
5. **本仓 byissue/ → bywork/**：`git mv byissue bywork`；活文档（memory 结论段、in_progress work、v2-delivery index 的当前契约表述）内路径改道；已完成 work 与台账里的历史路径叙述保留。checker 的「历史 work 断链」规则需核对：改道后旧路径引用是否被判死链——历史 work 中的 `bywork/...` 引用要么按历史记录豁免，要么统一改道（实施时以 checker 实跑结果定，倾向统一改道保链接可达，文字叙述保留旧名）。
6. **VERSION** 3.0.0；skills-lock.json 重新生成；`.agents/skills/` 软链接重建。

### byspace 仓库（39 个非 archive 文件）

1. `git mv byissue bywork`（memory 17 + work + vision + archive 整体移动，内部相对链接深度不变）。
2. 活引用改道：docs×7、design/references/shadcn/README.md、internal/hostsync/document.go、packages/protocol/src/messages.ts、web×3（含 language-cut.test.ts）、screenshots/_脚本/b5-schedules.js、bywork/memory 内的跨文件引用。
3. **archive/v1 内 171 个文件不改**——冻结历史，README 已声明不随 v2 工作改动；其中的 `bywork/` 字样是 v1 时代事实。
4. 守卫复跑：docs-links、audit:ledger、parity-surface、typecheck、lint、format、go test ./internal/hostsync/（GOROOT 用 /opt/homebrew/opt/go/libexec）。
5. byspace 的 `.agents/skills/` 无 bi，无需动；全局 `~/.agents/skills/bw` 由用户经宿主安装器处理，本次不碰。

## 实施顺序

1. ByIssue：分发包+checker+评测+文档改名 → release-check --no-deploy 全绿 → check_work.py 4/4 → 评测运行器 14 测试（历史路径夹具同步改）。
2. 本仓 `git mv byissue bywork` + 活引用改道 → checker 再跑（含断链检查）。
3. byspace：git mv + 改道 → 全部守卫复跑 → 与用户自己的 .gitignore/Makefile 在途改动隔离。
4. CHANGELOG 3.0.0 节写明迁移步骤（用户项目 `git mv byissue bywork` + 引用改道；技能重装为 bw）。
5. 新建 GitHub 仓库 ByteTrue/ByWork（public，main 即当前 v2 全量快照）；本地 remote 指向新仓。ByIssue 仓库保留作研发档案，不改名（外部副作用，随提交推送一并请求授权）。
6. 提交推送：ByWork 推 main、byspace 推 main（待授权）。

## 验证方式

- release-check 全绿；check_work 两仓各自通过；byspace 守卫全绿与迁移会话基线一致（audit:ledger MISSING 0）。
- 新会话冒烟：在 byspace 用 `bw` 触发技能，确认加载 skills/bw 且 init 幂等（bywork/ 已存在时保留）。
- 评测不重跑大型任务：改名是字面契约变更，无行为规则改动；运行器单测覆盖路径逻辑即可。

## 风险与代价

- 旧称别名期：用户肌肉记忆 `bi` 仍可触发（description 别名），但技能目录/脚本名已变，外部若有硬编码 `skills/bw` 路径会断——已知消费者仅本仓与 byspace，均在本次改道。
- 冻结评测快照与新技能不再互通：属预期，历史证据按当时契约读。
- 历史文档保留旧名可能造成新读者困惑：CHANGELOG 3.0.0 节首行写明「ByIssue 即本技能旧称」。