"""Report stage: a list of assessments -> a short Markdown briefing.

The aggregate numbers are computed in Python (cheap, exact); the LLM only turns
the already-scored data into prose.
"""

from __future__ import annotations

import json
from collections import Counter

from esg_risk_screener import prompts
from esg_risk_screener.llm import LLMProvider
from esg_risk_screener.models import Assessment, RiskBand


def summarise_counts(assessments: list[Assessment]) -> dict:
    """Plain-Python aggregates - also handy for the API and the tests."""
    return {
        "total": len(assessments),
        "by_band": dict(Counter(a.risk.band for a in assessments)),
        "by_category": dict(Counter(a.classification.category for a in assessments)),
        "high_risk": [
            {"title": a.article.title, "source": a.article.source, "score": a.risk.score}
            for a in assessments
            if a.risk.band == RiskBand.HIGH
        ],
    }


def _payload(assessments: list[Assessment]) -> str:
    items = [
        {
            "title": a.article.title,
            "source": a.article.source,
            "category": a.classification.category,
            "signal": a.classification.signal,
            "severity": a.classification.severity,
            "risk_score": a.risk.score,
            "risk_band": a.risk.band,
        }
        for a in assessments
    ]
    return json.dumps(items, ensure_ascii=False, indent=2)


def build_report(assessments: list[Assessment], llm: LLMProvider) -> str:
    """Return a Markdown briefing for ``assessments``."""
    if not assessments:
        return "## Summary\n\nNo assessed articles yet. Run `ingest` then `classify`."
    return llm.complete_text(
        system=prompts.report_system(),
        user=_payload(assessments),
    )
