#!/usr/bin/env python3
"""List open issues under byissue/ before committing or pushing.

The mechanical half of the commit contract: bound to the git action (run
right before commit / push / PR / release), not to any posture, so it
survives long sessions where the contract text has been compacted away.
The user's "wrap up / close / commit / push" already authorizes the fixed
order: sediment, graduation, close rename for the items this session worked
on or the user named that meet the close conditions, one commit, then push
only if asked.

Exit code 1 means an item exists under more than one state letter (reported
alone, rerun after resolving) or open regular issues exist (close gates).
Open ff files are reminders only; open epics are the normal state of ongoing
work and are not listed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OPEN_RE = re.compile(r"^(?:\d{4}-\d{1,2}-\d{1,2}|\d+)-o-")
FF_RE = re.compile(r"^(?:\d{4}-\d{1,2}-\d{1,2}|\d+)-o-ff-")
STATE_RE = re.compile(r"^((?:\d{4}-\d{1,2}-\d{1,2}|\d+)-)[oxw](-.+)$")


def issue_trees(workspace: Path) -> list[Path]:
    trees = [workspace / "issues"]
    epics = workspace / "epics"
    if epics.is_dir():
        trees += sorted(epic / "issues" for epic in epics.iterdir() if (epic / "issues").is_dir())
    return [tree for tree in trees if tree.is_dir()]


def scan(workspace: Path) -> tuple[list[Path], list[Path]]:
    """Return (open regular issues, open ff files) as repo-relative paths."""
    gates: list[Path] = []
    reminders: list[Path] = []
    for tree in issue_trees(workspace):
        for entry in sorted(tree.iterdir()):
            if not OPEN_RE.match(entry.name):
                continue
            if entry.is_file() and FF_RE.match(entry.name):
                reminders.append(entry)
            else:  # regular issue file, or an Explore issue directory
                gates.append(entry)
    return gates, reminders


def duplicates(workspace: Path) -> list[list[Path]]:
    """Items present under more than one state letter, e.g. a close that copied instead of renamed."""
    groups: dict[Path, list[Path]] = {}
    for parent in [workspace / "epics", *issue_trees(workspace)]:
        if not parent.is_dir():
            continue
        for entry in parent.iterdir():
            match = STATE_RE.match(entry.name)
            if match:
                groups.setdefault(parent / (match.group(1) + "?" + match.group(2)), []).append(entry)
    return [sorted(paths) for _, paths in sorted(groups.items()) if len(paths) > 1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="List open issues in byissue/ before committing or pushing."
    )
    parser.add_argument("--project", default=".", help="Project root whose byissue/ is checked.")
    args = parser.parse_args()

    root = Path(args.project).resolve()
    workspace = root / "byissue"
    if not workspace.is_dir():
        print(f"未找到 byissue/（{workspace}）；无可检查事项。")
        return 0

    dupes = duplicates(workspace)
    if dupes:
        print("同一事项同时以多个状态存在（关闭时复制而非改名），这次没有列出打开的 issue。逐个文件对照两份内容：一份相对另一份只缺关闭写入的内容（其余不同只是关闭改掉的状态与 -o-/-x-/-w- 名字）时，按 close.md「原则」用它的全名 grep，把引用改到留下的那份，再删掉它（通常是 -o-）；两份各有对方没有的内容时，列给用户问。处理完重跑本脚本再提交：")
        for paths in dupes:
            print("  - " + " 与 ".join(path.relative_to(root).as_posix() for path in paths))
        return 1

    gates, reminders = scan(workspace)
    if gates:
        print("打开的常规 issue（本会话推进过或用户点名、且满足关闭条件的随本次提交关闭，其余保持 -o-）：")
        for path in gates:
            print(f"  - {path.relative_to(root).as_posix()}")
    else:
        print("没有打开的常规 issue。")
    if reminders:
        print("打开的 ff（提醒，跨会话未关闭）：")
        for path in reminders:
            print(f"  - {path.relative_to(root).as_posix()}")

    if gates:
        print(
            "按提交契约：先补齐沉淀（用户要求无痕迹时只列不写）；本会话推进过或用户点名、且满足关闭条件的事项再毕业回写、修引用并改 -x-，"
            "不满足的保持 -o- 并在汇报里说原因；沉淀、回写、改名与代码合成一次 commit。用户点名不关的保持 -o-。"
        )
        return 1
    print("按提交契约：沉淀补齐落盘，随本次提交一起走；用户要求无痕迹时只列不写。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
