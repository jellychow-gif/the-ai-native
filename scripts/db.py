"""SQLite database for The AI Native.

One table `items` holds the entire pipeline state from raw scrape to published.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "items.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    url               TEXT    NOT NULL UNIQUE,
    title             TEXT    NOT NULL,
    source            TEXT    NOT NULL,
    source_type       TEXT    NOT NULL,
    section           TEXT,
    sub_tag           TEXT,
    hook              TEXT,
    summary           TEXT,
    implication       TEXT,
    author            TEXT,
    published_at      TEXT,
    raw_excerpt       TEXT,
    body              TEXT,
    perspective_score INTEGER,
    practice_score    INTEGER,
    frontier_score    INTEGER,
    score_reasoning   TEXT,
    status            TEXT    NOT NULL DEFAULT 'candidate',
    issue_number      INTEGER,
    scraped_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    processed_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_items_status  ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_section ON items(section);
CREATE INDEX IF NOT EXISTS idx_items_source  ON items(source);
"""

# Schema migrations applied to existing databases (idempotent).
# Adding a column twice raises an error; we catch and ignore it.
MIGRATIONS = [
    "ALTER TABLE items ADD COLUMN body TEXT",
    "ALTER TABLE items ADD COLUMN score_reasoning TEXT",
    "ALTER TABLE items ADD COLUMN processed_at TEXT",
]


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        for stmt in MIGRATIONS:
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    continue
                raise


def upsert_item(conn: sqlite3.Connection, item: dict) -> bool:
    """Insert a new item. Returns True if inserted, False if URL already exists."""
    cols = [
        "url", "title", "source", "source_type", "section",
        "author", "published_at", "raw_excerpt",
    ]
    values = [item.get(c) for c in cols]
    placeholders = ",".join("?" * len(cols))
    try:
        conn.execute(
            f"INSERT INTO items ({','.join(cols)}) VALUES ({placeholders})",
            values,
        )
        return True
    except sqlite3.IntegrityError:
        return False
