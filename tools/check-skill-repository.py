#!/usr/bin/env python3
"""Validate the ByIssue single-skill repository before release.

Checks only what can actually break a release: version bookkeeping, the skill
package layout, and that every path the skill points at really exists (and
that nothing in the package is unreachable). Contract wording lives in the
markdown itself — grepping for phrases here would only create a second,
drifting copy of it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/bi"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)\)")
PATH_RE = re.compile(r"`((?:references|templates|scripts|agents)/[\w./-]+\.(?:md|py|yaml))`")

# Reachable by the host, not by a link from inside the skill.
ENTRY_FILES = {"SKILL.md", "agents/openai.yaml", "scripts/init_byissue.py"}
INSTALL_COMMANDS = [
    "npx skills add ByteTrue/ByIssue",
    "npx skills add . --list",
    "npx skills update bi",
]


def check_version(report):
    version_file = ROOT / "VERSION"
    changelog = ROOT / "CHANGELOG.md"
    if not version_file.is_file():
        return report("VERSION", "file is missing")
    version = version_file.read_text(encoding="utf-8").strip()
    if not VERSION_RE.match(version):
        report("VERSION", f"not valid semver: {version!r}")
    if not changelog.is_file():
        report("CHANGELOG.md", "file is missing")
    elif f"## {version}" not in changelog.read_text(encoding="utf-8"):
        report("CHANGELOG.md", f"missing version section {version}")


def check_skill_layout(report):
    skills = ROOT / "skills"
    if not skills.is_dir():
        return report("skills", "directory is missing")
    found = sorted(path.name for path in skills.iterdir() if path.is_dir())
    if found != ["bi"]:
        report("skills", f"must contain exactly the bi skill, found {found!r}")
    for entry in sorted(ENTRY_FILES):
        if not (SKILL / entry).is_file():
            report(f"skills/bi/{entry}", "required entry file is missing")


def check_skill_links(report):
    """Every path the skill points at exists; every packaged file is reachable."""
    referenced = set()
    for source in sorted(SKILL.rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        targets = [t.strip() for t in LINK_RE.findall(text)] + PATH_RE.findall(text)
        for target in targets:
            if target.startswith(("http", "<")):
                continue
            for candidate in (source.parent / target, SKILL / target):
                if candidate.exists():
                    referenced.add(candidate.resolve())
                    break
            else:
                report(source.relative_to(ROOT).as_posix(), f"points at missing path: {target}")

    reachable = referenced | {(SKILL / entry).resolve() for entry in ENTRY_FILES}
    for packaged in sorted(SKILL.rglob("*")):
        if packaged.is_file() and packaged.resolve() not in reachable:
            report(packaged.relative_to(ROOT).as_posix(), "packaged but nothing references it")


def check_readmes(report):
    for filename in ["README.md", "README.en.md"]:
        path = ROOT / filename
        if not path.is_file():
            report(filename, "file is missing")
            continue
        text = path.read_text(encoding="utf-8")
        for command in INSTALL_COMMANDS:
            if command not in text:
                report(filename, f"missing documented command: {command}")


def main() -> int:
    findings: list[tuple[str, str]] = []
    report = lambda path, message: findings.append((path, message))  # noqa: E731
    check_version(report)
    check_skill_layout(report)
    check_skill_links(report)
    check_readmes(report)
    if (ROOT / "dist").exists():
        report("dist", "temporary distribution output must not be committed")

    if findings:
        print("Skill repository check failed:")
        for path, message in findings:
            print(f"- {path}: {message}")
        return 1
    print("Skill repository check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
