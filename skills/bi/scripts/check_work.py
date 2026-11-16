#!/usr/bin/env python3
"""Check every byissue/work/*/index.md against the contract SKILL.md states in prose.

Run it before declaring a work complete: exit code 0 means every checkpoint file is
consistent, non-zero prints one line per problem. Prose rules are reminders; this is
the gate that actually refuses the four illegal-status mistakes recorded in CHANGELOG.
"""
from __future__ import annotations

import argparse
from pathlib import Path

FIELDS = ("kind", "status", "current_unit", "next_action", "must_hold", "proof_gap")
STATUSES = ("in_progress", "blocked", "complete")
# A row still awaiting evidence contradicts `complete` with an empty proof_gap.
UNRESOLVED = ("待跑", "无法判定", "未通过")


def unresolved_verdicts(lines: list[str]) -> list[str]:
    """Return the verdicts of proof-table rows that are not yet `通过`.

    Only the final cell of a row is its verdict. The evidence column legitimately
    quotes what the checked subject did (`业务未通过`), so scanning the whole row
    would report a finished evaluation work as unfinished.
    """
    found = []
    for raw in lines:
        line = raw.strip()
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        verdict = cells[-1] if cells else ""
        if any(marker in verdict for marker in UNRESOLVED):
            found.append(verdict)
    return found


def parse_frontmatter(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """Read the leading `---` block. Values are single-line, optionally quoted."""
    problems: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, ["no frontmatter block: the file must start with ---"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["frontmatter is never closed by a second ---"]
    fields: dict[str, str] = {}
    for raw in lines[1:end]:
        if not raw.strip():
            problems.append("blank line inside the frontmatter block")
            continue
        key, sep, value = raw.partition(":")
        if not sep:
            problems.append(f"frontmatter line is not `key: value`: {raw.strip()[:60]}")
            continue
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key in fields:
            problems.append(f"duplicate frontmatter field: {key}")
        fields[key] = value
    return fields, problems


def check(index: Path) -> list[str]:
    text = index.read_text(encoding="utf-8")
    lines = text.splitlines()
    fields, problems = parse_frontmatter(lines)
    for name in FIELDS:
        if name not in fields:
            problems.append(f"frontmatter is missing `{name}`")
    status = fields.get("status", "")
    if "status" in fields and status not in STATUSES:
        problems.append(f"status: {status!r} is not one of {'/'.join(STATUSES)}")
    gap = fields.get("proof_gap")
    if status == "complete":
        if gap is None:
            pass  # already reported as missing
        elif gap != "":
            problems.append(f"status is complete but proof_gap is not empty: {gap[:60]!r}")
        else:
            for verdict in unresolved_verdicts(lines):
                problems.append(f"status is complete but a proof row is still {verdict[:20]!r}")
                break
    if not any(
        line.strip().startswith("|")
        and [c.strip() for c in line.strip().strip("|").split("|")][:1] == ["行为路径"]
        for line in lines
    ):
        problems.append("no behavior proof table (expected a `| 行为路径 |` header row)")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate byissue/work/*/index.md checkpoints.")
    parser.add_argument("--project", default=".", help="Project root containing byissue/.")
    args = parser.parse_args()

    work = Path(args.project).resolve() / "byissue" / "work"
    if not work.is_dir():
        print(f"nothing to check: {work} does not exist")
        return 0
    indexes = sorted(p for p in work.glob("*/index.md") if p.is_file())
    if not indexes:
        print(f"nothing to check: no work entry under {work}")
        return 0

    failed = 0
    for index in indexes:
        problems = check(index)
        name = index.parent.name
        if problems:
            failed += 1
            for problem in problems:
                print(f"FAIL {name}: {problem}")
        else:
            print(f"ok   {name}")
    print(f"{len(indexes) - failed}/{len(indexes)} work entries consistent")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
