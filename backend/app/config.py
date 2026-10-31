"""应用配置：所有参数均可通过环境变量覆盖（见 docker-compose.yml）。"""
import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "工单报修管理系统"

    # 开发环境默认 SQLite，部署时通过环境变量切换为 MySQL：
    # mysql+pymysql://ticket:ticket123456@db:3306/ticket_system?charset=utf8mb4
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'ticket.db'}"

    # JWT
    JWT_SECRET: str = "dev-insecure-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # 文件上传
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_MB: int = 5
    ALLOWED_IMAGE_EXT: tuple = (".jpg", ".jpeg", ".png", ".gif", ".webp")

    # 初始化的默认管理员账号（仅当库中无用户时创建）
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin123"


settings = Settings()

# 确保运行目录存在
os.makedirs(BASE_DIR / "data", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
