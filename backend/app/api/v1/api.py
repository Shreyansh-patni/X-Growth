from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, stats, replies, keywords, personas, lists, scheduler, analytics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(replies.router, prefix="/replies", tags=["replies"])
api_router.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(lists.router, prefix="/lists", tags=["lists"])
api_router.include_router(scheduler.router, prefix="/scheduler", tags=["scheduler"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
