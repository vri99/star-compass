from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ninja_stars_api_key: str

    model_config = SettingsConfigDict(env_file=".env")
