#!/usr/bin/env python3
"""Regression checks for the ledger migrate CLI. Run with unittest discover."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT_ROOT / "ledger.py"
HEADER = "id,customer,amount\n"


def run_migrate(source: Path, output: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LEDGER), "migrate", str(source), str(output)],
        capture_output=True,
        text=True,
    )


def run_report(ledger: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LEDGER), "report", str(ledger), *arguments],
        capture_output=True,
        text=True,
    )


class MigrateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.root = Path(self._temporary_directory.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.output = self.root / "output.json"

    def write_csv(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path:
        path = self.source / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)
        return path

    def assert_failed(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertNotEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stderr.strip(), "failure should explain itself on stderr")

    def test_migrates_all_csv_files_recursively_and_sorts_by_id(self) -> None:
        self.write_csv("01.csv", HEADER + "b001,Bob,12.34\na002,Alice,0.20\n")
        self.write_csv("nested/02.csv", HEADER + "c001,张三,1000.01\na001,Alice,0.10\n")
        self.write_csv("nested/deeper/03.csv", HEADER + "b002,Bob,2\nc002,张三,0\n")
        self.write_csv("ignored.txt", "not,a,csv\n")

        result = run_migrate(self.source, self.output)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        rows = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(
            rows,
            [
                {"id": "a001", "customer": "Alice", "amount_cents": 10},
                {"id": "a002", "customer": "Alice", "amount_cents": 20},
                {"id": "b001", "customer": "Bob", "amount_cents": 1234},
                {"id": "b002", "customer": "Bob", "amount_cents": 200},
                {"id": "c001", "customer": "张三", "amount_cents": 100001},
                {"id": "c002", "customer": "张三", "amount_cents": 0},
            ],
        )
        for row in rows:
            self.assertEqual(set(row), {"id", "customer", "amount_cents"})

    def test_amounts_convert_exactly_without_float_rounding(self) -> None:
        self.write_csv(
            "amounts.csv",
            HEADER
            + "a,Alice,0\n"
            + "b,Alice,12\n"
            + "c,Alice,0.1\n"
            + "d,Alice,0.10\n"
            + "e,Alice,12.34\n"
            + "f,Alice,123456789012345678901234567890.12\n",
        )

        result = run_migrate(self.source, self.output)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        amounts = {
            row["id"]: row["amount_cents"]
            for row in json.loads(self.output.read_text(encoding="utf-8"))
        }
        self.assertEqual(amounts["a"], 0)
        self.assertEqual(amounts["b"], 1200)
        self.assertEqual(amounts["c"], 10)
        self.assertEqual(amounts["d"], 10)
        self.assertEqual(amounts["e"], 1234)
        self.assertEqual(amounts["f"], 12345678901234567890123456789012)

    def test_rerun_is_byte_identical_and_sources_are_unchanged(self) -> None:
        first = self.write_csv("01.csv", HEADER + "b,Bob,2\na,Alice,0.10\n")
        second = self.write_csv("nested/02.csv", HEADER + "c,张三,1000.01\n")
        source_before = {path: path.read_bytes() for path in (first, second)}

        first_result = run_migrate(self.source, self.output)
        self.assertEqual(first_result.returncode, 0, msg=first_result.stderr)
        output_once = self.output.read_bytes()

        second_result = run_migrate(self.source, self.output)
        self.assertEqual(second_result.returncode, 0, msg=second_result.stderr)

        self.assertEqual(output_once, self.output.read_bytes())
        self.assertEqual(source_before, {path: path.read_bytes() for path in (first, second)})

    def test_quoted_customer_and_utf8_bom_header_are_supported(self) -> None:
        self.write_csv(
            "quoted.csv",
            HEADER + 'a,"张三, 李四",3.5\n',
            encoding="utf-8-sig",
        )

        result = run_migrate(self.source, self.output)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(
            json.loads(self.output.read_text(encoding="utf-8")),
            [{"id": "a", "customer": "张三, 李四", "amount_cents": 350}],
        )

    def test_empty_source_directory_writes_empty_array(self) -> None:
        result = run_migrate(self.source, self.output)

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(json.loads(self.output.read_text(encoding="utf-8")), [])

    def test_invalid_amounts_fail_without_creating_output(self) -> None:
        invalid_amounts = {
            "negative": "-1",
            "negative_zero": "-0",
            "nan": "NaN",
            "infinity": "Infinity",
            "exponent": "1e3",
            "three_decimals": "1.234",
            "empty": "",
            "trailing_dot": "12.",
            "leading_dot": ".5",
            "plus_sign": "+1",
            "leading_space": " 1",
            "fullwidth_digits": "１２",
        }

        for name, amount in invalid_amounts.items():
            with self.subTest(amount=amount):
                case_root = self.root / name
                case_source = case_root / "source"
                case_source.mkdir(parents=True)
                case_output = case_root / "output.json"
                (case_source / "bad.csv").write_text(
                    HEADER + f"a,Alice,{amount}\n", encoding="utf-8"
                )

                result = run_migrate(case_source, case_output)

                self.assert_failed(result)
                self.assertIn("invalid amount", result.stderr)
                self.assertFalse(case_output.exists())

    def test_empty_id_or_customer_fails(self) -> None:
        invalid_rows = {
            "empty_id": ",Alice,1",
            "blank_id": "   ,Alice,1",
            "empty_customer": "a,,1",
            "blank_customer": "a,   ,1",
        }

        for name, row in invalid_rows.items():
            with self.subTest(row=row):
                case_root = self.root / name
                case_source = case_root / "source"
                case_source.mkdir(parents=True)
                case_output = case_root / "output.json"
                (case_source / "bad.csv").write_text(HEADER + row + "\n", encoding="utf-8")

                result = run_migrate(case_source, case_output)

                self.assert_failed(result)
                self.assertIn("must not be empty", result.stderr)
                self.assertFalse(case_output.exists())

    def test_wrong_header_fails(self) -> None:
        invalid_headers = {
            "missing": "",
            "reordered": "customer,id,amount\n",
            "extra": "id,customer,amount,extra\n",
            "short": "id,customer\n",
        }

        for name, header in invalid_headers.items():
            with self.subTest(header=header):
                case_root = self.root / name
                case_source = case_root / "source"
                case_source.mkdir(parents=True)
                case_output = case_root / "output.json"
                (case_source / "bad.csv").write_text(header, encoding="utf-8")

                result = run_migrate(case_source, case_output)

                self.assert_failed(result)
                self.assertIn("header", result.stderr)
                self.assertFalse(case_output.exists())

    def test_wrong_field_count_fails(self) -> None:
        self.write_csv("bad.csv", HEADER + "a,Alice\n" + "b,Bob,1,extra\n")

        result = run_migrate(self.source, self.output)

        self.assert_failed(result)
        self.assertIn("fields", result.stderr)
        self.assertFalse(self.output.exists())

    def test_duplicate_ids_across_files_fail(self) -> None:
        self.write_csv("01.csv", HEADER + "same,Alice,1\n")
        self.write_csv("nested/02.csv", HEADER + "same,Bob,2\n")

        result = run_migrate(self.source, self.output)

        self.assert_failed(result)
        self.assertIn("duplicate id", result.stderr)
        self.assertIn("same", result.stderr)
        self.assertFalse(self.output.exists())

    def test_failure_preserves_existing_output_byte_for_byte(self) -> None:
        existing = b'{"keep": "this exactly"}\n'
        self.output.write_bytes(existing)
        self.write_csv("good.csv", HEADER + "a,Alice,1\n")
        self.write_csv("bad.csv", HEADER + "b,Bob,-1\n")

        result = run_migrate(self.source, self.output)

        self.assert_failed(result)
        self.assertEqual(self.output.read_bytes(), existing)
        self.assertEqual(
            sorted(path.name for path in self.root.iterdir()),
            ["output.json", "source"],
        )

    def test_missing_source_directory_fails(self) -> None:
        result = run_migrate(self.root / "does-not-exist", self.output)

        self.assert_failed(result)
        self.assertIn("source directory does not exist", result.stderr)
        self.assertFalse(self.output.exists())

    def test_missing_output_directory_fails_and_leaves_no_temp_file(self) -> None:
        self.write_csv("good.csv", HEADER + "a,Alice,1\n")
        output = self.root / "missing" / "output.json"

        result = run_migrate(self.source, output)

        self.assert_failed(result)
        self.assertIn("cannot write output", result.stderr)
        self.assertFalse(output.exists())
        self.assertFalse((self.root / "missing").exists())


class ReportTest(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self._temporary_directory.cleanup)
        self.root = Path(self._temporary_directory.name)
        self.ledger = self.root / "ledger.json"

    def write_ledger(self, rows: object) -> None:
        self.ledger.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def numbers(self, result: subprocess.CompletedProcess[str]) -> tuple[int, int]:
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2, msg=result.stdout)
        self.assertRegex(lines[0], r"^count=[0-9]+$")
        self.assertRegex(lines[1], r"^total_cents=[0-9]+$")
        return int(lines[0].split("=", 1)[1]), int(lines[1].split("=", 1)[1])

    def assert_report_failed(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertNotEqual(result.returncode, 0, msg=result.stdout)
        self.assertTrue(result.stderr.strip(), "failure should explain itself on stderr")

    def test_reports_every_row_with_default_threshold(self) -> None:
        self.write_ledger(
            [
                {"id": "a", "customer": "Alice", "amount_cents": 0},
                {"id": "b", "customer": "Bob", "amount_cents": 10},
                {"id": "c", "customer": "张三", "amount_cents": 100001},
            ]
        )
        before = self.ledger.read_bytes()

        result = run_report(self.ledger)

        self.assertEqual(self.numbers(result), (3, 100011))
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_customer_filter_is_exact_and_unmatched_is_zero(self) -> None:
        self.write_ledger(
            [
                {"id": "a", "customer": "Alice", "amount_cents": 10},
                {"id": "b", "customer": "Alice Smith", "amount_cents": 20},
                {"id": "c", "customer": "alice", "amount_cents": 40},
                {"id": "d", "customer": "张三", "amount_cents": 100001},
            ]
        )

        self.assertEqual(self.numbers(run_report(self.ledger, "--customer", "Alice")), (1, 10))
        self.assertEqual(self.numbers(run_report(self.ledger, "--customer", "张三")), (1, 100001))
        self.assertEqual(self.numbers(run_report(self.ledger, "--customer", "Nobody")), (0, 0))

    def test_min_cents_is_inclusive_and_combines_with_customer(self) -> None:
        self.write_ledger(
            [
                {"id": "a", "customer": "Alice", "amount_cents": 0},
                {"id": "b", "customer": "Bob", "amount_cents": 200},
                {"id": "c", "customer": "Bob", "amount_cents": 1234},
                {"id": "d", "customer": "张三", "amount_cents": 100001},
            ]
        )

        self.assertEqual(self.numbers(run_report(self.ledger, "--min-cents", "0")), (4, 101435))
        self.assertEqual(self.numbers(run_report(self.ledger, "--min-cents", "1234")), (2, 101235))
        self.assertEqual(self.numbers(run_report(self.ledger, "--min-cents", "1235")), (1, 100001))
        self.assertEqual(self.numbers(run_report(self.ledger, "--min-cents", "101436")), (0, 0))
        self.assertEqual(
            self.numbers(run_report(self.ledger, "--customer", "Bob", "--min-cents", "1000")),
            (1, 1234),
        )

    def test_invalid_min_cents_fails(self) -> None:
        self.write_ledger([{"id": "a", "customer": "Alice", "amount_cents": 10}])

        for value in ("-1", "1.5", "abc", "", "+1", " 1", "1e3", "１２"):
            with self.subTest(value=value):
                result = run_report(self.ledger, "--min-cents", value)

                self.assert_report_failed(result)
                self.assertIn("min-cents", result.stderr)

    def test_invalid_ledger_input_fails_without_modifying_file(self) -> None:
        invalid_contents = {
            "malformed": "{not json",
            "not_array": '{"id": "a"}\n',
            "row_not_object": '["a"]\n',
            "missing_amount": '[{"id": "a", "customer": "Alice"}]\n',
            "string_amount": '[{"id": "a", "customer": "Alice", "amount_cents": "10"}]\n',
            "bool_amount": '[{"id": "a", "customer": "Alice", "amount_cents": true}]\n',
            "negative_amount": '[{"id": "a", "customer": "Alice", "amount_cents": -1}]\n',
            "missing_id": '[{"customer": "Alice", "amount_cents": 1}]\n',
        }

        for name, content in invalid_contents.items():
            with self.subTest(name=name):
                case_ledger = self.root / f"{name}.json"
                case_ledger.write_text(content, encoding="utf-8")
                before = case_ledger.read_bytes()

                result = run_report(case_ledger)

                self.assert_report_failed(result)
                self.assertIn(str(case_ledger), result.stderr)
                self.assertEqual(case_ledger.read_bytes(), before)

    def test_missing_ledger_file_fails(self) -> None:
        result = run_report(self.root / "missing.json")

        self.assert_report_failed(result)
        self.assertIn("does not exist", result.stderr)


if __name__ == "__main__":
    unittest.main()
