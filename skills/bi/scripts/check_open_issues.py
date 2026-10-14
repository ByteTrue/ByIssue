#!/usr/bin/env python3
"""List open issues under byissue/ before committing or pushing.

The mechanical half of the commit contract (sediment and close settle before the push): bound to the git
action (run right before commit / push / PR / release), not to any posture,
so it survives long sessions where the contract text has been compacted
away. Rule: run it, present what it lists, request close AND sediment
authorization in the same turn, settle everything onto disk, then push
rename + graduation + sediment + code as one commit.

Exit code 1 means open regular issues exist (close gates). Open ff files
are reminders only; open epics are the normal state of ongoing work and
are not listed.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OPEN_RE = re.compile(r"^(?:\d{4}-\d{1,2}-\d{1,2}|\d+)-o-")
FF_RE = re.compile(r"^(?:\d{4}-\d{1,2}-\d{1,2}|\d+)-o-ff-")


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

    gates, reminders = scan(workspace)
    if gates:
        print("打开的常规 issue（提交前需要关闭裁决）：")
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
            "按提交契约：同轮给出关闭建议与沉淀候选并请求授权，关闭改名、毕业回写、沉淀落盘与代码合并为单次 commit 后再推送；"
            "用户明确暂不处理的，才单独提交代码。"
        )
        return 1
    print(
        "按提交契约：沉淀候选仍未裁决时，同轮列出并请求授权，"
        "落盘随本次提交一起走——合并后再冒出待办，意味着一笔可避免的第二提交和一轮白跑的 CI。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
