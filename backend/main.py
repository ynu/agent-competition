"""
智能体大赛网站 - 主应用入口
"""
import os
import sys

# Enable UTF-8 mode on Windows before any other imports
if sys.platform == 'win32':
    os.environ['PYTHONUTF8'] = '1'
    # Also try to set console encoding
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import logging

# Configure logging FIRST before any other imports that might set up loggers
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress SQLAlchemy logging completely to prevent charmap errors with Chinese characters
for logger_name in ['sqlalchemy', 'sqlalchemy.engine', 'sqlalchemy.pool', 'sqlalchemy.dialects', 'sqlalchemy.orm']:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.WARNING)
    logger.propagate = False

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import init_db
from app.api import (
    auth_router,
    users_router,
    teams_router,
    works_router,
    reviews_router,
    contents_router,
    settings_router,
    logs_router,
    permissions_router,
    votes_router,
    agent_center_router,
    media_router,
    webhooks_router,
    messages_router,
    event_channels_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()

    # 确保默认主题存在
    from app.core.database import SessionLocal
    from app.models.setting import CompetitionTheme
    db = SessionLocal()
    try:
        if db.query(CompetitionTheme).count() == 0:
            default_themes = [
                "智能问答", "Agent工作流", "多智能体协作", "智能客服", "数据分析", "内容生成"
            ]
            for i, name in enumerate(default_themes):
                theme = CompetitionTheme(name=name, description="", is_active=True, order=i)
                db.add(theme)
            db.commit()
    finally:
        db.close()

    yield
    # 关闭时清理资源


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能体大赛网站后端API",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/media", StaticFiles(directory="media"), name="media")

# 注册路由
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(teams_router, prefix="/api")
app.include_router(works_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(contents_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(logs_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")
app.include_router(votes_router, prefix="/api")
app.include_router(agent_center_router, prefix="/api")
app.include_router(media_router, prefix="/api")
app.include_router(webhooks_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
app.include_router(event_channels_router, prefix="/api")


@app.get("/")
async def root():
    """根路由"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "智能体大赛网站API"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)