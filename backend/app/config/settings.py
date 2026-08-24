from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class Settings:
    """Application configuration."""

    project_root: Path = PROJECT_ROOT
    database_path: Path = PROJECT_ROOT / "medical_db"

    app_name: str = "Xpharma Medical Knowledge API"
    app_version: str = "0.1.0"

    fda_timeout_seconds: float = 10.0


def get_settings() -> Settings:
    return Settings()