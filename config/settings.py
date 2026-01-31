"""
config/settings.py
─────────────────
Single source of truth for all runtime configuration.
Loaded once at import time from environment variables.
Every other module imports from here — never reads .env directly.
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

# Load .env file into environment
load_dotenv()


class LLMSettings(BaseModel):
    """Settings for the Groq LLM connection."""
    api_key: str = os.getenv("GROQ_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "llama3-8b-instruct")

    @field_validator("api_key")
    @classmethod
    def api_key_must_exist(cls, v):
        # Don't crash at import time — validate only when LLM is actually called
        return v


class SystemSettings(BaseModel):
    """Operational timing and behavior settings."""
    poll_interval_seconds: int = int(os.getenv("POLL_INTERVAL_SECONDS", "10"))
    decision_timeout_seconds: int = int(os.getenv("DECISION_TIMEOUT_SECONDS", "5"))
    max_idle_minutes: int = int(os.getenv("MAX_IDLE_MINUTES", "30"))


class MetricTargets(BaseModel):
    """Target KPIs the system optimizes toward."""
    target_utilization_rate: float = float(os.getenv("TARGET_UTILIZATION_RATE", "0.85"))
    target_empty_return_rate: float = float(os.getenv("TARGET_EMPTY_RETURN_RATE", "0.15"))
    min_profit_margin: float = float(os.getenv("MIN_PROFIT_MARGIN", "0.12"))


# ─── Singleton instances (import these everywhere) ───
llm_settings = LLMSettings()
system_settings = SystemSettings()
metric_targets = MetricTargets()