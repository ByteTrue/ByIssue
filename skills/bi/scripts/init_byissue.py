#!/usr/bin/env python3
"""Initialize the current-work and memory directories in byissue/."""
from __future__ import annotations

import argparse
from pathlib import Path

DIRS = ["work", "memory"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a ByIssue workspace in byissue/.")
    parser.add_argument("--project", default=".", help="Project root to initialize.")
    args = parser.parse_args()

    workspace = Path(args.project).resolve() / "byissue"
    print(f"Initialized ByIssue workspace at {workspace}")
    for name in DIRS:
        directory = workspace / name
        existed = directory.exists()
        directory.mkdir(parents=True, exist_ok=True)
        print(f"  {'=' if existed else '+'} {directory} ({'kept' if existed else 'created'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
