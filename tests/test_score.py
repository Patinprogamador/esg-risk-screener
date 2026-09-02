"""The deterministic scoring rules - the heart of the 'explainable' claim."""

from __future__ import annotations

import pytest

from esg_risk_screener.models import Classification
from esg_risk_screener.score import score_classification


def _c(signal: str, severity: int, category: str = "governance") -> Classification:
    return Classification(category=category, signal=signal, severity=severity, rationale="r")


@pytest.mark.parametrize(
    ("signal", "severity", "expected_score", "expected_band"),
    [
        ("positive", 0, 0, "low"),
        ("neutral", 0, 10, "low"),
        ("negative", 0, 25, "low"),
        ("negative", 1, 50, "medium"),
        ("negative", 2, 75, "high"),
        ("negative", 3, 100, "high"),
    ],
)
def test_score_table(signal, severity, expected_score, expected_band):
    result = score_classification(_c(signal, severity))
    assert result.score == expected_score
    assert result.band == expected_band


def test_score_never_exceeds_100():
    assert score_classification(_c("negative", 3)).score == 100


def test_positive_news_ignores_severity():
    assert score_classification(_c("positive", 3)).score == 0
