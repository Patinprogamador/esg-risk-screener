"""Persistence: insert, de-dupe, unprocessed query, assessment round-trip."""

from __future__ import annotations

from esg_risk_screener import db
from esg_risk_screener.models import (
    Article,
    Assessment,
    Classification,
    RiskScore,
)


def _a(url: str, title: str = "t") -> Article:
    return Article(url=url, title=title, source="s")


def test_insert_counts_only_new_rows(conn):
    first = db.insert_articles(conn, [_a("u1"), _a("u2")])
    second = db.insert_articles(conn, [_a("u2"), _a("u3")])  # u2 already there
    assert first == 2
    assert second == 1


def test_unprocessed_lists_articles_without_assessment(conn):
    db.insert_articles(conn, [_a("u1"), _a("u2")])
    assert {x.url for x in db.unprocessed_articles(conn)} == {"u1", "u2"}


def test_assessment_round_trip(conn):
    db.insert_articles(conn, [_a("u1", "Fraud probe at big bank")])
    article = db.unprocessed_articles(conn)[0]
    assessment = Assessment(
        article=article,
        classification=Classification(
            category="governance", signal="negative", severity=3, rationale="r"
        ),
        risk=RiskScore(score=100, band="high"),
        model="fake:test",
    )
    db.save_assessment(conn, assessment)

    assert db.unprocessed_articles(conn) == []
    stored = db.all_assessments(conn)
    assert len(stored) == 1
    assert stored[0].risk.score == 100
    assert stored[0].article.url == "u1"
