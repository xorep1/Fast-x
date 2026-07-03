"""Application settings loaded from environment / .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    app_name: str = "OTP Auth Service"
    debug: bool = True

    # Database
    database_url: str = "sqlite:///./otp_auth.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    max_session: int = 3

    # JWT
    secret_key: str = "CHANGE_ME_super_secret_key_please_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # OTP
    otp_length: int = 6
    otp_ttl_seconds: int = 120
    otp_resend_cooldown: int = 60
    otp_max_attempts: int = 5
    registration_ttl_seconds: int = 600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
