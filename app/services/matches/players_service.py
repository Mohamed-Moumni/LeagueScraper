import asyncio
import logging
from typing import Optional, Set, List, Dict, Any
from dataclasses import dataclass

from app.services.scraper import Scraper

logger = logging.getLogger(__name__)


@dataclass
class Player:
    """Data class representing a player."""
    player: dict
    transfers: Optional[list] = None
    seoContent: Optional[dict] = None
    lastYearSummary: Optional[dict] = None
    uniqueTournamentsMap: Optional[dict] = None


class PlayersService(Scraper):
    """
    Service for fetching player data from sports websites.
    Extends the base Scraper class for browser and cookie management.
    """

    def __init__(self, base_url: Optional[str] = None):
        super().__init__(base_url)

    async def get_player_data(self, player_url: str) -> Optional[dict]:
        """
        Get player data from a player's page.
        
        Args:
            player_url: Relative URL path to the player page (e.g., "/player/name/12345")
            
        Returns:
            Player data dict or None if not found
        """
        
        try:
            api_url = f"{self.base_url}/api/v1/player/{player_url}"
            print("api_url", api_url)
            player_data = await self.get_api_response(api_url)
            if player_data:
                return player_data
        except Exception as e:
            logger.error(f"Failed to get player data from {player_url}: {e}")
        
        return None

    async def get_players_by_team(self, team_slug: str, team_id: int) -> Set[str]:
        """
        Get all player URLs for a team.
        
        Args:
            team_slug: Team slug (URL-formatted name)
            team_id: Team ID
            
        Returns:
            Set of player URL paths
        """
        url = f"{self.base_url}/football/team/{team_slug}/{team_id}#tab:players"
        
        print("url", url)
        
        try:
            api_url = f"{self.base_url}/api/v1/team/{team_id}/players"
            
            players_data = await self.get_api_response(api_url)
            if players_data and "players" in players_data:
                player_urls = set()
                for player in players_data["players"]:
                    player_id = player.get("player", {}).get("id")
                    player_slug = player.get("player", {}).get("slug")
                    if player_id and player_slug:
                        player_urls.add(f"{player_id}")
                print("players_urls", player_urls)
                return player_urls
            return set()
        except Exception as e:
            logger.error(f"Failed to get players for team {team_slug}: {e}")
            return set()

    async def get_player_details(self, player_url: str) -> Optional[dict]:
        """
        Get detailed player information.
        
        Args:
            player_url: Relative URL path to the player page
            
        Returns:
            Player details dict or None if not found
        """
        player_data = await self.get_player_data(player_url)
        if player_data:
            try:
                return player_data["player"]
            except (KeyError, TypeError) as e:
                logger.error(f"Failed to extract player details: {e}")
        return None

    async def get_all_players_for_team(
        self, 
        team_slug: str, 
        team_id: int,
        max_concurrent: int = 15,
    ) -> List[Dict[str, Any]]:
        """
        Get all player details for a team.
        
        Args:
            team_slug: Team slug (URL-formatted name)
            team_id: Team ID
            delay_between_requests: Delay in seconds between player requests
            
        Returns:
            List of player detail dicts
        """
        player_urls = await self.get_players_by_team(team_slug, team_id)
        # Semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(url: str) -> Optional[Dict[str, Any]]:
            async with semaphore:
                print("fetching player details", url)
                result = await self.get_player_details(url)
                # Small delay to be respectful to the server
                await asyncio.sleep(0.5)
                return result
        
        # Run all requests concurrently (limited by semaphore)
        tasks = [fetch_with_semaphore(url) for url in player_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        players: List[Dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error fetching player: {result}")
            elif result is not None:
                players.append(result)
        
        logger.info(f"Retrieved {len(players)} player details for team {team_slug}")
        return players