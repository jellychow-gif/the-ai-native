"""Score candidate items using Claude Haiku.

Per PRD §5.3, each item is scored on three 1-5 dimensions:
  perspective_score (视角高度)
  practice_score    (实践锚点)
  frontier_score    (全球前沿性)

Total < 9 will be filtered out before summarization.

Idempotent: only scores items where perspective_score IS NULL.
"""
from __future__ import annotations

import json
import logging
import time

from dotenv import load_dotenv
from anthropic import Anthropic

from db import get_conn

load_dotenv(override=True)
client = Anthropic()
MODEL = "claude-haiku-4-5"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("score")


SYSTEM_PROMPT = """\
You are a curator for "The AI Native", a weekly site selecting 8-9 signals/week
about how ORGANIZATIONS are being rebuilt around AI. The target audience is
org-change leaders (CEOs, founders, HRDs).

═══════════════════════════════════════════════════════════════════
RELEVANCE GATE — apply BEFORE scoring
═══════════════════════════════════════════════════════════════════

The article must be primarily about ONE OR MORE of:
  ✓ Human capital, talent, HR functions in the AI era
  ✓ Organizational design, workflow, role architecture, team structure
  ✓ AI adoption INSIDE companies (operating-model change)
  ✓ Hiring, performance, comp, learning, employee experience under AI
  ✓ Leadership / culture / org strategy in the AI-native era
  ✓ The future of work, jobs, careers in the AI era
  ✓ Founder/CEO/HRD-level frameworks about building/running companies

The article must NOT be primarily about (even if high quality):
  ✗ AI applied to a non-org domain as PRIMARY topic — biology, medicine,
    drug discovery, materials, finance instruments, legal contracts, etc.
  ✗ AI infrastructure / model architecture / chips / training (technical AI)
  ✗ Generic tech industry news without an organizational / people angle
  ✗ Specific company news (funding, IPO, acquisitions, partner announcements,
    product launches) UNLESS the piece is about HOW the company is built
  ✗ Investment thesis / market analysis pieces (unless about org/talent)
  ✗ Consumer product reviews, app reviews

If the article fails the relevance gate, return scores {perspective: 0,
practice: 0, frontier: 0} and a Chinese reasoning that starts with "OFF-TOPIC:".

═══════════════════════════════════════════════════════════════════
SCORING DIMENSIONS — apply only if article passes the gate, 1-5 each
═══════════════════════════════════════════════════════════════════

PERSPECTIVE (视角高度):
  1 = pure tactics / how-to / 101-level / pure product news
  2 = some perspective but mostly execution-layer
  3 = manager-level paradigm
  4 = founder/CEO/HRD paradigm view, redefining how to think
  5 = industry-redefining take

PRACTICE (实践锚点):
  1 = pure abstraction, no concrete examples
  2 = name-drops without depth
  3 = one real case
  4 = multiple cases with specifics
  5 = deep dive with company names + data + outcomes

FRONTIER (全球前沿性):
  1 = old news, widely covered, well-known frameworks
  2 = recent but not novel
  3 = current best practice
  4 = leading edge
  5 = paradigm-shifting or first-of-its-kind insight

The bar is brutally high — 5 should be rare. Aggressively filter out company
news, hiring announcements, generic listicles, product changelogs, marketing.

Call the submit_score tool with your scores and a brief Chinese reasoning
(≤50 chars). For OFF-TOPIC items, start the reasoning with "OFF-TOPIC:".
"""

TOOLS = [{
    "name": "submit_score",
    "description": "Submit scores for an article",
    "input_schema": {
        "type": "object",
        "properties": {
            "perspective": {
                "type": "integer",
                "minimum": 0, "maximum": 5,
                "description": "Paradigm level: 0=off-topic, 1=tactical, 5=industry-redefining",
            },
            "practice": {
                "type": "integer",
                "minimum": 0, "maximum": 5,
                "description": "Concrete anchors: 0=off-topic, 1=pure abstraction, 5=deep case with data",
            },
            "frontier": {
                "type": "integer",
                "minimum": 0, "maximum": 5,
                "description": "Global frontier: 0=off-topic, 1=widely-known, 5=paradigm-shifting",
            },
            "reasoning": {
                "type": "string",
                "description": "One-sentence Chinese reasoning, ≤50 chars",
            },
        },
        "required": ["perspective", "practice", "frontier", "reasoning"],
    },
}]


def score_item(source: str, section: str, title: str, content: str) -> dict | None:
    user_msg = (
        f"Source: {source} / Section: {section}\n"
        f"Title: {title}\n\n"
        f"Content:\n{content[:6000]}"
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "tool", "name": "submit_score"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.error(f"  ! API error: {e}")
        return None

    for block in resp.content:
        if block.type == "tool_use" and block.name == "submit_score":
            return block.input
    log.error(f"  ! No tool_use block in response: {resp.content}")
    return None


def run() -> tuple[int, int, int]:
    """Returns (scored, skipped, total_tokens_in, total_tokens_out) — but as 3-tuple for brevity."""
    scored = 0
    skipped = 0
    total_in = 0
    total_out = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, url, title, source, section, body, raw_excerpt "
            "FROM items "
            "WHERE perspective_score IS NULL "
            "ORDER BY id"
        ).fetchall()

        log.info(f"Found {len(rows)} items needing scoring.")

        for r in rows:
            content = r["body"] or r["raw_excerpt"] or ""
            if len(content) < 50:
                log.info(f"[{r['id']:>3}] {r['title'][:60]}: insufficient content; skipping")
                skipped += 1
                continue

            log.info(f"[{r['id']:>3}] {r['source']} | {r['title'][:60]}")
            scores = score_item(r["source"], r["section"], r["title"], content)
            if scores is None:
                skipped += 1
                continue

            total = scores["perspective"] + scores["practice"] + scores["frontier"]
            log.info(
                f"  ✓ P={scores['perspective']} R={scores['practice']} F={scores['frontier']} "
                f"(总={total}) | {scores['reasoning']}"
            )

            conn.execute(
                "UPDATE items SET "
                "perspective_score = ?, practice_score = ?, frontier_score = ?, "
                "score_reasoning = ?, processed_at = datetime('now') "
                "WHERE id = ?",
                (scores["perspective"], scores["practice"], scores["frontier"],
                 scores["reasoning"], r["id"]),
            )
            conn.commit()
            scored += 1
            time.sleep(0.3)  # gentle rate-limit

    log.info(f"Done. Scored {scored}, skipped {skipped}.")
    return scored, skipped, 0


if __name__ == "__main__":
    run()
