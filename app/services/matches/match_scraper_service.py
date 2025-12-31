import httpx
from typing import Dict, List, Optional
import re
import json
import zendriver as zd
import logging
import os
import asyncio

logger = logging.getLogger(__name__)


class MatchLineupScraper:
    """
    Scraper class for fetching match lineups from sports websites.
    """

    def __init__(self):
        self.base_url = os.getenv("BASE_URL") or "https://www.sofascore.com"
        self.timeout = 30.0
        self.max_tries = 3
        self.config = zd.Config(
            headless=True,
            expert=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            browser_args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-site-isolation-trials",
                "--disable-ipc-flooding-protection",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ],
        )
        self.cookies = None

    async def start_browser(self):
        self.browser = await zd.start(self.config)

    async def stop_browser(self):
        await self.browser.stop()

    async def get_match_event_id(self, team1: str, team2: str) -> int | None:
        match_url: str = self.base_url or "https://www.sofascore.com"
        match_url = match_url + f"/football/match/{team1}-{team2}/tAosMax"
        tab = await self.browser.get(match_url)
        await tab.wait_for_ready_state("complete")

        match_script_elem = await tab.select("#__NEXT_DATA__")

        html_content = await match_script_elem.get_html()
        match_league_json = re.search(r">(.*)</script>", html_content, re.DOTALL)
        if match_league_json:
            league_team_data_json = match_league_json.group(1)
            league_team_data = json.loads(league_team_data_json)
            league_match_data = league_team_data["props"]["pageProps"]["initialProps"]
            match_event_id = int(league_match_data["event"]["id"])
            return match_event_id
        return None

    async def generate_cookies(self):
        base_url: str = self.base_url or "https://www.sofascore.com"
        if base_url:
            tab = await self.browser.get(base_url)
            await tab.wait_for_ready_state("complete")
            cookies = await self.browser.cookies.get_all()
            sofa_score_domain = [
                cookie for cookie in cookies if cookie.domain == "www.sofascore.com"
            ]
        return sofa_score_domain

    async def get_match_lineup(self, id: int):
        lineup_url = self.base_url + f"/api/v1/event/{id}/lineups"

        if self.cookies is None:
            self.cookies = await self.generate_cookies()

        zd_cookies = [
            zd.cdp.network.CookieParam(
                name=cookie.name,
                value=cookie.value,
                domain=cookie.domain,
                path=cookie.path,
            )
            for cookie in self.cookies
        ]
        await self.browser.cookies.set_all(zd_cookies)

        tab = await self.browser.get(lineup_url)
        lineup = await tab.evaluate("JSON.parse(document.body.innerText)")
        return lineup


async def main():
    scraper = MatchLineupScraper()
    await scraper.start_browser()
    event_id = await scraper.get_match_event_id("olympic-safi", "wydad-casablanca")
    if event_id:
        lineup = await scraper.get_match_lineup(event_id)
        print(lineup)
    await scraper.stop_browser()

if __name__ == "__main__":
    asyncio.run(main())