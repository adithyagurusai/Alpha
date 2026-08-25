from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, slots=True)
class Settings:
    """Application configuration."""

    project_root: Path = PROJECT_ROOT
    database_path: Path = PROJECT_ROOT / "data" / "xpharma_graph"
    app_name: str = "Xpharma Medical Knowledge API"
    app_version: str = "0.1.0"

    fda_timeout_seconds: float = 10.0

    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.1-flash-lite",
    )


def get_settings() -> Settings:
    return Settings()