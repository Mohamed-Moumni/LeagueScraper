from fastapi import APIRouter, HTTPException
from app.services.matches.players_service import PlayersService
from app.api.models.player import Player, PlayerListResponse

from app import logger

router = APIRouter()


@router.get("/players/{team_slug}/{team_id}", response_model=PlayerListResponse)
async def get_players(team_slug: str, team_id: int):
    """
    Get all players for a team.

    Args:
        team_slug: Team slug (URL-formatted name, e.g., "wydad-casablanca")
        team_id: Team ID (e.g., 36268)

    Returns:
        PlayerListResponse with list of players and total count

    Raises:
        HTTPException: If browser fails or players not found
    """
    scraper = PlayersService()
    browser_started = False

    try:
        await scraper.start_browser()
        browser_started = True

        players_data = await scraper.get_all_players_for_team(team_slug, team_id)

        if not players_data:
            raise HTTPException(
                status_code=404, detail=f"No players found for team: {team_slug}"
            )

        # Validate and convert to Pydantic models
        players = [Player(**p) for p in players_data]

        return PlayerListResponse(players=players, total=len(players))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching players for {team_slug}: {e}")
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if browser_started:
            try:
                await scraper.stop_browser()
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")
