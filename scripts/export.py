"""Export candidate items from SQLite to JSON for the web frontend.

The web/ Next.js app reads `data/items.json` (committed to git) so the site
can be deployed without needing the SQLite file. Run this after any pipeline
change (scrape / fetch_bodies / score / summarize).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from db import get_conn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("export")

MIN_SCORE = 9  # PRD §5.3 threshold

ROOT = Path(__file__).resolve().parent.parent
# JSON lives inside web/ so Vercel can read it without crossing project boundaries.
OUT_PATH = ROOT / "web" / "data" / "items.json"

# Phase 1 demo values — Step 7 will derive these from pipeline state.
DEFAULT_ISSUE = {
    "number": "01",
    "date_iso": "2026-05-15",
    "date_label": "May 15, 2026",
    "observation": "[本周观察 — 由发起人撰写，每周四晚审核改写。Step 7 接入后此字段从数据库读取。]",
}


def main() -> None:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              id, url, title, source, source_type, section,
              sub_tag, hook, summary, implication,
              author, published_at,
              perspective_score, practice_score, frontier_score, score_reasoning,
              COALESCE(perspective_score, 0)
                + COALESCE(practice_score, 0)
                + COALESCE(frontier_score, 0) AS total_score
            FROM items
            WHERE perspective_score IS NOT NULL
              AND (perspective_score + practice_score + frontier_score) >= ?
              AND summary IS NOT NULL
            ORDER BY total_score DESC, id DESC
            """,
            (MIN_SCORE,),
        ).fetchall()

    items = [dict(r) for r in rows]
    payload = {
        "issue": DEFAULT_ISSUE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_score_threshold": MIN_SCORE,
        "item_count": len(items),
        "items": items,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    log.info(f"Wrote {len(items)} items to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
