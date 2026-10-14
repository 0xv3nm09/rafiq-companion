"""Central settings — everything tunable lives here, nothing hard-coded elsewhere."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- data ---
    data_dir: Path = ROOT / "data"
    pack_dir: Path = ROOT / "data" / "pack"          # drop the official pack here
    synthetic_dir: Path = ROOT / "data" / "synthetic"  # generated fallback
    runtime_dir: Path = ROOT / "data" / "runtime"      # audit log, consent, handoffs, sweep state

    # --- demo clock ---
    sim_day: int = 5

    # --- retrieval / generation thresholds ---
    min_score: float = 0.5
    min_confidence: float = 0.6
    top_k: int = 4

    # --- proactive engine ---
    escalate_after: int = 2        # days overdue before a named owner is pinged
    sweep_interval_hours: float = 6.0
    pulse_weight: float = 0.1      # consent-gated tie-breaker only

    # --- llm (optional; extractive fallback when unset) ---
    openrouter_api_key: str = ""
    openrouter_model: str = "z-ai/glm-5.3-flash"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_timeout_s: float = 8.0

    # --- i18n ---
    default_lang: str = "en"


@lru_cache
def get_settings() -> Settings:
    return Settings()
