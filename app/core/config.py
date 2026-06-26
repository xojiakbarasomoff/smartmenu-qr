from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    BOT_TOKEN: str
    BOT_USERNAME: str = "@my_smart_menu_bot"
    NOTIFY_CHAT_ID: str = ""

    # FastAPI
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_TITLE: str = "SmartMenu QR"
    APP_VERSION: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
