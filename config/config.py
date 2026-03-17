"""
Configuration module for Finance Tracker Bot.
Loads settings from environment variables / .env file.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./finance_bot.db"
    )
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration values."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set in .env file!")


config = Config()
