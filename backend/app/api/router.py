from fastapi import APIRouter

from app.api import getlevels, verifycode
from app.api.levels import level_sublevel
from app.api.routes import auth, health, session


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(verifycode.router, tags=["verifycode"])
api_router.include_router(getlevels.router, tags=["levels"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(level_sublevel.router, prefix="/levels", tags=["level_sublevel"])
