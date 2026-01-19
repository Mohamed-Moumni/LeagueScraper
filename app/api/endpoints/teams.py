from typing import List, Optional
import logging
from pydantic import BaseModel, ConfigDict
from app.api.endpoints.match_lineup import router
from fastapi import HTTPException, Path

from app.services.teams.teams_service import TeamsScraper

logger = logging.getLogger(__name__)

# Schema for teams validation
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

# Schema for the response - handles both array and wrapped formats
class TeamsResponse(BaseModel):
    """Response model for teams endpoint - accepts array of teams."""
    teams: List[Team]

@router.get("/teams/league/{league_id}/season/{season_id}", response_model=TeamsResponse)
async def get_teams(
    league_id: int = Path(..., description="League/Unique Tournament ID", example=937),
    season_id: int = Path(..., description="Season ID", example=78750)
):
    """
    Get teams data for a specific league and season.
    
    Args:
        league_id: The unique tournament/league ID
        season_id: The season ID
        
    Returns:
        TeamsResponse with teams data (sport and fieldTranslations excluded)
        
    Raises:
        HTTPException: If teams not found or error occurs
    """
    teams_scraper = TeamsScraper()
    browser_started = False
    
    try:
        await teams_scraper.start_browser()
        browser_started = True
        
        teams_data = await teams_scraper.get_teams(league_id, season_id)
        if teams_data is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Teams not found for league {league_id} and season {season_id}"
            )
        
        cleaned_teams = [
            Team.model_validate(
                Team.model_validate(team).model_dump(
                    exclude={'sport', 'fieldTranslations', 'userCount', 'disabled', 'national', 'type'}, 
                    exclude_none=True
                )
            )
            for team in teams_data
        ]
        
        return TeamsResponse(teams=cleaned_teams)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching teams: {str(e)}"
        )
    finally:
        if browser_started:
            await teams_scraper.stop_browser()
    