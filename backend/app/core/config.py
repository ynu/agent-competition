"""
智能体大赛网站 - 核心配置模块
"""
import os
from typing import Any, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "智能体大赛"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./agent_competition.db",
        description="数据库连接地址，支持 sqlite:///、mysql+pymysql://、postgresql://"
    )

    # JWT 配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="JWT 密钥，生产环境请修改"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # 统一身份认证配置
    UNIFIED_AUTH_ENABLED: bool = True
    UNIFIED_AUTH_URL: str = "https://ids.ynu.edu.cn/authserver"
    UNIFIED_AUTH_CLIENT_ID: str = "agent-competition"
    UNIFIED_AUTH_CLIENT_SECRET: str = ""
    UNIFIED_AUTH_CAS_URL: str = "https://ids.ynu.edu.cn/authserver/oauth2.0/authorize"
    UNIFIED_AUTH_TOKEN_URL: str = "https://ids.ynu.edu.cn/authserver/oauth2.0/token"
    UNIFIED_AUTH_USERINFO_URL: str = "https://ids.ynu.edu.cn/authserver/oauth2.0/userAttributes"

    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_PDF_SIZE: int = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = ["pdf", "mp4", "jpg", "jpeg", "png", "gif"]

    # 媒体文件管理配置
    MEDIA_DIR: str = "./media"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    MEDIA_ALLOWED_EXTENSIONS: list = ["pdf", "jpg", "jpeg", "png", "gif", "svg", "webp", "mp4", "webm", "mp3", "wav", "doc", "docx", "zip"]

    # 静态页面配置
    STATIC_DIR: str = "./static"
    STATIC_TEMPLATE_DIR: str = "./templates"

    # 应用基础URL
    BASE_URL: str = "http://localhost:5173"

    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:5173"]

    # 火山引擎智能体中心配置
    VOLCENGINE_HOST: str = "10.10.160.222:30040"
    VOLCENGINE_AK: str = ""
    VOLCENGINE_SK: str = ""
    VOLCENGINE_REGION: str = "cn-north-1"
    VOLCENGINE_SERVICE: str = "app"
    VOLCENGINE_ACCOUNT_ID: str = "1000000000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()


def get_database_url() -> str:
    """获取数据库连接地址"""
    return settings.DATABASE_URL


def get_db_type() -> str:
    """获取数据库类型"""
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return "sqlite"
    elif url.startswith("mysql"):
        return "mysql"
    elif url.startswith("postgresql"):
        return "postgresql"
    return "sqlite"