from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str 
    OPENAI_API_KEY: str  # Required for LLM and embeddings (LangChain + OpenAI)
    UPLOAD_DIR: str = "storage"  # Base dir for uploaded files (relative to backend root)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
