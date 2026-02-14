from pydantic import BaseModel, ConfigDict


class Table(BaseModel):
    teamId: int
    position: int
    played: int
    wins: int
    losses: int
    scoresFor: int
    scoresAgainst: int
    draws: int
    points: int
    scoreDiffFormatted: int

    model_config = ConfigDict(extra="allow")
