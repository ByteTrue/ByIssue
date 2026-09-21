#!/usr/bin/env python3
"""Initialize a ByIssue workspace in byissue/."""
from __future__ import annotations

import argparse
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "entities"
DIRS = ["talks", "vision", "spec", "issues", "epics", "notes", "decisions", "tools"]
INDEXES = {"vision/index.md": "vision-index.md", "spec/index.md": "project-spec-index.md"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a ByIssue workspace in byissue/.")
    parser.add_argument("--project", default=".", help="Project root to initialize.")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite the existing vision and project spec indexes."
    )
    args = parser.parse_args()

    workspace = Path(args.project).resolve() / "byissue"
    for name in DIRS:
        (workspace / name).mkdir(parents=True, exist_ok=True)

    print(f"Initialized ByIssue workspace at {workspace}")
    for relative, template in INDEXES.items():
        index = workspace / relative
        if index.exists() and not args.force:
            print(f"  = {index} (kept)")
            continue
        index.write_text((TEMPLATES / template).read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  + {index}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
