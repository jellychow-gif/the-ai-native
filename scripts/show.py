"""Pretty-print the current state of the items table.

Usage: python scripts/inspect.py [--section Organization|HR|Industry]
"""
from __future__ import annotations

import argparse
import textwrap

from db import get_conn


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", help="Filter by section")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()

    with get_conn() as conn:
        # Summary by source
        print("\n=== Items by source ===")
        rows = conn.execute(
            "SELECT source, section, COUNT(*) AS n FROM items "
            "GROUP BY source, section ORDER BY source"
        ).fetchall()
        for r in rows:
            print(f"  {r['source']:<28} {r['section']:<13} {r['n']:>3} items")
        total = conn.execute("SELECT COUNT(*) AS n FROM items").fetchone()["n"]
        print(f"  {'TOTAL':<28} {'':<13} {total:>3}")

        # Item listing
        print(f"\n=== Most recent {args.limit} items ===")
        sql = "SELECT * FROM items"
        params: list = []
        if args.section:
            sql += " WHERE section = ?"
            params.append(args.section)
        sql += " ORDER BY id DESC LIMIT ?"
        params.append(args.limit)

        for r in conn.execute(sql, params):
            date = (r["published_at"] or "—")[:10]
            print(
                f"\n  [{r['id']:>3}] {r['section']:<12} | {r['source']:<22} | {date}"
            )
            wrapped = textwrap.fill(
                r["title"], width=88, initial_indent="        ", subsequent_indent="        "
            )
            print(wrapped)
            print(f"        {r['url']}")


if __name__ == "__main__":
    main()
