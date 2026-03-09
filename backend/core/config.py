from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/learning_ai_tracker"
    OPENAI_API_KEY: str | None = None  # Optional until AI is implemented
    UPLOAD_DIR: str = "storage"  # Base dir for uploaded files (relative to backend root)

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
