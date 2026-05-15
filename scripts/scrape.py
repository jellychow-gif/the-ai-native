"""Scrape demo sources and write items to SQLite.

Phase 1: three sources, covering the three fetch paths (RSS, Substack-as-RSS,
and HTML). Run with `python scripts/scrape.py` from project root, with the
venv activated.

The pipeline is intentionally minimal: fetch -> parse -> upsert by URL.
Scoring, classification, and summarization happen in a later step (Claude API).
"""
from __future__ import annotations

import logging
import sys
from typing import Optional
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser

from db import get_conn, init_db, upsert_item
from sources import SOURCES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("scrape")

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
TIMEOUT = 20
MAX_PER_SOURCE = 10  # cap during demo to avoid pulling deep history


def _norm_date(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    try:
        return dateparser.parse(s).isoformat()
    except (ValueError, TypeError):
        return None


def _strip_html(s: str) -> str:
    return BeautifulSoup(s, "lxml").get_text(" ", strip=True)


def fetch_rss(source: dict) -> list[dict]:
    """Parse an RSS or Atom feed. Also handles Substack newsletters."""
    log.info(f"Fetching RSS: {source['name']}")
    resp = requests.get(source["url"], headers=HTTP_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    items: list[dict] = []
    for entry in feed.entries[:MAX_PER_SOURCE]:
        excerpt = entry.get("summary") or entry.get("description") or ""
        excerpt = _strip_html(excerpt)[:2000] if excerpt else None
        items.append({
            "url": (entry.get("link") or "").strip(),
            "title": (entry.get("title") or "").strip(),
            "author": ((entry.get("author") or "").strip() or None),
            "published_at": _norm_date(entry.get("published") or entry.get("updated")),
            "raw_excerpt": excerpt,
            "source": source["name"],
            "source_type": source["type"],
            "section": source["section"],
        })
    log.info(f"  parsed {len(items)} entries")
    return items


def fetch_html_rippling(source: dict) -> list[dict]:
    """Scrape Rippling's blog index page for article links."""
    log.info(f"Fetching HTML: {source['name']}")
    resp = requests.get(source["url"], headers=HTTP_HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "lxml")

    base = "https://www.rippling.com"
    seen: set[str] = set()
    items: list[dict] = []

    import re
    slug_re = re.compile(r"^(?:/blog/|https://www\.rippling\.com/blog/)[a-z0-9-]+/?$")
    # strip leading category labels ("HR ", "IT ", "Finance ") or short dates from anchor text
    prefix_re = re.compile(
        r"^(?:HR|IT|Finance|Spend|Payroll|Talent|Operations|Compliance|"
        r"[A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})\s+",
    )

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not slug_re.match(href):
            continue
        full_url = urljoin(base, href).rstrip("/")
        if full_url in seen:
            continue
        title = a.get_text(" ", strip=True)
        title = prefix_re.sub("", title).strip()
        if not title or len(title) < 8:
            continue
        seen.add(full_url)
        items.append({
            "url": full_url,
            "title": title,
            "author": None,
            "published_at": None,
            "raw_excerpt": None,
            "source": source["name"],
            "source_type": source["type"],
            "section": source["section"],
        })
        if len(items) >= MAX_PER_SOURCE:
            break

    log.info(f"  parsed {len(items)} entries")
    return items


FETCHERS = {
    "rss": fetch_rss,
    "substack": fetch_rss,
    "html": fetch_html_rippling,
}


def run() -> tuple[int, int]:
    init_db()
    total_seen = 0
    total_new = 0
    with get_conn() as conn:
        for source in SOURCES:
            fetcher = FETCHERS.get(source["type"])
            if fetcher is None:
                log.warning(f"No fetcher for type {source['type']!r}; skipping {source['name']}")
                continue
            try:
                items = fetcher(source)
            except requests.RequestException as e:
                log.error(f"Network error on {source['name']}: {e}")
                continue
            except Exception as e:
                log.error(f"Parse error on {source['name']}: {e}")
                continue

            for item in items:
                if not item.get("url") or not item.get("title"):
                    continue
                total_seen += 1
                if upsert_item(conn, item):
                    total_new += 1
        conn.commit()

    log.info(f"Done. Saw {total_seen} items, inserted {total_new} new.")
    return total_seen, total_new


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        log.info("Interrupted.")
        sys.exit(130)
