"""SQLite persistence.

Two tables:

* ``articles``     - raw news items, one row per unique URL.
* ``assessments``  - one row per article that has been classified and scored.

An article with no matching ``assessments`` row is "unprocessed" and is what
the classify stage picks up.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from esg_risk_screener.config import settings
from esg_risk_screener.models import (
    Article,
    Assessment,
    Classification,
    RiskScore,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id            TEXT PRIMARY KEY,
    url           TEXT NOT NULL UNIQUE,
    title         TEXT NOT NULL,
    summary       TEXT NOT NULL DEFAULT '',
    source        TEXT NOT NULL,
    published_at  TEXT,
    fetched_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
    article_id    TEXT PRIMARY KEY REFERENCES articles(id),
    category      TEXT NOT NULL,
    signal        TEXT NOT NULL,
    severity      INTEGER NOT NULL,
    rationale     TEXT NOT NULL,
    risk_score    INTEGER NOT NULL,
    risk_band     TEXT NOT NULL,
    model         TEXT NOT NULL,
    assessed_at   TEXT NOT NULL
);
"""


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open a connection, creating the parent folder and row factory."""
    db_path = db_path or settings.db_path
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables if they do not exist yet."""
    conn.executescript(_SCHEMA)
    conn.commit()


def insert_articles(conn: sqlite3.Connection, articles: list[Article]) -> int:
    """Insert articles, skipping URLs already present. Return rows inserted."""
    rows = [
        (a.id, a.url, a.title, a.summary, a.source, a.published_at, a.fetched_at) for a in articles
    ]
    before = conn.total_changes
    conn.executemany(
        "INSERT OR IGNORE INTO articles "
        "(id, url, title, summary, source, published_at, fetched_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return conn.total_changes - before


def _row_to_article(row: sqlite3.Row) -> Article:
    return Article(
        url=row["url"],
        title=row["title"],
        summary=row["summary"],
        source=row["source"],
        published_at=row["published_at"],
        fetched_at=row["fetched_at"],
    )


def unprocessed_articles(conn: sqlite3.Connection, limit: int | None = None) -> list[Article]:
    """Articles with no assessment row yet."""
    sql = (
        "SELECT a.* FROM articles a "
        "LEFT JOIN assessments s ON s.article_id = a.id "
        "WHERE s.article_id IS NULL ORDER BY a.fetched_at"
    )
    if limit is not None:
        sql += f" LIMIT {int(limit)}"
    return [_row_to_article(r) for r in conn.execute(sql)]


def save_assessment(conn: sqlite3.Connection, assessment: Assessment) -> None:
    """Write (or replace) the assessment for one article."""
    a, c, r = assessment.article, assessment.classification, assessment.risk
    conn.execute(
        "INSERT OR REPLACE INTO assessments "
        "(article_id, category, signal, severity, rationale, risk_score, "
        " risk_band, model, assessed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            a.id,
            c.category,
            c.signal,
            c.severity,
            c.rationale,
            r.score,
            r.band,
            assessment.model,
            assessment.assessed_at,
        ),
    )
    conn.commit()


def all_assessments(conn: sqlite3.Connection) -> list[Assessment]:
    """Every assessed article, highest risk first."""
    sql = (
        "SELECT a.*, s.category, s.signal, s.severity, s.rationale, "
        "       s.risk_score, s.risk_band, s.model, s.assessed_at "
        "FROM assessments s JOIN articles a ON a.id = s.article_id "
        "ORDER BY s.risk_score DESC"
    )
    out: list[Assessment] = []
    for row in conn.execute(sql):
        out.append(
            Assessment(
                article=_row_to_article(row),
                classification=Classification(
                    category=row["category"],
                    signal=row["signal"],
                    severity=row["severity"],
                    rationale=row["rationale"],
                ),
                risk=RiskScore(score=row["risk_score"], band=row["risk_band"]),
                model=row["model"],
                assessed_at=row["assessed_at"],
            )
        )
    return out
