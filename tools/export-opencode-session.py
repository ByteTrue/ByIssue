#!/usr/bin/env python3
"""Export one opencode session from opencode.db as readable text for review.

Usage:
  python3 tools/export-opencode-session.py --list [substring]
  python3 tools/export-opencode-session.py --session <id-or-title-substring> [--output path]

Read-only. Defaults to ~/.local/share/opencode/opencode.db. Reasoning is kept
in full; tool results are truncated (default 2000 chars) to keep exports small.
pi sessions use a different JSONL store and are not covered by this script.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import sys


def part_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text")
    return ""


def export(db: Path, session_id: str, title: str, tool_limit: int) -> str:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT type, seq, data FROM session_message WHERE session_id=? ORDER BY seq", (session_id,)
    ).fetchall()
    out = [f"# {title}\n\nsession: {session_id} · messages: {len(rows)}\n"]
    for kind, seq, raw in rows:
        d = json.loads(raw)
        if kind == "user":
            out.append(f"\n--- USER seq{seq} ---\n{d.get('text', '')}\n")
            continue
        for p in d.get("content", []) or []:
            if not isinstance(p, dict):
                continue
            t = p.get("type")
            if t == "reasoning" and p.get("text"):
                out.append(f"\n--- REASONING seq{seq} ---\n{p['text']}\n")
            elif t == "text" and p.get("text"):
                out.append(f"\n--- TEXT seq{seq} ---\n{p['text']}\n")
            elif t == "tool":
                st = p.get("state", {}) or {}
                args = json.dumps(st.get("input", {}), ensure_ascii=False)
                body = part_text(st.get("content"))
                if len(body) > tool_limit:
                    body = body[:tool_limit] + f"\n[... truncated, {len(body)} chars total]"
                out.append(f"\n[TOOL seq{seq} {p.get('name')} {st.get('status', '')}]\nargs: {args}\n{body}\n")
    return "".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(Path.home() / ".local/share/opencode/opencode.db"))
    ap.add_argument("--list", nargs="?", const="", metavar="SUBSTRING")
    ap.add_argument("--session", help="session id or title substring")
    ap.add_argument("--output", help="write here instead of stdout")
    ap.add_argument("--tool-limit", type=int, default=2000)
    args = ap.parse_args()
    db = Path(args.db)
    if not db.is_file():
        print(f"db not found: {db}", file=sys.stderr)
        return 1
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    if args.list is not None:
        for sid, title, directory in con.execute(
            "SELECT id, title, directory FROM session_v2 WHERE title LIKE ? ORDER BY time_updated DESC LIMIT 50",
            (f"%{args.list}%",),
        ):
            print(f"{sid}  {title}  ({directory})")
        return 0
    if not args.session:
        ap.error("--session or --list required")
    matches = con.execute(
        "SELECT id, title FROM session_v2 WHERE id=? OR title LIKE ?", (args.session, f"%{args.session}%")
    ).fetchall()
    if len(matches) != 1:
        for sid, title in matches:
            print(f"{sid}  {title}", file=sys.stderr)
        print(f"expected exactly 1 match, got {len(matches)}", file=sys.stderr)
        return 1
    sid, title = matches[0]
    text = export(db, sid, title, args.tool_limit)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} ({len(text)} chars)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())