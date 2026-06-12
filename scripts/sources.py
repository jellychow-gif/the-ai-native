"""Source registry for The AI Native — AI Native Organization Observatory.

Per PRD v2 §1-2 Source Architecture and editor refinement (May 2026):

  Organization → paradigm-level content for CEO / HRD-一号位
                 (frontier operators, org-design thinkers, deep-essay outlets)
  HR           → HR practitioner deep-dives + practice frameworks
  Industry     → HR Tech vendors' AI product launches + industry news
                 (NOT general SaaS thinking — that belongs in Organization)

The pipeline silently skips unknown types. See bottom for deferred sources
that need custom HTML scrapers.
"""
from __future__ import annotations

SOURCES: list[dict] = [
    # ═════════════════════════════════════════════════════════════════
    # Organization · CEO / 创始人 / HRD-一号位 视角
    # Frontier operators, org-design thinkers, paradigm essays
    # ═════════════════════════════════════════════════════════════════
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
    },    {
        "name": "Stanford HAI",
        "type": "rss",
        "url": "https://hai.stanford.edu/news/rss.xml",
        "section": "Organization",
    },    {
        "name": "Shreyas Doshi",
        "type": "rss",
        "url": "https://www.shreyasdoshi.com/feed",
        "section": "Organization",
    },

    # ── CEO / founder-tier (Iteration v3, June 2026) ─────────────
    # Editor-confirmed priority: close the CEO 一号位 audience gap.
    # Note: Patrick Collison / Cash App·Block / BCG Henderson Institute
    # all probed 200 initially but block subsequent automated reads.
    # Documented in SOURCES.md as "deferred — bot-protected".
    {
        "name": "Reid Hoffman",
        "type": "substack",
        "url": "https://reidhoffman.org/feed/",
        "section": "Organization",
    },    {
        "name": "McKinsey Insights",
        "type": "rss",
        "url": "https://www.mckinsey.com/insights/rss",
        "section": "Organization",
    },
    # AI lab leaders / founders — June 2026 expansion per editor request
    # "Claude 类的创始人、联创等大牛有关原生组织、人才等观点分享"
    {
        "name": "Greg Brockman",
        "type": "rss",
        "url": "https://blog.gregbrockman.com/rss/",
        "section": "Organization",
    },    # Individual blogs — high-leverage editor / founder voices (June 2026)
    {
        "name": "Patty McCord",
        "type": "rss",
        "url": "https://pattymccord.com/feed/",
        "section": "Organization",
    },
    {
        "name": "Andrew Chen",
        "type": "rss",
        "url": "https://andrewchen.com/feed/",
        "section": "Organization",
    },
    {
        "name": "Paul Graham",
        "type": "rss",
        "url": "https://paulgraham.com/rss.html",
        "section": "Organization",
    },
    {
        "name": "Marc Andreessen · pmarca",
        "type": "substack",
        "url": "https://pmarca.substack.com/feed",
        "section": "Organization",
    },
    {
        "name": "DHH · 37signals",
        "type": "rss",
        "url": "https://world.hey.com/dhh/feed.atom",
        "section": "Organization",
    },
    # ═════════════════════════════════════════════════════════════════
    # HR · HR 各模块的实践与重构
    # ═════════════════════════════════════════════════════════════════
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

    # ═════════════════════════════════════════════════════════════════
    # Industry · AI Native SaaS 公司产品动态
    # HR Tech 公司优先（最直接命中受众），其次通用 SaaS / AI 基础设施。
    # 板块页通过 lib/db.ts HR_TECH_SOURCES + industryPriority() 做显示排序。
    # ═════════════════════════════════════════════════════════════════
    # HR Tech 公司（priority 1）
    {
        "name": "Rippling Blog",
        "type": "html",
        "url": "https://www.rippling.com/blog",
        "section": "Industry",
    },
    {
        "name": "Eightfold AI",
        "type": "rss",
        "url": "https://eightfold.ai/blog/rss/",
        "section": "Industry",
    },
    {
        "name": "HR Dive",
        "type": "rss",
        "url": "https://www.hrdive.com/feeds/news/",
        "section": "Industry",
    },
    {
        "name": "Glint · LinkedIn",
        "type": "rss",
        "url": "https://www.glintinc.com/blog/feed/",
        "section": "Industry",
    },
    {
        "name": "Workhuman",
        "type": "rss",
        "url": "https://www.workhuman.com/blog/feed/",
        "section": "Industry",
    },
    # 通用 SaaS / AI 基础设施（priority 2）—— 仍属"产品动态"范畴
    {
        "name": "SaaStr",
        "type": "rss",
        "url": "https://www.saastr.com/feed/",
        "section": "Industry",
    },
]


# ── TODO sources (deferred — need custom HTML scrapers) ─────────────
#
# HR Tech vendors (Priority for Industry section, all behind Marketo/HubSpot):
#   - Workday (newsroom + blog)
#   - Lattice
#   - Deel
#   - BambooHR
#   - ServiceNow HR
#   - Greenhouse
#   - Personio
#   - Gusto
#   - Cornerstone
#   - HiBob
#   - Beamery
#   - Phenom
#   - Visier
#   - Culture Amp
#   - 15Five
#
# Frontier operators without RSS:
#   - Block, Duolingo, Tesla, Notion, Cursor, Perplexity, Figma, Snowflake
#
# Org Design Thinkers (Twitter/LinkedIn only):
#   - Claire Hughes Johnson, Patty McCord, Reed Hastings, Brian Chesky,
#     Keith Rabois, Lars Schmidt, Laszlo Bock, Diana Hu (YC Library)
#
# Research / Consulting (long-form reports, irregular cadence):
#   - McKinsey Global Institute, BCG Henderson Institute, Bain
#   - HBS Working Knowledge, MIT Sloan Future of Work, NBER
#   - Microsoft Research, PwC Future of Work, Deloitte Human Capital
#
# Chinese sources (need WeChat → RSSHub bridge):
#   - 穆胜事务所, 陈春花数智新解, 华夏基石管理评论
#   - 杨国安, 中欧 HR Value, 混沌大学 CEO 课
#   - 经纬创投, 红杉中国, 真格基金, 险峰长青
#   - 晚点 LatePost, 36氪潜望, 远川研究所, 乱翻书
