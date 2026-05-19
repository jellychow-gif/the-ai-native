"""Pretty-print items from the database.

Usage:
  python scripts/show.py                          # compact view, top 30
  python scripts/show.py --candidates             # items above PRD threshold (9), fully expanded with AI fields
  python scripts/show.py --section HR             # filter by section
  python scripts/show.py --all                    # expanded view of every item
"""
from __future__ import annotations

import argparse
import textwrap

from db import get_conn


def wrap(text: str, indent: int = 8, width: int = 92) -> str:
    if not text:
        return ""
    pad = " " * indent
    return textwrap.fill(text, width=width, initial_indent=pad, subsequent_indent=pad)


def show_brief(rows) -> None:
    """Compact one-row-per-item view."""
    print(f"\n=== {len(rows)} items (compact) ===")
    for r in rows:
        date = (r["published_at"] or "—")[:10]
        scored = ""
        if r["perspective_score"] is not None:
            total = (r["perspective_score"] or 0) + (r["practice_score"] or 0) + (r["frontier_score"] or 0)
            scored = f" [{r['perspective_score']}/{r['practice_score']}/{r['frontier_score']}={total}]"
        print(f"\n  [{r['id']:>3}] {r['section']:<12} | {r['source']:<22} | {date}{scored}")
        print(wrap(r["title"]))
        print(f"        {r['url']}")


def show_expanded(rows) -> None:
    """Full expanded view with all AI-generated fields."""
    print(f"\n=== {len(rows)} items (expanded) ===")
    for r in rows:
        total = (r["perspective_score"] or 0) + (r["practice_score"] or 0) + (r["frontier_score"] or 0)
        print("\n" + "─" * 100)
        print(f"  ID {r['id']:>3} · {r['section']} · {r['source']} · score {total}/15  "
              f"(P={r['perspective_score']} R={r['practice_score']} F={r['frontier_score']})")
        if r["score_reasoning"]:
            print(f"  评分理由: {r['score_reasoning']}")
        print(f"\n  📌 {r['title']}")
        print(f"     {r['url']}")
        if r["sub_tag"]:
            print(f"\n  🏷  {r['sub_tag']}")
        if r["summary"]:
            print(f"\n  摘要：")
            print(wrap(r["summary"], indent=6, width=94))
        if r["implication"]:
            print(f"\n  对组织变革的含义：")
            print(wrap(r["implication"], indent=6, width=94))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", help="Filter by section (Organization / HR / Industry)")
    ap.add_argument("--candidates", action="store_true",
                    help="Only items above PRD score threshold (9), expanded with AI fields")
    ap.add_argument("--all", action="store_true", help="Expanded view of all items")
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

        # Pipeline state
        stats = conn.execute("""
            SELECT
              COUNT(*) AS total,
              SUM(CASE WHEN body IS NOT NULL THEN 1 ELSE 0 END) AS bodied,
              SUM(CASE WHEN perspective_score IS NOT NULL THEN 1 ELSE 0 END) AS scored,
              SUM(CASE WHEN summary IS NOT NULL THEN 1 ELSE 0 END) AS summarized,
              SUM(CASE WHEN (perspective_score + practice_score + frontier_score) >= 9 THEN 1 ELSE 0 END) AS passing
            FROM items
        """).fetchone()
        print(f"\n=== Pipeline state ===")
        print(f"  total      : {stats['total']}")
        print(f"  bodied     : {stats['bodied']}")
        print(f"  scored     : {stats['scored']}")
        print(f"  passing ≥9 : {stats['passing']}")
        print(f"  summarized : {stats['summarized']}")

        # Item view
        sql_base = "SELECT * FROM items"
        where = []
        params: list = []
        if args.section:
            where.append("section = ?")
            params.append(args.section)
        if args.candidates:
            where.append("perspective_score IS NOT NULL")
            where.append("(perspective_score + practice_score + frontier_score) >= 9")
        if where:
            sql_base += " WHERE " + " AND ".join(where)
        sql_base += (" ORDER BY "
                     "(COALESCE(perspective_score, 0) + COALESCE(practice_score, 0) + COALESCE(frontier_score, 0)) DESC, "
                     "id DESC")
        sql_base += " LIMIT ?"
        params.append(args.limit)

        rows = conn.execute(sql_base, params).fetchall()
        if args.candidates or args.all:
            show_expanded(rows)
        else:
            show_brief(rows)


if __name__ == "__main__":
    main()
