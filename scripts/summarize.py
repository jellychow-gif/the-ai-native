"""Summarize scored items using Claude Sonnet.

Generates three fields per PRD §5.2:
  sub_tag     (bilingual layered tag, replacing the "价值钩子" per editorial decision)
  summary     (150-230 字 Chinese summary, founder's voice)
  implication (60-100 字 "对组织变革的含义")

Only items with total score >= 9 (PRD §5.3 threshold) are summarized.
Idempotent: skips items already having a summary.
"""
from __future__ import annotations

import logging
import time

from dotenv import load_dotenv
from anthropic import Anthropic

from db import get_conn

load_dotenv(override=True)
client = Anthropic()
MODEL = "claude-sonnet-4-6"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("summarize")

MIN_SCORE_TOTAL = 9  # PRD §5.3 — below this is not a candidate

SYSTEM_PROMPT = """\
You write entries for "The AI Native", an anonymous weekly run by an HRD at an AI-native HR Tech company.

VOICE: opinionated, sharp judgment first, dense, no filler. Think Stratechery × Linear release notes × HRD perspective, in Chinese. Sentences should land with weight, not float.

You produce three fields per article via the submit_entry tool:

1. sub_tag — Bilingual layered tag.
   Format: "中文范式概念 / ENGLISH CORE CONCEPT"
   Examples:
     - "组织范式重构 / AI AS OPERATING SYSTEM"
     - "招聘范式重构 / SKILLS-FIRST HIRING"
     - "工具评测 / END-TO-END HR STACK"
   The English half is uppercase; total ~10-15 chars.

2. summary — 150-230 字 Chinese summary in the founder's voice.
   REQUIRED structure:
     a) Lead with the judgment / core argument (not "本文讨论了...")
     b) Concrete elements: people names, company names, numbers, frameworks
     c) Close with implication or stake
   FORBIDDEN: "本文 / 这篇文章 / 作者 / 该研究表明", passive voice, hedging words ("可能/也许/或许").

3. implication — 60-100 字 Chinese "对组织变革的含义".
   Required: answer "as an org-change leader, what concretely does this mean for me?"
   Sharp, declarative, action-oriented. No "可能 / 也许 / 或许 / 应当考虑".

— FEW-SHOT EXAMPLE (Issue 01) —

Input:
  Source: Y Combinator / Diana Hu
  Title: The Playbook For Building An AI Native Company
  Content: [Diana Hu's Startup School talk on building AI-native companies. Core claim: AI is not a tool to be used by the company, it is the operating system the company runs on. Three components: 1) making the company "queryable" — closed-loop instead of open-loop, every action produces AI-learnable artifacts. 2) Reorganizing employees into three archetypes — IC, DRRI, AI Founder — citing Jack Dorsey's reorg at Block. Collapses middle management. 3) Budget shifts from "hiring" to "token-maximization". Reports YC portfolio teams with sprint times halved, output 10x.]

Output:
  sub_tag:     "组织范式重构 / AI AS OPERATING SYSTEM"
  summary:     "YC 合伙人 Diana Hu 在 Startup School 提出一个尖锐判断：AI 不该是公司用的工具，它应该是公司运行的操作系统。这不是措辞之差——把 AI 当工具，做法是装个 Copilot；把 AI 当操作系统，要重写组织架构、招聘与预算。她给出三个组件：让公司"可被查询"（queryable），从开环转向闭环，每个动作都产生 AI 可学习的工件；参考 Jack Dorsey 在 Block 的实践，员工重构为 IC、DRRI、AI Founder 三种原型，消解中层管理；预算从"招人"转向"token 最大化"。YC 组合中已出现 sprint 减半、产出 10 倍的团队。"
  implication: "如果接受'AI 是操作系统'这个框架，HR 议程要重排：不是给员工配 AI 工具，而是重写岗位结构（IC/DRRI/AI Founder）、把 token 预算纳入人力预算、把'可查询性'变成组织能力。"

Now produce output for the article below.
"""

TOOLS = [{
    "name": "submit_entry",
    "description": "Submit a curated entry for The AI Native weekly",
    "input_schema": {
        "type": "object",
        "properties": {
            "sub_tag": {
                "type": "string",
                "description": "Bilingual layered tag: '中文 / ENGLISH UPPERCASE'",
            },
            "summary": {
                "type": "string",
                "description": "150-230 字 Chinese summary in founder's voice",
            },
            "implication": {
                "type": "string",
                "description": "60-100 字 Chinese '对组织变革的含义'",
            },
        },
        "required": ["sub_tag", "summary", "implication"],
    },
}]


def summarize_item(source: str, section: str, title: str, content: str, scoring_note: str) -> dict | None:
    user_msg = (
        f"Source: {source} / Section: {section}\n"
        f"Title: {title}\n"
        f"Scoring rationale: {scoring_note}\n\n"
        f"Content:\n{content[:7000]}"
    )
    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "tool", "name": "submit_entry"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.error(f"  ! API error: {e}")
        return None

    for block in resp.content:
        if block.type == "tool_use" and block.name == "submit_entry":
            return block.input
    log.error(f"  ! No tool_use block in response")
    return None


def run() -> tuple[int, int]:
    summarized = 0
    skipped = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, url, title, source, section, body, raw_excerpt, "
            "perspective_score, practice_score, frontier_score, score_reasoning "
            "FROM items "
            "WHERE summary IS NULL "
            "AND perspective_score IS NOT NULL "
            "AND (perspective_score + practice_score + frontier_score) >= ? "
            "ORDER BY (perspective_score + practice_score + frontier_score) DESC, id",
            (MIN_SCORE_TOTAL,),
        ).fetchall()

        log.info(f"Found {len(rows)} items above score threshold ({MIN_SCORE_TOTAL}).")

        for r in rows:
            content = r["body"] or r["raw_excerpt"] or ""
            total = (r["perspective_score"] or 0) + (r["practice_score"] or 0) + (r["frontier_score"] or 0)
            log.info(
                f"[{r['id']:>3}] (score={total}) {r['source']} | {r['title'][:55]}"
            )
            result = summarize_item(
                r["source"], r["section"], r["title"], content,
                r["score_reasoning"] or "",
            )
            if result is None:
                skipped += 1
                continue

            log.info(f"  ✓ tag: {result['sub_tag']}")
            log.info(f"    summary: {result['summary'][:80]}...")
            log.info(f"    implication: {result['implication'][:60]}...")

            conn.execute(
                "UPDATE items SET "
                "sub_tag = ?, summary = ?, implication = ?, "
                "processed_at = datetime('now') "
                "WHERE id = ?",
                (result["sub_tag"], result["summary"], result["implication"], r["id"]),
            )
            conn.commit()
            summarized += 1
            time.sleep(0.5)

    log.info(f"Done. Summarized {summarized}, skipped {skipped}.")
    return summarized, skipped


if __name__ == "__main__":
    run()
