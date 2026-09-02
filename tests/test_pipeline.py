"""End-to-end: local fixture feed -> DB -> classify -> score -> report."""

from __future__ import annotations

from esg_risk_screener import db
from esg_risk_screener.pipeline import run
from esg_risk_screener.report import build_report, summarise_counts


def test_run_full_pipeline_offline(conn, fake_llm, sample_feed_path):
    feeds = [(sample_feed_path, "Fixture")]
    stats = run(conn, llm=fake_llm, feeds=feeds)

    assert stats.fetched == 5
    assert stats.stored == 5
    assert stats.assessed == 5

    assessments = db.all_assessments(conn)
    assert len(assessments) == 5
    # sorted by risk score descending
    scores = [a.risk.score for a in assessments]
    assert scores == sorted(scores, reverse=True)

    # the fraud-probe headline should land in the high band
    fraud = next(a for a in assessments if "fraud" in a.article.title.lower())
    assert fraud.risk.band == "high"


def test_run_is_idempotent(conn, fake_llm, sample_feed_path):
    feeds = [(sample_feed_path, "Fixture")]
    run(conn, llm=fake_llm, feeds=feeds)
    second = run(conn, llm=fake_llm, feeds=feeds)
    assert second.stored == 0
    assert second.assessed == 0


def test_summarise_and_report(conn, fake_llm, sample_feed_path):
    run(conn, llm=fake_llm, feeds=[(sample_feed_path, "Fixture")])
    counts = summarise_counts(db.all_assessments(conn))
    assert counts["total"] == 5

    report = build_report(db.all_assessments(conn), fake_llm)
    assert isinstance(report, str) and len(report) > 0
