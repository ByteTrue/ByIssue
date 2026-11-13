#!/usr/bin/env python3
"""测试技能包分发到用户项目里的初始化脚本。"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/bi/scripts/init_byissue.py"


def run(project: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def main() -> int:
    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = root / "project"
        project.mkdir()

        code, output = run(project)
        created = all((project / "byissue" / name).is_dir() for name in ("work", "memory"))
        ok = code == 0 and created and "created" in output
        print(f"{'ok  ' if ok else 'FAIL'} fresh init creates work/ and memory/")
        if not ok:
            failures += 1
            print(output)

        marker = project / "byissue/work/example/index.md"
        marker.parent.mkdir(parents=True)
        marker.write_text("# existing work\n", encoding="utf-8")
        code, output = run(project)
        ok = code == 0 and marker.read_text(encoding="utf-8") == "# existing work\n" and "kept" in output
        print(f"{'ok  ' if ok else 'FAIL'} rerun keeps existing work")
        if not ok:
            failures += 1
            print(output)

        vision = project / "byissue/vision/index.md"
        vision.parent.mkdir(parents=True, exist_ok=True)
        vision.write_text("# user vision\n", encoding="utf-8")
        code, output = run(project)
        ok = code == 0 and vision.read_text(encoding="utf-8") == "# user vision\n"
        print(f"{'ok  ' if ok else 'FAIL'} rerun preserves optional vision")
        if not ok:
            failures += 1
            print(output)

    print(f"{'all' if not failures else failures} init script case{'s' if failures != 1 else ''} {'pass' if not failures else 'failed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
