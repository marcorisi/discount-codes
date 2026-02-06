"""Application configuration classes."""

import os
from typing import ClassVar


def _parse_reminder_days(env_value: str | None, default: str) -> list[int]:
    """Parse comma-separated reminder days from environment variable."""
    value = env_value or default
    return sorted([int(d.strip()) for d in value.split(",")], reverse=True)


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = False
    SLACK_NOTIFIER_CMD: str | None = os.environ.get("SLACK_NOTIFIER_CMD")
    # Legacy single-value config (kept for backwards compatibility)
    REMINDER_DAYS_BEFORE: int = int(os.environ.get("REMINDER_DAYS_BEFORE", "7"))
    # Multiple reminder thresholds (comma-separated, e.g., "7,3")
    REMINDER_DAYS_LIST: list[int] = _parse_reminder_days(
        os.environ.get("REMINDER_DAYS_LIST"), "7,3"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: ClassVar[bool] = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///discount_codes.db"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING: ClassVar[bool] = True
    SQLALCHEMY_DATABASE_URI: ClassVar[str] = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: ClassVar[bool] = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get("DATABASE_URL", "sqlite:///discount_codes.db")


config: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
