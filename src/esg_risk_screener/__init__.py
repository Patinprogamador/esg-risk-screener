"""ESG risk screener package.

``main`` is the console-script entry point declared in pyproject.toml; the real
implementation lives in :mod:`esg_risk_screener.cli`.
"""

from __future__ import annotations

from esg_risk_screener.cli import main

__all__ = ["main"]
