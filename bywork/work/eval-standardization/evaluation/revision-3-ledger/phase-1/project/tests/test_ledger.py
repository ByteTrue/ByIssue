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

    def test_report_is_explicitly_not_implemented_yet(self) -> None:
        result = run_ledger("report", self.output)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not implemented", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
