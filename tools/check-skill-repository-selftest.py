#!/usr/bin/env python3
"""Prove every check in check-skill-repository.py can actually fail.

Each case copies the repository to a temp dir, plants one known-bad change,
runs the copied checker, and expects its message. Cases commented "Real
mistake" replay something this repo really shipped. A check that cannot go red
here guards nothing.

Every fix to the checker, a new check or a silent miss closed, adds the case
that the previous checker lets through, and is run once against that previous
checker to see it fail. Run after any change to tools/check-skill-repository.py.
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


def prepend(rel, text):
    def apply(root: Path):
        path = root / rel
        path.write_text(text + path.read_text(encoding="utf-8"), encoding="utf-8")
    return apply


def duplicate_current_version(root: Path):
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    with (root / "CHANGELOG.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {version}\n\nagain\n")


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
    # Real mistake: an anchored link matched nothing and was never checked (issue 009).
    ("anchored link to missing file", append("skills/bi/references/note.md", "[x](references/nope.md#a)"),
     "points at missing path: references/nope.md"),
    # Real mistake: the release chain told people to run a deleted script (issue 009).
    ("current doc names a deleted tool", append("byissue/spec/index.md", "跑 `tools/check-posture-routing.py`"),
     "names missing path: tools/check-posture-routing.py"),
    ("current doc links a missing file", append("README.md", "[x](docs/nope.md)"),
     "link points at missing path: docs/nope.md"),
    ("angle-bracket link to a missing file with a space", append("README.md", "[x](<WHY NOPE.md>)"),
     "link points at missing path: WHY NOPE.md"),
    # The original 009 shape: a command in the fenced release chain runs a deleted script.
    ("fenced release chain runs a deleted tool",
     edit("byissue/spec/index.md", "改 skills/bi/ → bash tools/release-check.sh", "改 skills/bi/ → python3 tools/check-posture-routing.py"),
     "fenced command runs missing path: tools/check-posture-routing.py"),
    ("inline command runs a deleted tool", append("byissue/spec/index.md", "跑 `python3 tools/deleted.py` 一下"),
     "names missing path: tools/deleted.py"),
    ("spec count rewritten out of the checker's sight",
     both(edit("byissue/spec/index.md", "`references/` 下的 ", "`references/` 目前 "),
          edit("byissue/spec/index.md", " 个 `.md` 平铺", " 个文件平铺")),
     "no references/ count the checker recognizes"),
    ("changelog newest section is not VERSION", prepend("CHANGELOG.md", "## 0.0.0\n\nold\n\n"),
     "newest section is 0.0.0"),
    ("changelog repeats a version", duplicate_current_version, "has more than one section"),
    # Real mistake: the spec said references/ had 20 files while it had 22.
    ("new reference leaves the spec count stale", write("skills/bi/references/extra.md", "# extra\n"),
     "says references/ has"),
    ("license edited but the packaged NOTICE not", edit("LICENSE", "2026 ByteTrue", "2027 ByteTrue"),
     "must contain the repository LICENSE verbatim"),
    ("packaged NOTICE loses the upstream attribution",
     edit("skills/bi/NOTICE.md", "Copyright (c) 2026 Matt Pocock", "Copyright (c) 2026"),
     "must keep the mattpocock/skills attribution"),
    ("command with flags and ./ runs a deleted tool", append("byissue/spec/index.md", "跑 `bash -x ./tools/deleted.py` 一下"),
     "names missing path: tools/deleted.py"),
    ("fenced command with a flag runs a deleted tool",
     edit("byissue/spec/index.md", "改 skills/bi/ → bash tools/release-check.sh", "改 skills/bi/ → python3 -u tools/gone.py"),
     "fenced command runs missing path: tools/gone.py"),
    ("line reference to a deleted file", append("byissue/spec/index.md", "见 `tools/deleted.py:12`"),
     "names missing path: tools/deleted.py"),
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
