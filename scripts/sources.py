"""Source registry for The AI Native — AI Native Organization Weekly.

Each source carries an internal `tier` (S/A/B/C) that influences ranking but
is NEVER exposed externally per editor directive (June 2026):
  - S: 40% target weight in content pool (highest editorial trust)
  - A: 35% target weight
  - B: 25% target weight
  - C: legacy / probationary (kept running, lowest priority in tiebreaks)

Tiers are used ONLY as a tiebreaker on score, never as a multiplier — to
prevent low-quality S items from beating high-quality B items.
"""
from __future__ import annotations

SOURCES: list[dict] = [
    # ═════════════════════════════════════════════════════════════════
    # S TIER — 40% weight target (highest editorial trust)
    # ═════════════════════════════════════════════════════════════════
    {"name": "OpenAI",                 "type": "rss",            "url": "https://openai.com/blog/rss.xml",                    "section": "Organization", "tier": "S"},
    {"name": "Anthropic News",         "type": "html_anthropic", "url": "https://www.anthropic.com/news",                     "section": "Organization", "tier": "S"},
    {"name": "Josh Bersin",            "type": "rss",            "url": "https://joshbersin.com/feed/",                       "section": "HR",           "tier": "S"},
    {"name": "SaaStr",                 "type": "rss",            "url": "https://www.saastr.com/feed/",                       "section": "Industry",     "tier": "S"},
    {"name": "Lenny's Newsletter",     "type": "substack",       "url": "https://www.lennysnewsletter.com/feed",              "section": "HR",           "tier": "S"},
    {"name": "The Generalist",         "type": "substack",       "url": "https://www.generalist.com/feed",                    "section": "Organization", "tier": "S"},
    {"name": "Stanford HAI",           "type": "rss",            "url": "https://hai.stanford.edu/news/feed",                 "section": "Organization", "tier": "S"},
    {"name": "Elad Gil",               "type": "substack",       "url": "https://eladgil.substack.com/feed",                  "section": "Organization", "tier": "S"},

    # ═════════════════════════════════════════════════════════════════
    # A TIER — 35% weight target
    # ═════════════════════════════════════════════════════════════════
    {"name": "Harvard Business Review · Talent", "type": "html_hbr",  "url": "https://hbr.org/topic/subject/talent-management", "section": "HR",       "tier": "A"},
    {"name": "HR Executive",           "type": "rss",            "url": "https://hrexecutive.com/feed/",                      "section": "HR",           "tier": "A"},
    {"name": "Sequoia Capital",        "type": "rss",            "url": "https://www.sequoiacap.com/feed/",                   "section": "Organization", "tier": "A"},
    {"name": "Reid Hoffman",           "type": "substack",       "url": "https://reidhoffman.org/feed/",                      "section": "Organization", "tier": "A"},
    {"name": "Stratechery",            "type": "rss",            "url": "https://stratechery.com/feed/",                      "section": "Organization", "tier": "A"},
    {"name": "Sarah Tavel",            "type": "substack",       "url": "https://sarahtavel.substack.com/feed",               "section": "Organization", "tier": "A"},
    {"name": "Dwarkesh Podcast",       "type": "rss",            "url": "https://www.dwarkesh.com/feed",                      "section": "Organization", "tier": "A"},
    # Text-rich podcast/newsletter feeds (verified full content:encoded, not audio-only
    # show notes). True audio podcasts (No Priors, Acquired) publish <500 chars of notes
    # and need the transcript pipeline before they're usable — deferred.
    {"name": "Latent Space",           "type": "substack",       "url": "https://www.latent.space/feed",                      "section": "Organization", "tier": "A"},
    {"name": "One Useful Thing",       "type": "substack",       "url": "https://www.oneusefulthing.org/feed",                "section": "Organization", "tier": "A"},
    {"name": "Exponential View",       "type": "substack",       "url": "https://www.exponentialview.co/feed",                "section": "Organization", "tier": "B"},

    # ═════════════════════════════════════════════════════════════════
    # B TIER — 25% weight target
    # ═════════════════════════════════════════════════════════════════
    {"name": "HR Dive",                "type": "rss",            "url": "https://www.hrdive.com/feeds/news/",                 "section": "Industry",     "tier": "B"},
    {"name": "McKinsey Insights",      "type": "rss",            "url": "https://www.mckinsey.com/insights/rss",              "section": "Organization", "tier": "B"},
    {"name": "Y Combinator Blog",      "type": "rss",            "url": "https://www.ycombinator.com/blog/feed.xml",          "section": "Organization", "tier": "B"},
    {"name": "Not Boring",             "type": "substack",       "url": "https://www.notboring.co/feed",                      "section": "Organization", "tier": "B"},

    # ═════════════════════════════════════════════════════════════════
    # C TIER — probationary / legacy. Lowest internal priority but kept
    # running. Some were recent additions; some have niche value.
    # ═════════════════════════════════════════════════════════════════
    {"name": "Sam Altman",                "type": "rss",      "url": "https://blog.samaltman.com/posts.atom",       "section": "Organization", "tier": "C"},
    {"name": "Greg Brockman",             "type": "rss",      "url": "https://blog.gregbrockman.com/rss/",          "section": "Organization", "tier": "C"},
    {"name": "Hebba Youssef · I Hate It Here", "type": "substack", "url": "https://ihateithere.substack.com/feed",  "section": "HR",           "tier": "C"},
    {"name": "Adam Grant",                "type": "substack", "url": "https://adamgrant.substack.com/feed",         "section": "HR",           "tier": "C"},
    {"name": "Patty McCord",              "type": "rss",      "url": "https://pattymccord.com/feed/",               "section": "Organization", "tier": "C"},
    {"name": "Andrew Chen",               "type": "rss",      "url": "https://andrewchen.com/feed/",                "section": "Organization", "tier": "C"},
    {"name": "Paul Graham",               "type": "rss",      "url": "https://paulgraham.com/rss.html",             "section": "Organization", "tier": "C"},
    {"name": "Marc Andreessen · pmarca",  "type": "substack", "url": "https://pmarca.substack.com/feed",            "section": "Organization", "tier": "C"},
    {"name": "DHH · 37signals",           "type": "rss",      "url": "https://world.hey.com/dhh/feed.atom",         "section": "Organization", "tier": "C"},
    {"name": "Rippling Blog",             "type": "html",     "url": "https://www.rippling.com/blog",               "section": "Industry",     "tier": "C"},
    {"name": "Eightfold AI",              "type": "rss",      "url": "https://eightfold.ai/blog/rss/",              "section": "Industry",     "tier": "C"},
]


# ── TODO: NEXT_BACKLOG sources ───────────────────────────────────────
#
# HTML scrapers to write (each 30-60 min):
#   - First Round Review   — index page works, no RSS
#   - a16z                 — needs HTML scrape via main /posts/ feed
#   - Patrick Collison     — /blog index page accessible
#   - Korn Ferry insights  — HTML accessible
#   - Deloitte HC Trends   — HTML accessible
#
# Bot-protected (need Playwright or paid bypass — defer):
#   - MIT Sloan Management Review · BCG · Mercer · Gartner HR
#
# Dead / no longer accessible:
#   - Every · SHRM · Bain
#   - Reforge Blog / Shreyas Doshi / Glint / Workhuman
