from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATHS = "../config/.env", "config/.env"


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    TEST_MODE: bool

    model_config = SettingsConfigDict(env_file=ENV_PATHS[0])


try:
    settings = Settings()
except ValidationError:
    Settings.model_config = SettingsConfigDict(env_file=ENV_PATHS[1])
    settings = Settings()

__all__ = ["Settings", "settings"]
