# Next Iteration Backlog

> Open items deferred when Claude Code paused. Ranked by ROI.
> When editor + Claude resume, pick top items first.

## 🎯 EDITOR-CONFIRMED PRIORITY FOR NEXT ITERATION

**B + C** (per editor decision 2026-05-29 before pause):

- **B**: Top 5 structural guarantee — at least 1 Organization slot (B2 below)
- **C**: Add CEO-tier sources to close the CEO/founder一号位 gap (B1 below)

Skip everything else until B+C ship.

---

## 🔴 High value, low effort

### B1. Add CEO-tier sources (CEO/founder一号位 coverage gap)

**Problem**: Current 32 sources skew heavily HR + SaaS. Pure CEO/founder
content under-represented. PRD v2 target audience explicitly lists
Anthropic / OpenAI / Block / Tesla / Duolingo / YC People leaders.

**Action**:
- Re-probe First Round Review (`https://review.firstround.com/feed` was
  301 — follow redirect, find new feed URL)
- Find a16z's current RSS (their `/feed/` 404'd — try `a16z.com/feed/rss/`
  or scrape `a16z.com/posts/` HTML)
- Add Block Engineering blog (likely needs HTML scraper)
- Add Duolingo Engineering (`https://blog.duolingo.com/feed/`?)
- Add Substack-discoverable CEO essays: Reid Hoffman, Marc Andreessen,
  Aaron Levie if any has Substack mirror

**Effort**: ~1.5 hours.

**Impact**: +0.2 score, materially better Top 5 for CEO audience.

---

### B2. Top 5 structural guarantee — at least 1 Organization slot

**Problem**: Score-only ranking can produce a Top 5 with 0 Organization
items in slow-news weeks. CEO/founder audience needs a guaranteed
voice from their tier.

**Action**: Modify `getTopSignals()` to ensure ≥ 1 Organization item
before applying score+diversity. If no Organization item qualifies
above threshold, drop to threshold 8 just for Organization slot.

**Effort**: ~10 minutes.

**Impact**: +0.1 score, immediate.

---

### B3. Section page freshness exception for "evergreen" frameworks

**Problem**: Some content is paradigm-defining and stays valuable >
180 days (e.g. Anthropic's Founder's Playbook PDF). Current strict
180-day gate hides them from archives.

**Action**: Add `is_evergreen` boolean on items, default false. Editor
manually flips to true for ~5-10 paradigm pieces. These bypass freshness
gate on section archives (still excluded from Top 5 which stays fresh).

**Effort**: ~30 min (schema + UI annotation).

**Impact**: +0.1 score, preserves long-tail value.

---

## 🟡 Medium value, medium effort

### B4. `/companies/[name]` company timeline pages

**Concept**: For each company mentioned across many signals (Anthropic,
OpenAI, Stripe, Workday, YC...) create an archive page showing every
signal about that company over time. Editor said CHROs at peer companies
want to "follow specific company AI-native evolution".

**Action**:
- Add company-extraction pass (Claude Haiku) on every item — outputs
  list of companies mentioned
- Build `/companies` index + `/companies/[slug]` detail
- Start with hardcoded canonical 6: Anthropic / OpenAI / Stripe /
  Workday / YC / Block

**Effort**: ~1.5 hours.

**Impact**: +0.15 score. High share-value per page.

---

### B5. Chinese source ingestion

**Problem**: PRD §4 mandates 35-40% Chinese sources. Currently 0%.
Editor "naturally share with colleagues" goal handicapped for Chinese
HR circles without Chinese sources.

**Targets** (PRD list):
- 穆胜事务所 (org design)
- 陈春花 数智新解
- 华夏基石管理评论
- 中欧 HR Value
- 混沌大学 CEO 课文字稿
- 经纬创投 / 红杉中国 / 真格基金
- 晚点 LatePost 创始人深访
- 36氪潜望 / 远川研究所

**Tech challenge**: All are WeChat 公众号 — no public RSS. Options:
1. RSSHub bridge (rsshub.app or self-host) — unreliable in China
2. Editor manually pastes URLs to a sidecar JSON, AI processes
3. Use wechat2rss.xlab.app / wechatify.com (paid services)

**Recommendation**: Start with option 2 (manual paste) — zero infra cost
+ editor retains curation control. Can automate later.

**Effort**: ~2 hours for option 2.

**Impact**: +0.3 score. PRD compliance + Chinese audience reach.

---

### B6. RSS output `/feed.xml`

**Problem**: Heavy readers use RSS readers, not browser. No way for
target CHRO audience to subscribe via Feedly / Inoreader.

**Action**: Generate `/feed.xml` Next.js route from items.json. Include
latest issue contents.

**Effort**: ~30 min.

**Impact**: +0.1 score. Better retention for power readers.

---

## 🟢 Long-term

### B7. Weighting Top 5 by real visitor heat (after analytics matures)

**Wait for**: 4+ weeks of Vercel Analytics data (~100 unique visitors
per item URL minimum for signal).

**Action**: Modify `getTopSignals()` to blend AI score (60%) and recent
visitor count per source (40%).

**Effort**: ~1 hour. **Do not execute before data exists** — meaningless
without N ≥ 100.

---

### B8. Editor inbox — manual signal-add path

**Concept**: Editor sees something on Twitter / WeChat / podcast that
doesn't match any source. Today they have no path to inject it.

**Action**: Build `scripts/add_signal.py` — takes a URL, fetches body,
runs AI pipeline manually, slots into next issue.

**Effort**: ~1 hour.

**Impact**: +0.2 score. Editor sovereignty over content.

---

### B9. Visual: dark mode toggle

**Defer**: Editor explicitly prioritized clean light mode for reading
experience. Add only if user-segment data shows dark-mode preference.

---

### B10. PDF / long-form report ingestion

**Concept**: Some signals come as PDFs (Anthropic Founder Playbook,
McKinsey reports). Currently can only enter Skills (manual) or be
ignored.

**Action**: Build `scripts/ingest_pdf.py` — uses pdftotext + AI to
score + summarize a PDF given a URL.

**Effort**: ~2 hours.

**Impact**: Unlocks "Reports & Playbooks" content lane.

---

## ⚪ Deferred / parked

### B11. MokaHR commercial parallel site

Editor's CEO wants a separate branded content channel for client
acquisition ("组织 AI native 进化"). I recommended bifurcation — keep
The AI Native anonymous, build the MokaHR-branded site separately
sharing 80% of the tech stack but different brand / CTAs / lead
capture. Editor parked decision pending later capacity discussion.

**Don't merge with The AI Native under any condition** — would destroy
the anonymous editorial position.
