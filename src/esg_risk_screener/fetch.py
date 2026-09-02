"""Fetch and normalise news items from RSS/Atom feeds."""

from __future__ import annotations

import feedparser

from esg_risk_screener.models import Article

# (feed url, human-readable source name)
DEFAULT_FEEDS: list[tuple[str, str]] = [
    ("https://feeds.bbci.co.uk/news/business/rss.xml", "BBC Business"),
    ("http://feeds.reuters.com/reuters/businessNews", "Reuters Business"),
    ("https://www.theguardian.com/business/rss", "The Guardian Business"),
]


def _clean(text: str | None) -> str:
    return (text or "").strip()


def fetch_feed(url: str, source: str) -> list[Article]:
    """Parse one feed and return its entries as :class:`Article` objects.

    Duplicate URLs within the same feed are collapsed. Network and parse errors
    are swallowed and yield an empty list - one dead feed should not stop a run.
    """
    parsed = feedparser.parse(url)
    articles: dict[str, Article] = {}

    for entry in parsed.entries:
        link = _clean(getattr(entry, "link", None))
        title = _clean(getattr(entry, "title", None))
        if not link or not title:
            continue
        articles[link] = Article(
            url=link,
            title=title,
            summary=_clean(getattr(entry, "summary", None)),
            source=source,
            published_at=_clean(getattr(entry, "published", None)) or None,
        )

    return list(articles.values())


def fetch_all(feeds: list[tuple[str, str]] | None = None) -> list[Article]:
    """Fetch every feed in ``feeds`` (defaults to :data:`DEFAULT_FEEDS`)."""
    feeds = feeds or DEFAULT_FEEDS
    out: list[Article] = []
    seen: set[str] = set()
    for url, source in feeds:
        for article in fetch_feed(url, source):
            if article.url not in seen:
                seen.add(article.url)
                out.append(article)
    return out
