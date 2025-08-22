from fastapi import APIRouter
from app.api.v1.endpoints import tasks, health

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])