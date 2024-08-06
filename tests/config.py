from pydantic_settings import BaseSettings, SettingsConfigDict

TEST_ENV_PATH = "../config/.env.test"


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    model_config = SettingsConfigDict(env_file=TEST_ENV_PATH)

test_settings = Settings()
