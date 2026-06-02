"""配置管理"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    app_name: str = "电力设备智能运维分析与决策支持系统"
    app_version: str = "1.0.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    # CORS 配置
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # WebSocket 配置
    ws_heartbeat_interval: int = 30
    
    # Mock 数据配置
    mock_data_dir: str = "app/mock_data"
    
    class Config:
        env_file = ".env"
        env_prefix = "POWER_OM_"


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
