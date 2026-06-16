"""Generate structured intelligence per article using Claude Sonnet.

PRD v2 §3 Intelligence Extraction Pipeline — produces 7 fields per article
instead of the earlier {summary, implication} pair:

  what_happened              — factual summary
  why_matters                — strategic significance
  org_implication            — how organizational design shifts
  talent_implication         — new capabilities / roles emerging
  hr_operating_implication   — changes to hiring/leveling/dev/perf/workforce planning
  prediction                 — forward-looking inference
  insight_class              — 10-category classification

Also still emits:
  sub_tag                    — bilingual signature tag for the card

Only items with total_score >= 9 (PRD §5.3) are summarized.
Idempotent: skips items already having what_happened (the canonical v2 field).
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

MIN_SCORE_TOTAL = 9

# ANO Framework — 8 dimensions of AI Native Organization (the product's IP)
# Replaces the earlier 10-category insight_class taxonomy. Cleaner mapping,
# closer to editor's mental model of the audience's framework needs.
ANO_DIMENSIONS = [
    "Leadership",          # AI 如何改变领导方式
    "Organization Design", # AI 是否减少管理层级 / 组织架构如何变
    "Talent",              # 企业需要什么样的人才
    "Performance",         # AI 如何改变绩效管理
    "Knowledge",           # 知识如何沉淀与调用
    "Agent Workforce",     # Agent 如何成为团队成员
    "Decision Making",     # AI 如何参与决策
    "Operating System",    # 企业如何运行 AI First 工作流
]

SYSTEM_PROMPT = f"""\
You write structured intelligence for "The AI Native — AI Native Organization
Weekly", the first stop for global CEOs, CHROs and org leaders researching
AI Native Companies. Audience: founders / CEOs / CHROs / HRDs at Anthropic /
OpenAI / ServiceNow / Workday / Block / Tesla / Duolingo / YC.

VOICE: Sharp, declarative, dense. Treat each entry as an analyst note an
informed peer would slack to their VP-People. No hedging, no "本文讨论了",
no SaaS-marketing fluff. Chinese for the body fields. Concrete names, numbers,
companies, frameworks — wherever the source supports them.

For each article, call submit_intel with these fields:

1. sub_tag — Bilingual tag "中文范式概念 / ENGLISH CORE CONCEPT" (~10-15 chars total).
   English half UPPERCASE. Example: "组织范式重构 / AI AS OPERATING SYSTEM".

2. what_happened — 60-100 字 Chinese. Factual: who did what, when, with what
   measurable specifics. Lead with the actor. NO judgment yet.

3. why_matters — 50-80 字 Chinese. Strategic significance. Why this is a
   signal worth a CHRO's 30 seconds. Sharp claim, not summary.

4. org_implication — 50-90 字 Chinese. How organizational architecture or
   coordination shifts because of this. Reference roles, teams, decision rights.

5. talent_implication — 50-90 字 Chinese. What new capabilities, roles, or
   talent archetypes emerge. Be specific (titles, skills, levels).

6. hr_operating_implication — 60-100 字 Chinese. Concrete changes to the HR
   operating model: hiring criteria, leveling, learning, performance, comp,
   workforce planning. Action-oriented.

7. prediction — 30-60 字 Chinese. Forward-looking inference: "By 20XX, ...".
   One concrete prediction, falsifiable in principle.

8. ano_dimension — Map this signal to ONE of 8 ANO Framework dimensions:
   - "Leadership": AI changing how executives lead / CEO time allocation /
     leadership behavior under AI augmentation
   - "Organization Design": org chart shifts / layer compression / role
     merging / team-size reset / reporting structure
   - "Talent": new role archetypes / hiring criteria / skills demanded /
     who you bring in (not how you evaluate them)
   - "Performance": calibration / OKRs / reviews / comp linkage /
     AI-augmented evaluation
   - "Knowledge": institutional memory / documentation / AI-queryable
     knowledge bases / skills artifacts
   - "Agent Workforce": agents joining the team / agent-human collaboration
     / agent ownership of work
   - "Decision Making": AI in boardroom / governance / decision-support
     systems / AI augmenting judgment
   - "Operating System": workflows / processes / infrastructure for
     AI-first work (Notion's spec-driven dev, Stripe's Protodash, etc.)
   Pick the SINGLE dimension MOST central to the piece.

— FEW-SHOT EXAMPLE —

Input title: "The Playbook For Building An AI Native Company"
Input source: Y Combinator / Diana Hu

Output:
  sub_tag: "组织范式重构 / AI AS OPERATING SYSTEM"
  what_happened: "YC 合伙人 Diana Hu 在 2026 Startup School 提出 AI Native 公司构建框架：让公司'可被查询'、员工重构为 IC/DRRI/AI Founder 三种原型、预算从招人转向 token 最大化。引用 Jack Dorsey 在 Block 的实践。YC 组合中已出现 sprint 减半、产出 10 倍团队。"
  why_matters: "把'AI 是工具'升级为'AI 是操作系统'——这不是措辞之差。装 Copilot vs 重写组织架构、招聘、预算结构，是两种公司之间的鸿沟。"
  org_implication: "公司必须从'开环'切到'闭环'：每个动作产生 AI 可学习的工件，中层管理被三型架构（IC/DRRI/AI Founder）消解。决策路径变短，决策可学习。"
  talent_implication: "新增 DRRI（Directly Responsible Resourcing Individual）和 AI Founder 角色；传统 manager 岗压缩。员工核心能力从'执行'转为'编排上下文 + 校准 AI 输出'。"
  hr_operating_implication: "招聘 JD 重写：删除年限要求，加 token 工作流熟练度、AI 编排能力、自驱密度三项。绩效评估从产出物转为 token-per-outcome 杠杆率。HR 预算条目新增 token quota。"
  prediction: "至 2028 年，YC 主流公司将正式发布 AI Founder 岗位职级，DRRI 进入 HR ATS 标准选项。"
  ano_dimension: "Organization Design"

Now produce structured intelligence for the article below.
"""

TOOLS = [{
    "name": "submit_intel",
    "description": "Submit structured intelligence for a single article",
    "input_schema": {
        "type": "object",
        "properties": {
            "sub_tag": {
                "type": "string",
                "description": "Bilingual tag: '中文 / ENGLISH UPPERCASE'",
            },
            "what_happened": {
                "type": "string",
                "description": "60-100 字 Chinese factual summary",
            },
            "why_matters": {
                "type": "string",
                "description": "50-80 字 Chinese strategic significance",
            },
            "org_implication": {
                "type": "string",
                "description": "50-90 字 Chinese organizational implication",
            },
            "talent_implication": {
                "type": "string",
                "description": "50-90 字 Chinese talent/role implication",
            },
            "hr_operating_implication": {
                "type": "string",
                "description": "60-100 字 Chinese HR operating model implication",
            },
            "prediction": {
                "type": "string",
                "description": "30-60 字 Chinese forward-looking inference",
            },
            "ano_dimension": {
                "type": "string",
                "enum": ANO_DIMENSIONS,
                "description": "One of 8 ANO Framework dimensions",
            },
        },
        "required": [
            "sub_tag", "what_happened", "why_matters",
            "org_implication", "talent_implication", "hr_operating_implication",
            "prediction", "ano_dimension",
        ],
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
            max_tokens=2500,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            tool_choice={"type": "tool", "name": "submit_intel"},
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.error(f"  ! API error: {e}")
        return None

    for block in resp.content:
        if block.type == "tool_use" and block.name == "submit_intel":
            return block.input
    log.error("  ! No tool_use block in response")
    return None


def run() -> tuple[int, int]:
    summarized = 0
    skipped = 0
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, url, title, source, section, body, raw_excerpt, "
            "perspective_score, practice_score, frontier_score, score_reasoning "
            "FROM items "
            "WHERE what_happened IS NULL "             # v2 canonical gate
            "AND perspective_score IS NOT NULL "
            "AND (perspective_score + practice_score + frontier_score) >= ? "
            "ORDER BY (perspective_score + practice_score + frontier_score) DESC, id",
            (MIN_SCORE_TOTAL,),
        ).fetchall()

        log.info(f"Found {len(rows)} items needing v2 intelligence (threshold {MIN_SCORE_TOTAL}).")

        for r in rows:
            content = r["body"] or r["raw_excerpt"] or ""
            total = (r["perspective_score"] or 0) + (r["practice_score"] or 0) + (r["frontier_score"] or 0)
            log.info(f"[{r['id']:>3}] (score={total}) {r['source']} | {r['title'][:55]}")
            result = summarize_item(
                r["source"], r["section"], r["title"], content,
                r["score_reasoning"] or "",
            )
            if result is None:
                skipped += 1
                continue

            log.info(f"  ✓ ANO: {result['ano_dimension']} | tag: {result['sub_tag']}")

            conn.execute(
                """
                UPDATE items SET
                  sub_tag = ?,
                  what_happened = ?,
                  why_matters = ?,
                  org_implication = ?,
                  talent_implication = ?,
                  hr_operating_implication = ?,
                  prediction = ?,
                  ano_dimension = ?,
                  processed_at = datetime('now')
                WHERE id = ?
                """,
                (
                    result["sub_tag"],
                    result["what_happened"],
                    result["why_matters"],
                    result["org_implication"],
                    result["talent_implication"],
                    result["hr_operating_implication"],
                    result["prediction"],
                    result["ano_dimension"],
                    r["id"],
                ),
            )
            conn.commit()
            summarized += 1
            time.sleep(0.4)

    log.info(f"Done. Summarized {summarized} (v2 6-field intel), skipped {skipped}.")
    return summarized, skipped


if __name__ == "__main__":
    run()
