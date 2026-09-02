"""Shared fixtures. Every test runs offline against a temp database."""

from __future__ import annotations

from pathlib import Path

import pytest

from esg_risk_screener import db
from esg_risk_screener.config import settings
from esg_risk_screener.llm import FakeProvider

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Point the DB at a temp file and force the offline LLM for every test."""
    monkeypatch.setattr(settings, "db_path", tmp_path / "test.db")
    monkeypatch.setattr(settings, "llm_provider", "fake")
    monkeypatch.setattr(settings, "gemini_api_key", None)


@pytest.fixture
def conn():
    c = db.get_connection()
    db.init_db(c)
    yield c
    c.close()


@pytest.fixture
def fake_llm():
    return FakeProvider()


@pytest.fixture
def sample_feed_path() -> str:
    return str(FIXTURES / "sample_feed.xml")
