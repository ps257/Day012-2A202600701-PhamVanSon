"""Production config — 12-Factor: tất cả từ environment variables."""
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    debug: bool = False

    # App
    app_name: str = "Production AI Agent"
    app_version: str = "1.0.0"

    # LLM
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Security
    agent_api_key: str = "dev-key-change-me"
    jwt_secret: str = "dev-jwt-secret"
    allowed_origins: str = "*"

    # Rate limiting
    rate_limit_per_minute: int = 20

    # Budget
    daily_budget_usd: float = 5.0

    # Storage
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def get_allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

settings = Settings()

# Validate logic
logger = logging.getLogger(__name__)
if settings.environment == "production":
    if settings.agent_api_key == "dev-key-change-me" or not settings.agent_api_key:
        raise ValueError("AGENT_API_KEY must be set in production!")
if not settings.openai_api_key:
    logger.warning("OPENAI_API_KEY not set — using mock LLM")
