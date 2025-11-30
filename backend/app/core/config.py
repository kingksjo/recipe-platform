from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    MONGODB_URL: str
    DATABASE_NAME: str = "recipe_db"

    model_config = SettingsConfigDict(
        env_file=".env.local",   # ← loads your .env.local automatically
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

settings = Settings()  # ← instantiated once, imported everywhere