"""API smoke tests (no network - /run is covered in test_pipeline)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from esg_risk_screener import db
from esg_risk_screener.api import app
from esg_risk_screener.models import Article, Assessment, Classification, RiskScore

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_stats_empty():
    r = client.get("/stats")
    assert r.status_code == 200
    assert r.json()["total"] == 0


def test_assessments_after_manual_insert():
    conn = db.get_connection()
    db.init_db(conn)
    db.insert_articles(conn, [Article(url="u1", title="Fraud probe", source="s")])
    article = db.unprocessed_articles(conn)[0]
    db.save_assessment(
        conn,
        Assessment(
            article=article,
            classification=Classification(
                category="governance", signal="negative", severity=3, rationale="r"
            ),
            risk=RiskScore(score=100, band="high"),
            model="fake:test",
        ),
    )
    conn.close()

    r = client.get("/assessments")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["risk"]["band"] == "high"
