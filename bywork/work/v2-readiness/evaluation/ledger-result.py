#!/usr/bin/env python3
"""Migrate legacy CSV billing exports into one JSON ledger.

Usage:
    python3 ledger.py migrate <source-dir> <output.json>
    python3 ledger.py report <output.json> [--customer NAME] [--min-cents N]

Every CSV under <source-dir> (recursively) must use the header
``id,customer,amount``. Amounts are non-negative decimals with at most two
fraction digits. They are converted to integer cents without ever going
through binary floating point.

The output file is written atomically and only after every input row has
passed validation, so a failed run leaves an existing output untouched.

``report`` reads that output file and prints a JSON object with ``count`` and
``total_cents`` for the rows that match the optional customer and minimum
amount filters. It never modifies the ledger file.
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

EXPECTED_HEADER = ["id", "customer", "amount"]
AMOUNT_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]{1,2})?")


class MigrationError(Exception):
    """A problem with the input data or an I/O failure."""


def parse_amount_cents(raw: str) -> int:
    """Return the exact cent value of a decimal amount string."""
    if not AMOUNT_PATTERN.fullmatch(raw):
        raise ValueError(
            "amount must be a non-negative decimal with at most two fraction "
            f"digits, got {raw!r}"
        )
    if "." in raw:
        whole, fraction = raw.split(".")
        fraction = fraction.ljust(2, "0")
    else:
        whole, fraction = raw, "00"
    return int(whole) * 100 + int(fraction)


def find_csv_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        raise MigrationError(f"source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise MigrationError(f"source path is not a directory: {source_dir}")
    files = [
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".csv"
    ]
    return sorted(files, key=lambda path: path.as_posix())


def read_csv_rows(path: Path, rows: list[dict], seen_ids: dict[str, str]) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            try:
                header = next(reader)
            except StopIteration:
                raise MigrationError(f"{path}: file is empty, missing header") from None
            if header != EXPECTED_HEADER:
                raise MigrationError(
                    f"{path}: header must be {','.join(EXPECTED_HEADER)}, "
                    f"got {','.join(header)}"
                )
            for line_number, record in enumerate(reader, start=2):
                location = f"{path}:{line_number}"
                if len(record) != 3:
                    raise MigrationError(
                        f"{location}: expected 3 fields, got {len(record)}"
                    )
                record_id, customer, raw_amount = record
                if record_id == "":
                    raise MigrationError(f"{location}: id must not be empty")
                if customer == "":
                    raise MigrationError(f"{location}: customer must not be empty")
                try:
                    amount_cents = parse_amount_cents(raw_amount)
                except ValueError as error:
                    raise MigrationError(f"{location}: {error}") from None
                if record_id in seen_ids:
                    raise MigrationError(
                        f"{location}: duplicate id {record_id!r} "
                        f"(first seen at {seen_ids[record_id]})"
                    )
                seen_ids[record_id] = location
                rows.append(
                    {
                        "id": record_id,
                        "customer": customer,
                        "amount_cents": amount_cents,
                    }
                )
    except OSError as error:
        raise MigrationError(f"{path}: cannot read file: {error}") from None
    except UnicodeDecodeError as error:
        raise MigrationError(f"{path}: cannot decode as UTF-8: {error}") from None


def write_atomic(path: Path, text: str) -> None:
    """Write text to path via a temporary file and an atomic rename."""
    parent = path.parent
    try:
        descriptor, tmp_name = tempfile.mkstemp(
            dir=str(parent), prefix=f".{path.name}.", suffix=".tmp"
        )
    except OSError as error:
        raise MigrationError(f"{path}: cannot write output: {error}") from None
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except OSError as error:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise MigrationError(f"{path}: cannot write output: {error}") from None


def load_ledger(path: Path) -> list[dict]:
    """Read and validate a ledger written by the migrate command."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise MigrationError(f"{path}: cannot read ledger: {error}") from None
    except UnicodeDecodeError as error:
        raise MigrationError(f"{path}: cannot decode as UTF-8: {error}") from None
    try:
        rows = json.loads(text)
    except json.JSONDecodeError as error:
        raise MigrationError(f"{path}: invalid JSON: {error}") from None
    if not isinstance(rows, list):
        raise MigrationError(f"{path}: ledger must be a JSON array")
    for index, row in enumerate(rows):
        location = f"{path}: row {index}"
        if not isinstance(row, dict):
            raise MigrationError(f"{location}: expected a JSON object")
        for field in ("id", "customer"):
            if not isinstance(row.get(field), str):
                raise MigrationError(f"{location}: {field} must be a string")
        if type(row.get("amount_cents")) is not int:
            raise MigrationError(f"{location}: amount_cents must be an integer")
        if row["amount_cents"] < 0:
            raise MigrationError(f"{location}: amount_cents must not be negative")
    return rows


def non_negative_int(raw: str) -> int:
    """argparse type for --min-cents: an integer that is not negative."""
    try:
        value = int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be a non-negative integer, got {raw!r}"
        ) from None
    if value < 0:
        raise argparse.ArgumentTypeError(
            f"must be a non-negative integer, got {raw!r}"
        )
    return value


def cmd_migrate(source_dir: Path, output: Path) -> int:
    files = find_csv_files(source_dir)
    rows: list[dict] = []
    seen_ids: dict[str, str] = {}
    for path in files:
        read_csv_rows(path, rows, seen_ids)
    rows.sort(key=lambda row: row["id"])
    text = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    write_atomic(output, text)
    return 0


def cmd_report(ledger: Path, customer: str | None, min_cents: int) -> int:
    rows = load_ledger(ledger)
    count = 0
    total_cents = 0
    for row in rows:
        if customer is not None and row["customer"] != customer:
            continue
        if row["amount_cents"] < min_cents:
            continue
        count += 1
        total_cents += row["amount_cents"]
    print(json.dumps({"count": count, "total_cents": total_cents}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger.py", description="Migrate and report on billing exports."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    migrate = subparsers.add_parser(
        "migrate", help="merge every CSV under a directory into one JSON ledger"
    )
    migrate.add_argument("source_dir", type=Path)
    migrate.add_argument("output", type=Path)
    report = subparsers.add_parser(
        "report", help="summarize a JSON ledger by count and total cents"
    )
    report.add_argument("ledger", type=Path)
    report.add_argument("--customer", default=None)
    report.add_argument("--min-cents", type=non_negative_int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "migrate":
            return cmd_migrate(args.source_dir, args.output)
        if args.command == "report":
            return cmd_report(args.ledger, args.customer, args.min_cents)
    except MigrationError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
