from fastapi import APIRouter
from app.api.endpoints import match_lineup

api_router = APIRouter()
api_router.include_router(
    match_lineup.router, prefix="/football", tags=["matches"]
)
