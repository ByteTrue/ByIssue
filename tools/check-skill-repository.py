#!/usr/bin/env python3
"""Validate the ByIssue single-skill repository before release.

Checks only what can actually break a release: version bookkeeping, the skill
package layout, every path the skill points at (and that nothing packaged is
unreachable), the posture table plus its scenario coverage, and dangling
references inside byissue/.

Contract wording is deliberately not checked — grepping for phrases here would
only create a second, drifting copy of it. Semantic routing is not checked
either; that needs the subagent eval described in tools/posture-scenarios.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/bi"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")  # anchors allowed, path captured
PATH_RE = re.compile(r"`((?:references|templates|scripts|agents)/[\w./-]+\.(?:md|py|yaml))`")

# Reachable by the host, not by a link from inside the skill.
ENTRY_FILES = {"SKILL.md", "agents/openai.yaml", "scripts/init_byissue.py"}


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


POSTURE_ROW_RE = re.compile(r"^\|\s*\*\*(?P<posture>[^*]+)\*\*\s*\|(?P<rest>.*)\|\s*$")


def check_posture_table(report):
    """The posture table routes everything; guard it against structural damage.

    Semantic routing (does this sentence reach the right posture?) is judged by
    a model, not here — run the subagent eval in tools/posture-scenarios.md.
    """
    text_all = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    # Routing has two stages: the host opens the skill by text-matching the
    # frontmatter description, and only then does the posture table apply.
    # A posture whose triggers appear nowhere in the description is unreachable.
    front = text_all.split("---", 2)[1] if text_all.startswith("---") else ""
    description = front.split("description:", 1)[-1] if "description:" in front else ""

    postures, owner = set(), {}
    for line in text_all.splitlines():
        match = POSTURE_ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in match.group("rest").split("|")]
        if len(cells) < 4:
            continue  # some other bolded table
        posture = match.group("posture").strip()
        postures.add(posture)
        triggers = [t.strip() for t in re.split(r"[、，]", cells[0]) if t.strip()]
        if not triggers:
            report("skills/bi/SKILL.md", f"posture {posture!r} has no trigger phrases")
        for trigger in triggers:
            if trigger in owner:
                report("skills/bi/SKILL.md", f"trigger {trigger!r} claimed by both {owner[trigger]!r} and {posture!r}")
            owner[trigger] = posture

        if not any(trigger in description for trigger in triggers):
            report(
                "skills/bi/SKILL.md",
                f"posture {posture!r} is unreachable: none of its triggers appear in the description",
            )

    if len(postures) < 5:
        report("skills/bi/SKILL.md", f"posture table looks broken, parsed only {len(postures)} rows")

    check_scenarios(report, postures)


def check_scenarios(report, postures):
    """Every posture is covered by a scenario, and scenarios name real files."""
    scenarios = ROOT / "tools/posture-scenarios.md"
    if not scenarios.is_file():
        return report("tools/posture-scenarios.md", "file is missing")
    text = scenarios.read_text(encoding="utf-8")
    for posture in sorted(postures):
        if f"| {posture} |" not in text:
            report("tools/posture-scenarios.md", f"posture {posture!r} has no scenario")

    # Scenario rows name references in the 应读取 / 不应读取 columns; a typo there
    # would silently weaken the eval. Prose assertions are skipped by the shape filter.
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        for cell in cells[3:]:
            for name in re.split(r"[、,]", cell):
                if re.fullmatch(r"[a-z][a-z-]*", name.strip()) and not (
                    SKILL / "references" / f"{name.strip()}.md"
                ).is_file():
                    report("tools/posture-scenarios.md", f"scenario {cells[0]}: unknown reference {name.strip()!r}")


def check_byissue_references(report):
    """Closing an issue renames it (-o- to -x-), which breaks every full-name
    reference pointing at it. The full-name rule and path-encoded state pull
    against each other; this check is the forcing function that keeps the
    rename and the reference update in the same commit.
    """
    workspace = ROOT / "byissue"
    if not workspace.is_dir():
        return
    pattern = re.compile(r"(?<![\w/-])byissue/(?:issues|epics|notes|talks|decisions)/[\w./-]+\.md")
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for match in pattern.finditer(line):
                target = match.group(0).rstrip(".")
                if not (ROOT / target).exists():
                    report(source.relative_to(ROOT).as_posix(), f"line {number}: dangling reference {target}")


def main() -> int:
    findings: list[tuple[str, str]] = []

    def report(path, message):
        findings.append((path, message))
    check_version(report)
    check_skill_layout(report)
    check_skill_links(report)
    check_posture_table(report)
    check_byissue_references(report)
    if findings:
        print("Skill repository check failed:")
        for path, message in findings:
            print(f"- {path}: {message}")
        return 1
    print("Skill repository check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
