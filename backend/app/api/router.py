from fastapi import APIRouter

from app.api import verifycode
from app.api.routes import health, session


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(verifycode.router, tags=["verifycode"])
