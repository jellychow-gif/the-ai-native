# Decisions Log

> Chronological record of product decisions and their reasoning.
> Read top-to-bottom for trajectory; jump to a section if a future
> question relates to a specific feature.

---

## Score trajectory

| Date | Score | Trigger |
|---|---|---|
| 2026-05-14 | — | Project kickoff (PRD v1) |
| 2026-05-15 | 7.5 | First public deploy (Step 5 finished) |
| 2026-05-18 | 7.7 | v2.2 — Industry re-merge + Top 5 diversity + Anthropic Playbook + criteria transparency |
| 2026-05-19 | 7.7 → 7.9 | Skills removed from homepage |
| 2026-05-20 | 8.0 | After relevance gate fix (killed 67 % off-topic content) |
| 2026-05-25 | 8.6 | Issue 化 — permanent /issues/[N] URLs + GitHub Action freeze cycle |
| 2026-05-29 | 8.7 | Click-throughs to Issue 01 + Vercel Analytics installed |

---

## D-01 · Anonymity strategy

**Decision**: Strict anonymous publication. No editor name, no MokaHR
mention, no commercial CTA.

**Why**:
- PRD §1.2 third goal: preserve editorial freedom
- Need to be able to criticize MokaHR's own competitors honestly
- HRD-circle trust is built by content quality, not brand affiliation

**Trade-off accepted**: Slower distribution growth, but higher single-
read trust value.

---

## D-02 · Visual aesthetic ≠ Moka Ascend VI

**Decision**: Borrow only the three Eva accent colors (purple / magenta
/ cyan) as section signature lines. Keep the Stripe Press × Anthropic
Research base intact. No dark theme, no glow, no decoration.

**Why**:
- PRD §7.1 explicitly: "视觉本身即声明——一眼让人觉得'这不像一个中国 HR
  公司做的东西'"
- Dark + neon would directly identify the site as Moka brand
- 230-character Chinese summaries need long-form reading affordance —
  serif on light is empirically more readable

**Editor request 2026-05-29**: Color the nav underlines per section.
Done — adds AI-era polish without breaking restraint.

---

## D-03 · Editor voice = C (no human voice)

**Decision**: Drop 本周观察 (weekly observation) editor block entirely.
Rely on Claude's 6-field structured intelligence for "interpretation
layer". Editor doesn't write any prose.

**Why**:
- Editor explicitly chose "C — 纯聚合 + 更多高质量输入" over options A/B
  that would have required their writing time
- 6-field intelligence captures "interpretation" via Sonnet's outputs:
  What Happened / Why Matters / Org/Talent/HR-Op Implications / Prediction
- This is the "Bloomberg Terminal vs News Feed" axis from PRD v2

**Trade-off accepted**: Sacrifices ~1 point of "editorial soul" score.
Bought back partially via curated Skills hand-list.

---

## D-04 · Industry section composition

**Initial v2.1 decision**: Move SaaStr / Stripe / GitHub / Databricks /
HubSpot from Industry to Organization (since they write paradigm content,
not HR Tech product news).

**Editor reversal same day**: "都放一起吧，只是 HR Tech 公司在前面". So:
- Industry = ALL SaaS / AI-native companies
- HR Tech vendors rendered FIRST (Rippling, Eightfold, HR Dive, Glint, Workhuman)
- General SaaS / AI infra rendered SECOND

**Implementation**: `HR_TECH_SOURCES` set in `lib/db.ts`. Section page
splits into two H2 subsections.

---

## D-05 · AI Native relevance gate

**Decision**: Add binary relevance pass BEFORE 3-axis scoring. Off-topic
items get {0, 0, 0} and never enter the candidate pool.

**Why**:
- Editor saw "The Future of Drug Discovery Is 4 Billion Years Old" on
  the homepage. Bio-AI content scored 12/15 on perspective/practice/
  frontier but is irrelevant to HRD audience
- Pure quality without topical relevance = category error

**Impact**: Re-scored 199 items → 135 (67 %) filtered as off-topic.
Remaining 64 → 32 in pool after this gate + freshness. **Single biggest
content-quality improvement in the project.**

---

## D-06 · Section archive freshness gate (180 days)

**Decision** (2026-05-29): Items > 180 days old don't surface on
`/organization`, `/hr`, `/industry` archive pages. Issue archive pages
(`/issues/01` etc.) exempted — they're date-stamped historical records.

**Why**:
- Editor: "不要将超过180天的新闻推到网站"
- Freshness gate already in Top 5 + Featured + Issue freezing
- Section archives were the loophole — 10 items aged out

**Items affected**: 10 (3 Organization / 4 HR / 3 Industry) hidden from
archive pages, still accessible via their Issue URL.

---

## D-07 · Top 5 diversity rule (max 1 per source)

**Decision**: Top 5 homepage hero enforces max 1 item per source, even
when score ranking would put 3 SaaStr items in a row.

**Why**:
- Editor saw "目前看太多来自 SaaStr 的信息源，是否可以多元化来源？"
- A homepage where every signal is from the same publisher feels low-
  signal even if individual quality is high

**Implementation**: `getTopSignals()` iterates score-sorted items but
skips any source already used in current Top 5. Falls through to next
unique source.

---

## D-08 · Issue 化 (weekly issue freezing)

**Decision**: Each Thursday 21:00 BJT, freeze 9 items into a permanent
Issue NN. Item bindings never change after freeze. Section archive +
homepage keep showing newest issue.

**Why**:
- PRD §1.2 second goal — "naturally share with colleagues" requires a
  shareable permanent URL, not "the current state of the homepage"
- Bloomberg-Terminal metaphor: each issue is a date-stamped report

**Implementation**:
- `items.issue_number` column bound at freeze, never modified
- `issues` table stores metadata (number, date_label, item_count)
- `/issues/[number]` page route, statically generated
- `weekly-draft.yml` workflow runs `freeze_issue.py` + commit + deploy

**Result**: Issue 01 (May 25, 9 items) and Issue 02 (May 28, 7 items)
exist. Editor can paste these URLs anywhere — they're permanent.

---

## D-09 · HR 7-module taxonomy (2026-05-29)

**v1 (PRD §6.1)**: 6 modules — 组织设计 / 薪酬 / 绩效 / 员工体验 / 学发 / 招聘

**v2 (this iteration)**: 7 modules — added **HRBP**, relabeled **学发 → L&D**

**Why**:
- Editor: "什么是'学发'？调整为 HRBP 会更好"
- Two distinct points:
  - L&D abbreviation "学发" was unclear to non-Chinese-HR readers
  - HRBP is the most strategically loaded sub-topic for HRD audience in
    AI era (HRBP role transformation > pure L&D)

**Implementation**: rename in `HRModule` type + `HR_MODULE_ORDER`. Reset
all 80 HR items' `hr_module` to NULL and re-ran `classify_hr.py` with
expanded 7-option enum. HRBP captured 9 items previously absorbed into
组织设计 — confirming the new module pulls real signal.

---

## D-10 · Auth strategy for CI deployment

**Decision**: Use Vercel Classic Token (`vcp_*`) stored in GitHub Secret,
NOT Vercel CLI device session token (`vca_*`).

**Why**:
- Tried device token → Vercel fraud-detected cross-environment use and
  revoked it within hours. Workflow hung indefinitely
- Classic tokens (from dashboard) never expire, no rotation
- One-time browser setup cost (editor created `github-actions-deploy`)
  amortizes over forever

**Implementation**:
- Editor created token at vercel.com/account/tokens
- Stored in GitHub Secret `VERCEL_TOKEN` (plus `VERCEL_ORG_ID` and
  `VERCEL_PROJECT_ID`)
- Workflow runs `cd web && npx vercel --yes --prod --token=$VERCEL_TOKEN`
- Vercel project's `rootDirectory` set to null (CLI directs from CWD)

---

## D-11 · Vercel Web Analytics installed (2026-05-29)

**Decision**: Free Hobby tier analytics, no third-party tracking, no
cookies.

**Why**:
- Top 5 ranking currently uses AI score as heat proxy
- In 2-4 weeks, real visitor data could re-rank by actual reading patterns
- Cost: $0, install effort: 5 minutes

**Implementation**: `<Analytics />` from `@vercel/analytics/next` in
root layout. Auto-detects on Vercel-hosted deploys.

**Followup**: Once 1000+ pageviews accumulated, consider weighting AI
score 60% + visitor heat 40% in Top 5 ranking.
