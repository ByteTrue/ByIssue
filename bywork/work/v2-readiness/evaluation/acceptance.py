#!/usr/bin/env python3
"""独立黑盒验收：python3 acceptance.py <pi 项目目录> [migrate]。"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PROJECT = Path(sys.argv[1]).resolve()
FIXTURES = Path(__file__).resolve().parent / "legacy"
EXPECTED = [
    {"id": "a001", "customer": "Alice", "amount_cents": 10},
    {"id": "a002", "customer": "Alice", "amount_cents": 20},
    {"id": "a003", "customer": "Alice", "amount_cents": 105},
    {"id": "b001", "customer": "Bob", "amount_cents": 1234},
    {"id": "b002", "customer": "Bob", "amount_cents": 200},
    {"id": "c001", "customer": "张三", "amount_cents": 100001},
    {"id": "c002", "customer": "张三", "amount_cents": 0},
]


def run(*args):
    return subprocess.run(
        [sys.executable, str(PROJECT / "ledger.py"), *map(str, args)],
        cwd=PROJECT, capture_output=True, text=True, timeout=20,
    )


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    source, output = root / "legacy", root / "ledger.json"
    shutil.copytree(FIXTURES, source)
    before = {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    result = run("migrate", source, output)
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text()) == EXPECTED
    assert all(type(row["amount_cents"]) is int for row in json.loads(output.read_text()))
    saved = output.read_bytes()
    result = run("migrate", source, output)
    assert result.returncode == 0 and output.read_bytes() == saved
    assert before == {p.relative_to(source): p.read_bytes() for p in source.rglob("*") if p.is_file()}
    print("PASS: recursive coverage, exact cents, stable rerun, sources preserved")

    invalid = source / "bad.csv"
    bad_rows = [f"id,customer,amount\nx,Bad,{value}\n" for value in (
        "-1", "NaN", "Infinity", "1e2", "1.001", "",
    )] + [
        "id,customer,amount\na001,Duplicate,1\n",
        "id,customer,amount\n,Empty,1\n",
        "id,customer,amount\nx,,1\n",
        "id,customer,value\nx,Bad,1\n",
    ]
    for csv in bad_rows:
        invalid.write_text(csv, encoding="utf-8")
        result = run("migrate", source, output)
        assert result.returncode != 0 and result.stderr.strip(), (csv, result)
        assert output.read_bytes() == saved, csv
    invalid.unlink()
    print(f"PASS: {len(bad_rows)} invalid inputs fail without overwriting output")

    if len(sys.argv) < 3:
        reports = [
            ([], {"count": 7, "total_cents": 101570}),
            (["--customer", "Alice"], {"count": 3, "total_cents": 135}),
            (["--customer", "张三"], {"count": 2, "total_cents": 100001}),
            (["--customer", "Nobody"], {"count": 0, "total_cents": 0}),
            (["--min-cents", "200"], {"count": 3, "total_cents": 101435}),
            (["--customer", "Bob", "--min-cents", "201"], {"count": 1, "total_cents": 1234}),
            (["--min-cents", "999999"], {"count": 0, "total_cents": 0}),
        ]
        for args, expected in reports:
            result = run("report", output, *args)
            assert result.returncode == 0, result.stderr
            actual = json.loads(result.stdout)
            assert actual == expected, (args, actual, expected)
            assert all(type(value) is int for value in actual.values())
        for minimum in ("-1", "1.5", "NaN"):
            result = run("report", output, "--min-cents", minimum)
            assert result.returncode != 0 and result.stderr.strip()
        print("PASS: 7 report paths and 3 invalid thresholds")
