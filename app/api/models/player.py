from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class Country(BaseModel):
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None


class Sport(BaseModel):
    id: int
    name: str
    slug: str


class MarketValue(BaseModel):
    value: Optional[int] = None
    currency: Optional[str] = None


class FieldTranslations(BaseModel):
    nameTranslation: Optional[Dict[str, str]] = None
    shortNameTranslation: Optional[Dict[str, str]] = None


class TeamColors(BaseModel):
    primary: Optional[str] = None
    secondary: Optional[str] = None
    text: Optional[str] = None


class Category(BaseModel):
    id: int
    name: str
    slug: str
    sport: Optional[Sport] = None
    country: Optional[Country] = None
    flag: Optional[str] = None
    alpha2: Optional[str] = None
    fieldTranslations: Optional[FieldTranslations] = None


class UniqueTournament(BaseModel):
    id: int
    name: str
    slug: str
    primaryColorHex: Optional[str] = None
    secondaryColorHex: Optional[str] = None
    category: Optional[Category] = None
    userCount: Optional[int] = None
    country: Optional[Dict[str, Any]] = None
    displayInverseHomeAwayTeams: Optional[bool] = None
    fieldTranslations: Optional[FieldTranslations] = None


class Tournament(BaseModel):
    id: int
    name: str
    slug: str
    category: Optional[Category] = None
    uniqueTournament: Optional[UniqueTournament] = None
    priority: Optional[int] = None
    isLive: Optional[bool] = None
    fieldTranslations: Optional[FieldTranslations] = None


class Team(BaseModel):
    id: int
    name: str
    slug: str
    shortName: Optional[str] = None
    gender: Optional[str] = None
    sport: Optional[Sport] = None
    tournament: Optional[Tournament] = None
    primaryUniqueTournament: Optional[UniqueTournament] = None
    userCount: Optional[int] = None
    nameCode: Optional[str] = None
    disabled: Optional[bool] = None
    national: Optional[bool] = None
    type: Optional[int] = None
    country: Optional[Country] = None
    teamColors: Optional[TeamColors] = None
    fieldTranslations: Optional[FieldTranslations] = None


class Player(BaseModel):
    """Player model matching API response fields."""
    id: int
    name: str
    slug: str
    shortName: Optional[str] = None
    position: Optional[str] = None  # G, D, M, F
    positionsDetailed: Optional[List[str]] = None
    jerseyNumber: Optional[str] = None
    height: Optional[float] = None
    gender: Optional[str] = None  # M, F
    sofascoreId: Optional[str] = None
    dateOfBirth: Optional[str] = None
    dateOfBirthTimestamp: Optional[int] = None
    preferredFoot: Optional[str] = None
    userCount: Optional[int] = None
    deceased: Optional[bool] = None
    shirtNumber: Optional[int] = None
    contractUntilTimestamp: Optional[int] = None
    proposedMarketValue: Optional[int] = None
    proposedMarketValueRaw: Optional[MarketValue] = None
    team: Optional[Team] = None
    country: Optional[Country] = None
    fieldTranslations: Optional[FieldTranslations] = None


class PlayerResponse(BaseModel):
    """API response wrapper for single player."""
    player: Player


class PlayerRequest(BaseModel):
    """Request model for player lookup."""
    team_slug: str
    team_id: int


class PlayerListResponse(BaseModel):
    """Response model for list of players."""
    players: List[Player]
    total: int