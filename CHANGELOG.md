# Changelog

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
