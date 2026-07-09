"""Application settings loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typisierte Konfiguration — Werte kommen aus .env oder Umgebung."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- App ---
    app_name: str = "alpine-career"
    app_env: str = "development"
    app_debug: bool = True

    # --- Database ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "alpine_career"
    postgres_user: str = "alpine_career"
    postgres_password: str = Field(default="")

    @property
    def database_url(self) -> str:
        """Async PostgreSQL connection string."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL URL fuer Alembic."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # --- Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # --- Telegram ---
    telegram_bot_token: str = Field(default="")
    telegram_allowed_usernames: str = "Dorender"

    @property
    def allowed_usernames_list(self) -> list[str]:
        """Komma-getrennte Usernames als Liste."""
        return [u.strip() for u in self.telegram_allowed_usernames.split(",") if u.strip()]

    # --- Claude API ---
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 4096

    # --- Gmail ---
    gmail_credentials_file: str = ""

    # --- Logging ---
    log_level: str = "INFO"
    log_format: str = "json"


# Singleton — einmal laden, ueberall verwenden
settings = Settings()
