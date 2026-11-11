"""Fetch full article bodies for items missing them, using trafilatura.

Idempotent: only fetches items where body IS NULL. Run after scrape.py.
"""
from __future__ import annotations

import logging
import os
import time

import requests
import trafilatura

from db import get_conn

# Per-run cap so one run always finishes under the CI timeout. Newest items are
# fetched first; a months-old backlog drains over subsequent daily runs instead
# of blowing a single run's budget. Override with env BODIES_MAX.
MAX_PER_RUN = int(os.environ.get("BODIES_MAX", "40"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fetch_bodies")

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
}
TIMEOUT = 15  # bound worst-case per-request time so a run can't stall on slow hosts
DELAY_SEC = 1.0  # polite delay between requests


def extract_body(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HTTP_HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        log.warning(f"  ! HTTP fail: {e}")
        return None

    text = trafilatura.extract(
        resp.text,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
        no_fallback=False,
    )
    if not text or len(text) < 200:
        return None
    # Cap to keep prompt costs sane — most articles' core is in the first 8K chars
    return text[:8000]


def run() -> tuple[int, int]:
    fetched = 0
    skipped = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, url, title, source FROM items "
            "WHERE body IS NULL OR length(body) < 200 "
            "ORDER BY id DESC LIMIT ?",
            (MAX_PER_RUN,),
        ).fetchall()

        log.info(f"Fetching up to {MAX_PER_RUN} newest; {len(rows)} queued this run.")

        for r in rows:
            log.info(f"[{r['id']:>3}] {r['source']}: {r['title'][:70]}")
            body = extract_body(r["url"])
            if body:
                conn.execute("UPDATE items SET body = ? WHERE id = ?", (body, r["id"]))
                conn.commit()
                fetched += 1
                log.info(f"  ✓ {len(body)} chars extracted")
            else:
                skipped += 1
                log.info("  - no body extracted, skipping")
            time.sleep(DELAY_SEC)

    log.info(f"Done. Fetched {fetched} bodies, skipped {skipped}.")
    return fetched, skipped


if __name__ == "__main__":
    run()
