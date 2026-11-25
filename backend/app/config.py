from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SalesPilot AI"
    database_url: str = "sqlite:///./salespilot.db"
    frontend_origin: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    business_timezone: str = "Asia/Kolkata"
    max_upload_mb: int = 5
    rag_top_k: int = 4
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
