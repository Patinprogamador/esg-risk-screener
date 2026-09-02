"""Article identity and Classification validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from esg_risk_screener.models import Article, Classification


def _article(url: str = "https://example.com/a") -> Article:
    return Article(url=url, title="t", source="s")


def test_article_id_is_stable_for_same_url():
    assert _article().id == _article().id


def test_article_id_differs_for_different_url():
    assert _article("https://example.com/a").id != _article("https://example.com/b").id


def test_article_defaults():
    a = _article()
    assert a.summary == ""
    assert a.published_at is None
    assert a.fetched_at  # populated by default_factory


def test_classification_rejects_out_of_range_severity():
    with pytest.raises(ValidationError):
        Classification(category="social", signal="negative", severity=9, rationale="x")


def test_classification_rejects_unknown_category():
    with pytest.raises(ValidationError):
        Classification(category="political", signal="neutral", severity=0, rationale="x")
