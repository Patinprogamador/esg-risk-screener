"""Glue: run the stages in order and persist results.

    fetch  ->  store  ->  classify (unprocessed)  ->  score  ->  save

Each function is small and independently callable; ``run`` chains them.
"""

from __future__ import annotations

from dataclasses import dataclass

from esg_risk_screener import db
from esg_risk_screener.classify import classify_article
from esg_risk_screener.config import settings
from esg_risk_screener.fetch import DEFAULT_FEEDS, fetch_all
from esg_risk_screener.llm import LLMProvider, get_llm
from esg_risk_screener.models import Assessment
from esg_risk_screener.score import score_classification


@dataclass
class RunStats:
    fetched: int = 0
    stored: int = 0
    assessed: int = 0


def ingest(conn, feeds: list[tuple[str, str]] | None = None) -> tuple[int, int]:
    """Fetch feeds and store new articles. Returns (fetched, newly_stored)."""
    articles = fetch_all(feeds or DEFAULT_FEEDS)
    stored = db.insert_articles(conn, articles)
    return len(articles), stored


def assess_pending(conn, llm: LLMProvider, limit: int | None = None) -> int:
    """Classify + score every unprocessed article. Returns count assessed."""
    pending = db.unprocessed_articles(conn, limit=limit)
    for article in pending:
        classification = classify_article(article, llm)
        risk = score_classification(classification)
        db.save_assessment(
            conn,
            Assessment(
                article=article,
                classification=classification,
                risk=risk,
                model=f"{settings.effective_provider}:{settings.llm_model}",
            ),
        )
    return len(pending)


def run(
    conn,
    llm: LLMProvider | None = None,
    feeds: list[tuple[str, str]] | None = None,
    limit: int | None = None,
) -> RunStats:
    """Full pipeline against an already-open connection."""
    llm = llm or get_llm()
    db.init_db(conn)
    fetched, stored = ingest(conn, feeds)
    assessed = assess_pending(conn, llm, limit=limit)
    return RunStats(fetched=fetched, stored=stored, assessed=assessed)
