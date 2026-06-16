"""Re-classify already-summarized items into ANO Framework 8 dimensions.

ANO replaces the legacy 10-category insight_class. This is a one-shot
migration: items with what_happened but no ano_dimension get a single
Claude Haiku call to assign their dimension.

Future items go through summarize.py which writes ano_dimension directly.
"""
from __future__ import annotations

import logging
import time

from dotenv import load_dotenv
from anthropic import Anthropic

from db import get_conn

load_dotenv(override=True)
client = Anthropic()
MODEL = "claude-haiku-4-5"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("classify_ano")

ANO_DIMENSIONS = [
    "Leadership", "Organization Design", "Talent", "Performance",
    "Knowledge", "Agent Workforce", "Decision Making", "Operating System",
]

SYSTEM_PROMPT = f"""\
Classify the article into exactly ONE ANO Framework dimension:

- "Leadership": how executives lead under AI / CEO time allocation /
  leadership behavior augmented by AI
- "Organization Design": org chart shifts / layer compression / role merging
  / team size / reporting structure
- "Talent": new role archetypes / hiring criteria / skills demanded /
  who you bring in (NOT how you evaluate them)
- "Performance": calibration / OKRs / reviews / comp linkage /
  AI-augmented evaluation
- "Knowledge": institutional memory / documentation / AI-queryable
  knowledge bases / skills artifacts
- "Agent Workforce": agents joining the team / agent-human collaboration
  / agent ownership of work
- "Decision Making": AI in boardroom / governance / decision-support
  systems / AI augmenting judgment
- "Operating System": workflows / processes / infrastructure for AI-first
  work (Notion's spec-driven dev, Stripe's Protodash, etc.)

Pick the SINGLE dimension MOST central to the piece. Output only the
exact dimension name (one of: {", ".join(ANO_DIMENSIONS)}).
"""

TOOLS = [{
    "name": "classify",
    "description": "Submit ANO dimension classification",
    "input_schema": {
        "type": "object",
        "properties": {
            "ano_dimension": {"type": "string", "enum": ANO_DIMENSIONS},
        },
        "required": ["ano_dimension"],
    },
}]


def classify(title, sub_tag, what_happened, why_matters):
    user_msg = (
        f"Title: {title}\n"
        f"Sub-tag: {sub_tag or '-'}\n"
        f"What happened: {what_happened or ''}\n"
        f"Why matters: {why_matters or ''}"
    )
    try:
        resp = client.messages.create(
            model=MODEL, max_tokens=80, system=SYSTEM_PROMPT,
            tools=TOOLS, tool_choice={"type": "tool", "name": "classify"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.error(f"  ! API error: {e}")
        return None
    for block in resp.content:
        if block.type == "tool_use" and block.name == "classify":
            return block.input.get("ano_dimension")
    return None


def run():
    classified = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, sub_tag, what_happened, why_matters FROM items "
            "WHERE what_happened IS NOT NULL AND ano_dimension IS NULL "
            "ORDER BY id"
        ).fetchall()
        log.info(f"Found {len(rows)} items needing ANO classification.")
        for r in rows:
            dim = classify(r["title"], r["sub_tag"], r["what_happened"], r["why_matters"])
            if dim:
                log.info(f"[{r['id']:>3}] → {dim:<20} | {r['title'][:55]}")
                conn.execute("UPDATE items SET ano_dimension = ? WHERE id = ?", (dim, r["id"]))
                conn.commit()
                classified += 1
            time.sleep(0.2)
    log.info(f"Done. ANO-classified {classified} items.")


if __name__ == "__main__":
    run()
