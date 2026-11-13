#!/usr/bin/env python3
"""Check that every bi quote in a unit's verdict table exists in the cited file near the cited line.

Usage: python3 check_quotes.py /tmp/pstack-U1.md [...]

A citation is `path:N` (or `path:N-M`, `path:N,M`) followed by 「quote」. The quote may elide
with …… or ...; each fragment must appear in the file within 3 lines of a cited line. Only
citations of skills/bi files are checked; prints each failure and a per-file count.
"""
import re
import sys
from pathlib import Path

BI = Path(__file__).resolve().parents[3] / "skills/bi"
CITE = re.compile(r"`?((?:skills/bi/)?(?:SKILL\.md|(?:references|templates|scripts)/[\w./-]+?))`?:([\d,\-]+)`?\s*[^「\n|]{0,12}「([^」]+)」")


def lines_of(rel):
    p = BI / rel.removeprefix("skills/bi/")
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else None


def cited_lines(spec):
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-", 1)
            if a.isdigit() and b.isdigit():
                out += range(int(a), int(b) + 1)
        elif part.isdigit():
            out.append(int(part))
    return out


def norm(s):
    return re.sub(r"[\s*`]", "", s)


for src in sys.argv[1:]:
    ok = bad = 0
    for row in Path(src).read_text(encoding="utf-8").splitlines():
        for m in CITE.finditer(row):
            rel, spec, quote = m.groups()
            text = lines_of(rel)
            if text is None:
                print(f"  NOFILE {rel}")
                bad += 1
                continue
            nums = cited_lines(spec) or [1]
            window = norm("".join(text[max(0, min(nums) - 4): max(nums) + 3]))
            frags = [norm(f) for f in re.split(r"……|\.\.\.|…", quote) if norm(f)]
            missing = [f for f in frags if f not in window]
            if missing:
                bad += 1
                print(f"  BAD {rel}:{spec} 「{quote[:60]}」 missing: {missing[0][:40]}")
            else:
                ok += 1
    print(f"{src}: {ok} ok, {bad} bad")
