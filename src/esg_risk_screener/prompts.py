"""Prompt loader.

Prompts live as plain Markdown files under ``prompts/`` so they can be versioned,
diffed, and evaluated independently of the code that uses them. Bump the version
in the filename when you change a prompt; keep the old file so eval runs stay
reproducible.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"

CLASSIFY_PROMPT_VERSION = "v1"
REPORT_PROMPT_VERSION = "v1"


@cache
def load(name: str) -> str:
    """Read ``prompts/<name>.md`` and return its text."""
    path = _PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


def classify_system() -> str:
    return load(f"classify_{CLASSIFY_PROMPT_VERSION}")


def report_system() -> str:
    return load(f"report_{REPORT_PROMPT_VERSION}")
