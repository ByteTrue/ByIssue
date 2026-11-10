#!/usr/bin/env python3
"""Fixture tests for the two scripts skills/bi/ ships into users' projects.

check_open_issues.py and init_byissue.py run in projects this repo never sees, so a bug
surfaces there first: the duplicate-state-letter case shipped and listed seven false open
items in a user project before 1.13.1 caught it. Each case builds a byissue/ tree in a temp
dir, runs the packaged script, and checks its exit code and output.

Usage: python3 tools/check-skill-scripts.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills/bi/scripts"
TEMPLATES = ROOT / "skills/bi/templates/entities"


def tree(root: Path, *paths: str) -> None:
    """Create files (or directories, for paths ending in /) under root."""
    for rel in paths:
        target = root / rel
        if rel.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# x\n", encoding="utf-8")


def run(script: str, project: Path, *args: str) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), "--project", str(project), *args],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def open_issues_cases(base: Path):
    p = base / "none"
    p.mkdir()
    code, out = run("check_open_issues.py", p)
    yield "no byissue/ passes", code == 0 and "未找到 byissue/" in out, out

    p = base / "quiet"
    tree(p, "byissue/issues/2026-01-01-x-done.md", "byissue/issues/2026-01-02-o-ff-tweak.md",
         "byissue/issues/2026-01-05-w-dropped.md", "byissue/epics/2026-01-03-o-big/spec.md")
    code, out = run("check_open_issues.py", p)
    yield ("delivered and dropped items, an open ff and an open epic pass; the ff is a reminder, the rest unlisted",
           code == 0 and "2026-01-02-o-ff-tweak" in out
           and not any(n in out for n in ("2026-01-03-o-big", "2026-01-05-w-dropped", "2026-01-01-x-done")), out)

    p = base / "open"
    tree(p, "byissue/issues/2026-01-01-o-login.md", "byissue/issues/2026-01-02-o-explore-auth/index.md",
         "byissue/epics/2026-01-03-o-big/issues/2026-01-04-o-api.md")
    code, out = run("check_open_issues.py", p)
    yield ("open issues in the root tree, an Explore directory and an epic tree all gate",
           code == 1 and all(n in out for n in ("o-login", "o-explore-auth", "o-api")), out)

    # Real mistake: a close that copied instead of renamed (fixed in 1.13.1).
    p = base / "dup"
    tree(p, "byissue/issues/2026-01-01-o-login.md", "byissue/issues/2026-01-01-x-login.md",
         "byissue/issues/2026-01-02-o-other.md")
    code, out = run("check_open_issues.py", p)
    yield ("an issue under -o- and -x- is reported alone, without the open list",
           code == 1 and "多个状态" in out and "o-other" not in out, out)

    p = base / "dup-w"
    tree(p, "byissue/issues/2026-01-01-o-login.md", "byissue/issues/2026-01-01-w-login.md")
    code, out = run("check_open_issues.py", p)
    yield "an issue under -o- and -w- is reported", code == 1 and "多个状态" in out and "w-login" in out, out

    p = base / "dup-epic"
    tree(p, "byissue/epics/2026-01-03-o-big/spec.md", "byissue/epics/2026-01-03-x-big/spec.md")
    code, out = run("check_open_issues.py", p)
    yield "an epic directory under -o- and -x- is reported", code == 1 and "o-big" in out and "x-big" in out, out


def init_cases(base: Path):
    p = base / "init"
    p.mkdir()
    code, out = run("init_byissue.py", p)
    dirs = ["talks", "vision", "spec", "issues", "epics", "notes", "decisions", "tools"]
    spec, vision = p / "byissue/spec/index.md", p / "byissue/vision/index.md"
    same = lambda path, template: path.is_file() and path.read_text(encoding="utf-8") == (TEMPLATES / template).read_text(encoding="utf-8")
    fresh = (code == 0 and all((p / "byissue" / d).is_dir() for d in dirs)
             and same(spec, "project-spec-index.md") and same(vision, "vision-index.md"))
    yield "fresh init creates every directory and both indexes from the templates", fresh, out

    spec.write_text("# 用户写过的 spec\n", encoding="utf-8")
    vision.write_text("# 用户写过的 vision\n", encoding="utf-8")
    code, out = run("init_byissue.py", p)
    yield ("rerun keeps both indexes the user edited", code == 0 and spec.read_text(encoding="utf-8") == "# 用户写过的 spec\n"
           and vision.read_text(encoding="utf-8") == "# 用户写过的 vision\n", out)

    code, out = run("init_byissue.py", p, "--force")
    yield "--force rewrites both from the templates", code == 0 and same(spec, "project-spec-index.md") and same(vision, "vision-index.md"), out


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for cases in (open_issues_cases, init_cases):
            for name, ok, out in cases(base):
                print(f"{'ok  ' if ok else 'FAIL'} {name}")
                if not ok:
                    failures += 1
                    print("     " + out.replace("\n", "\n     "))
    print(f"{'all' if not failures else failures} script case{'s' if failures != 1 else ''} {'pass' if not failures else 'failed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
