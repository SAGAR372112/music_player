"""
config.py
---------
Centralized application configuration using Pydantic Settings.
All environment variables are read from a .env file or the shell environment.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/music_player"
    DB_ECHO: bool = False  # Set True to print SQL queries (debug mode)

    # --- Auth ---
    # Default credentials — override via .env in production
    AUTH_USERNAME: str = "admin"
    AUTH_PASSWORD: str = "secret"

    # --- Media Storage ---
    MEDIA_DIR: str = "../media"  # Relative to the backend directory

    # --- App ---
    APP_TITLE: str = "Music Player API"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings instance — import this everywhere
settings = Settings()
