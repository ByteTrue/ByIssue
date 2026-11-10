#!/usr/bin/env python3
"""Validate the ByIssue single-skill repository before release.

Checks only what can actually break a release: version bookkeeping, the skill
package layout, every path the skill points at (and that nothing packaged is
unreachable), every path the repo's current-truth docs point at, one derived
count in the project spec, the license text inside the package, the posture table plus its scenario coverage, and
dangling references inside byissue/.

Contract wording is deliberately not checked — grepping for phrases here would
only create a second, drifting copy of it. Semantic routing is not checked
either; that needs the subagent eval described in tools/posture-scenarios.md.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/bi"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#]+)(?:#[^)]*)?\)")  # anchors allowed, path captured
PATH_RE = re.compile(r"`((?:references|templates|scripts|agents)/[\w./-]+\.(?:md|py|yaml))`")
# Root docs plus every file under tools/, derived so a new tool file needs no edit here.
REPO_ONLY_NAMES = ["WHY BYISSUE.md", "CHANGELOG.md"] + sorted(
    {p.name for p in (ROOT / "tools").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
)
REPO_ONLY_RE = re.compile("|".join([r"\bVERSION\b"] + [re.escape(name) for name in REPO_ONLY_NAMES]))

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
        return report("CHANGELOG.md", "file is missing")
    headings = [h for h in (line[3:].split()[0] for line in unfenced(changelog.read_text(encoding="utf-8").splitlines())
                            if line.startswith("## ") and line[3:].strip()) if VERSION_RE.match(h)]
    if version not in headings:
        report("CHANGELOG.md", f"missing version section {version}")
    elif headings[0] != version:
        report("CHANGELOG.md", f"newest section is {headings[0]}, not VERSION {version}")
    for dup in sorted({h for h in headings if headings.count(h) > 1}):
        report("CHANGELOG.md", f"version {dup} has more than one section")


def unfenced(lines):
    """Lines outside ``` fences: a heading or link quoted in a code block is an example, not a claim."""
    return (line for _, line in numbered_unfenced(lines))


def check_license_travels(report):
    """MIT needs its notice in every copy; only skills/bi/ is distributed, so its NOTICE.md carries LICENSE."""
    license_file, notice = ROOT / "LICENSE", SKILL / "NOTICE.md"
    if not license_file.is_file():
        return report("LICENSE", "file is missing")
    text = notice.read_text(encoding="utf-8") if notice.is_file() else ""
    if license_file.read_text(encoding="utf-8").strip() not in text:
        report("skills/bi/NOTICE.md", "must contain the repository LICENSE verbatim, so installed copies carry it")
    # grilling.md and domain-modeling.md copy mattpocock/skills; its MIT notice must ship with them.
    if "mattpocock/skills" not in text or "Copyright (c) 2026 Matt Pocock" not in text:
        report("skills/bi/NOTICE.md", "must keep the mattpocock/skills attribution and its MIT copyright line")


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
        rel_doc = source.relative_to(SKILL).as_posix()
        leak = REPO_ONLY_RE.search(text)
        if leak:
            report(source.relative_to(ROOT).as_posix(), f"references repo-only file not distributed with skills/bi/: {leak.group(0)}")
        targets = [t.strip() for t in LINK_RE.findall(text)] + PATH_RE.findall(text)
        for target in targets:
            if rel_doc.startswith("templates/") and not target.startswith(("http", "<")):
                report(source.relative_to(ROOT).as_posix(), f"template contains skill-internal path: {target}")
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


# Docs that state current truth. History legitimately quotes deleted files and broken examples:
# byissue/ records (issues, epics, notes, talks, decisions), the changelog, and the one-off
# failure-mode analysis are out of scope.
HISTORY_DIRS = {"issues", "epics", "notes", "talks", "decisions"}
HISTORY_FILES = {"CHANGELOG.md", "tools/retro-failure-modes.md"}
REPO_LINK_RE = re.compile(r"\[[^\]]*\]\((<[^>]+>|(?:[^()\s]|\([^()\s]*\))+)\)")  # one level of balanced parens, as CommonMark
REPO_PREFIX = r"(?:tools|skills/bi|byissue/spec|byissue/tools)/"
# A repo path in backticks, possibly after a command word and its flags (`python3 -u ./tools/x.py`),
# or one a command line inside a fenced block runs (the release chain lives in a ```text block).
# Placeholders are written <...> and skipped; a trailing :12 or #L12 line reference is dropped.
COMMAND = r"(?:bash|sh|python3|npx)(?:\s+-\S+)*\s+"
REPO_PATH_RE = re.compile(rf"`(?:{COMMAND})?(?:\./)?({REPO_PREFIX}[^`\s]*[\w/])")
FENCED_COMMAND_RE = re.compile(rf"{COMMAND}(?:\./)?({REPO_PREFIX}[^\s`]*[\w/])")
LINE_REF_RE = re.compile(r"(?::\d+(?:-\d+)?|#L\d+(?:-L?\d+)?)$")


def check_repo_paths(report):
    """Links and backticked repo paths in current-truth docs outside the skill resolve."""
    for source in sorted(ROOT.rglob("*.md")):
        rel = source.relative_to(ROOT)
        if ".git" in rel.parts or rel.parts[0] == "skills" or rel.as_posix() in HISTORY_FILES or (
            rel.parts[0] == "byissue" and len(rel.parts) > 1 and rel.parts[1] in HISTORY_DIRS
        ):
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
        unfenced_numbers = set()
        for number, line in numbered_unfenced(lines):
            unfenced_numbers.add(number)
            for raw in REPO_LINK_RE.findall(line):
                target = unquote(raw[1:-1] if raw.startswith("<") else raw).split("#", 1)[0]
                if target and not target.startswith(("http:", "https:", "mailto:")) and not (source.parent / target).exists():
                    report(rel.as_posix(), f"line {number}: link points at missing path: {target}")
            for target in REPO_PATH_RE.findall(line):
                target = LINE_REF_RE.sub("", target)
                if not any(c in target for c in "*{<") and not (ROOT / target).exists():
                    report(rel.as_posix(), f"line {number}: names missing path: {target}")
        for number, line in enumerate(lines, 1):
            if number in unfenced_numbers or line.lstrip().startswith("```"):
                continue
            for target in map(lambda t: LINE_REF_RE.sub("", t), FENCED_COMMAND_RE.findall(line)):
                if not any(c in target for c in "*{<") and not (ROOT / target).exists():
                    report(rel.as_posix(), f"line {number}: fenced command runs missing path: {target}")


def numbered_unfenced(lines):
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def check_derived_facts(report):
    """A count the project spec states must match the tree it counts."""
    spec = ROOT / "byissue/spec/index.md"
    if not spec.is_file():
        return
    actual = len(list((SKILL / "references").glob("*.md")))
    text = spec.read_text(encoding="utf-8")
    claims = re.findall(r"`references/` 下的 (\d+) 篇", text) + re.findall(r"(\d+) 个 `\.md` 平铺", text)
    if not claims:
        report("byissue/spec/index.md", "no references/ count the checker recognizes; it looks for "
               "「`references/` 下的 N 篇」 and 「N 个 `.md` 平铺」, update both together")
    for claimed in claims:
        if int(claimed) != actual:
            report("byissue/spec/index.md", f"says references/ has {claimed} files, it has {actual}")


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

    if "触发：" in description:
        desc_tail = description.split("触发：", 1)[1].strip().rstrip("。")
        claimed = set(owner)
        for t in list(owner):
            for part in t.split("/"):
                if part.strip():
                    claimed.add(part.strip())
        for group in desc_tail.split("；"):
            for item in group.split("、"):
                tok = item.strip()
                if tok and tok not in {"bi", "ByIssue"} and tok not in claimed:
                    report("skills/bi/SKILL.md", f"description trigger {tok!r} is not claimed by any posture")

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
    item_parts_re = re.compile(r"^(?P<prefix>\d{4}-\d{1,2}-\d{1,2}|\d{3})-[oxdw]-(?P<slug>.+)$")
    item_ref_re = re.compile(r"(?<![A-Za-z0-9_-])((?:\d{4}-\d{1,2}-\d{1,2}|\d{3})-[oxdw]-[A-Za-z0-9_-]+(?:\.md)?)(?![A-Za-z0-9_-])")
    existing: set[str] = set()
    local_keys: set[tuple[str, str]] = set()
    issue_and_epic_dirs = [workspace / "issues", workspace / "epics"]
    if (workspace / "epics").is_dir():
        issue_and_epic_dirs += [p / "issues" for p in (workspace / "epics").iterdir() if (p / "issues").is_dir()]
    for folder in issue_and_epic_dirs:
        if not folder.is_dir():
            continue
        for entry in folder.iterdir():
            if entry.name == ".gitkeep":
                continue
            existing.add(entry.name)
            stem = entry.stem if entry.suffix == ".md" else entry.name
            existing.add(stem)
            m = item_parts_re.match(stem)
            if m:
                local_keys.add((m.group("prefix"), m.group("slug")))

    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        in_byissue = workspace in source.parents
        for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for match in pattern.finditer(line):
                target = match.group(0).rstrip(".")
                if not (ROOT / target).exists():
                    report(source.relative_to(ROOT).as_posix(), f"line {number}: dangling reference {target}")
            if in_byissue:
                for match in item_ref_re.finditer(line):
                    ref = match.group(1)
                    ref_stem = ref[:-3] if ref.endswith(".md") else ref
                    m = item_parts_re.match(ref_stem)
                    if m and (m.group("prefix"), m.group("slug")) in local_keys and ref not in existing:
                        report(source.relative_to(ROOT).as_posix(), f"line {number}: stale item state in {ref}")


def main() -> int:
    findings: list[tuple[str, str]] = []

    def report(path, message):
        findings.append((path, message))
    check_version(report)
    check_skill_layout(report)
    check_license_travels(report)
    check_skill_links(report)
    check_repo_paths(report)
    check_derived_facts(report)
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
