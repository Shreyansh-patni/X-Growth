import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "X Growth Automation"
    API_V1_STR: str = "/api/v1"
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "changeme")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "x_growth_db")
    DATABASE_URL: str | None = None
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret")
    
    # LLM keys
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")

    # X API keys
    X_API_KEY: str | None = os.getenv("X_API_KEY")
    X_API_SECRET_KEY: str | None = os.getenv("X_API_SECRET_KEY")
    X_ACCESS_TOKEN: str | None = os.getenv("X_ACCESS_TOKEN")
    X_ACCESS_TOKEN_SECRET: str | None = os.getenv("X_ACCESS_TOKEN_SECRET")

    # Browser Automation
    X_USERNAME: str | None = os.getenv("X_USERNAME")
    X_PASSWORD: str | None = os.getenv("X_PASSWORD")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()
