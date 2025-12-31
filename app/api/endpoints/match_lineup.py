from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

# Schema for the match request
class MatchRequest(BaseModel):
    team1: str = Field(examples=["olympic-safi"])
    team2: str = Field(examples=["wydad-casablanca"])

# Schema for the response
class MatchResponse(BaseModel):
    message: str
    match_id: str
    team1: str
    team2: str

router = APIRouter()

@router.post("/match/lineup")
async def match_lineup():
    return await UserService.create(user)