

import asyncio

from app.api.endpoints import teams
from  ..scraper  import Scraper, logger


class TeamsScraper(Scraper):
    
    async def get_teams(self, league_id:int, season_id:int):
        URL:str = self.base_url + f"/api/v1/unique-tournament/{league_id}/season/{season_id}/standings/total"
            
        try:
            teams_data = await self.get_api_response(URL)
            if teams_data is None:
                return None
            standings = teams_data["standings"][0]
            return [row["team"] for row in standings["rows"]]
        except Exception as e:
            logger.error(f"Error fetching teams: {e}")
            return None