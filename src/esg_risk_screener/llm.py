"""Provider-abstracted LLM layer.

The rest of the codebase talks to ``LLMProvider`` and never imports a vendor SDK
directly. Swapping Gemini for another model, or running fully offline in tests,
is a one-line change in configuration.
"""

from __future__ import annotations

import json
import re
import time
from typing import Protocol

from esg_risk_screener.config import settings


class LLMProvider(Protocol):
    """The contract every provider implements."""

    name: str

    def complete_text(self, system: str, user: str) -> str: ...

    def complete_json(self, system: str, user: str) -> dict: ...


# --------------------------------------------------------------------------- #
# Real provider: Google Gemini
# --------------------------------------------------------------------------- #
class GeminiProvider:
    """Calls the Google Gemini API. Needs ``GEMINI_API_KEY``."""

    name = "gemini"

    def __init__(self, api_key: str, model: str) -> None:
        # Imported lazily so the package still imports with no SDK / no key.
        from google import genai

        self._client = genai.Client(api_key=api_key)
        self._model = model

    # Transient API failures (503 high demand, 429 rate limit) are retried with a
    # widening back-off; everything else propagates immediately.
    _MAX_ATTEMPTS = 5
    _BACKOFF_SECONDS = 3

    def _generate(self, system: str, user: str, *, as_json: bool) -> str:
        from google.genai import errors, types

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=0.0,
            response_mime_type="application/json" if as_json else "text/plain",
        )
        last_exc: Exception | None = None
        for attempt in range(self._MAX_ATTEMPTS):
            try:
                resp = self._client.models.generate_content(
                    model=self._model, contents=user, config=config
                )
                return (resp.text or "").strip()
            except errors.ServerError as exc:  # 5xx - transient, back off and retry
                last_exc = exc
            except errors.ClientError as exc:  # retry only on 429 rate-limit
                if exc.code != 429:
                    raise
                last_exc = exc
            time.sleep(self._BACKOFF_SECONDS * (attempt + 1))
        raise RuntimeError(
            f"Gemini still unavailable after {self._MAX_ATTEMPTS} attempts: {last_exc}"
        )

    def complete_text(self, system: str, user: str) -> str:
        return self._generate(system, user, as_json=False)

    def complete_json(self, system: str, user: str) -> dict:
        raw = self._generate(system, user, as_json=True)
        return json.loads(raw)


# --------------------------------------------------------------------------- #
# Offline provider: deterministic stub for tests and keyless runs
# --------------------------------------------------------------------------- #
_NEGATIVE = {
    "fraud",
    "lawsuit",
    "sued",
    "spill",
    "pollution",
    "polluting",
    "strike",
    "layoff",
    "layoffs",
    "bribery",
    "bribe",
    "corruption",
    "fine",
    "fined",
    "probe",
    "boycott",
    "greenwashing",
    "harassment",
    "recall",
    "leak",
    "contamination",
    "explosion",
    "deforestation",
    "scandal",
    "misconduct",
}
_POSITIVE = {
    "renewable",
    "solar",
    "wind",
    "pledge",
    "pledges",
    "award",
    "awarded",
    "upgrade",
    "upgraded",
    "diversity",
    "transparency",
    "net-zero",
    "recycling",
    "sustainable",
    "sustainability",
    "donation",
    "philanthropy",
}
_ENV = {
    "emission",
    "emissions",
    "carbon",
    "climate",
    "pollution",
    "spill",
    "renewable",
    "solar",
    "wind",
    "deforestation",
    "water",
    "waste",
}
_GOV = {
    "board",
    "fraud",
    "bribery",
    "corruption",
    "audit",
    "probe",
    "sec",
    "lawsuit",
    "regulator",
    "regulatory",
    "disclosure",
    "governance",
}
_SOC = {
    "workers",
    "worker",
    "strike",
    "layoff",
    "layoffs",
    "harassment",
    "diversity",
    "safety",
    "union",
    "community",
    "labour",
    "labor",
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9-]+", text.lower()))


class FakeProvider:
    """Keyword heuristic. Not accurate - just deterministic and dependency-free."""

    name = "fake"

    def complete_json(self, system: str, user: str) -> dict:
        w = _words(user)
        neg, pos = w & _NEGATIVE, w & _POSITIVE
        if neg:
            signal, severity = "negative", min(3, 1 + len(neg))
        elif pos:
            signal, severity = "positive", 1
        else:
            signal, severity = "neutral", 0

        if w & _ENV:
            category = "environmental"
        elif w & _GOV:
            category = "governance"
        elif w & _SOC:
            category = "social"
        else:
            category = "none"
            signal, severity = "neutral", 0

        return {
            "category": category,
            "signal": signal,
            "severity": severity,
            "rationale": f"Heuristic match on {sorted(neg | pos) or 'no risk keywords'}.",
        }

    def complete_text(self, system: str, user: str) -> str:
        return "## ESG risk summary (offline stub)\n\nNo LLM configured; this is placeholder text."


# --------------------------------------------------------------------------- #
# Factory
# --------------------------------------------------------------------------- #
def get_llm() -> LLMProvider:
    """Return the provider selected by configuration."""
    provider = settings.effective_provider
    if provider == "gemini":
        return GeminiProvider(settings.gemini_api_key, settings.llm_model)  # type: ignore[arg-type]
    if provider == "fake":
        return FakeProvider()
    raise ValueError(f"Unknown LLM provider: {provider!r}")
