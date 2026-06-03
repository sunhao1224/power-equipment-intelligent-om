"""Application settings for the Hermes Agent demo service."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Runtime configuration."""

    app_name: str = "Hermes Agent 电力设备智能运维系统"
    app_version: str = "2.0.0-hermes"
    debug: bool = True
    api_prefix: str = "/api/v1"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    class Config:
        env_file = ".env"
        env_prefix = "POWER_OM_"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
