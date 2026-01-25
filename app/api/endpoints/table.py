from fastapi import APIRouter, HTTPException

from app.services.teams.teams_service import TeamsScraper
from app import logger

router = APIRouter()


@router.get("/table/league/{league_id}/season/{season_id}")
async def get_table(league_id: int, season_id: int):
    teams_scraper = TeamsScraper()
    browser_started = False

    try:
        await teams_scraper.start_browser()
        browser_started = True
        table_data = await teams_scraper.get_teams(league_id, season_id)
        if table_data is None:
            logger.error(
                f"Table not found for league {league_id} and season {season_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Table not found for league {league_id} and season {season_id}",
            )
        return table_data
    except HTTPException as e:
        logger.error(f"HTTPException: {e}")
        raise
    except Exception as e:
        logger.error(f"Error fetching table: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching table: {str(e)}")
    finally:
        if browser_started:
            await teams_scraper.stop_browser()
