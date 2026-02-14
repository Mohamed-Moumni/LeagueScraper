from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any


class MatchRequest(BaseModel):
    team1: str = Field(examples=["olympic-safi"])
    team2: str = Field(examples=["wydad-casablanca"])


class Country(BaseModel):
    alpha2: Optional[str] = None
    alpha3: Optional[str] = None
    name: Optional[str] = None
    slug: Optional[str] = None


class MarketValue(BaseModel):
    value: Optional[int] = None
    currency: Optional[str] = None


class FieldTranslations(BaseModel):
    nameTranslation: Optional[Dict[str, str]] = None
    shortNameTranslation: Optional[Dict[str, str]] = None


class Player(BaseModel):
    name: str
    slug: str
    shortName: str
    position: str
    jerseyNumber: Optional[str] = None
    height: Optional[int] = None
    userCount: int
    gender: Optional[str] = None
    id: int
    country: Optional[Country] = None
    marketValueCurrency: Optional[str] = None
    dateOfBirthTimestamp: Optional[int] = None
    proposedMarketValueRaw: Optional[MarketValue] = None
    fieldTranslations: Optional[FieldTranslations] = None


class RatingVersions(BaseModel):
    original: Optional[float] = None
    alternative: Optional[float] = None


class StatisticsType(BaseModel):
    sportSlug: Optional[str] = None
    statisticsType: Optional[str] = None


class PlayerStatistics(BaseModel):
    totalPass: Optional[int] = None
    accuratePass: Optional[int] = None
    totalLongBalls: Optional[int] = None
    accurateLongBalls: Optional[int] = None
    goalAssist: Optional[int] = None
    accurateOwnHalfPasses: Optional[int] = None
    totalOwnHalfPasses: Optional[int] = None
    accurateOppositionHalfPasses: Optional[int] = None
    totalOppositionHalfPasses: Optional[int] = None
    totalCross: Optional[int] = None
    accurateCross: Optional[int] = None
    aerialLost: Optional[int] = None
    aerialWon: Optional[int] = None
    duelLost: Optional[int] = None
    duelWon: Optional[int] = None
    challengeLost: Optional[int] = None
    totalContest: Optional[int] = None
    wonContest: Optional[int] = None
    onTargetScoringAttempt: Optional[int] = None
    goals: Optional[int] = None
    totalClearance: Optional[int] = None
    outfielderBlock: Optional[int] = None
    ballRecovery: Optional[int] = None
    totalTackle: Optional[int] = None
    wonTackle: Optional[int] = None
    errorLeadToAShot: Optional[int] = None
    ownGoals: Optional[int] = None
    unsuccessfulTouch: Optional[int] = None
    penaltyConceded: Optional[int] = None
    wasFouled: Optional[int] = None
    fouls: Optional[int] = None
    totalOffside: Optional[int] = None
    crossNotClaimed: Optional[int] = None
    goodHighClaim: Optional[int] = None
    savedShotsFromInsideTheBox: Optional[int] = None
    saves: Optional[int] = None
    totalKeeperSweeper: Optional[int] = None
    accurateKeeperSweeper: Optional[int] = None
    minutesPlayed: Optional[int] = None
    touches: Optional[int] = None
    rating: Optional[float] = None
    possessionLostCtrl: Optional[int] = None
    expectedGoals: Optional[float] = None
    expectedAssists: Optional[float] = None
    keyPass: Optional[int] = None
    interceptionWon: Optional[int] = None
    shotOffTarget: Optional[int] = None
    blockedScoringAttempt: Optional[int] = None
    dispossessed: Optional[int] = None
    penaltyWon: Optional[int] = None
    totalShots: Optional[int] = None
    ratingVersions: Optional[RatingVersions] = None
    statisticsType: Optional[StatisticsType] = None

    model_config = ConfigDict(extra="allow")


class PlayerEntry(BaseModel):
    player: Player
    teamId: int
    shirtNumber: int
    jerseyNumber: str
    position: str
    substitute: bool
    statistics: Optional[PlayerStatistics] = None


class TeamColor(BaseModel):
    primary: str
    number: str
    outline: str
    fancyNumber: str


class TeamLineup(BaseModel):
    players: List[PlayerEntry]
    supportStaff: List[Any] = []
    formation: Optional[str] = None
    playerColor: Optional[TeamColor] = None
    goalkeeperColor: Optional[TeamColor] = None


class LineupData(BaseModel):
    confirmed: bool
    home: TeamLineup
    away: TeamLineup
    statisticalVersion: Optional[int] = None


# Schema for the response
class MatchResponse(BaseModel):
    lineup: LineupData
