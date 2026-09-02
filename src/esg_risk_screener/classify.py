"""Classify stage: one article -> one :class:`Classification` via the LLM."""

from __future__ import annotations

from esg_risk_screener import prompts
from esg_risk_screener.llm import LLMProvider
from esg_risk_screener.models import Article, Classification


def _render_article(article: Article) -> str:
    summary = article.summary[:600]
    return f"TITLE: {article.title}\nSUMMARY: {summary}"


def classify_article(article: Article, llm: LLMProvider) -> Classification:
    """Ask the LLM to classify ``article``.

    The raw dict from the model is validated into a :class:`Classification`, so
    a missing field or an out-of-range severity raises here rather than later.
    """
    raw = llm.complete_json(
        system=prompts.classify_system(),
        user=_render_article(article),
    )
    return Classification.model_validate(raw)
