from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./blog.db"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    admin_username: str = "admin"
    admin_password: str = "change-me"
    user_username: str = "user"
    user_password: str = "change-me-user"
    jwt_secret: str = "dev-only-change-this-secret"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
