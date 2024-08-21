from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "smolvault"
    environment: str
    smolvault_bucket: str
    smolvault_db: str
    smolvault_cache: str
    auth_secret_key: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[reportCallIssue, call-arg]
