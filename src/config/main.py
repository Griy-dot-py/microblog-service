from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = "../config/.env"


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    model_config = SettingsConfigDict(env_file=ENV_PATH)
