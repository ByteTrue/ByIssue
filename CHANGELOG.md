# Changelog

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
