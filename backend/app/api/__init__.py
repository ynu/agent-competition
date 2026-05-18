"""API routes package"""
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.teams import router as teams_router
from app.api.works import router as works_router
from app.api.reviews import router as reviews_router
from app.api.contents import router as contents_router
from app.api.settings import router as settings_router
from app.api.logs import router as logs_router
from app.api.permissions import router as permissions_router
from app.api.votes import router as votes_router
from app.api.agent_center import router as agent_center_router
from app.api.media import router as media_router
from app.api.webhooks import router as webhooks_router
from app.api.messages import router as messages_router

__all__ = [
    "auth_router",
    "users_router",
    "teams_router",
    "works_router",
    "reviews_router",
    "contents_router",
    "settings_router",
    "logs_router",
    "permissions_router",
    "votes_router",
    "agent_center_router",
    "media_router",
    "webhooks_router",
    "messages_router"
]