# Changelog

## 1.7.0

- Talk had borrowed the *nouns* of Matt Pocock's `grilling` without its *verbs*: it said 「前沿清空，即对齐完成」 but never defined a decision tree, never said "recompute the frontier", and set its stop condition to 「真问题一句话且用户确认 / 做什么有轮廓 / 最大未知已标出」 — none of which require the user to speak, so the model declared itself satisfied on round one. The one numeric instruction in the whole file, 「最多三到五轮深挖」, was read as a target rather than a ceiling. This is a variant of the descriptive-vs-imperative trap already in the spec: borrowing a noun without the verbs that produce it.
- Added `references/grilling.md`, carrying all 31 load-bearing behaviours of the upstream pair `grilling` + `domain-modeling` sentence by sentence: build the design tree (kept in the head, not on disk — a persisted tree is a second source of truth); ask the *whole frontier* per round — neither one question at a time nor everything at once; the round template with a title per question, the recommendation on its own line and `---` between questions, since the title is what forces each item onto a decision and the format is what makes a round answerable by number; recompute the frontier from the answers; when a same-round dependency turns up afterwards, *reopen that branch in the next round* and say so; dispatch a subagent for facts and don't block the round on it; decisions are the user's, and answering them yourself means the skill is broken, not liberally interpreted; stop only when the frontier is empty **and** the user confirms a shared understanding. No round or question ceiling; the calibration is "46 questions across 4 rounds is an ordinary session". A four-row table names the false signals (「最大未知已标出」, 「接口未清，标待确认」, 「做什么有轮廓」, 「真问题一句话」) that let a model swap self-statement for asking, plus upstream's two escape hatches: ask one at a time if the user prefers, and stop grilling an ungrillable question to build something to react to.
- Carried over the *other half* of `grill-with-docs`: the `domain-modeling` read side, so terms get challenged against the project's ubiquitous language mid-interview, fuzzy words get sharpened, boundaries get probed with invented concrete scenarios, and a user's claim about how something works gets checked against the code and contradicted on the spot. The **write** side is deliberately not duplicated — ubiquitous language belongs to `spec.md`, the three ADR gates to `SKILL.md` and the decision template; `grilling.md` keeps only the reflex ("catch a resolved term inline, don't batch it to the end") with pointers. One contract, one owner.
- Promoted `grilling.md` to **必读** for 讨论 and 愿景 in the posture table rather than leaving it in 按需读. Upstream's most-reported failure is precisely a session where the skill ran but `grilling` never loaded, so the model improvised an interview: everything at once, no recommendations, no rounds. That is verbatim the symptom reported here, and the on-demand column is exactly the slot that reproduces it.
- `talk.md` is now a wrapper over that primitive, keeping only Talk's increment: no construction plan and no on-disk output until the frontier is empty and the user confirms. Deleted the duplicated stop-condition detail and the round ceiling. Mirrors the upstream split of `grilling` (primitive) from `grill-with-docs` (stateful wrapper).
- Fixed the same disease in two sibling postures: `vision.md` no longer asks "the single most map-changing question" (its frontier is now the map's open decisions — journey ownership, capability boundaries, mutually exclusive directions, naming, priority), and `design.md` no longer lets 「标待确认」 stand in for asking the user when an interface is unclear.
- Wiring: 「提问必须带建议」 points at `grilling.md`; the trigger 「拷问我」 was added to **both** the frontmatter description and the posture table, since routing has two stages (see issue 007); `grilling.md` did *not* get a row in the principle-file table, because it is now a posture 必读 and one contract is not stated in two places.
- Contract sync: README (zh/en) Talk stop-condition now reads "frontier asked out and user confirms" instead of the old 「已能说清最大未知」 false signal; spec/index.md updates the references count 18→19, adds the Grilling term, and records the borrow-nouns-not-verbs variant; posture-scenarios.md adds scenario 25 and lists `grilling` under 应读取 for scenarios 1, 2 and 16, so the eval and the posture table cannot contradict each other.
- Known gap: whether grilling actually produces multi-round interviews can only be falsified by a multi-round subagent eval, and the current harness is single-turn (`task`). Scenario 25 validates the routing wiring, not the interview quality. Tracked as leftover in issue 011.

## 1.6.1

- Closing and graduation are now aligned as part of the commit flow rather than a trailing afterthought. Implementation wrap-up presents the closing recommendation alongside sediment candidates; upon commit authorization, issue renaming (`-o-` → `-x-`), graduation writeback, and code changes are batched into a single commit.
- Removed permissive phrasing in `do.md` that tolerated trailing close decisions after code commits, cutting off the failure mode where pushed code triggers a round of CI and closing triggers a second.
- Cleaned up three stale references to `Agent 指令` in `close.md` that survived the 1.5.0 migration.

## 1.6.0

- Prohibitions now have to earn their attention cost. A "don't do X" is only worth writing when X is a strong model default; forbidding something the model was never going to do both costs context and puts the thing into attention — don't think of an elephant.
- "Don't auto-commit / auto-push / auto-close" was stated seven times, three of them in consecutive rows of one table. It is now stated once, above the table, and the rows carry only what differs. The rule counters a genuine default, so the rule stays; the restatements go.
- "No unbounded whole-repo audit" was forbidden once in each of five files, while the actual model default is the opposite — over-focusing on the current file. Removed from all five. Kept where Review is defined, since users really do say "review the whole repo".
- Collapsed the remaining duplicated prohibitions onto single owners: the Security/Safety distinction to `quality.md`, the no-trace exception's six restatements to its own section.
- Quantified claims written into `byissue/` must carry a way to reproduce them — a command, a file and line, a call sequence. Induction pulled tighter than its sample is the failure mode this catches.

## 1.5.0

- `bi` no longer writes to `AGENTS.md` / `CLAUDE.md` anywhere in the workflow. Knowledge capture has exactly one destination, `byissue/notes/`; the graduation route, the maketools branch and the onboard clause that pointed at agent instruction files are gone. When a rule really does deserve to fire on every startup, bi writes the note and *tells the user* — the user decides and does it.

  The reason is not that such a line is harmful, it is that the user does not know about it. Those files are injected into every session, so one appended line changes how every later session in that project behaves. That should not happen as a side effect of "jot this down"; people discover the changed behaviour weeks later and cannot trace it.

## 1.4.0

- Fixed stage-one routing. Routing has two stages — the host opens the skill by text-matching the frontmatter `description`, and only then does the posture table apply — and only the second was ever guarded. Three postures (设计 / 记知识 / 学流程) had no trigger coverage in the description at all, so they were unreachable in a fresh project. The description now covers all thirteen, the inert conditional trigger ("or when the project already has byissue/") is gone because the host never looks at the filesystem, and the release check now asserts that every posture has at least one trigger in the description.
- The no-trace exception has a single owner in `SKILL.md`, with the load-bearing clause stated positively: **it does not change the posture**. "Do this issue, but leave no trace" stays managed implementation and simply skips the `ff`. Five restatements across fast/do/complain became links — that duplication was mis-routing real requests.
- Closing an issue must now fix inbound references before renaming: `grep` for the old path, update what it finds, and report "N references updated" or "none" in the wrap-up. Path-encoded state and the full-name reference rule pull against each other, so every close was silently breaking references.
- References to issues must use the full filename or directory name; bare numbers are out. Numbers keep colliding by design (parallel sessions both take max+1): measured 14% collisions but only single-digit ambiguous references, so the cheap fix is the reference rule.
- Added `tools/posture-scenarios.md` — 24 routing scenarios evaluated by subagents, not by a script, plus the harness disciplines learned the hard way. Structural checks (posture table well-formed, no trigger claimed twice, every posture covered, no dangling `byissue/` references, anchored links validated) live in `tools/check-skill-repository.py`.

## 1.3.0

- Project Spec now has an admission rule: only what cannot be rebuilt from the code goes in (glossary, boundaries, excluded options, long-term constraints). Capability walkthroughs, architecture maps and data-flow prose are out — they are a second copy of the code and will drift. Graduation at close becomes filtering, not copying. Dry run on a real 311-line spec: 68% of it goes.
- Sediment is now a mandatory enumeration at close instead of a routing table: `close.md` and `fast.md` must list candidates with recommendations, and say "none" when there are none. The question must have a factual answer ("did this hit a fact from outside the repo?") rather than a judgement one.
- New writing-layer contract in `SKILL.md`: every question to the user carries a numbered recommendation and a reason. `talk.md` now links to it instead of restating it.
- Posture is action-scoped: a single authorized action inside a discussion no longer flips the whole session into execution mode. Added as posture rule 9, scoped the "keep going to completion" clause, and gave `talk.md` a "stay here" condition opposite its existing stop condition.
- References to issues must give the full filename or directory name; bare numbers are out. Issue numbers keep colliding by design (parallel sessions both take max+1) — measured 14% collisions but only single-digit ambiguous references, so the cheap fix is the reference rule, not a new numbering scheme.
- Added `tools/posture-scenarios.md` (24 routing scenarios) and folded a posture-table structural check into `tools/check-skill-repository.py`: triggers must be non-empty, no trigger claimed by two postures, every posture covered by a scenario. Semantic routing is evaluated with subagents, documented in the scenario sheet — not by a script.

## 1.2.0

- Removed the `done/` archive leftovers that survived 1.1.0 (`SKILL.md`, `docs.md`, `explore.md`), and stopped `onboard.md` from hand-copying the workspace directory list (it had already drifted — `decisions/` was missing).
- Deleted two unreferenced documents: `asset/programming-paradigm.md` (674 lines; already distilled into `code-design.md`, and still preaching the hard line quotas that `code-design.md` and `AGENTS.md` reject) and `what-is-skills.md` (236 lines; authoring scaffolding, out of ByIssue's declared scope).
- Rewrote `tools/check-skill-repository.py` (254 → 112 lines): dropped the hardcoded 34-file manifest, the Chinese marker greps, the per-file `git check-ignore` subprocesses and the unused `--json` flag. It now verifies that every path the skill points at exists and that every packaged file is reachable — strictly stronger than the manifest, and it no longer has to be edited whenever prose is rewritten.
- Converged duplicated contracts onto single owners: root-cause extrapolation to `debug.md`, structural-decay judgement to `code-design.md`, path/numbering rules to `SKILL.md`. The other files keep their stance-specific increment and link.
- Templates now carry a self-check instead of an empty slot skeleton (372 → 201 lines), matching what `docs.md` already demanded: 「模板是自检，不是槽位」.
- Slimmed `init_byissue.py` (67 → 34 lines); same directories, same `+`/`=` reporting, same `--force` semantics.
- Trimmed `WHY BYISSUE.md` (55 → 32 lines): dropped its stale third copy of the world model (it still said "three core entities", predating Vision and `decisions/`), kept the motivation, the evolution stance and the single-control-plane argument, and sharpened the two "no refactor pipeline / no default audit" claims so they no longer read as contradicting `type: refactor` and the user-invoked Review action.

## 1.1.0

- Rewrote the fast reference as a writing-layer pilot: prohibitions restated positively, duplicated rules removed, naming details trimmed (behavior verified by subagent scenarios).
- Talk mode now batches independent questions into numbered rounds with recommended answers and defers dependent questions (adapted from Matt Pocock's grilling).
- Added `byissue/decisions/` as an addressable graduation target for landmark trade-offs: 1–5 sentence records gated by three conditions (hard to reverse, surprising without context, real alternatives), independent numbering, `superseded-by` instead of deletion.
- State is now fully path-encoded: `-o-` (open), `-x-` (delivered), `-d-` (dropped) — closing records the outcome in the filename; dropped items keep a one-line reason and skip graduation.
- Removed the `done/` archive area: closed files stay in place, retrieval scans paths recursively, numbering rules lose their done/ exception.

## 1.0.0

- First release as ByIssue, an independent project continuing from CodeStable (upstream dormant).
- Single skill `bi` at `skills/bi/`; project workspace lives in `byissue/`, initialized by `init_byissue.py`.
- Install via `npx skills add ByteTrue/ByIssue`. No legacy compatibility or migration logic is carried.
