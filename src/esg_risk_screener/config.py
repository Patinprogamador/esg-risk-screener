"""Central configuration.

All tunables live here and are read from environment variables (or a local
``.env`` file). Nothing else in the codebase should call ``os.environ`` directly
- import ``settings`` from this module instead.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings. Values come from the environment / ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- LLM ---
    # "gemini" uses the real Google API and needs GEMINI_API_KEY.
    # "fake" is a deterministic offline stub used by the tests and by anyone
    # who wants to run the pipeline without a key.
    llm_provider: str = "gemini"
    llm_model: str = "gemini-2.0-flash"
    gemini_api_key: str | None = None

    # --- storage ---
    db_path: Path = Path("data/articles.db")

    # --- scoring thresholds (score 0-100 -> band) ---
    band_medium_at: int = 34
    band_high_at: int = 67

    @property
    def effective_provider(self) -> str:
        """Fall back to the offline stub when gemini is asked for but no key is set."""
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            return "fake"
        return self.llm_provider


settings = Settings()
