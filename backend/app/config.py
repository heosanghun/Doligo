"""Application configuration."""
from pathlib import Path

from pydantic_settings import BaseSettings

# .env 경로: backend/.env (스크립트 기준)
_BASE_DIR = Path(__file__).resolve().parent.parent
_ENV_FILE = _BASE_DIR / ".env"


class Settings(BaseSettings):
    """App settings from environment variables."""

    # Gemini API (gemini-2.5-pro: 최신 추론 모델, gemini-3.1-pro-preview 사용 시 해당 모델명으로 변경)
    google_api_key: str = ""
    gemini_model_text: str = "gemini-2.5-pro"
    gemini_model_image: str = "gemini-2.5-pro"

    # App
    feedback_min_rounds: int = 5
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    max_file_size_mb: int = 10
    job_timeout_minutes: int = 15
    file_retention_hours: int = 24
    cors_origins: str = "http://localhost:5173"
    log_level: str = "info"
    gemini_retry_count: int = 3

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = str(_ENV_FILE) if _ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
