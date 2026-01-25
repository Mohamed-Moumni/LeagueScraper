from fastapi import APIRouter
from app.api.endpoints import match_lineup, players, teams, table

api_router = APIRouter()
api_router.include_router(
    match_lineup.router, prefix="/football", tags=["matches"]
)

api_router.include_router(
    teams.router, prefix="/football", tags=["teams"]
)

api_router.include_router(
    players.router, prefix="/football", tags=["players"]
)

api_router.include_router(
    table.router, prefix="/football", tags=["table"]
)