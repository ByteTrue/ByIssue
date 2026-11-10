#!/usr/bin/env python3
"""Run the reference-repair search command exactly as close.md writes it, without a model.

close.md tells the agent to search for an item's old full name before renaming it. That
command was rewritten nine times before it stopped missing references or catching .git. This
script takes every `grep -rnF ...` span in close.md, checks they all use the same flags, runs
the first one against the fixture from tools/fixtures/close-reference-repair.sh, and compares
the hits with the lines the fixture planted. It then drops --exclude-dir=.git from the command
and expects the comparison to fail, so the check is shown able to go red.

Usage: python3 tools/check-close-reference-command.py
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOSE = ROOT / "skills/bi/references/close.md"
FIXTURE = ROOT / "tools/fixtures/close-reference-repair.sh"
NAME = "2026-10-13-o-login"  # the item the fixture closes

# Every line the fixture writes the name into, outside .git. Noise directories are hits too:
# grep reads them, and close.md has the agent judge them, not the command skip them.
EXPECTED = {
    "./byissue/spec/index.md:5", "./byissue/spec/index.md:6", "./byissue/spec/index.md:7",
    "./byissue/spec/index.md:8", "./byissue/spec/index.md:9", "./byissue/spec/index.md:10",
    "./byissue/notes/n.md:1",
    "./node_modules/pkg/dist.js:1", "./dist/site.html:1", "./.venv/lib/cache.txt:1",
}


def commands() -> list[str]:
    spans = re.findall(r"`(grep [^`]*)`", CLOSE.read_text(encoding="utf-8"))
    if not spans:
        raise SystemExit("FAIL close.md has no `grep ...` command in backticks to check")
    return spans


def placeholder(span: str, value: str) -> str:
    """Replace the quoted search string, in double or single quotes."""
    return re.sub(r'"[^"]*"|\'[^\']*\'', value, span)


def hits(command: str, cwd: Path) -> set[str]:
    out = subprocess.run(["sh", "-c", command], cwd=cwd, capture_output=True, text=True).stdout
    return {":".join(line.split(":", 2)[:2]) for line in out.splitlines() if line}


def main() -> int:
    spans = commands()
    flags = {placeholder(span, '"…"') for span in spans}
    failed = False
    if len(flags) != 1:
        print(f"FAIL close.md writes the search command {len(flags)} different ways: {sorted(flags)}")
        failed = True
    # Item names have no regex metacharacters today, so the fixture cannot tell -F apart; require
    # the flags by name instead: -F keeps a future name with "." from matching neighbours.
    for span in spans:
        short = "".join(tok[1:] for tok in span.split() if re.fullmatch(r"-[A-Za-z]+", tok))
        missing = [f for f in ("r", "n", "F") if f not in short] + ([] if "--exclude-dir=.git" in span else ["--exclude-dir=.git"])
        if missing:
            print(f"FAIL {span} lacks {missing}")
            failed = True
    command = placeholder(spans[0], f'"{NAME}"')
    with tempfile.TemporaryDirectory() as tmp:
        fixture = Path(tmp) / "webapp"
        subprocess.run(["bash", str(FIXTURE), str(fixture)], check=True, capture_output=True)
        got = hits(command, fixture)
        if got != EXPECTED:
            print(f"FAIL {command}\n  missing: {sorted(EXPECTED - got)}\n  extra:   {sorted(got - EXPECTED)}")
            failed = True
        else:
            print(f"ok   {command} finds exactly the {len(EXPECTED)} planted lines")
        mutant = command.replace(" --exclude-dir=.git", "")
        if mutant == command or hits(mutant, fixture) == EXPECTED:
            print("FAIL the check cannot tell a command without --exclude-dir=.git apart")
            failed = True
        else:
            print("ok   dropping --exclude-dir=.git is caught")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
