from typing import List
from fastapi import APIRouter, HTTPException

from app.services.teams.teams_service import TeamsScraper
from app import logger
from app.api.models.table import Table

router = APIRouter()


@router.get("/table/league/{league_id}/season/{season_id}", response_model=List[Table])
async def get_table(league_id: int, season_id: int):
    teams_scraper = TeamsScraper()
    browser_started = False

    try:
        await teams_scraper.start_browser()
        browser_started = True
        table_data = await teams_scraper.get_team_table(league_id, season_id)
        if table_data is None:
            logger.error(
                f"Table not found for league {league_id} and season {season_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Table not found for league {league_id} and season {season_id}",
            )
        table = []
        for team in table_data:
            team_table = Table(
                teamId=team["team"]["id"],
                position=team["position"],
                played=team["matches"],
                wins=team["wins"],
                losses=team["losses"],
                scoresFor=team["scoresFor"],
                scoresAgainst=team["scoresAgainst"],
                draws=team["draws"],
                points=team["points"],
                scoreDiffFormatted=team["scoreDiffFormatted"],
            )
            table.append(team_table)
        return table
    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching table: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching table: {str(e)}")
    finally:
        if browser_started:
            await teams_scraper.stop_browser()
