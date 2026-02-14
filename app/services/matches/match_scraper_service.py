from typing import Optional
import logging

from app.services.scraper import Scraper

logger = logging.getLogger(__name__)


class MatchLineupScraper(Scraper):
    """
    Scraper class for fetching match lineups from sports websites.
    Extends the base Scraper class for browser and cookie management.
    """

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url)

    async def get_match_event_id(self, team1: str, team2: str) -> int | None:
        """
        Get the match event ID for a match between two teams.

        Args:
            team1: First team name (URL-formatted)
            team2: Second team name (URL-formatted)

        Returns:
            Match event ID or None if not found
        """
        match_url = f"{self.base_url}/football/match/{team1}-{team2}/tAosMax"

        tab = await self.get_page(match_url)

        json_data = await self.get_json_from_page(tab)
        if json_data:
            try:
                league_match_data = json_data["props"]["pageProps"]["initialProps"]
                match_event_id = int(league_match_data["event"]["id"])
                return match_event_id
            except (KeyError, TypeError) as e:
                logger.error(f"Failed to extract match event ID: {e}")

        return None

    async def get_match_lineup(self, id: int) -> Optional[dict]:
        """
        Get the lineup for a match by event ID.

        Args:
            id: Match event ID

        Returns:
            Lineup data as dict or None if request fails
        """
        lineup_url = f"{self.base_url}/api/v1/event/{id}/lineups"

        # Try API request first (faster)
        lineup = await self.get_api_response(lineup_url)
        if lineup:
            return lineup

        # Fallback to browser if API fails
        logger.info("API request failed, falling back to browser")
        await self.set_cookies()

        tab = await self.get_page(lineup_url)
        lineup = await self.evaluate_javascript(
            tab, "JSON.parse(document.body.innerText)"
        )
        return lineup
