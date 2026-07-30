"""Export candidate items + skills to JSON for the web frontend.

The Python pipeline is the source of truth; this snapshot is what Vercel
reads at build time. Run after any pipeline change (scrape / score /
summarize / classify_hr / skills.json edit).
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
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
# Freshness gate for featured/top: editor v3.4 — 180 days was too loose
# ("frontier signals" promise was being violated by 6-month-old content).
# Now strict: items must be from the last 7 days to enter Featured.
FEATURED_MAX_AGE_DAYS = 7

ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = ROOT / "web" / "data" / "items.json"
SKILLS_PATH = ROOT / "data" / "skills.json"

def _load_issues(conn) -> list[dict]:
    """All frozen issues, newest first. Each carries metadata + item IDs."""
    issues = conn.execute(
        "SELECT number, date_iso, date_label, frozen_at, item_count "
        "FROM issues ORDER BY number DESC"
    ).fetchall()
    out = []
    for issue in issues:
        item_ids = [
            r["id"] for r in conn.execute(
                # Freshest-first within an issue: a frontier-signals site must
                # never lead with a months-old piece just because it scored high.
                "SELECT id FROM items WHERE issue_number = ? "
                "ORDER BY published_at DESC, "
                "(perspective_score+practice_score+frontier_score) DESC, id DESC",
                (issue["number"],),
            ).fetchall()
        ]
        out.append({
            "number": issue["number"],
            "date_iso": issue["date_iso"],
            "date_label": issue["date_label"],
            "frozen_at": issue["frozen_at"],
            "item_count": issue["item_count"],
            "item_ids": item_ids,
        })
    return out


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
              what_happened, why_matters, org_implication, talent_implication,
              hr_operating_implication, prediction, ano_dimension,
              long_form_zh, preview_hook,
              author, published_at, issue_number,
              perspective_score, practice_score, frontier_score, score_reasoning,
              COALESCE(perspective_score, 0)
                + COALESCE(practice_score, 0)
                + COALESCE(frontier_score, 0) AS total_score
            FROM items
            -- Issue-bound items are permanent snapshots and always export,
            -- regardless of their current score. Everything else must clear
            -- the candidate gate (scored + relevant + summarized).
            WHERE issue_number IS NOT NULL
               OR (
                 perspective_score IS NOT NULL
                 AND (perspective_score + practice_score + frontier_score) >= ?
                 AND (summary IS NOT NULL OR what_happened IS NOT NULL)
               )
            ORDER BY
              CASE WHEN what_happened IS NOT NULL THEN 0 ELSE 1 END,
              total_score DESC, id DESC
            """,
            (MIN_SCORE,),
        ).fetchall()

    # Freshness gate: featured candidates must be within MAX_AGE_DAYS.
    # Older items still appear in section archives but never on the hero.
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=FEATURED_MAX_AGE_DAYS)

    def is_fresh(row) -> bool:
        raw = row["published_at"]
        if not raw:
            return False  # no date = treat as old; safer for "frontier" promise
        # Normalize ISO strings: accept "Z", "+00:00", date-only, with/without time.
        s = raw.rstrip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except ValueError:
            try:
                dt = datetime.strptime(s[:10], "%Y-%m-%d")
            except ValueError:
                return False
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt >= cutoff

    # Pick top-N items per section as "featured" — fresh items only.
    featured_ids: set[int] = set()
    for section, cap in FEATURED_TOP_PER_SECTION.items():
        in_section = [r for r in rows if r["section"] == section and is_fresh(r)]
        featured_ids.update(r["id"] for r in in_section[:cap])

    items = [_row_to_item(r, featured_ids) for r in rows]

    # Issues: pull table + current (latest) issue for masthead
    with get_conn() as conn:
        issues = _load_issues(conn)
    current_issue = issues[0] if issues else None

    # Load curated skills (editor-maintained file)
    skills_data = {"skills": []}
    if SKILLS_PATH.exists():
        with SKILLS_PATH.open() as f:
            raw = json.load(f)
            skills_data = {"skills": raw.get("skills", [])}

    # Backward-compat: "issue" key still exposed at top level (latest issue)
    issue_payload = (
        {
            "number": f"{current_issue['number']:02d}",
            "date_iso": current_issue["date_iso"],
            "date_label": current_issue["date_label"],
        }
        if current_issue
        else {"number": "00", "date_iso": "", "date_label": "Pre-launch"}
    )

    payload = {
        "issue": issue_payload,
        "issues": issues,
        "current_issue_number": current_issue["number"] if current_issue else None,
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
