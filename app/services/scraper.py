import zendriver as zd
import logging
import os
import asyncio
from curl_cffi.requests import AsyncSession
from typing import List, Optional

logger = logging.getLogger(__name__)


class Scraper:
    """
    Base scraper class for web scraping operations.
    Handles browser initialization, cookie management, and common scraping utilities.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the scraper.

        Args:
            base_url: Base URL for scraping. Defaults to BASE_URL env var or SofaScore.
        """
        self.base_url = base_url or os.getenv("BASE_URL") or "https://www.sofascore.com"
        self.timeout = 30.0
        self.max_tries = 3
        self.browser = None
        self.cookies = None

        self.config = zd.Config(
            headless=True,
            expert=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/120.0.0.0 Safari/537.36",
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

    async def start_browser(self):
        """
        Start the browser instance.

        Raises:
            Exception: If browser fails to start
        """
        if self.browser is None:
            self.browser = await zd.start(self.config)
            logger.info("Browser started successfully")

    async def stop_browser(self):
        """
        Stop the browser instance.

        Raises:
            Exception: If browser fails to stop
        """
        if self.browser is not None:
            await self.browser.stop()
            self.browser = None
            logger.info("Browser stopped successfully")

    async def generate_cookies(self, domain: List[str] = []) -> List:
        """
        Generate cookies by visiting the base URL.

        Args:
            domain: Cookie domain to filter. Defaults to base_url domain.

        Returns:
            List of cookies for the specified domain
        """
        if not self.browser:
            raise RuntimeError("Browser must be started before generating cookies")

        domain.append("www.sofascore.com")
        domain.append(".sofascore.com")

        try:
            await self.browser.get(self.base_url)
            # Don't wait for ready state - just a short sleep for cookies to be set
            await asyncio.sleep(6)

            cookies = await self.browser.cookies.get_all()
            # # print("Cookies: ", cookies, len(cookies))
            # for cookie in cookies:
            #     print("Cookie Domain: ", cookie.domain)
            # filtered_cookies = [cookie for cookie in cookies if cookie.domain in domain]

            self.cookies = cookies
            logger.info(f"Generated {len(cookies)} cookies for domain {domain}")
            return cookies
        except Exception as e:
            logger.warning(f"Cookie generation failed: {e}, continuing without cookies")
            self.cookies = []
            return []

    async def set_cookies(self, cookies: Optional[List] = None):
        """
        Set cookies in the browser.

        Args:
            cookies: List of cookies to set. If None, uses self.cookies.
                    If self.cookies is None, generates new cookies.
        """
        if not self.browser:
            raise RuntimeError("Browser must be started before setting cookies")

        if cookies is None:
            if self.cookies is None:
                await self.generate_cookies()
            cookies = self.cookies

        if cookies is None:
            logger.warning("No cookies available to set")
            return

        zd_cookies = [
            zd.cdp.network.CookieParam(
                name=cookie.name,
                value=cookie.value,
                domain=cookie.domain,
                path=cookie.path,
            )
            for cookie in cookies
        ]

        await self.browser.cookies.set_all(zd_cookies)
        logger.info(f"Set {len(zd_cookies)} cookies in browser")

    async def get_page(self, url: str, wait_for: str = "complete"):
        """
        Navigate to a URL and wait for page to load.

        Args:
            url: URL to navigate to
            wait_for: Ready state to wait for - "loading", "interactive", or "complete" (default: "complete")

        Returns:
            Tab object for the loaded page

        Raises:
            Exception: If page navigation fails
        """
        if not self.browser:
            raise RuntimeError("Browser must be started before getting pages")

        # Validate wait_for parameter
        # valid_states = ["loading", "interactive", "complete"]
        # if wait_for not in valid_states:
        #     wait_for = "complete"

        tab = await self.browser.get(url)
        await tab.wait_for_ready_state(wait_for)  # type: ignore

        return tab

    async def evaluate_javascript(self, tab, script: str):
        """
        Evaluate JavaScript on a tab.

        Args:
            tab: Tab object
            script: JavaScript code to evaluate

        Returns:
            Result of JavaScript evaluation
        """
        return await tab.evaluate(script)

    async def get_json_from_page(
        self, tab, selector: str = "#__NEXT_DATA__"
    ) -> Optional[dict]:
        """
        Extract JSON data from a page element.

        Args:
            tab: Tab object
            selector: CSS selector for the element containing JSON

        Returns:
            Parsed JSON data or None if not found
        """
        import re
        import json

        try:
            element = await tab.select(selector)
            html_content = await element.get_html()

            # Extract JSON from script tag
            json_match = re.search(r">(.*)</script>", html_content, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group(1))
                return json_data
        except Exception as e:
            logger.error(f"Failed to extract JSON from page: {str(e)}")

        return None

    async def get_api_response(
        self, url: str, use_cookies: bool = True
    ) -> Optional[dict]:
        """
        Get JSON response from an API endpoint using httpx (faster than browser).

        Args:
            url: API endpoint URL
            use_cookies: Whether to use cookies for the request

        Returns:
            Parsed JSON response or None if request fails
        """
        if use_cookies:
            if self.cookies is None and self.browser:
                await self.generate_cookies()

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": self.base_url,
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": self.base_url,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "TE": "trailers",
        }
        try:
            async with AsyncSession(impersonate="chrome120") as session:
                if self.cookies:
                    cookies_string = "; ".join(
                        [
                            f"{cookie.name}={cookie.value}"
                            for cookie in self.cookies
                            if cookie.value is not None
                        ]
                    )
                    headers["Cookie"] = cookies_string
                    print("Cookies: ", cookies_string)
                response = await session.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_browser()
