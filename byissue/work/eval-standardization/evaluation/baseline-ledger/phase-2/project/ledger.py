#!/usr/bin/env python3
"""Ledger migration CLI.

The migrate command reads every CSV under a source directory and writes one
JSON array, sorted by id, with amounts converted exactly to integer cents.
The report command summarizes that JSON array, optionally filtered by
customer and by a minimum amount in cents.
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
AMOUNT_PATTERN = re.compile(r"^(?P<whole>[0-9]+)(?:\.(?P<fraction>[0-9]{1,2}))?$")


class LedgerError(Exception):
    """A problem that must be reported to the user without a traceback."""


class MigrateError(LedgerError):
    """An input problem that must leave the output file untouched."""


class ReportError(LedgerError):
    """A problem that prevents producing a report."""


def parse_amount(raw: str) -> int:
    """Return the exact number of cents represented by a decimal amount."""
    match = AMOUNT_PATTERN.fullmatch(raw)
    if match is None:
        raise ValueError(
            "amount must be a non-negative decimal with at most two fractional digits"
        )

    fraction = (match.group("fraction") or "").ljust(2, "0")
    try:
        return int(match.group("whole")) * 100 + int(fraction)
    except ValueError as exc:  # pragma: no cover - guarded by the regex
        raise ValueError("amount is not a valid decimal") from exc


def parse_min_cents(raw: str) -> int:
    """Parse a non-negative integer threshold for report filtering."""
    if re.fullmatch(r"[0-9]+", raw) is None:
        raise argparse.ArgumentTypeError(
            f"min-cents must be a non-negative integer, got {raw!r}"
        )
    return int(raw)


def discover_csv_files(source: Path) -> list[Path]:
    if not source.exists():
        raise MigrateError(f"source directory does not exist: {source}")
    if not source.is_dir():
        raise MigrateError(f"source path is not a directory: {source}")

    files: list[Path] = []

    def on_walk_error(error: OSError) -> None:
        raise MigrateError(f"{source}: cannot scan directory: {error}") from error

    for root, dirnames, filenames in os.walk(source, onerror=on_walk_error):
        dirnames.sort()
        for filename in sorted(filenames):
            if filename.lower().endswith(".csv"):
                files.append(Path(root) / filename)
    return sorted(files, key=lambda path: path.as_posix())


def read_csv(path: Path, rows: list[dict[str, object]], seen: dict[str, str]) -> None:
    try:
        handle = path.open("r", encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise MigrateError(f"{path}: cannot read file: {exc}") from exc

    with handle:
        reader = csv.reader(handle, strict=True)
        try:
            header = next(reader)
        except StopIteration:
            raise MigrateError(f"{path}: empty file, expected header {','.join(HEADER)}")
        except (csv.Error, UnicodeDecodeError) as exc:
            raise MigrateError(f"{path}: cannot parse CSV: {exc}") from exc

        if header != HEADER:
            raise MigrateError(
                f"{path}: bad header {header!r}, expected {HEADER!r}"
            )

        try:
            for line_number, values in enumerate(reader, start=2):
                if len(values) != 3:
                    raise MigrateError(
                        f"{path}:{line_number}: expected 3 columns, got {len(values)}"
                    )

                record_id, customer, raw_amount = values
                if record_id.strip() == "":
                    raise MigrateError(f"{path}:{line_number}: id must not be empty")
                if customer.strip() == "":
                    raise MigrateError(f"{path}:{line_number}: customer must not be empty")

                try:
                    amount_cents = parse_amount(raw_amount)
                except ValueError as exc:
                    raise MigrateError(
                        f"{path}:{line_number}: invalid amount {raw_amount!r}: {exc}"
                    ) from exc

                previous = seen.get(record_id)
                if previous is not None:
                    raise MigrateError(
                        f"{path}:{line_number}: duplicate id {record_id!r}, "
                        f"already used at {previous}"
                    )
                seen[record_id] = f"{path}:{line_number}"
                rows.append(
                    {
                        "id": record_id,
                        "customer": customer,
                        "amount_cents": amount_cents,
                    }
                )
        except csv.Error as exc:
            raise MigrateError(f"{path}: cannot parse CSV: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise MigrateError(f"{path}: cannot decode CSV as UTF-8: {exc}") from exc


def write_output(path: Path, payload: str) -> None:
    """Replace the output atomically, so a failure cannot truncate it."""
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
    except OSError as exc:
        raise MigrateError(f"{path}: cannot create output file: {exc}") from exc

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except OSError as exc:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise MigrateError(f"{path}: cannot write output file: {exc}") from exc


def migrate(source: Path, output: Path) -> None:
    files = discover_csv_files(source)
    rows: list[dict[str, object]] = []
    seen: dict[str, str] = {}

    for path in files:
        read_csv(path, rows, seen)

    rows.sort(key=lambda row: row["id"])
    payload = json.dumps(rows, ensure_ascii=False, indent=2) + "\n"
    write_output(output, payload)


def load_records(path: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ReportError(f"{path}: cannot read file: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ReportError(f"{path}: cannot decode file as UTF-8: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ReportError(f"{path}: invalid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ReportError(f"{path}: expected a JSON array of records")

    records: list[dict[str, object]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ReportError(f"{path}: record {index} is not a JSON object")

        customer = item.get("customer")
        if not isinstance(customer, str):
            raise ReportError(f"{path}: record {index} has no string 'customer'")

        amount_cents = item.get("amount_cents")
        if isinstance(amount_cents, bool) or not isinstance(amount_cents, int):
            raise ReportError(
                f"{path}: record {index} has no integer 'amount_cents'"
            )
        if amount_cents < 0:
            raise ReportError(
                f"{path}: record {index} has negative 'amount_cents'"
            )

        records.append({"customer": customer, "amount_cents": amount_cents})
    return records


def summarize(
    records: list[dict[str, object]], customer: str | None, min_cents: int
) -> dict[str, int]:
    selected = [
        record
        for record in records
        if (customer is None or record["customer"] == customer)
        and record["amount_cents"] >= min_cents
    ]
    return {
        "count": len(selected),
        "total_cents": sum(int(record["amount_cents"]) for record in selected),
    }


def report(path: Path, customer: str | None, min_cents: int) -> None:
    records = load_records(path)
    print(json.dumps(summarize(records, customer, min_cents), ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger.py", description="Ledger migration tool.")
    commands = parser.add_subparsers(dest="command", required=True)

    migrate_parser = commands.add_parser(
        "migrate", help="migrate every CSV under a directory into one JSON array"
    )
    migrate_parser.add_argument("source_dir", metavar="source-dir")
    migrate_parser.add_argument("output_json", metavar="output.json")

    report_parser = commands.add_parser(
        "report", help="summarize a migrated JSON array"
    )
    report_parser.add_argument("output_json", metavar="output.json")
    report_parser.add_argument("--customer", default=None)
    report_parser.add_argument("--min-cents", type=parse_min_cents, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "migrate":
            migrate(Path(args.source_dir), Path(args.output_json))
        elif args.command == "report":
            report(Path(args.output_json), args.customer, args.min_cents)
        else:  # pragma: no cover - argparse rejects unknown subcommands
            parser.error(f"unknown command: {args.command}")
    except LedgerError as exc:
        print(f"ledger: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
