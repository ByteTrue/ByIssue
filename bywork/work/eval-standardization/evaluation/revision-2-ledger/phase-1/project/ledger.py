#!/usr/bin/env python3
"""Migrate legacy CSV ledgers to a canonical JSON ledger."""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

HEADER = ["id", "customer", "amount"]
AMOUNT_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]{1,2})?$")


class LedgerError(Exception):
    """A user-facing migration failure with one or more messages."""

    def __init__(self, messages: list[str]) -> None:
        super().__init__("\n".join(messages))
        self.messages = messages


def amount_to_cents(text: str) -> int:
    """Convert a plain non-negative decimal string to exact integer cents."""
    if not AMOUNT_PATTERN.fullmatch(text):
        raise ValueError(text)
    whole, dot, fraction = text.partition(".")
    cents = int(whole) * 100
    if dot:
        cents += int(fraction.ljust(2, "0"))
    return cents


def _find_csv_files(source: Path, errors: list[str]) -> list[Path]:
    files: list[Path] = []

    def on_error(error: OSError) -> None:
        errors.append(f"{source}: cannot traverse directory: {error}")

    for root, dir_names, file_names in os.walk(source, onerror=on_error):
        dir_names.sort()
        for name in file_names:
            if Path(name).suffix.lower() == ".csv":
                files.append(Path(root) / name)
    return sorted(files, key=lambda path: path.as_posix())


def _read_csv(path: Path, errors: list[str], seen_ids: dict[str, str]) -> list[dict[str, Any]]:
    display = str(path)
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except (OSError, UnicodeError) as error:
        errors.append(f"{display}: cannot read file: {error}")
        return []

    rows: list[dict[str, Any]] = []
    try:
        with handle:
            reader = csv.reader(handle, strict=True)
            try:
                header = next(reader)
            except StopIteration:
                errors.append(f"{display}: missing header; expected 'id,customer,amount'")
                return []

            if header != HEADER:
                errors.append(
                    f"{display}: expected header 'id,customer,amount', "
                    f"got {','.join(header)!r}"
                )
                return []

            for line_number, record in enumerate(reader, start=2):
                if len(record) != len(HEADER):
                    errors.append(
                        f"{display}:{line_number}: expected {len(HEADER)} fields, "
                        f"got {len(record)}"
                    )
                    continue

                row_id, customer, amount = record
                if not row_id.strip():
                    errors.append(f"{display}:{line_number}: id must not be empty")
                    continue
                if not customer.strip():
                    errors.append(f"{display}:{line_number}: customer must not be empty")
                    continue

                try:
                    amount_cents = amount_to_cents(amount)
                except ValueError:
                    errors.append(
                        f"{display}:{line_number}: invalid amount {amount!r}; "
                        "expected a non-negative decimal with at most two decimal places"
                    )
                    continue

                location = f"{display}:{line_number}"
                first_location = seen_ids.get(row_id)
                if first_location is not None:
                    errors.append(
                        f"{display}:{line_number}: duplicate id {row_id!r}; "
                        f"first seen at {first_location}"
                    )
                    continue

                seen_ids[row_id] = location
                rows.append(
                    {
                        "id": row_id,
                        "customer": customer,
                        "amount_cents": amount_cents,
                    }
                )
    except (OSError, UnicodeError, csv.Error) as error:
        errors.append(f"{display}: cannot parse CSV: {error}")
        return []

    return rows


def _write_json(output: Path, rows: list[dict[str, Any]]) -> None:
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=str(output.parent),
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
        os.replace(temporary_path, output)
        temporary_path = None
    except OSError as error:
        raise LedgerError([f"{output}: cannot write output: {error}"]) from error
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def migrate(source: Path | str, output: Path | str) -> int:
    """Migrate every CSV below source into output. Return the number of rows."""
    source_path = Path(source)
    output_path = Path(output)

    if not source_path.exists():
        raise LedgerError([f"{source_path}: source directory does not exist"])
    if not source_path.is_dir():
        raise LedgerError([f"{source_path}: source is not a directory"])

    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    seen_ids: dict[str, str] = {}

    for csv_path in _find_csv_files(source_path, errors):
        rows.extend(_read_csv(csv_path, errors, seen_ids))

    if errors:
        raise LedgerError(errors)

    rows.sort(key=lambda row: row["id"])
    _write_json(output_path, rows)
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Migrate legacy CSV ledgers to JSON.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    migrate_parser = subparsers.add_parser("migrate", help="migrate a directory of CSV files")
    migrate_parser.add_argument("source_dir", help="directory searched recursively for CSV files")
    migrate_parser.add_argument("output", help="JSON file to write")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "migrate":
            migrate(args.source_dir, args.output)
    except LedgerError as error:
        for message in error.messages:
            print(f"error: {message}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
