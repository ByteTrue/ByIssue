import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "ledger.py"


def run_ledger(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(LEDGER), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MigrateTests(unittest.TestCase):
    def assert_fails_without_touching_output(
        self, source: Path, output: Path, sentinel: bytes, stderr_contains: str
    ) -> None:
        result = run_ledger("migrate", str(source), str(output))
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn(stderr_contains, result.stderr)
        self.assertTrue(output.read_bytes() == sentinel)

    def test_migrates_legacy_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out.json"
            sources = sorted((ROOT / "legacy").rglob("*.csv"))
            before = {path: sha256(path) for path in sources}

            result = run_ledger("migrate", "legacy", str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            data = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(
                data,
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
            for row in data:
                self.assertEqual(list(row), ["id", "customer", "amount_cents"])

            after = {path: sha256(path) for path in sources}
            self.assertEqual(before, after)

    def test_accepts_valid_amount_forms(self) -> None:
        cases = [
            ("a", "0", 0),
            ("b", "12", 1200),
            ("c", "0.1", 10),
            ("d", "0.10", 10),
            ("e", "0.01", 1),
            ("f", "12.34", 1234),
            ("g", "0.29", 29),
            ("h", "1.15", 115),
            ("i", "999999999999999999.99", 99999999999999999999),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            rows = "".join(
                f"{record_id},Customer,{amount}\n"
                for record_id, amount, _ in cases
            )
            (source / "input.csv").write_text(
                "id,customer,amount\n" + rows, encoding="utf-8"
            )
            output = Path(temporary) / "out.json"

            result = run_ledger("migrate", str(source), str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                [
                    {"id": record_id, "customer": "Customer", "amount_cents": cents}
                    for record_id, _, cents in cases
                ],
            )

    def test_sorts_by_id_across_nested_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            (source / "z").mkdir(parents=True)
            (source / "a.csv").write_text(
                "id,customer,amount\nb,Second,2\n", encoding="utf-8"
            )
            (source / "z" / "b.csv").write_text(
                "id,customer,amount\na,First,1\nc,Third,3\n", encoding="utf-8"
            )
            output = Path(temporary) / "out.json"

            result = run_ledger("migrate", str(source), str(output))

            self.assertEqual(result.returncode, 0, result.stderr)
            ids = [
                row["id"]
                for row in json.loads(output.read_text(encoding="utf-8"))
            ]
            self.assertEqual(ids, ["a", "b", "c"])

    def test_rejects_invalid_amounts_without_touching_output(self) -> None:
        invalid_amounts = [
            "-1",
            "-0",
            "NaN",
            "Infinity",
            "-Infinity",
            "1e3",
            "1E3",
            "1.234",
            "1.",
            ".5",
            "+1",
            " 1",
            "1 ",
            "",
            "0x10",
            "1_000",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            output = Path(temporary) / "out.json"
            sentinel = b'{"keep":"this byte for byte"}\n'
            output.write_bytes(sentinel)

            for amount in invalid_amounts:
                with self.subTest(amount=amount):
                    (source / "input.csv").write_text(
                        f"id,customer,amount\nx,Customer,{amount}\n",
                        encoding="utf-8",
                    )
                    self.assert_fails_without_touching_output(
                        source, output, sentinel, "invalid amount"
                    )

    def test_rejects_invalid_structure_without_touching_output(self) -> None:
        invalid_csvs = [
            "customer,id,amount\nx,Customer,1\n",
            "id,customer,amount,extra\nx,Customer,1\n",
            "id,customer\nx,Customer\n",
            "",
            "id,customer,amount\n,Customer,1\n",
            "id,customer,amount\n   ,Customer,1\n",
            "id,customer,amount\nx,,1\n",
            "id,customer,amount\nx,   ,1\n",
            "id,customer,amount\nx,Customer\n",
            "id,customer,amount\nx,Customer,1,extra\n",
            "id,customer,amount\nx,Customer,1\n\n",
            "id,customer,amount\nx,Customer,1\nx,Other,2\n",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            output = Path(temporary) / "out.json"
            sentinel = b"previous output\n"
            output.write_bytes(sentinel)

            for csv_text in invalid_csvs:
                with self.subTest(csv_text=csv_text):
                    (source / "input.csv").write_text(csv_text, encoding="utf-8")
                    result = run_ledger("migrate", str(source), str(output))
                    self.assertNotEqual(result.returncode, 0, result.stderr)
                    self.assertNotEqual(result.stderr, "")
                    self.assertEqual(output.read_bytes(), sentinel)

    def test_rejects_duplicate_id_across_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            (source / "nested").mkdir(parents=True)
            (source / "a.csv").write_text(
                "id,customer,amount\nduplicate,First,1\n", encoding="utf-8"
            )
            (source / "nested" / "b.csv").write_text(
                "id,customer,amount\nduplicate,Second,2\n", encoding="utf-8"
            )
            output = Path(temporary) / "out.json"
            sentinel = b"do not replace me\n"
            output.write_bytes(sentinel)

            result = run_ledger("migrate", str(source), str(output))

            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertIn("duplicate id", result.stderr)
            self.assertIn("duplicate", result.stderr)
            self.assertEqual(output.read_bytes(), sentinel)

    def test_failure_does_not_create_missing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source"
            source.mkdir()
            (source / "input.csv").write_text(
                "id,customer,amount\nx,Customer,not-a-number\n", encoding="utf-8"
            )
            output = Path(temporary) / "out.json"

            result = run_ledger("migrate", str(source), str(output))

            self.assertNotEqual(result.returncode, 0, result.stderr)
            self.assertFalse(output.exists())

    def test_rerun_is_byte_identical_and_sources_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output_one = Path(temporary) / "one.json"
            output_two = Path(temporary) / "two.json"
            sources = sorted((ROOT / "legacy").rglob("*.csv"))
            before = {path: sha256(path) for path in sources}

            first = run_ledger("migrate", "legacy", str(output_one))
            second = run_ledger("migrate", "legacy", str(output_two))
            rerun = run_ledger("migrate", "legacy", str(output_one))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual(output_one.read_bytes(), output_two.read_bytes())
            self.assertEqual(before, {path: sha256(path) for path in sources})

    def test_missing_source_directory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out.json"

            result = run_ledger(
                "migrate", str(Path(temporary) / "missing"), str(output)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("does not exist", result.stderr)
            self.assertFalse(output.exists())


class ReportTests(unittest.TestCase):
    def migrate_legacy(self, temporary: str) -> Path:
        output = Path(temporary) / "out.json"
        result = run_ledger("migrate", "legacy", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        return output

    def run_report(self, output: Path, *args: str) -> dict[str, int]:
        result = run_ledger("report", str(output), *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_reports_all_and_by_exact_customer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.migrate_legacy(temporary)
            before = sha256(output)

            self.assertEqual(
                self.run_report(output), {"count": 7, "total_cents": 101570}
            )
            self.assertEqual(
                self.run_report(output, "--customer", "Alice"),
                {"count": 3, "total_cents": 135},
            )
            self.assertEqual(
                self.run_report(output, "--customer", "张三"),
                {"count": 2, "total_cents": 100001},
            )
            self.assertEqual(
                self.run_report(
                    output, "--customer", "张三", "--min-cents", "100001"
                ),
                {"count": 1, "total_cents": 100001},
            )
            self.assertEqual(
                self.run_report(output, "--customer", "Ali"),
                {"count": 0, "total_cents": 0},
            )
            self.assertEqual(
                self.run_report(output, "--customer", "alice"),
                {"count": 0, "total_cents": 0},
            )
            self.assertEqual(before, sha256(output))

    def test_min_cents_filters_and_combines_with_customer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = self.migrate_legacy(temporary)
            before = sha256(output)

            self.assertEqual(
                self.run_report(output, "--min-cents", "200"),
                {"count": 3, "total_cents": 101435},
            )
            self.assertEqual(
                self.run_report(output, "--min-cents", "201"),
                {"count": 2, "total_cents": 101235},
            )
            self.assertEqual(
                self.run_report(
                    output, "--customer", "Bob", "--min-cents", "200"
                ),
                {"count": 2, "total_cents": 1434},
            )
            self.assertEqual(
                self.run_report(
                    output, "--customer", "Bob", "--min-cents", "1000"
                ),
                {"count": 1, "total_cents": 1234},
            )
            self.assertEqual(
                self.run_report(output, "--min-cents", "200000"),
                {"count": 0, "total_cents": 0},
            )
            self.assertEqual(before, sha256(output))

    def test_rejects_invalid_min_cents(self) -> None:
        invalid_values = ["-1", "-0", "1.5", "1.0", "abc", "1e3", "+1", " 1", "1 ", ""]
        with tempfile.TemporaryDirectory() as temporary:
            output = self.migrate_legacy(temporary)
            before = sha256(output)

            for value in invalid_values:
                with self.subTest(value=value):
                    result = run_ledger("report", str(output), "--min-cents", value)
                    self.assertNotEqual(result.returncode, 0, result.stderr)
                    self.assertNotEqual(result.stderr, "")
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(before, sha256(output))

    def test_report_rejects_bad_input(self) -> None:
        bad_inputs = [
            "not json\n",
            "{}\n",
            "[1]\n",
            '[{"amount_cents": 1}]\n',
            '[{"customer": "Alice"}]\n',
            '[{"customer": "Alice", "amount_cents": 1.5}]\n',
            '[{"customer": "Alice", "amount_cents": true}]\n',
            '[{"customer": "Alice", "amount_cents": -1}]\n',
        ]
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "out.json"

            for text in bad_inputs:
                with self.subTest(text=text):
                    output.write_text(text, encoding="utf-8")
                    before = sha256(output)
                    result = run_ledger("report", str(output))
                    self.assertNotEqual(result.returncode, 0, result.stderr)
                    self.assertNotEqual(result.stderr, "")
                    self.assertEqual(result.stdout, "")
                    self.assertEqual(before, sha256(output))

            missing = Path(temporary) / "missing.json"
            result = run_ledger("report", str(missing))
            self.assertNotEqual(result.returncode, 0)
            self.assertNotEqual(result.stderr, "")
            self.assertFalse(missing.exists())


if __name__ == "__main__":
    unittest.main()
