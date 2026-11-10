#!/usr/bin/env python3
"""Merge one unit's verdict table into ledger.md and keep the full table as evidence.

Usage: python3 merge_unit.py M4 /tmp/pstack-M4.md

The unit table (| 项 | 结论 | 证据 |) is copied to verdicts/<unit>.md. Each ledger row of
that unit gets 结论 `做了` and evidence `<verdict> 见 verdicts/<unit>.md`. Rows the unit
table does not cover stay `没做` and are listed; items the table has but the ledger lacks
are appended to the ledger as new rows of that unit, so a gap in the enumeration surfaces.
"""
import re
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
unit, src = sys.argv[1], Path(sys.argv[2])
rows = {}
for line in src.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (.+?) \| \[?(已有·部分|已有|候选|不吸收)\]? \|", line)
    if m and m.group(1) != "项":
        name = m.group(1).strip()
        # units name principles `principle x` or `skill principle-x`; the ledger uses the latter
        name = re.sub(r"^principle `(.+)`$", r"skill `principle-\1`", name)
        rows[name] = f"[{m.group(2)}]"

(here / "verdicts").mkdir(exist_ok=True)
(here / "verdicts" / f"{unit}.md").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

ledger = here / "ledger.md"
lines = ledger.read_text(encoding="utf-8").splitlines()
seen, missing, last = set(), [], 0
row_re = re.compile(rf"^\| (\d+) \| (.+?) \| {unit} \| \S+ \| .*\|$")
for i, line in enumerate(lines):
    m = row_re.match(line)
    if not m:
        continue
    last = max(last, i)
    name = m.group(2).strip()
    if name in rows:
        seen.add(name)
        lines[i] = f"| {m.group(1)} | {name} | {unit} | 做了 | {rows[name]} 见 [verdicts/{unit}.md](verdicts/{unit}.md) |"
    else:
        missing.append(name)

numbers = [int(m.group(1)) for l in lines if (m := re.match(r"^\| (\d+) \|", l))]
extra = [n for n in rows if n not in seen]
for k, name in enumerate(extra, 1):
    lines.insert(last + k, f"| {max(numbers) + k} | {name} | {unit} | 做了 | {rows[name]} 见 [verdicts/{unit}.md](verdicts/{unit}.md) |")

ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"{unit}: {len(seen)} rows set, {len(extra)} appended, still 没做: {missing}")
