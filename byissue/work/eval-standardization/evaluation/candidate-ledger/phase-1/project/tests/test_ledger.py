"""Regression checks for the ledger.py migrate CLI.

Run from the project root:
    python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger.py"
LEGACY = ROOT / "legacy"


def run_migrate(source_dir: Path, output_json: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(LEDGER), "migrate", str(source_dir), str(output_json)],
        capture_output=True,
        text=True,
    )


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MigrateTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work = Path(self.temp_dir.name)

    def write_csv(self, relative_path: str, content: str) -> Path:
        path = self.work / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def migrate_ok(self, source: Path, output: Path) -> list[dict]:
        result = run_migrate(source, output)
        self.assertEqual(
            result.returncode, 0, msg=f"stderr: {result.stderr}\nstdout: {result.stdout}"
        )
        return json.loads(output.read_text(encoding="utf-8"))

    def assert_migrate_fails(self, source: Path, output: Path, message_part: str) -> None:
        result = run_migrate(source, output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message_part, result.stderr)
        self.assertEqual(result.stdout, "")


class LegacyMigrationTests(MigrateTestCase):
    def test_legacy_tree_migrates_recursively_in_id_order(self) -> None:
        output = self.work / "output.json"
        records = self.migrate_ok(LEGACY, output)

        self.assertEqual(
            records,
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
        self.assertEqual([record["id"] for record in records], sorted(r["id"] for r in records))
        for record in records:
            self.assertEqual(list(record), ["id", "customer", "amount_cents"])
            self.assertIsInstance(record["amount_cents"], int)

    def test_rerun_is_byte_identical_and_inputs_are_untouched(self) -> None:
        csv_files = sorted(LEGACY.rglob("*.csv"))
        before = {path: file_hash(path) for path in csv_files}

        first = self.work / "first.json"
        second = self.work / "second.json"
        self.migrate_ok(LEGACY, first)
        self.migrate_ok(LEGACY, second)

        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(before, {path: file_hash(path) for path in csv_files})


class AmountTests(MigrateTestCase):
    def test_valid_amounts_convert_exactly(self) -> None:
        source = self.work / "source"
        self.write_csv(
            "source/amounts.csv",
            "id,customer,amount\n"
            "a,Zero,0\n"
            "b,Whole,12\n"
            "c,TenCents,0.10\n"
            "d,Cents,12.34\n"
            "e,OneDecimal,0.1\n"
            "f,ZeroPadded,00.10\n"
            "g,Max,999999999999999999.99\n",
        )
        records = self.migrate_ok(source, self.work / "output.json")

        self.assertEqual(
            {record["id"]: record["amount_cents"] for record in records},
            {
                "a": 0,
                "b": 1200,
                "c": 10,
                "d": 1234,
                "e": 10,
                "f": 10,
                "g": 99999999999999999999,
            },
        )

    def test_invalid_amounts_are_rejected(self) -> None:
        invalid = ["-1", "-0.01", "NaN", "Infinity", "-Infinity", "1e2", "1.234", "1.", ".5", "+1", " 12", "12 ", "abc", ""]
        for index, amount in enumerate(invalid):
            with self.subTest(amount=amount):
                source = self.work / f"bad-{index}"
                self.write_csv(
                    f"bad-{index}/rows.csv",
                    f"id,customer,amount\na,Alice,{amount}\n",
                )
                self.assert_migrate_fails(source, self.work / f"out-{index}.json", "invalid amount")


class ValidationTests(MigrateTestCase):
    def test_wrong_header_is_rejected(self) -> None:
        source = self.work / "source"
        self.write_csv("source/rows.csv", "id,name,amount\na,Alice,1\n")
        self.assert_migrate_fails(source, self.work / "output.json", "invalid header")

    def test_missing_header_is_rejected(self) -> None:
        source = self.work / "source"
        self.write_csv("source/empty.csv", "")
        self.assert_migrate_fails(source, self.work / "output.json", "invalid header")

    def test_empty_id_or_customer_is_rejected(self) -> None:
        cases = {
            "empty-id": "id,customer,amount\n,Alice,1\n",
            "blank-id": "id,customer,amount\n   ,Alice,1\n",
            "empty-customer": "id,customer,amount\na,,1\n",
            "blank-customer": "id,customer,amount\na,   ,1\n",
        }
        for name, content in cases.items():
            with self.subTest(case=name):
                source = self.work / name
                self.write_csv(f"{name}/rows.csv", content)
                self.assert_migrate_fails(
                    source, self.work / f"{name}.json", "must not be empty"
                )

    def test_wrong_column_count_is_rejected(self) -> None:
        source = self.work / "source"
        self.write_csv("source/rows.csv", "id,customer,amount\na,Alice\n")
        self.assert_migrate_fails(source, self.work / "output.json", "expected 3 columns")

    def test_duplicate_id_across_files_is_rejected(self) -> None:
        source = self.work / "source"
        self.write_csv("source/a.csv", "id,customer,amount\nsame,Alice,1\n")
        self.write_csv("source/nested/b.csv", "id,customer,amount\nsame,Bob,2\n")
        self.assert_migrate_fails(source, self.work / "output.json", "duplicate id")

    def test_missing_source_directory_is_rejected(self) -> None:
        self.assert_migrate_fails(
            self.work / "does-not-exist", self.work / "output.json", "does not exist"
        )


class OutputSafetyTests(MigrateTestCase):
    def test_failure_keeps_existing_output_byte_for_byte(self) -> None:
        source = self.work / "source"
        self.write_csv("source/a.csv", "id,customer,amount\na,Alice,1\n")
        self.write_csv("source/b.csv", "id,customer,amount\na,Bob,2\n")
        output = self.work / "output.json"
        original = b'{"previous": true}\n'
        output.write_bytes(original)

        result = run_migrate(source, output)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip() != "", True)
        self.assertEqual(output.read_bytes(), original)
        self.assertEqual(
            sorted(path.name for path in self.work.iterdir() if path.is_file()),
            ["output.json"],
        )

    def test_failure_does_not_create_output_when_absent(self) -> None:
        source = self.work / "source"
        self.write_csv("source/a.csv", "id,customer,amount\na,Alice,bad\n")
        output = self.work / "output.json"

        result = run_migrate(source, output)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(output.exists())

    def test_empty_source_produces_empty_array(self) -> None:
        source = self.work / "source"
        source.mkdir()
        (source / "notes.txt").write_text("not a csv\n", encoding="utf-8")
        records = self.migrate_ok(source, self.work / "output.json")
        self.assertEqual(records, [])

    def test_output_parent_directory_is_created(self) -> None:
        source = self.work / "source"
        self.write_csv("source/a.csv", "id,customer,amount\na,Alice,1\n")
        output = self.work / "nested" / "dir" / "output.json"
        records = self.migrate_ok(source, output)
        self.assertEqual(records, [{"id": "a", "customer": "Alice", "amount_cents": 100}])


class CsvFormatTests(MigrateTestCase):
    def test_quoted_comma_bom_and_crlf_are_handled(self) -> None:
        source = self.work / "source"
        path = source / "rows.csv"
        source.mkdir()
        path.write_bytes(
            b"\xef\xbb\xbfid,customer,amount\r\n"
            b'a,"Smith, Jane",1.20\r\n'
            b'b,Alice,2\r\n'
        )
        records = self.migrate_ok(source, self.work / "output.json")
        self.assertEqual(
            records,
            [
                {"id": "a", "customer": "Smith, Jane", "amount_cents": 120},
                {"id": "b", "customer": "Alice", "amount_cents": 200},
            ],
        )

    def test_id_sorting_is_lexicographic(self) -> None:
        source = self.work / "source"
        self.write_csv(
            "source/rows.csv",
            "id,customer,amount\nb,Alice,1\na,Alice,1\n10,Alice,1\n2,Alice,1\n",
        )
        records = self.migrate_ok(source, self.work / "output.json")
        self.assertEqual([record["id"] for record in records], ["10", "2", "a", "b"])


if __name__ == "__main__":
    unittest.main()
