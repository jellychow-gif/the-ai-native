"""Classify HR-section items into the 6 PRD modules.

Per PRD §6.1, the HR section has a sub-filter:
  组织设计 / 薪酬 / 绩效 / 员工体验 / 学发 / 招聘
The editor's display-priority order is:
  组织设计 > 薪酬 > 绩效 > 员工体验 > 学发 > 招聘

This runs on items where section='HR' and hr_module IS NULL.
Uses Haiku (cheap, fast — ~$0.001/item). Idempotent.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("classify_hr")

MODULES = ["组织设计", "薪酬", "绩效", "员工体验", "HRBP", "L&D", "招聘"]

SYSTEM_PROMPT = f"""\
Classify the HR article into exactly ONE of these seven modules:

- 组织设计 (org design): role architecture, workflow, agent-employee structure,
  reporting lines, decision rights, role-redesign for AI-augmented work
- 薪酬 (compensation): pay structure, equity, performance pay, total rewards
- 绩效 (performance): performance management, calibration, OKRs, reviews,
  feedback cycles, talent calibration
- 员工体验 (employee experience): onboarding, internal tools, DEI, culture,
  retention, internal communication
- HRBP (HR Business Partner): HRBP role transformation, business-embedded HR,
  HRBP-CEO partnership, strategic workforce planning, business-unit advisory
- L&D (learning & development): training, upskilling, career pathing,
  internal mobility, skills marketplace
- 招聘 (recruiting): sourcing, interviewing, hiring, talent assessment, ATS

Pick the SINGLE module most central to the article. Output only the
module label (one of: {', '.join(MODULES)}).
"""

TOOLS = [{
    "name": "classify",
    "description": "Submit the HR module classification",
    "input_schema": {
        "type": "object",
        "properties": {
            "hr_module": {
                "type": "string",
                "enum": MODULES,
                "description": "The single HR module this article most centrally belongs to",
            },
        },
        "required": ["hr_module"],
    },
}]


def classify(title: str, summary: str, sub_tag: str | None) -> str | None:
    user_msg = (
        f"Title: {title}\n"
        f"Sub-tag: {sub_tag or '-'}\n\n"
        f"Summary:\n{summary or '(no summary)'}"
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=80,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "tool", "name": "classify"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.error(f"  ! API error: {e}")
        return None
    for block in resp.content:
        if block.type == "tool_use" and block.name == "classify":
            return block.input.get("hr_module")
    return None


def run() -> tuple[int, int]:
    classified = 0
    skipped = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, title, summary, sub_tag FROM items "
            "WHERE section = 'HR' AND hr_module IS NULL "
            "ORDER BY id"
        ).fetchall()

        log.info(f"Found {len(rows)} HR items needing module classification.")

        for r in rows:
            module = classify(r["title"], r["summary"], r["sub_tag"])
            if module:
                log.info(f"[{r['id']:>3}] → {module}  | {r['title'][:60]}")
                conn.execute(
                    "UPDATE items SET hr_module = ? WHERE id = ?",
                    (module, r["id"]),
                )
                conn.commit()
                classified += 1
            else:
                skipped += 1
            time.sleep(0.2)

    log.info(f"Done. Classified {classified}, skipped {skipped}.")
    return classified, skipped


if __name__ == "__main__":
    run()
