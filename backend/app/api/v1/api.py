from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, stats, replies, keywords

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(replies.router, prefix="/replies", tags=["replies"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
