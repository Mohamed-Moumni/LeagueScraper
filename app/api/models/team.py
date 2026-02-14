from pydantic import BaseModel, ConfigDict
from typing import Optional


class Country(BaseModel):
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None


class TeamColor(BaseModel):
    primary: Optional[str] = None
    secondary: Optional[str] = None
    text: Optional[str] = None
    number: Optional[str] = None
    outline: Optional[str] = None
    fancyNumber: Optional[str] = None


class Team(BaseModel):
    """Team model matching the API response."""

    id: int
    name: str
    slug: str
    shortName: Optional[str] = None
    gender: Optional[str] = None
    nameCode: Optional[str] = None
    country: Optional[Country] = None
    teamColors: Optional[TeamColor] = None

    model_config = ConfigDict(extra="allow")
