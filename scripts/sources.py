"""Source registry for The AI Native.

Each source has: name, type ('rss' | 'substack' | 'html'), url, section.
Sources marked TODO require custom HTML scrapers; they will be added
in a later iteration. The Python pipeline silently skips unknown types.

Per PRD §4, the target is ~45 sources with 60-65% international.
Current state: 18 active international sources covering Organization (9),
HR (5), Industry (4). More to be added; see TODO block below.
"""
from __future__ import annotations

SOURCES: list[dict] = [
    # ── Organization · 认知输入 ──────────────────────────────────────────
    # VC firms & founder voices — paradigm-level org content
    {
        "name": "Y Combinator Blog",
        "type": "rss",
        "url": "https://www.ycombinator.com/blog/feed.xml",
        "section": "Organization",
    },
    {
        "name": "OpenAI",
        "type": "rss",
        "url": "https://openai.com/blog/rss.xml",
        "section": "Organization",
    },
    {
        "name": "Anthropic News",
        "type": "html_anthropic",
        "url": "https://www.anthropic.com/news",
        "section": "Organization",
    },
    {
        "name": "Sequoia Capital",
        "type": "rss",
        "url": "https://www.sequoiacap.com/feed/",
        "section": "Organization",
    },
    {
        "name": "Elad Gil",
        "type": "substack",
        "url": "https://eladgil.substack.com/feed",
        "section": "Organization",
    },
    {
        "name": "Sarah Tavel",
        "type": "substack",
        "url": "https://sarahtavel.substack.com/feed",
        "section": "Organization",
    },
    {
        "name": "Sam Altman",
        "type": "rss",
        "url": "https://blog.samaltman.com/posts.atom",
        "section": "Organization",
    },
    # Deep-essay outlets — Stratechery / Generalist / Not Boring
    {
        "name": "Stratechery",
        "type": "rss",
        "url": "https://stratechery.com/feed/",
        "section": "Organization",
    },
    {
        "name": "The Generalist",
        "type": "substack",
        "url": "https://www.generalist.com/feed",
        "section": "Organization",
    },
    {
        "name": "Not Boring",
        "type": "substack",
        "url": "https://www.notboring.co/feed",
        "section": "Organization",
    },
    {
        "name": "Vercel Blog",
        "type": "rss",
        "url": "https://vercel.com/atom",
        "section": "Organization",
    },
    {
        "name": "Stanford HAI",
        "type": "rss",
        "url": "https://hai.stanford.edu/news/rss.xml",
        "section": "Organization",
    },
    {
        "name": "Latent Space",
        "type": "substack",
        "url": "https://www.latent.space/feed",
        "section": "Organization",
    },
    {
        "name": "SemiAnalysis",
        "type": "substack",
        "url": "https://semianalysis.com/feed",
        "section": "Organization",
    },
    {
        "name": "Shreyas Doshi",
        "type": "rss",
        "url": "https://www.shreyasdoshi.com/feed",
        "section": "Organization",
    },

    # ── HR · 专业输入 ────────────────────────────────────────────────────
    {
        "name": "Lenny's Newsletter",
        "type": "substack",
        "url": "https://www.lennysnewsletter.com/feed",
        "section": "HR",
    },
    {
        "name": "Hebba Youssef · I Hate It Here",
        "type": "substack",
        "url": "https://ihateithere.substack.com/feed",
        "section": "HR",
    },
    {
        "name": "Harvard Business Review · Talent",
        "type": "html_hbr",
        "url": "https://hbr.org/topic/subject/talent-management",
        "section": "HR",
    },
    {
        "name": "Josh Bersin",
        "type": "rss",
        "url": "https://joshbersin.com/feed/",
        "section": "HR",
    },
    {
        "name": "Reforge Blog",
        "type": "rss",
        "url": "https://www.reforge.com/blog/rss",
        "section": "HR",
    },
    {
        "name": "HR Executive",
        "type": "rss",
        "url": "https://hrexecutive.com/feed/",
        "section": "HR",
    },
    {
        "name": "Adam Grant",
        "type": "substack",
        "url": "https://adamgrant.substack.com/feed",
        "section": "HR",
    },

    # ── Industry · 行动输入 ─────────────────────────────────────────────
    {
        "name": "Rippling Blog",
        "type": "html",
        "url": "https://www.rippling.com/blog",
        "section": "Industry",
    },
    {
        "name": "Stripe Blog",
        "type": "rss",
        "url": "https://stripe.com/blog/feed.rss",
        "section": "Industry",
    },
    {
        "name": "HubSpot Marketing",
        "type": "rss",
        "url": "https://blog.hubspot.com/marketing/rss.xml",
        "section": "Industry",
    },
    {
        "name": "SaaStr",
        "type": "rss",
        "url": "https://www.saastr.com/feed/",
        "section": "Industry",
    },
    {
        "name": "Eightfold AI",
        "type": "rss",
        "url": "https://eightfold.ai/blog/rss/",
        "section": "Industry",
    },
    {
        "name": "GitHub Blog",
        "type": "rss",
        "url": "https://github.blog/feed/",
        "section": "Industry",
    },
    {
        "name": "Databricks Blog",
        "type": "rss",
        "url": "https://www.databricks.com/blog/feed.xml",
        "section": "Industry",
    },
]


# ── TODO sources (need custom HTML scrapers or special access) ─────────
# These appear in PRD §4 but lack public RSS:
#
# Organization:
#   - a16z (no public RSS as of 2026)
#   - First Round Review (newsletter-only)
#   - Foundation Capital
#   - McKinsey Quarterly + Organization Practice
#   - BCG Henderson Institute
#   - Bain & Company
#   - Aaron Levie / Patrick Collison (Twitter — needs Twitter API or browser scraping)
#   - Anthropic letters (SSL/cert issues; retry later)
#
# HR:
#   - Mercer Global Talent Trends
#   - Deloitte Global Human Capital Trends
#   - Korn Ferry Workforce Insights
#   - Gartner HR (paywall)
#   - PwC Workforce of the Future
#   - MIT Sloan Future of Work
#   - HR Brew (returns 403; may need user-agent tweak)
#
# Industry:
#   - Deel / Lattice / Workday / Gusto blogs (no public RSS)
#   - Notion Blog (no public RSS)
#   - Salesforce / Agentforce updates
#   - Juicebox / Lexiom (founder uses; small no-RSS startups)
#   - Gartner Magic Quadrant (paywall)
#   - Forrester HR Tech Wave (paywall)
#   - Product Hunt HR Tech tag
#
# Chinese sources (no public RSS — most are 微信公众号 / 知乎):
#   - 经纬创投, 真格基金, 红杉中国, 险峰长青
#   - 晚点 LatePost, 36氪潜望, 远川研究所, 乱翻书
#   - 腾讯研究院
#   - 穆胜事务所, 陈春花, 彭剑锋华夏基石
#   - 杨国安, 中欧 HR Value, 混沌大学
#
# Strategy: add per-source HTML scrapers as needed, prioritized by signal value.
# WeChat 公众号 may require a third-party RSS bridge (e.g., RSSHub).
