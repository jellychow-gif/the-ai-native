# Sources Inventory

> The authoritative source list lives in `scripts/sources.py`. This file
> is a human-readable mirror with context + adding/removing guidance.

**Current total: 32 sources · 100% international**

---

## Organization (15)

Target reader: CEO / founder / HRD-一号位. Paradigm-level content.

| # | Source | Type | URL | Notes |
|---|---|---|---|---|
| 1 | Y Combinator Blog | RSS | https://www.ycombinator.com/blog/feed.xml | Diana Hu, Garry Tan, Jared Friedman |
| 2 | OpenAI | RSS | https://openai.com/blog/rss.xml | Research + product |
| 3 | Anthropic News | HTML scraper | https://www.anthropic.com/news | Custom scraper in scrape.py (no RSS) |
| 4 | Sequoia Capital | RSS | https://www.sequoiacap.com/feed/ | Partners essays |
| 5 | Elad Gil | Substack | https://eladgil.substack.com/feed | AI investor |
| 6 | Sarah Tavel | Substack | https://sarahtavel.substack.com/feed | Benchmark GP |
| 7 | Sam Altman | Atom | https://blog.samaltman.com/posts.atom | OpenAI CEO |
| 8 | Stratechery | RSS | https://stratechery.com/feed/ | Ben Thompson |
| 9 | The Generalist | Substack | https://www.generalist.com/feed | Mario Gabriele |
| 10 | Not Boring | Substack | https://www.notboring.co/feed | Packy McCormick |
| 11 | Vercel Blog | RSS | https://vercel.com/atom | Frontier eng |
| 12 | Stanford HAI | RSS | https://hai.stanford.edu/news/rss.xml | Research |
| 13 | Latent Space | Substack | https://www.latent.space/feed | AI engineering |
| 14 | SemiAnalysis | Substack | https://semianalysis.com/feed | AI infra |
| 15 | Shreyas Doshi | RSS | https://www.shreyasdoshi.com/feed | Product/PM |

---

## HR (7)

Target reader: HR-一号位. Practitioner deep-dives + frameworks.

| # | Source | Type | URL | Notes |
|---|---|---|---|---|
| 16 | Lenny's Newsletter | Substack | https://www.lennysnewsletter.com/feed | Best general HR/PM signal |
| 17 | Hebba Youssef · I Hate It Here | Substack | https://ihateithere.substack.com/feed | HR meta-newsletter, highest HRD pass-rate |
| 18 | Harvard Business Review · Talent | HTML | https://hbr.org/topic/subject/talent-management | Custom scraper, AI-relevance filtered |
| 19 | Josh Bersin | RSS | https://joshbersin.com/feed/ | HR industry analyst |
| 20 | Reforge Blog | RSS | https://www.reforge.com/blog/rss | Talent + org content |
| 21 | HR Executive | RSS | https://hrexecutive.com/feed/ | CHRO-level |
| 22 | Adam Grant | Substack | https://adamgrant.substack.com/feed | Org psych |

---

## Industry (10) — HR Tech first, then general SaaS / AI infra

Target reader: practitioner curious about AI product evolution.

### HR Tech vendors (priority 1)

| # | Source | Type | URL |
|---|---|---|---|
| 23 | Rippling Blog | HTML | https://www.rippling.com/blog |
| 24 | Eightfold AI | RSS | https://eightfold.ai/blog/rss/ |
| 25 | HR Dive | RSS | https://www.hrdive.com/feeds/news/ |
| 26 | Glint · LinkedIn | RSS | https://www.glintinc.com/blog/feed/ |
| 27 | Workhuman | RSS | https://www.workhuman.com/blog/feed/ |

### General SaaS / AI infra (priority 2)

| # | Source | Type | URL |
|---|---|---|---|
| 28 | SaaStr | RSS | https://www.saastr.com/feed/ |
| 29 | Stripe Blog | RSS | https://stripe.com/blog/feed.rss |
| 30 | GitHub Blog | RSS | https://github.blog/feed/ |
| 31 | Databricks Blog | RSS | https://www.databricks.com/blog/feed.xml |
| 32 | HubSpot Marketing | RSS | https://blog.hubspot.com/marketing/rss.xml |

---

## Sources tried but not added

### Failed RSS probes
- **a16z**: `https://a16z.com/feed/` → 404
- **First Round Review**: 301 redirect, didn't follow up
- **Foundation Capital**: 404
- **Workday Newsroom / Blog**: 404 (all paths tried)
- **Lattice**: 404
- **Deel**: 404
- **BambooHR / Greenhouse / Personio / Gusto / Cornerstone / HiBob /
  Paychex**: All 404 or 403
- **Beamery / Phenom / Visier / Culture Amp / 15Five**: 404 / timeout
- **Notion blog**: 404 (no public RSS as of 2026-05)
- **Snowflake / Perplexity**: 403 (rate-limited bots)
- **Figma blog**: 404
- **Linear changelog**: 404
- **MIT Sloan ideas**: 404
- **Microsoft Research**: 403
- **HBR generic feed**: 404 (used topic-specific HTML scraper instead)

### Deferred (need custom HTML scrapers)
- Cursor Engineering
- Block / Duolingo / Tesla
- Notion News / Snowflake / Figma / Perplexity
- McKinsey Global Institute reports
- BCG Henderson Institute
- Bain Org reports

### Deferred (Twitter / X only, no RSS available)
- Patrick Collison
- Tobi Lütke
- Aaron Levie
- Brian Chesky
- Keith Rabois
- Reid Hoffman (Substack possible — check)
- Marc Andreessen
- Jack Dorsey letters

### Deferred (Chinese WeChat 公众号 — need RSSHub or manual)
- 穆胜事务所
- 陈春花 数智新解
- 华夏基石管理评论
- 中欧 HR Value
- 混沌大学 CEO 课
- 经纬创投 / 红杉中国 / 真格基金 / 险峰长青
- 晚点 LatePost
- 36氪潜望
- 远川研究所
- 乱翻书 (潘乱)
- 腾讯研究院

---

## Adding a new source

1. Probe RSS first: `curl -sS -o /dev/null -L --max-time 10 -w "%{http_code}\n" <feed-url>`
2. If 200 + valid XML: add to `scripts/sources.py` with type "rss" or "substack"
3. If 200 + HTML only: write a custom function in `scripts/scrape.py`
   (see `fetch_html_anthropic` / `fetch_html_hbr` as templates)
4. Section assignment:
   - Paradigm essay / VC / founder / consulting → Organization
   - HR practitioner / HR media → HR
   - HR Tech vendor / SaaS / AI infra company → Industry
5. Run `python scripts/scrape.py` locally to validate
6. Commit + push → daily-pipeline picks it up next 14:00 BJT

---

## Removing a source

1. Delete from `scripts/sources.py`
2. Existing items remain in DB with their old `source` value; they won't
   be re-scraped but they'll keep appearing in archives until they age
   out of the 180-day window
3. If you want to fully purge: `DELETE FROM items WHERE source = '<name>'`
