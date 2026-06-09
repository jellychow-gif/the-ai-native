"""Freeze the current pool of featured items into a permanent Issue.

Run by the weekly-draft GitHub Action each Thursday 21:00 BJT (= 13:00 UTC).
Idempotent: if today's issue already exists, prints status and exits.

The Friday morning publish then just builds Vercel against the new state.
"""
from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone, timedelta

from db import get_conn, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("freeze_issue")

MIN_SCORE = 9
FEATURED_TOP_PER_SECTION = {"Organization": 4, "HR": 3, "Industry": 2}
FRESH_DAYS = 7  # editor v3.4: tightened from 180 to true weekly freshness


def _parse_date(raw: str | None):
    if not raw:
        return None
    s = raw.rstrip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        try:
            dt = datetime.strptime(s[:10], "%Y-%m-%d")
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def select_issue_items(conn) -> list[int]:
    """Pick 4 Org + 3 HR + 2 Industry from fresh, on-topic, summarized items
    that haven't already been frozen into an earlier issue."""
    rows = conn.execute(
        """
        SELECT id, section, source, published_at,
               (perspective_score + practice_score + frontier_score) AS total
        FROM items
        WHERE issue_number IS NULL
          AND what_happened IS NOT NULL
          AND perspective_score IS NOT NULL
          AND (perspective_score + practice_score + frontier_score) >= ?
        ORDER BY total DESC, id DESC
        """,
        (MIN_SCORE,),
    ).fetchall()

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=FRESH_DAYS)
    fresh = [r for r in rows if (_parse_date(r["published_at"]) or cutoff) >= cutoff]

    picked_ids: list[int] = []
    for section, cap in FEATURED_TOP_PER_SECTION.items():
        in_section = [r for r in fresh if r["section"] == section]
        picked_ids.extend(r["id"] for r in in_section[:cap])
    return picked_ids


def next_issue_number(conn) -> int:
    row = conn.execute("SELECT MAX(number) AS n FROM issues").fetchone()
    return (row["n"] or 0) + 1


def freeze(force_number: int | None = None) -> int:
    init_db()
    with get_conn() as conn:
        number = force_number or next_issue_number(conn)

        # If this number already exists, abort gracefully (idempotent)
        existing = conn.execute(
            "SELECT number, item_count FROM issues WHERE number = ?", (number,)
        ).fetchone()
        if existing:
            log.info(f"Issue {number:02d} already frozen ({existing['item_count']} items). Skipping.")
            return number

        item_ids = select_issue_items(conn)
        if not item_ids:
            log.warning(f"No eligible items to freeze for Issue {number:02d}. Skipping.")
            return number

        # Editor-facing dates always in Beijing time (UTC+8) — issues are
        # published "Friday morning Beijing time" per PRD §5.4, so the
        # date stamp should match the reader's timezone, not the runner's.
        bjt = timezone(timedelta(hours=8))
        today = datetime.now(bjt)
        date_iso = today.date().isoformat()
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        date_label = f"{months[today.month-1]} {today.day}, {today.year}"

        conn.execute(
            "INSERT INTO issues (number, date_iso, date_label, item_count) VALUES (?, ?, ?, ?)",
            (number, date_iso, date_label, len(item_ids)),
        )
        for iid in item_ids:
            conn.execute("UPDATE items SET issue_number = ? WHERE id = ?", (number, iid))
        conn.commit()

        log.info(f"Froze Issue {number:02d} · {date_label} · {len(item_ids)} items")
        for iid in item_ids:
            r = conn.execute("SELECT source, title FROM items WHERE id = ?", (iid,)).fetchone()
            log.info(f"  [{iid:>3}] {r['source']:<22} | {r['title'][:55]}")
        return number


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--force-number", type=int,
        help="Override the auto-incremented issue number (used for backfilling)",
    )
    args = ap.parse_args()
    freeze(force_number=args.force_number)
