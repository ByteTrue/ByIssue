#!/usr/bin/env python3
"""Migrate legacy bill CSV files into a JSON ledger with integer cents.

Usage:
    python3 ledger.py migrate <source-dir> <output.json>
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path

HEADER = ["id", "customer", "amount"]
AMOUNT_RE = re.compile(r"^[0-9]+(?:\.[0-9]{1,2})?$")


class LedgerError(Exception):
    """A data or input error that should be reported without a traceback."""


def parse_amount_cents(text: str, path: Path, line: int) -> int:
    """Convert a decimal amount string to integer cents without using floats."""
    if not AMOUNT_RE.fullmatch(text):
        raise LedgerError(
            f"{path}:{line}: invalid amount {text!r}; expected a non-negative "
            "decimal with at most two decimal places"
        )
    if "." in text:
        whole, fraction = text.split(".", 1)
    else:
        whole, fraction = text, ""
    fraction = fraction.ljust(2, "0")
    return int(whole) * 100 + int(fraction)


def read_csv_file(path: Path, rows: dict[str, dict], locations: dict[str, str]) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            if header != HEADER:
                raise LedgerError(
                    f"{path}: invalid header {header!r}; expected {HEADER!r}"
                )
            for line, row in enumerate(reader, start=2):
                if not row:
                    continue
                if len(row) != 3:
                    raise LedgerError(
                        f"{path}:{line}: expected 3 columns, got {len(row)}"
                    )
                record_id, customer, amount = row
                if not record_id.strip():
                    raise LedgerError(f"{path}:{line}: id must not be empty")
                if not customer.strip():
                    raise LedgerError(f"{path}:{line}: customer must not be empty")
                where = f"{path}:{line}"
                if record_id in rows:
                    raise LedgerError(
                        f"{where}: duplicate id {record_id!r}; "
                        f"first seen at {locations[record_id]}"
                    )
                rows[record_id] = {
                    "id": record_id,
                    "customer": customer,
                    "amount_cents": parse_amount_cents(amount, path, line),
                }
                locations[record_id] = where
    except UnicodeDecodeError as exc:
        raise LedgerError(f"{path}: not valid UTF-8: {exc}") from exc
    except OSError as exc:
        raise LedgerError(f"{path}: cannot read: {exc}") from exc


def collect_records(source_dir: Path) -> list[dict]:
    if not source_dir.exists():
        raise LedgerError(f"{source_dir}: source directory does not exist")
    if not source_dir.is_dir():
        raise LedgerError(f"{source_dir}: source is not a directory")

    files = sorted(
        (path for path in source_dir.rglob("*") if path.is_file() and path.suffix.lower() == ".csv"),
        key=lambda path: path.relative_to(source_dir).as_posix(),
    )
    rows: dict[str, dict] = {}
    locations: dict[str, str] = {}
    for path in files:
        read_csv_file(path, rows, locations)
    return [rows[record_id] for record_id in sorted(rows)]


def write_output(output_path: Path, records: list[dict]) -> None:
    """Write atomically so a failed run never changes an existing output file."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
        fd, temp_name = tempfile.mkstemp(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=str(output_path.parent)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, output_path)
        except BaseException:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise LedgerError(f"{output_path}: cannot write output: {exc}") from exc


def migrate(source_dir: Path, output_path: Path) -> None:
    records = collect_records(source_dir)
    write_output(output_path, records)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger.py", description="Migrate and report on bill CSV ledgers."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    migrate_parser = subparsers.add_parser(
        "migrate", help="Migrate every CSV under a directory into one JSON file."
    )
    migrate_parser.add_argument("source_dir", type=Path)
    migrate_parser.add_argument("output_json", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "migrate":
        try:
            migrate(args.source_dir, args.output_json)
        except LedgerError as exc:
            print(f"ledger.py: error: {exc}", file=sys.stderr)
            return 1
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
