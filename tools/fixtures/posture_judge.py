#!/usr/bin/env python3
"""Score a posture_table.py run from the children's session logs and the fixtures' git state.

Usage: python3 tools/fixtures/posture_judge.py /tmp/shop-plan.json

Reads are taken from tool-call arguments, never from log text: SKILL.md's own links would
otherwise count as reads. Expected reads that never happened and forbidden reads that did are
printed per scenario, with the model the child actually ran on. Behavior assertions (the
plan's check column) still need a look at the fixture; this script only prints its git state.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REFS = sorted(p.stem for p in (Path(__file__).resolve().parents[2] / "skills/bi/references").glob("*.md"))
SESSIONS = Path.home() / ".pi/agent/sessions"


def session_log(d: str) -> Path | None:
    key = "--" + os.path.realpath(d).strip("/").replace("/", "-") + "--"
    logs = sorted((SESSIONS / key).glob("*.jsonl"))
    return logs[-1] if logs else None


def reads_and_models(log: Path) -> tuple[set[str], set[str]]:
    reads, models = set(), set()
    for line in log.open(encoding="utf-8"):
        m = json.loads(line).get("message") or {}
        if m.get("role") != "assistant":
            continue
        if m.get("model"):
            models.add(m["model"])
        for c in m.get("content", []):
            if c.get("type") != "toolCall":
                continue
            args = json.dumps(c.get("arguments") or {}, ensure_ascii=False)
            if "references" not in args:
                continue
            for name in REFS:
                if re.search(rf'[/"\'+]{re.escape(name)}\.md', args):
                    reads.add(name)
    return reads, models


def git_state(d: str) -> str:
    def run(*a):
        r = subprocess.run(["git", "-C", d, *a], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "?"
    commits = run("rev-list", "--count", "HEAD")
    dirty = len([l for l in run("status", "--porcelain", "-uall").splitlines() if l.strip()])
    return f"commits={commits} dirty={dirty}"


def main() -> None:
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    bad = 0
    for e in plan:
        log = session_log(e["dir"])
        if not log:
            print(f"[{e['id']:>12}] {Path(e['dir']).name}: no session log")
            bad += 1
            continue
        reads, models = reads_and_models(log)
        missing = [r for r in e["expect"] if r not in reads]
        hit = [r for r in e["forbid"] if r in reads]
        ok = not missing and not hit
        bad += not ok
        print(f"[{e['id']:>12}] {Path(e['dir']).name} {'ok ' if ok else 'BAD'} "
              f"model={','.join(sorted(models))} reads={','.join(sorted(reads)) or '-'} "
              f"{'missing=' + ','.join(missing) + ' ' if missing else ''}{'forbidden=' + ','.join(hit) + ' ' if hit else ''}"
              f"{git_state(e['dir'])}\n{'':>15}check: {e['check']}")
    print(f"\nrouting: {len(plan) - bad}/{len(plan)} clean")


if __name__ == "__main__":
    main()
