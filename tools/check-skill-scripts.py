#!/usr/bin/env python3
"""测试技能包分发到用户项目里的脚本：初始化目录与 work 检查点校验。"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills/bw/scripts/init_bywork.py"
CHECKER = ROOT / "skills/bw/scripts/check_work.py"

VALID = """---
kind: work
status: complete
current_unit: "已验证的行为"
next_action: ""
must_hold: "约束"
proof_gap: ""
---

# 工作

| 行为路径 | 真实入口 | 操作 | 应观察到 | 证据 | 结果 |
|---|---|---|---|---|---|
| 下单成功 | CLI | 提交订单 | 返回订单号 | logs/order.txt | 通过 |
"""


def run_init(project: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--project", str(project)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def run_check(project: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--project", str(project)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


def write_work(root: Path, slug: str, text: str) -> Path:
    index = root / "bywork" / "work" / slug / "index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(text, encoding="utf-8")
    return index


def main() -> int:
    failures = 0
    cases = 0

    def case(label: str, ok: bool, output: str = "") -> None:
        nonlocal failures, cases
        cases += 1
        print(f"{'ok  ' if ok else 'FAIL'} {label}")
        if not ok:
            failures += 1
            print(output)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        project = root / "project"
        project.mkdir()
        # The checker cases need their own root: the init cases above deliberately
        # leave a non-conforming example/index.md behind.
        checked = root / "checked"
        checked.mkdir()

        code, output = run_init(project)
        created = all((project / "bywork" / name).is_dir() for name in ("work", "memory"))
        case("fresh init creates work/ and memory/", code == 0 and created and "created" in output, output)

        marker = project / "bywork/work/example/index.md"
        marker.parent.mkdir(parents=True)
        marker.write_text("# existing work\n", encoding="utf-8")
        code, output = run_init(project)
        case("rerun keeps existing work",
             code == 0 and marker.read_text(encoding="utf-8") == "# existing work\n" and "kept" in output, output)

        vision = project / "bywork/vision/index.md"
        vision.parent.mkdir(parents=True, exist_ok=True)
        vision.write_text("# user vision\n", encoding="utf-8")
        code, output = run_init(project)
        case("rerun preserves optional vision",
             code == 0 and vision.read_text(encoding="utf-8") == "# user vision\n", output)

        # A workspace with no work entry is not a failure.
        code, output = run_check(checked)
        case("check passes when there is no bywork/work yet", code == 0, output)

        write_work(checked, "valid", VALID)
        code, output = run_check(checked)
        case("check accepts a consistent complete entry", code == 0, output)

        # The illegal status values recorded four times in CHANGELOG must go red.
        for bad in ("done", "completed", "finished", "in-progress"):
            write_work(checked, "valid", VALID.replace("status: complete", f"status: {bad}"))
            code, output = run_check(checked)
            case(f"check rejects status: {bad}", code != 0 and "not one of" in output, output)

        write_work(checked, "valid", VALID.replace('proof_gap: ""', 'proof_gap: "relay 测试未复验"'))
        code, output = run_check(checked)
        case("check rejects complete with a non-empty proof_gap", code != 0 and "proof_gap" in output, output)

        write_work(checked, "valid", VALID.replace("| 通过 |", "| 待跑 |"))
        code, output = run_check(checked)
        case("check rejects complete while a proof row is still 待跑", code != 0 and "待跑" in output, output)

        write_work(checked, "valid", VALID.replace("| 通过 |", "| 无法判定 |"))
        code, output = run_check(checked)
        case("check rejects complete while a proof row is 无法判定", code != 0 and "无法判定" in output, output)

        # The evidence column may quote a failed subject; only the verdict column counts.
        quoted = VALID.replace("| logs/order.txt | 通过 |", "| 业务未通过，见 review.md | 通过 |")
        write_work(checked, "valid", quoted)
        code, output = run_check(checked)
        case("check ignores 未通过 quoted in the evidence column", code == 0, output)

        # An unfinished work may legitimately carry gaps and unresolved rows.
        write_work(checked, "valid", VALID
                   .replace("status: complete", "status: in_progress")
                   .replace('proof_gap: ""', 'proof_gap: "report 未实现"')
                   .replace("| 通过 |", "| 待跑 |"))
        code, output = run_check(checked)
        case("check accepts in_progress with gaps and unresolved rows", code == 0, output)

        write_work(checked, "valid", VALID.replace('must_hold: "约束"\n', ""))
        code, output = run_check(checked)
        case("check reports a missing frontmatter field", code != 0 and "must_hold" in output, output)

        write_work(checked, "valid", VALID.replace("---\n\n# 工作", "# 工作", 1))
        code, output = run_check(checked)
        case("check reports a missing frontmatter block", code != 0 and "frontmatter" in output, output)

        write_work(checked, "valid", VALID.replace("| 行为路径 |", "| 步骤 |"))
        code, output = run_check(checked)
        case("check reports a missing behavior proof table", code != 0 and "proof table" in output, output)

        # Formatters pad table cells with spaces; the header is still the same table.
        # Real-world regression: byspace v1-migration burned ~6 calls compacting its
        # header by hand before the checker accepted a formatter-padded table.
        padded = VALID.replace("| 行为路径 | 真实入口 |", "| 行为路径            | 真实入口 |")
        write_work(checked, "valid", padded)
        code, output = run_check(checked)
        case("check accepts a formatter-padded proof table header", code == 0, output)

        # A complete work is sealed: anything added later must be reachable from
        # index.md. Real-world regression: a new rename task plan was dropped into
        # the complete v2-delivery dir without a link, silently reopening it.
        write_work(checked, "valid", VALID)
        stray = checked / "bywork/work/valid/new-task.md"
        stray.write_text("# 新任务计划\n", encoding="utf-8")
        code, output = run_check(checked)
        case("check rejects an unlinked file in a complete work", code != 0 and "new-task.md" in output, output)

        stray.unlink()
        evidence_dir = checked / "bywork/work/valid/evidence"
        evidence_dir.mkdir()
        (evidence_dir / "run.log").write_text("ok\n", encoding="utf-8")
        write_work(checked, "valid", VALID + "\n证据见同目录 `evidence/`。\n")
        code, output = run_check(checked)
        case("check accepts a mentioned evidence directory in a complete work", code == 0, output)

        import shutil
        shutil.rmtree(evidence_dir)
        write_work(checked, "valid", VALID)

        # One bad entry must not hide the others, and the summary counts both.
        write_work(checked, "valid", VALID)
        write_work(checked, "broken", VALID.replace("status: complete", "status: done"))
        code, output = run_check(checked)
        case("check reports every entry instead of stopping at the first",
             code != 0 and "ok   valid" in output and "FAIL broken" in output and "1/2" in output, output)

    print(f"{'all' if not failures else failures} packaged script case{'s' if cases != 1 else ''} "
          f"{'pass' if not failures else 'failed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
