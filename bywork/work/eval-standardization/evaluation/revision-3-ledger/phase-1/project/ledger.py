#!/usr/bin/env python3
"""Migrate legacy CSV ledgers into exact JSON amounts.

Usage:
    python3 ledger.py migrate <source-dir> <output.json>
    python3 ledger.py report <output.json> [--customer <name>]

Only the migrate command is implemented in this round.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile

HEADER = ["id", "customer", "amount"]
AMOUNT_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]{1,2})?\Z")


class MigrationError(Exception):
    """A user-facing migration failure."""


def parse_amount_cents(text: str, where: str) -> int:
    """Convert a validated decimal amount string to integer cents exactly."""
    value = text
    if not AMOUNT_PATTERN.match(value):
        raise MigrationError(f"{where}: invalid amount {text!r}")

    whole, dot, fraction = value.partition(".")
    if not dot:
        fraction = ""
    fraction = (fraction + "00")[:2]
    return int(whole) * 100 + int(fraction)


def csv_files(source_dir: str) -> list[str]:
    if not os.path.isdir(source_dir):
        raise MigrationError(f"source directory does not exist: {source_dir}")

    found = []
    for root, dirs, files in os.walk(source_dir):
        dirs.sort()
        for name in sorted(files):
            if name.lower().endswith(".csv"):
                found.append(os.path.join(root, name))
    return found


def read_rows(path: str) -> list[dict]:
    records = []
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                raise MigrationError(f"{path}: empty file, expected header {','.join(HEADER)}")
            except csv.Error as exc:
                raise MigrationError(f"{path}: malformed CSV: {exc}")

            if header != HEADER:
                got = ",".join(header)
                raise MigrationError(
                    f"{path}: bad header {got!r}, expected {','.join(HEADER)!r}"
                )

            try:
                for line_no, row in enumerate(reader, start=2):
                    where = f"{path}:{line_no}"
                    if len(row) != len(HEADER):
                        raise MigrationError(
                            f"{where}: expected {len(HEADER)} columns, got {len(row)}"
                        )
                    record_id, customer, amount = row
                    if not record_id.strip():
                        raise MigrationError(f"{where}: id must not be empty")
                    if not customer.strip():
                        raise MigrationError(f"{where}: customer must not be empty")
                    records.append(
                        {
                            "id": record_id,
                            "customer": customer,
                            "amount_cents": parse_amount_cents(amount, where),
                        }
                    )
            except csv.Error as exc:
                raise MigrationError(f"{path}: malformed CSV: {exc}")
    except UnicodeDecodeError as exc:
        raise MigrationError(f"{path}: not valid UTF-8: {exc}")

    return records


def collect_records(source_dir: str) -> list[dict]:
    merged = {}
    origin = {}
    for path in csv_files(source_dir):
        for record in read_rows(path):
            record_id = record["id"]
            if record_id in merged:
                raise MigrationError(
                    f"{path}: duplicate id {record_id!r}, first seen in {origin[record_id]}"
                )
            merged[record_id] = record
            origin[record_id] = path

    return sorted(merged.values(), key=lambda record: record["id"])


def write_atomically(path: str, text: str) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(directory):
        raise MigrationError(f"output directory does not exist: {directory}")

    fd, temporary = tempfile.mkstemp(dir=directory, prefix=".ledger-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def migrate(source_dir: str, output_path: str) -> None:
    records = collect_records(source_dir)
    text = json.dumps(records, ensure_ascii=False, indent=2) + "\n"
    write_atomically(output_path, text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger.py")
    commands = parser.add_subparsers(dest="command", required=True)

    migrate_parser = commands.add_parser("migrate", help="migrate CSV files to JSON")
    migrate_parser.add_argument("source_dir")
    migrate_parser.add_argument("output_json")

    report_parser = commands.add_parser("report", help="summarize a migrated JSON file")
    report_parser.add_argument("output_json")
    report_parser.add_argument("--customer")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "report":
        print("ledger.py: report is not implemented yet", file=sys.stderr)
        return 2

    try:
        migrate(args.source_dir, args.output_json)
    except (MigrationError, OSError) as exc:
        print(f"ledger.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
