"""Data models for the ESG risk screener.

Every object that moves between pipeline stages is a Pydantic model. Pydantic
validates types at the boundary, so a bad LLM response or a malformed feed item
fails loudly here instead of corrupting the database three steps later.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


def _utcnow_iso() -> str:
    """Current UTC time as an ISO 8601 string."""
    return datetime.now(UTC).isoformat()


class Article(BaseModel):
    """A single news item pulled from an RSS feed."""

    url: str
    title: str
    summary: str = ""
    source: str
    published_at: str | None = None
    fetched_at: str = Field(default_factory=_utcnow_iso)

    @property
    def id(self) -> str:
        """Stable identifier: SHA-256 hex digest of the URL.

        Derived from the URL so the same article always gets the same id, which
        is what lets the database skip duplicates on re-runs.
        """
        return hashlib.sha256(self.url.encode("utf-8")).hexdigest()


class EsgCategory(StrEnum):
    """Which ESG pillar a news item touches."""

    ENVIRONMENTAL = "environmental"
    SOCIAL = "social"
    GOVERNANCE = "governance"
    NONE = "none"


class Signal(StrEnum):
    """Direction of the ESG signal for the company in the news item."""

    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class Classification(BaseModel):
    """The LLM's read of one article. Produced by ``classify`` stage."""

    category: EsgCategory
    signal: Signal
    severity: int = Field(ge=0, le=3, description="0 none, 1 low, 2 medium, 3 high")
    rationale: str = Field(description="One sentence, grounded in the headline/summary.")


class RiskBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskScore(BaseModel):
    """Deterministic score derived from a Classification. No LLM here."""

    score: int = Field(ge=0, le=100)
    band: RiskBand


class Assessment(BaseModel):
    """Everything known about one article after the full pipeline runs.

    This is what gets written to the ``assessments`` table and what the report
    and the API read back.
    """

    article: Article
    classification: Classification
    risk: RiskScore
    model: str
    assessed_at: str = Field(default_factory=_utcnow_iso)
