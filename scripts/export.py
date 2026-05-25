"""Export candidate items + skills to JSON for the web frontend.

The Python pipeline is the source of truth; this snapshot is what Vercel
reads at build time. Run after any pipeline change (scrape / score /
summarize / classify_hr / skills.json edit).
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

MIN_SCORE = 9                # PRD §5.3 threshold to enter candidate pool
FEATURED_TOP_PER_SECTION = { # Per PRD §5.4 issue makeup: 3-4 / 3 / 2 = 8-9
    "Organization": 4,
    "HR": 3,
    "Industry": 2,
}

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "web" / "data" / "items.json"
SKILLS_PATH = ROOT / "data" / "skills.json"

# Phase 1 demo issue values — will be auto-derived from publish state later.
ISSUE = {
    "number": "01",
    "date_iso": "2026-05-29",
    "date_label": "May 29, 2026",
}


def _row_to_item(row, featured_ids: set[int]) -> dict:
    d = dict(row)
    d["is_featured"] = row["id"] in featured_ids
    return d


def main() -> None:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
              id, url, title, source, source_type, section, hr_module,
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

    # Pick top-N items per section as "featured" for the current issue.
    featured_ids: set[int] = set()
    for section, cap in FEATURED_TOP_PER_SECTION.items():
        in_section = [r for r in rows if r["section"] == section]
        featured_ids.update(r["id"] for r in in_section[:cap])

    items = [_row_to_item(r, featured_ids) for r in rows]

    # Load curated skills (editor-maintained file)
    skills_data = {"skills": []}
    if SKILLS_PATH.exists():
        with SKILLS_PATH.open() as f:
            raw = json.load(f)
            skills_data = {"skills": raw.get("skills", [])}

    payload = {
        "issue": ISSUE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_score_threshold": MIN_SCORE,
        "item_count": len(items),
        "featured_count": len(featured_ids),
        "items": items,
        "skills": skills_data["skills"],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    log.info(
        f"Wrote {len(items)} items ({len(featured_ids)} featured) + "
        f"{len(skills_data['skills'])} skills → {OUT_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
