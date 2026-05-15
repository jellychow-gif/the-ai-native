"""Source registry. Phase 1 has 3 demo sources; Phase 7 will scale to ~45."""
from __future__ import annotations

SOURCES: list[dict] = [
    {
        "name": "Y Combinator Blog",
        "type": "rss",
        "url": "https://www.ycombinator.com/blog/feed.xml",
        "section": "Organization",
    },
    {
        "name": "Lenny's Newsletter",
        "type": "substack",
        "url": "https://www.lennysnewsletter.com/feed",
        "section": "HR",
    },
    {
        "name": "Rippling Blog",
        "type": "html",
        "url": "https://www.rippling.com/blog",
        "section": "Industry",
    },
]
