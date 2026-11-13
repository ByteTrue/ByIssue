#!/usr/bin/env python3
"""证明仓库 checker 的每个检查都能在坏夹具上失败。"""
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
        assert text.count(old) == 1, f"{rel}: fixture anchor occurs {text.count(old)} times: {old!r}"
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


def duplicate_current_version(root: Path):
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    with (root / "CHANGELOG.md").open("a", encoding="utf-8") as handle:
        handle.write(f"\n## {version}\n\nagain\n")


CASES = [
    ("version without changelog section", write("VERSION", "9.9.9\n"), "missing version section 9.9.9"),
    ("version not semver", write("VERSION", "1.x\n"), "not valid semver"),
    ("second skill in package", write("skills/extra/SKILL.md", "# extra\n"), "must contain exactly the bi skill"),
    ("entry file missing", delete("skills/bi/agents/openai.yaml"), "required entry file is missing"),
    (
        "link to missing file",
        append("skills/bi/references/clarify.md", "[x](references/nope.md)"),
        "points at missing path: references/nope.md",
    ),
    ("packaged file nobody references", write("skills/bi/references/orphan.md", "# orphan\n"), "packaged but nothing references it"),
    ("skill names a repo-only file", append("skills/bi/references/clarify.md", "见 `VERSION`"), "repo-only file not distributed"),
    (
        "new tool file is repo-only without editing the checker",
        both(write("tools/brand-new-tool.md", "# new\n"), append("skills/bi/references/clarify.md", "见 `brand-new-tool.md`")),
        "repo-only file not distributed with skills/bi/: brand-new-tool.md",
    ),
    (
        "template carries a skill-internal path",
        append("skills/bi/templates/work.md", "[x](../references/clarify.md)"),
        "template contains skill-internal path",
    ),
    (
        "work template loses a checkpoint field",
        edit("skills/bi/templates/work.md", "status: in_progress", "state: in_progress"),
        "frontmatter fields must be",
    ),
    (
        "anchored link to missing file",
        append("skills/bi/references/clarify.md", "[x](references/nope.md#part)"),
        "points at missing path: references/nope.md",
    ),
    (
        "current doc names a deleted tool",
        append("byissue/memory/project.md", "见 `tools/check-deleted.py`"),
        "names missing path: tools/check-deleted.py",
    ),
    (
        "current doc links a missing file",
        append("README.md", "[x](docs/nope.md)"),
        "link points at missing path: docs/nope.md",
    ),
    (
        "inline command names a deleted tool",
        append("byissue/memory/project.md", "运行 python3 tools/deleted.py"),
        "command names missing path: tools/deleted.py",
    ),
    (
        "fenced command names a deleted tool",
        append("README.md", "```bash\npython3 tools/deleted.py\n```"),
        "command names missing path: tools/deleted.py",
    ),
    (
        "current work links a missing file",
        write("byissue/work/example/index.md", "[proof](missing.md)\n"),
        "link points at missing path: missing.md",
    ),
    (
        "historical records left in active workspace",
        write("byissue/issues/legacy.md", "# historical issue\n"),
        "unexpected workspace entry; historical records belong in archive/",
    ),
    ("changelog newest section is not VERSION", lambda root: (root / "CHANGELOG.md").write_text("## 0.0.0\n\nold\n\n" + (root / "CHANGELOG.md").read_text(encoding="utf-8"), encoding="utf-8"), "newest section is 0.0.0"),
    ("changelog repeats a version", duplicate_current_version, "has more than one section"),
    ("license edited but packaged NOTICE not", edit("LICENSE", "2026 ByteTrue", "2027 ByteTrue"), "must contain the repository LICENSE verbatim"),
    ("packaged NOTICE loses upstream attribution", edit("skills/bi/NOTICE.md", "Copyright (c) 2026 Matt Pocock", "Copyright (c) 2026"), "must keep the upstream attribution"),
    ("project memory deleted", delete("byissue/memory/project.md"), "byissue/memory/project.md: file is missing"),
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
            print("FAIL clean copy: checker must pass before planted cases mean anything")
            return 1
        print("ok   clean copy passes")
        archive = fresh_copy(base, "archive")
        write("archive/v1/example.md", "[historical](missing.md)\n运行 python3 tools/old.py\n")(archive)
        code, output = run(archive)
        if code != 0:
            print(f"FAIL historical references must stay isolated\n{output}")
            return 1
        print("ok   archived references stay outside current checks")
        for index, (name, plant, expected) in enumerate(CASES):
            root = fresh_copy(base, f"case{index}")
            plant(root)
            code, output = run(root)
            if code == 1 and expected in output:
                print(f"ok   {name}")
            else:
                failures.append(name)
                print(f"FAIL {name}: expected exit 1 with {expected!r}, got exit {code}\n{output}")
    print(f"{len(CASES) - len(failures)}/{len(CASES)} planted defects caught")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
