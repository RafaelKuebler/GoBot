import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

from gobot.persistence.persistence_factory import DBs

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
        validate_default=True,
    )

    TOKEN: str

    DB_TYPE: DBs = DBs.DYNAMODB

    DATABASE_URL: str | None = None
    USE_DB: bool = True

    USE_LOCAL_DB: bool = False
    DYNAMODB_ENDPOINT: str | None = None


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        logger.info("Loaded settings from env vars and .env")
        _settings = Settings()  # type: ignore
    return _settings
