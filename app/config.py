"""Application configuration classes."""

import os
from typing import ClassVar


class Config:
    """Base configuration."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS: ClassVar[bool] = False


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
