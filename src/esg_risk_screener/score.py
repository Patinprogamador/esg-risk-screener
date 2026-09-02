"""Score stage: :class:`Classification` -> :class:`RiskScore`.

Deliberately rule-based, not an LLM call. Credit committees need a score they
can explain and reproduce, and a pure function is trivial to unit-test.

Model
-----
score = base(signal) + severity_weight * severity, clamped to 0..100.

* positive / none    -> 0
* neutral            -> 10 base
* negative           -> 25 base, +25 per severity point
"""

from __future__ import annotations

from esg_risk_screener.config import settings
from esg_risk_screener.models import Classification, RiskBand, RiskScore, Signal

_BASE = {Signal.POSITIVE: 0, Signal.NEUTRAL: 10, Signal.NEGATIVE: 25}
_SEVERITY_WEIGHT = 25


def _band(score: int) -> RiskBand:
    if score >= settings.band_high_at:
        return RiskBand.HIGH
    if score >= settings.band_medium_at:
        return RiskBand.MEDIUM
    return RiskBand.LOW


def score_classification(c: Classification) -> RiskScore:
    base = _BASE[Signal(c.signal)]
    raw = base + (_SEVERITY_WEIGHT * c.severity if c.signal == Signal.NEGATIVE else 0)
    score = max(0, min(100, raw))
    return RiskScore(score=score, band=_band(score))
