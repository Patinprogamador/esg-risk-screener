"""Feed parsing and in-feed de-duplication."""

from __future__ import annotations

from esg_risk_screener.fetch import fetch_feed


def test_fetch_feed_parses_items(sample_feed_path):
    articles = fetch_feed(sample_feed_path, "Fixture")
    # 6 items in the file, 2 share a URL -> 5 unique
    assert len(articles) == 5
    assert all(a.source == "Fixture" for a in articles)
    assert all(a.url.startswith("https://example.com/") for a in articles)


def test_fetch_feed_keeps_title_and_summary(sample_feed_path):
    by_url = {a.url: a for a in fetch_feed(sample_feed_path, "Fixture")}
    fraud = by_url["https://example.com/news/fraud-probe"]
    assert "fraud probe" in fraud.title.lower()
    assert "sec" in fraud.summary.lower()


def test_fetch_feed_bad_url_returns_empty():
    assert fetch_feed("file:///no/such/feed.xml", "Nope") == []
