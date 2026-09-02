"""Classify stage against the offline FakeProvider."""

from __future__ import annotations

from esg_risk_screener.classify import classify_article
from esg_risk_screener.models import Article, Classification


def _article(title: str, summary: str = "") -> Article:
    return Article(url="https://example.com/x", title=title, summary=summary, source="s")


def test_classify_returns_validated_model(fake_llm):
    result = classify_article(_article("Company update"), fake_llm)
    assert isinstance(result, Classification)


def test_classify_flags_negative_environmental_news(fake_llm):
    result = classify_article(
        _article("Oil firm fined over pipeline spill and pollution"), fake_llm
    )
    assert result.category == "environmental"
    assert result.signal == "negative"
    assert result.severity >= 1


def test_classify_neutral_for_non_esg_news(fake_llm):
    result = classify_article(_article("Central bank holds interest rates"), fake_llm)
    assert result.signal == "neutral"
