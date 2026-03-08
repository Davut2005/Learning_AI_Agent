from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    

    DATABASE_URL: str
    OPENAI_API_KEY: str | None = None  # Optional until AI is implemented

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
