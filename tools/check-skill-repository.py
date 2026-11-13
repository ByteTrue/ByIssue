#!/usr/bin/env python3
"""发布前检查 ByIssue 单技能仓库的结构和可达路径。

检查版本记录、技能包布局、许可证、技能内路径、当前文档里的仓库路径、
工作区隔离和 work 模板的检查点字段。工作流语义由人工审查和真实使用验证，
这里不复制一份提示词契约。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills/bi"

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
LINK_RE = re.compile(r"\[[^\]]*\]\(<?([^)#>]+)>?(?:#[^)]*)?\)")
PATH_RE = re.compile(r"`((?:references|templates|scripts|agents)/[\w./-]+\.(?:md|py|yaml))`")
REPO_ONLY_NAMES = ["WHY BYISSUE.md", "CHANGELOG.md"] + sorted(
    {p.name for p in (ROOT / "tools").rglob("*") if p.is_file() and "__pycache__" not in p.parts}
)
REPO_ONLY_RE = re.compile("|".join([r"\bVERSION\b"] + [re.escape(name) for name in REPO_ONLY_NAMES]))

# These files are loaded by the host or are the package's main entry. Everything else
# must be reachable from one of them or from a Markdown link in the package.
ENTRY_FILES = {"SKILL.md", "NOTICE.md", "agents/openai.yaml", "scripts/init_byissue.py"}
WORK_FIELDS = {"kind", "status", "current_unit", "next_action", "must_hold", "proof_gap"}


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
    headings = [
        h
        for h in (
            line[3:].split()[0]
            for line in unfenced(changelog.read_text(encoding="utf-8").splitlines())
            if line.startswith("## ") and line[3:].strip()
        )
        if VERSION_RE.match(h)
    ]
    if version not in headings:
        report("CHANGELOG.md", f"missing version section {version}")
    elif headings[0] != version:
        report("CHANGELOG.md", f"newest section is {headings[0]}, not VERSION {version}")
    for duplicate in sorted({h for h in headings if headings.count(h) > 1}):
        report("CHANGELOG.md", f"version {duplicate} has more than one section")


def unfenced(lines):
    return (line for _, line in numbered_unfenced(lines))


def numbered_unfenced(lines):
    fenced = False
    for number, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            yield number, line


def check_license_travels(report):
    license_file, notice = ROOT / "LICENSE", SKILL / "NOTICE.md"
    if not license_file.is_file():
        return report("LICENSE", "file is missing")
    text = notice.read_text(encoding="utf-8") if notice.is_file() else ""
    if license_file.read_text(encoding="utf-8").strip() not in text:
        report("skills/bi/NOTICE.md", "must contain the repository LICENSE verbatim")
    if "mattpocock/skills" not in text or "Copyright (c) 2026 Matt Pocock" not in text:
        report("skills/bi/NOTICE.md", "must keep the upstream attribution and copyright line")


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
    """Check skill-local links and make sure every packaged file is reachable."""
    referenced = set()
    for source in sorted(SKILL.rglob("*.md")):
        text = source.read_text(encoding="utf-8")
        rel_doc = source.relative_to(SKILL).as_posix()
        leak = REPO_ONLY_RE.search(text)
        if leak:
            report(
                source.relative_to(ROOT).as_posix(),
                f"references repo-only file not distributed with skills/bi/: {leak.group(0)}",
            )
        targets = [target.strip() for target in LINK_RE.findall(text)] + PATH_RE.findall(text)
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


def check_work_template(report):
    path = SKILL / "templates/work.md"
    if not path.is_file():
        return report("skills/bi/templates/work.md", "work template is missing")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return report("skills/bi/templates/work.md", "frontmatter is missing")
    try:
        end = lines.index("---", 1)
    except ValueError:
        return report("skills/bi/templates/work.md", "frontmatter is not closed")
    fields = {line.split(":", 1)[0].strip() for line in lines[1:end] if ":" in line}
    if fields != WORK_FIELDS:
        report(
            "skills/bi/templates/work.md",
            f"frontmatter fields must be {sorted(WORK_FIELDS)!r}, found {sorted(fields)!r}",
        )


# These documents state the repository's current truth. Historical records can quote
# paths that no longer exist and therefore stay outside this check.
HISTORY_FILES = {"CHANGELOG.md"}
REPO_LINK_RE = re.compile(r"\[[^\]]*\]\((<[^>]+>|(?:[^()\s]|\([^()\s]*\))+)\)")
REPO_PREFIX = r"(?:tools|skills/bi|byissue/(?:work|memory|vision)|archive)/"
COMMAND = r"(?:bash|sh|python3|npx)(?:\s+-\S+)*\s+"
REPO_PATH_RE = re.compile(rf"`(?:{COMMAND})?(?:\./)?({REPO_PREFIX}[^`\s]*[\w/])")
INLINE_COMMAND_RE = re.compile(rf"{COMMAND}(?:\./)?({REPO_PREFIX}[^\s`]*[\w/])")
LINE_REF_RE = re.compile(r"(?::\d+(?:-\d+)?|#L\d+(?:-L?\d+)?)$")


def check_repo_paths(report):
    for source in sorted(ROOT.rglob("*.md")):
        rel = source.relative_to(ROOT)
        if ".git" in rel.parts or rel.parts[0] in {"skills", "archive"} or rel.as_posix() in HISTORY_FILES:
            continue
        lines = source.read_text(encoding="utf-8").splitlines()
        for number, line in numbered_unfenced(lines):
            for raw in REPO_LINK_RE.findall(line):
                target = unquote(raw[1:-1] if raw.startswith("<") else raw).split("#", 1)[0]
                if target and not target.startswith(("http:", "https:", "mailto:")) and not (source.parent / target).exists():
                    report(rel.as_posix(), f"line {number}: link points at missing path: {target}")
            for target in REPO_PATH_RE.findall(line):
                target = LINE_REF_RE.sub("", target)
                if not any(char in target for char in "*{<") and not (ROOT / target).exists():
                    report(rel.as_posix(), f"line {number}: names missing path: {target}")
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                continue
            for target in map(lambda item: LINE_REF_RE.sub("", item), INLINE_COMMAND_RE.findall(line)):
                if not any(char in target for char in "*{<") and not (ROOT / target).exists():
                    report(rel.as_posix(), f"line {number}: command names missing path: {target}")


def check_workspace_layout(report):
    workspace = ROOT / "byissue"
    for name in ("work", "memory"):
        if not (workspace / name).is_dir():
            report(f"byissue/{name}", "directory is missing")
    if workspace.is_dir():
        for entry in sorted(workspace.iterdir()):
            if entry.name not in {"work", "memory", "vision"} or not entry.is_dir():
                report(entry.relative_to(ROOT).as_posix(), "unexpected workspace entry; historical records belong in archive/")
    if not (workspace / "memory/project.md").is_file():
        report("byissue/memory/project.md", "file is missing")


def main() -> int:
    findings: list[tuple[str, str]] = []

    def report(path, message):
        findings.append((path, message))

    check_version(report)
    check_skill_layout(report)
    check_license_travels(report)
    check_skill_links(report)
    check_work_template(report)
    check_repo_paths(report)
    check_workspace_layout(report)
    if findings:
        print("Skill repository check failed:")
        for path, message in findings:
            print(f"- {path}: {message}")
        return 1
    print("Skill repository check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
