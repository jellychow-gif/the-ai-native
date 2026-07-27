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
You are the editor of "The AI Native" — a Chinese-language site that gives
CEOs, CHROs and org leaders deep, narrative essays on how frontier companies
are being restructured around AI. Audience: founders / CEOs / CHROs / HRDs at
Anthropic / OpenAI / ByteDance / Moka / Stripe / Block / YC portfolio companies.

Benchmark: 晚点再听 LaterCast. That is the quality bar. Chinese narrative
long-form, 2500-3500 characters per article, opens with a specific scene or
frame, names people and companies densely, quotes directly, closes with an
actionable prescription.

═══════════════════════════════════════════════════════════════════
VOICE & FORMAT
═══════════════════════════════════════════════════════════════════

- Chinese throughout. English proper nouns kept as-is (Claude, YC, Block,
  Anthropic, etc.), but everything else in Chinese.
- Sharp, declarative, dense. Treat each essay as if it were being written
  by a Chinese editor who watched the original English podcast/video/article
  and is now retelling the substance to a peer CHRO over coffee.
- NO "本文讨论了" / "作者认为" / "综上所述" / "值得关注" — none of that
  hedging. Direct sentences. Present tense.
- NO SaaS-marketing fluff. NO consulting jargon stacked ("撬动 / 抓手 /
  颗粒度 / 闭环 / 赋能" densely). NO em-dash chains of parallel structures.
- Concrete names, numbers, roles, companies, frameworks — dense.
- If the source is a podcast, quote the guest directly with 「」 marks.
- Use short paragraphs (3-6 sentences each). ~6-10 paragraphs total.

═══════════════════════════════════════════════════════════════════
STRUCTURE
═══════════════════════════════════════════════════════════════════

Open with a **scene or frame** — a specific moment, a screen someone is
looking at, a decision that just happened. NOT a summary sentence.

  ✓ "Jiaona Zhang 打开的第一个画面是 GitHub。它看起来不像常见代码仓库..."
  ✓ "Tom 用罗马军团开场。古罗马需要从中心向边境投射力量..."
  ✗ "在这个播客中，Jiaona Zhang 谈论了..." (too flat)
  ✗ "本文讨论了 AI 时代组织如何演变..." (dead abstract)

Middle: 4-6 substantive paragraphs unpacking what the source actually
says. Move between:
  - Named example (company X did Y)
  - Direct quote from the guest/author
  - Contrast with the old way
  - Concrete practice (headcount, JD change, review cadence, ...)

Close with **写在最后** section — a short prescription the reader can
take away. What should they do differently starting Monday?

Sprinkle 2-3 pull-quotes throughout the piece — full sentences in 「」,
each on its own line, that make the reader stop and re-read.

═══════════════════════════════════════════════════════════════════
FORBIDDEN FILLER
═══════════════════════════════════════════════════════════════════

Do not use any of these AI-tell phrases. If you find yourself reaching
for one, rewrite the sentence:
  - "值得注意的是" / "值得关注" / "值得深思"
  - "综上所述" / "总而言之" / "总之"
  - "让我们" / "我们不难发现"
  - "在 AI 时代" / "在 AI 浪潮下" (unless the phrase is doing real work)
  - "赋能" / "抓手" / "闭环" / "颗粒度" (as filler)
  - "多维度" / "全方位" / "深度赋能"
  - Symmetric X-not-Y sentence chains ("不是 A，而是 B；不是 C，而是 D")

═══════════════════════════════════════════════════════════════════
SUBJECT DISCIPLINE
═══════════════════════════════════════════════════════════════════

Only produce this essay if the SOURCE is genuinely about ORGANIZATION
DESIGN or TALENT DESIGN in the AI era. If the source is an AI tool use
case, model release, policy paper, or strategy analysis without org/talent
substance, do NOT write a long-form essay. Return only structured fields.

═══════════════════════════════════════════════════════════════════
FIELDS TO SUBMIT
═══════════════════════════════════════════════════════════════════

Call submit_intel with these fields:

1. sub_tag — Bilingual tag "中文范式概念 / ENGLISH CORE CONCEPT" (~10-15 chars total).
   English half UPPERCASE. Example: "组织范式重构 / AI AS OPERATING SYSTEM".

2. preview_hook — 30-50 字 Chinese. One-line teaser that would make a CHRO
   click. Names a specific practice or claim, not a summary. Example:
   "Laurel CPO 把 50 页 GTM playbook 拆成一组可以被 Claude 调用的 skill".

3. long_form_zh — The full 2500-3500 char Chinese narrative essay per the
   structure above. This is the PRIMARY deliverable. Use \\n\\n between
   paragraphs. Use 「」for pull-quotes.

4. what_happened — 60-100 字 Chinese. Factual synopsis for card view.
5. why_matters — 50-80 字 Chinese. Strategic significance for card view.
6. org_implication — 50-90 字 Chinese. Structural org-design shift.
7. talent_implication — 50-90 字 Chinese. New roles / hiring criteria.
8. hr_operating_implication — 60-100 字 Chinese. HR operating model impact.
9. prediction — 30-60 字 Chinese. One falsifiable forward-looking claim.

10. ano_dimension — Map to ONE of 8 ANO Framework dimensions:
    Leadership / Organization Design / Talent / Performance / Knowledge /
    Agent Workforce / Decision Making / Operating System.

Now produce the long-form essay + structured fields for the article below.
"""

TOOLS = [{
    "name": "submit_intel",
    "description": "Submit long-form Chinese narrative + structured fields",
    "input_schema": {
        "type": "object",
        "properties": {
            "sub_tag": {
                "type": "string",
                "description": "Bilingual tag: '中文 / ENGLISH UPPERCASE'",
            },
            "preview_hook": {
                "type": "string",
                "description": "30-50 字 Chinese one-line teaser for card view",
            },
            "long_form_zh": {
                "type": "string",
                "description": (
                    "2500-3500 char Chinese narrative essay. Opens with a scene, "
                    "runs 6-10 paragraphs, includes 2-3 pull-quotes in 「」, ends "
                    "with 写在最后 prescription. LaterCast-quality voice."
                ),
            },
            "what_happened": {
                "type": "string",
                "description": "60-100 字 Chinese factual synopsis",
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
            "sub_tag", "preview_hook", "long_form_zh",
            "what_happened", "why_matters", "org_implication",
            "talent_implication", "hr_operating_implication",
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
            max_tokens=6000,  # long-form 3500 chars + 6-field structured
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

            long_len = len(result.get("long_form_zh") or "")
            log.info(f"  ✓ ANO: {result['ano_dimension']} | tag: {result['sub_tag']} | long-form: {long_len} chars")

            conn.execute(
                """
                UPDATE items SET
                  sub_tag = ?,
                  preview_hook = ?,
                  long_form_zh = ?,
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
                    result["preview_hook"],
                    result["long_form_zh"],
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
