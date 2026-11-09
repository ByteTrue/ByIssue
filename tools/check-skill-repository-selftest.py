#!/usr/bin/env python3
"""Prove every check in check-skill-repository.py can actually fail.

Each case copies the repository to a temp dir, plants one known-bad change,
runs the copied checker, and expects its message. Two cases replay mistakes
this repo really made (a scenario typo, a reference left pointing at a closed
item's old -o- name). A check that cannot go red here guards nothing.

Run after any change to tools/check-skill-repository.py.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECKER = "tools/check-skill-repository.py"


def edit(rel, old, new):
    def apply(root: Path):
        path = root / rel
        text = path.read_text(encoding="utf-8")
        assert old in text, f"{rel}: fixture anchor not found: {old!r}"
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return apply


def append(rel, line):
    def apply(root: Path):
        with (root / rel).open("a", encoding="utf-8") as handle:
            handle.write(f"\n{line}\n")
    return apply


def write(rel, text):
    def apply(root: Path):
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return apply


def delete(rel):
    return lambda root: (root / rel).unlink()


def both(*steps):
    def apply(root: Path):
        for step in steps:
            step(root)
    return apply


def unbold_posture_rows(root: Path):
    path = root / "skills/bi/SKILL.md"
    path.write_text(path.read_text(encoding="utf-8").replace("| **", "| "), encoding="utf-8")


CASES = [
    ("version without changelog section", write("VERSION", "9.9.9\n"), "missing version section 9.9.9"),
    ("version not semver", write("VERSION", "1.x\n"), "not valid semver"),
    ("second skill in package", write("skills/extra/SKILL.md", "# extra\n"), "must contain exactly the bi skill"),
    ("entry file missing", delete("skills/bi/agents/openai.yaml"), "required entry file is missing"),
    ("link to missing file", append("skills/bi/references/note.md", "[x](references/nope.md)"),
     "points at missing path: references/nope.md"),
    ("packaged file nobody references", write("skills/bi/references/orphan.md", "# orphan\n"),
     "packaged but nothing references it"),
    ("skill names a repo-only tool", append("skills/bi/references/note.md", "见 `posture-scenarios.md`"),
     "repo-only file not distributed with skills/bi/: posture-scenarios.md"),
    ("new tool file is repo-only without editing the checker",
     both(write("tools/brand-new-tool.md", "# new\n"),
          append("skills/bi/references/note.md", "见 brand-new-tool.md")),
     "repo-only file not distributed with skills/bi/: brand-new-tool.md"),
    ("template carries a skill-internal path", append("skills/bi/templates/entities/decision.md", "[x](../../references/note.md)"),
     "template contains skill-internal path"),
    ("trigger claimed by two postures", edit("skills/bi/SKILL.md", "| **讨论** | 聊聊、", "| **讨论** | 聊聊、快改、"),
     "trigger '快改' claimed by both"),
    ("posture triggers missing from description", edit("skills/bi/SKILL.md", "；我带你跑一遍、教 AI 做某流程。", "。"),
     "posture '学流程' is unreachable"),
    ("description trigger no posture claims", edit("skills/bi/SKILL.md", "教 AI 做某流程。", "教 AI 做某流程；随便聊聊天。"),
     "description trigger '随便聊聊天' is not claimed"),
    ("posture table unparsable", unbold_posture_rows, "posture table looks broken"),
    ("posture without scenario", edit("tools/posture-scenarios.md", "| 我带你跑一遍这个发布流程 | 学流程 |",
                                      "| 我带你跑一遍这个发布流程 | 学东西 |"),
     "posture '学流程' has no scenario"),
    # Real mistake: issue 006's negative test.
    ("scenario names a misspelled reference", edit("tools/posture-scenarios.md", "| 设计 | design |", "| 设计 | desgin |"),
     "unknown reference 'desgin'"),
    ("dangling byissue reference", append("byissue/spec/index.md", "见 `byissue/notes/2026-01-01-nope.md`"),
     "dangling reference byissue/notes/2026-01-01-nope.md"),
    # Real mistake: closing renames break full-name references (issue 008).
    ("reference keeps a closed item's -o- name", append("byissue/spec/index.md", "见 2026-10-29-o-ponytail-audit"),
     "stale item state in 2026-10-29-o-ponytail-audit"),
]


def run(root: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, str(root / CHECKER)], capture_output=True, text=True)
    return proc.returncode, proc.stdout + proc.stderr


def fresh_copy(base: Path, name: str) -> Path:
    target = base / name
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    return target


def main() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        code, output = run(fresh_copy(base, "clean"))
        if code != 0:
            print(output)
            print("FAIL clean copy: the checker must pass before any case means anything")
            return 1
        print("ok   clean copy passes")
        for index, (name, plant, expected) in enumerate(CASES):
            root = fresh_copy(base, f"case{index}")
            plant(root)
            code, output = run(root)
            if code != 0 and expected in output:
                print(f"ok   {name}")
            else:
                failures.append(name)
                print(f"FAIL {name}: expected exit 1 with {expected!r}, got exit {code}\n{output}")
    print(f"{len(CASES) - len(failures)}/{len(CASES)} planted defects caught")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
