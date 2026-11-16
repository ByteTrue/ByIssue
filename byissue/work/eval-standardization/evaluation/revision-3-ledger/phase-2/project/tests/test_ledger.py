"""Regression checks for ledger.py's migrate command.

Run with:
    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(PROJECT_ROOT, "ledger.py")
LEGACY = os.path.join(PROJECT_ROOT, "legacy")
SENTINEL = b"existing output that must survive failures\n"


def run_ledger(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, LEDGER, *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def write_bytes(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(data)


def read_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


class MigrateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.source = os.path.join(self.tmp, "source")
        self.output = os.path.join(self.tmp, "output.json")
        os.makedirs(self.source)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def migrate(self) -> subprocess.CompletedProcess:
        return run_ledger("migrate", self.source, self.output)

    def load(self) -> list[dict]:
        with open(self.output, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def add_csv(self, relative: str, text: str) -> None:
        write_text(os.path.join(self.source, relative), text)

    def assert_fails_without_touching_output(self, csv_text: str) -> None:
        self.add_csv("bad.csv", csv_text)
        write_bytes(self.output, SENTINEL)
        result = self.migrate()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip(), "failure must explain itself on stderr")
        self.assertEqual(read_bytes(self.output), SENTINEL)

    def test_migrates_legacy_tree(self) -> None:
        before = {
            path: hashlib.sha256(read_bytes(path)).hexdigest()
            for path in self.walk(LEGACY)
        }

        result = run_ledger("migrate", LEGACY, self.output)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            self.load(),
            [
                {"id": "a001", "customer": "Alice", "amount_cents": 10},
                {"id": "a002", "customer": "Alice", "amount_cents": 20},
                {"id": "a003", "customer": "Alice", "amount_cents": 105},
                {"id": "b001", "customer": "Bob", "amount_cents": 1234},
                {"id": "b002", "customer": "Bob", "amount_cents": 200},
                {"id": "c001", "customer": "张三", "amount_cents": 100001},
                {"id": "c002", "customer": "张三", "amount_cents": 0},
            ],
        )
        for row in self.load():
            self.assertEqual(list(row.keys()), ["id", "customer", "amount_cents"])

        after = {
            path: hashlib.sha256(read_bytes(path)).hexdigest()
            for path in self.walk(LEGACY)
        }
        self.assertEqual(before, after, "migrate must not modify source CSV files")

    @staticmethod
    def walk(directory: str) -> list[str]:
        paths = []
        for root, dirs, files in os.walk(directory):
            dirs.sort()
            for name in sorted(files):
                if name.endswith(".csv"):
                    paths.append(os.path.join(root, name))
        return paths

    def test_recurses_into_subdirectories(self) -> None:
        self.add_csv("top.csv", "id,customer,amount\nb,Bob,1\n")
        self.add_csv("deep/deeper/nested.csv", "id,customer,amount\na,Alice,2\n")

        result = self.migrate()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.load(),
            [
                {"id": "a", "customer": "Alice", "amount_cents": 200},
                {"id": "b", "customer": "Bob", "amount_cents": 100},
            ],
        )

    def test_rerun_is_byte_identical(self) -> None:
        self.add_csv("a.csv", "id,customer,amount\nx,Alice,0.10\ny,Bob,12.34\n")
        self.assertEqual(self.migrate().returncode, 0)
        first = read_bytes(self.output)
        self.assertEqual(self.migrate().returncode, 0)
        self.assertEqual(read_bytes(self.output), first)

    def test_accepts_boundary_amounts_and_keeps_exact_cents(self) -> None:
        self.add_csv(
            "a.csv",
            "id,customer,amount\n"
            "a,Alice,0\n"
            "b,Alice,12\n"
            "c,Alice,0.10\n"
            "d,Alice,12.34\n"
            "e,Alice,00.05\n"
            "f,Alice,999999999999999999.99\n",
        )

        result = self.migrate()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            [row["amount_cents"] for row in self.load()],
            [0, 1200, 10, 1234, 5, 99999999999999999999],
        )

    def test_rejects_invalid_amounts_without_replacing_output(self) -> None:
        cases = ["-1", "-0.10", "NaN", "Infinity", "inf", "1e3", "1.234", "", "12.", ".5", " 1 "]
        for amount in cases:
            with self.subTest(amount=amount):
                with tempfile.TemporaryDirectory() as work:
                    self.source = os.path.join(work, "source")
                    self.output = os.path.join(work, "output.json")
                    os.makedirs(self.source)
                    self.assert_fails_without_touching_output(
                        f"id,customer,amount\na,Alice,{amount}\n"
                    )

    def test_rejects_negative_zero(self) -> None:
        self.assert_fails_without_touching_output("id,customer,amount\na,Alice,-0\n")

    def test_rejects_duplicate_ids_across_files(self) -> None:
        self.add_csv("one.csv", "id,customer,amount\ndup,Alice,1\n")
        self.add_csv("nested/two.csv", "id,customer,amount\ndup,Bob,2\n")
        write_bytes(self.output, SENTINEL)

        result = self.migrate()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate id", result.stderr)
        self.assertEqual(read_bytes(self.output), SENTINEL)

    def test_rejects_wrong_headers(self) -> None:
        headers = [
            "id,customer\n",
            "id,customer,amount,extra\n",
            "id,name,amount\n",
            "ID,CUSTOMER,AMOUNT\n",
            "",
        ]
        for header in headers:
            with self.subTest(header=header):
                with tempfile.TemporaryDirectory() as work:
                    self.source = os.path.join(work, "source")
                    self.output = os.path.join(work, "output.json")
                    os.makedirs(self.source)
                    self.assert_fails_without_touching_output(header + "a,Alice,1\n")

    def test_rejects_empty_id_or_customer(self) -> None:
        for row in [",Alice,1", "a,,1", "  ,Alice,1", "a,   ,1"]:
            with self.subTest(row=row):
                with tempfile.TemporaryDirectory() as work:
                    self.source = os.path.join(work, "source")
                    self.output = os.path.join(work, "output.json")
                    os.makedirs(self.source)
                    self.assert_fails_without_touching_output(
                        f"id,customer,amount\n{row}\n"
                    )

    def test_rejects_wrong_column_count(self) -> None:
        self.assert_fails_without_touching_output(
            "id,customer,amount\na,Alice,1,extra\n"
        )

    def test_rejects_invalid_utf8(self) -> None:
        write_bytes(
            os.path.join(self.source, "bad.csv"),
            b"id,customer,amount\na,Alice,\xff\n",
        )
        write_bytes(self.output, SENTINEL)

        result = self.migrate()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_bytes(self.output), SENTINEL)

    def test_failure_in_later_file_keeps_old_output(self) -> None:
        self.add_csv("a_good.csv", "id,customer,amount\nok,Alice,1\n")
        self.add_csv("z_bad.csv", "id,customer,amount\nbad,Bob,1.234\n")
        write_bytes(self.output, SENTINEL)

        result = self.migrate()

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(read_bytes(self.output), SENTINEL)

    def test_accepts_utf8_bom_and_crlf(self) -> None:
        write_bytes(
            os.path.join(self.source, "bom.csv"),
            b"\xef\xbb\xbfid,customer,amount\r\na,Alice,1.05\r\n",
        )

        result = self.migrate()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            self.load(), [{"id": "a", "customer": "Alice", "amount_cents": 105}]
        )

    def test_empty_source_directory_writes_empty_array(self) -> None:
        result = self.migrate()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.load(), [])

    def test_missing_source_directory_fails(self) -> None:
        missing = os.path.join(self.tmp, "missing")
        write_bytes(self.output, SENTINEL)

        result = run_ledger("migrate", missing, self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(read_bytes(self.output), SENTINEL)

    def test_missing_output_directory_fails_without_writing(self) -> None:
        self.add_csv("a.csv", "id,customer,amount\na,Alice,1\n")
        missing_dir_output = os.path.join(self.tmp, "no-such-dir", "out.json")

        result = run_ledger("migrate", self.source, missing_dir_output)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertFalse(os.path.exists(missing_dir_output))

class ReportTest(unittest.TestCase):
    """Checks for the report command against the real CLI entry point."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = self._tmp.name
        self.output = os.path.join(self.tmp, "output.json")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def migrate_legacy(self) -> None:
        result = run_ledger("migrate", LEGACY, self.output)
        self.assertEqual(result.returncode, 0, result.stderr)

    def write_records(self, records: list[dict]) -> None:
        write_text(self.output, json.dumps(records, ensure_ascii=False) + "\n")

    def report(self, *args: str) -> subprocess.CompletedProcess:
        return run_ledger("report", self.output, *args)

    def summary(self, *args: str) -> dict:
        result = self.report(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_reports_all_records_by_default(self) -> None:
        self.migrate_legacy()

        result = self.report()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        summary = json.loads(result.stdout)
        self.assertEqual(summary, {"count": 7, "total_cents": 101570})
        self.assertEqual(list(summary), ["count", "total_cents"])
        for value in summary.values():
            self.assertIs(type(value), int)

    def test_filters_by_exact_customer_name(self) -> None:
        self.migrate_legacy()
        cases = {
            "Alice": {"count": 3, "total_cents": 135},
            "Bob": {"count": 2, "total_cents": 1434},
            "张三": {"count": 2, "total_cents": 100001},
            "Ali": {"count": 0, "total_cents": 0},
            "alice": {"count": 0, "total_cents": 0},
            "张三丰": {"count": 0, "total_cents": 0},
        }
        for customer, expected in cases.items():
            with self.subTest(customer=customer):
                self.assertEqual(self.summary("--customer", customer), expected)

    def test_unknown_customer_reports_zero_with_success(self) -> None:
        self.migrate_legacy()

        result = self.report("--customer", "Nobody")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout), {"count": 0, "total_cents": 0}
        )

    def test_min_cents_threshold_is_inclusive(self) -> None:
        self.write_records(
            [
                {"id": "a", "customer": "Alice", "amount_cents": 0},
                {"id": "b", "customer": "Alice", "amount_cents": 9},
                {"id": "c", "customer": "Alice", "amount_cents": 10},
                {"id": "d", "customer": "Bob", "amount_cents": 11},
                {"id": "e", "customer": "Bob", "amount_cents": 100001},
            ]
        )

        self.assertEqual(
            self.summary("--min-cents", "10"),
            {"count": 3, "total_cents": 100022},
        )
        self.assertEqual(
            self.summary("--min-cents=11"),
            {"count": 2, "total_cents": 100012},
        )
        self.assertEqual(
            self.summary("--min-cents", "100001"),
            {"count": 1, "total_cents": 100001},
        )
        self.assertEqual(
            self.summary("--min-cents", "100002"),
            {"count": 0, "total_cents": 0},
        )

    def test_min_cents_defaults_to_zero(self) -> None:
        self.migrate_legacy()

        default = self.summary()

        self.assertEqual(default, self.summary("--min-cents", "0"))
        self.assertEqual(default, {"count": 7, "total_cents": 101570})

    def test_combines_customer_and_min_cents(self) -> None:
        self.migrate_legacy()

        self.assertEqual(
            self.summary("--customer", "Alice", "--min-cents", "105"),
            {"count": 1, "total_cents": 105},
        )
        self.assertEqual(
            self.summary("--min-cents", "106", "--customer", "Alice"),
            {"count": 0, "total_cents": 0},
        )
        self.assertEqual(
            self.summary("--customer", "Bob", "--min-cents", "200"),
            {"count": 2, "total_cents": 1434},
        )

    def test_rejects_invalid_min_cents(self) -> None:
        self.migrate_legacy()
        before = read_bytes(self.output)
        cases = ["-1", "1.5", "abc", "", "1e3", " 5", "3.0", "-0", "٠"]

        for value in cases:
            with self.subTest(value=value):
                result = self.report("--min-cents", value)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.strip())
                self.assertEqual(result.stdout, "")
                self.assertEqual(read_bytes(self.output), before)

    def test_rejects_min_cents_without_value(self) -> None:
        self.migrate_legacy()

        result = self.report("--min-cents")

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")

    def test_accepts_large_threshold_and_keeps_exact_total(self) -> None:
        self.write_records(
            [
                {"id": "a", "customer": "Alice", "amount_cents": 10**30},
                {"id": "b", "customer": "Alice", "amount_cents": 10**30 - 1},
            ]
        )

        self.assertEqual(
            self.summary("--min-cents", str(10**30)),
            {"count": 1, "total_cents": 10**30},
        )

    def test_empty_array_reports_zero(self) -> None:
        self.write_records([])

        self.assertEqual(self.summary(), {"count": 0, "total_cents": 0})
        self.assertEqual(
            self.summary("--customer", "Alice", "--min-cents", "5"),
            {"count": 0, "total_cents": 0},
        )

    def test_report_does_not_modify_its_inputs(self) -> None:
        self.migrate_legacy()
        watched = {
            path: hashlib.sha256(read_bytes(path)).hexdigest()
            for path in [self.output, *MigrateTest.walk(LEGACY)]
        }

        result = self.report("--customer", "Alice", "--min-cents", "0")

        self.assertEqual(result.returncode, 0, result.stderr)
        for path, digest in watched.items():
            self.assertEqual(
                hashlib.sha256(read_bytes(path)).hexdigest(), digest, path
            )
        self.assertEqual(os.listdir(self.tmp), ["output.json"])

    def test_missing_input_file_fails(self) -> None:
        self.output = os.path.join(self.tmp, "missing.json")

        result = self.report()

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")
        self.assertFalse(os.path.exists(self.output))

    def test_malformed_json_fails(self) -> None:
        write_text(self.output, "{not json")

        result = self.report()

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")

    def test_non_array_json_fails(self) -> None:
        write_text(self.output, '{"count": 1}\n')

        result = self.report()

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(result.stderr.strip())
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
