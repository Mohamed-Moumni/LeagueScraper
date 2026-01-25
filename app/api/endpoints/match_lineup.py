from typing import Any, Dict, List, Optional
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, ConfigDict
from app.services.matches.match_scraper_service import MatchLineupScraper
from fastapi import HTTPException, WebSocketException
from app import logger
from app.api.models.match_lineup import MatchRequest, MatchResponse


router = APIRouter()


@router.post("/match/lineup", response_model=MatchResponse)
async def match_lineup(request: MatchRequest):
    """
    Get match lineup for the specified teams.

    Args:
        request: MatchRequest containing team1 and team2 slugs

    Returns:
        MatchResponse with lineup data

    Raises:
        HTTPException: If browser fails to start, event not found, or lineup not found
    """
    scraper = MatchLineupScraper()
    browser_started = False

    try:
        # Start browser
        await scraper.start_browser()
        browser_started = True

        # Get match event ID using team names from request
        event_id = await scraper.get_match_event_id(request.team1, request.team2)

        if not event_id:
            raise HTTPException(
                status_code=404,
                detail=f"Match not found for teams: {request.team1} vs {request.team2}",
            )

        # Get match lineup
        lineup_data = await scraper.get_match_lineup(event_id)

        if lineup_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Lineup not found for match: {request.team1} vs {request.team2}",
            )

        # Pydantic will automatically convert the dict to LineupData
        # Type ignore needed because scraper returns Any from evaluate()
        return MatchResponse(lineup=lineup_data)  # type: ignore

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=f"Error fetching lineup: {str(e)}")
    finally:
        # Ensure browser is always stopped, even if an error occurs
        if browser_started:
            try:
                await scraper.stop_browser()
            except Exception as e:
                # Log browser stop errors but don't fail the request
                logger.error(f"Error stopping browser: {str(e)}")
