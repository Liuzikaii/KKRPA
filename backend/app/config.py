"""
KKRPA Application Configuration (Desktop Mode)
"""
import os
import sys
from pydantic_settings import BaseSettings
from typing import Optional


def get_data_dir() -> str:
    """Get persistent data directory for the app."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


class Settings(BaseSettings):
    # App
    APP_NAME: str = "KKRPA"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Database (SQLite - local file)
    DATABASE_URL: str = ""  # Will be set dynamically

    # JWT
    JWT_SECRET_KEY: str = "kkrpa-desktop-secret-key-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days for desktop

    # Python Sandbox
    SANDBOX_TIMEOUT_SECONDS: int = 30
    SANDBOX_MAX_MEMORY_MB: int = 256

    # Edition Limits
    COMMUNITY_MAX_WORKFLOWS: int = 5

    # License
    LICENSE_KEY: str = ""
    EDITION: str = "community"  # Set after activation

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 18090

    # Snowflake
    SNOWFLAKE_DATACENTER_ID: int = 1
    SNOWFLAKE_WORKER_ID: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            data_dir = get_data_dir()
            db_path = os.path.join(data_dir, "kkrpa.db")
            self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"


settings = Settings()
