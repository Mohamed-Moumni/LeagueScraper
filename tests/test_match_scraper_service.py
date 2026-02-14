import pytest
from unittest.mock import AsyncMock, patch, Mock
import os
from app.services.matches.match_scraper_service import MatchLineupScraper


class TestMatchLineupScraper:
    """Unit tests for the MatchLineupScraper service."""

    @pytest.fixture
    def scraper(self):
        """Create a MatchLineupScraper instance."""
        return MatchLineupScraper()

    @pytest.fixture
    def mock_browser(self):
        """Create a mock browser object."""
        browser = AsyncMock()
        return browser

    @pytest.fixture
    def mock_tab(self):
        """Create a mock tab object."""
        tab = AsyncMock()
        return tab

    def test_init_default_values(self, scraper):
        """Test that scraper initializes with default values."""
        assert scraper.base_url == "https://www.sofascore.com"
        assert scraper.timeout == 30.0
        assert scraper.max_tries == 3
        assert scraper.cookies is None
        assert scraper.config is not None
        assert scraper.config.headless is True
        assert scraper.config.expert is True

    @patch.dict(os.environ, {"BASE_URL": "https://custom-url.com"})
    def test_init_with_custom_base_url(self):
        """Test that scraper uses custom BASE_URL from environment."""
        scraper = MatchLineupScraper()
        assert scraper.base_url == "https://custom-url.com"

    @pytest.mark.asyncio
    async def test_stop_browser_success(self, scraper, mock_browser):
        """Test successful browser stop."""
        scraper.browser = mock_browser
        mock_browser.stop = AsyncMock()

        await scraper.stop_browser()

        mock_browser.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_browser_error(self, scraper, mock_browser):
        """Test browser stop error handling."""
        scraper.browser = mock_browser
        mock_browser.stop = AsyncMock(side_effect=Exception("Stop failed"))

        with pytest.raises(Exception, match="Stop failed"):
            await scraper.stop_browser()

    @pytest.mark.asyncio
    async def test_get_match_event_id_no_json_match(
        self, scraper, mock_browser, mock_tab
    ):
        """Test event ID retrieval when JSON is not found in HTML."""
        scraper.browser = mock_browser
        mock_browser.get = AsyncMock(return_value=mock_tab)
        mock_tab.wait_for_ready_state = AsyncMock()
        mock_tab.select = AsyncMock(return_value=mock_tab)

        # Mock HTML without matching JSON pattern
        mock_html = "<div>No JSON data here</div>"
        mock_tab.get_html = AsyncMock(return_value=mock_html)

        event_id = await scraper.get_match_event_id("team1", "team2")

        assert event_id is None

    @pytest.mark.asyncio
    async def test_get_match_event_id_browser_error(self, scraper, mock_browser):
        """Test event ID retrieval when browser.get fails."""
        scraper.browser = mock_browser
        mock_browser.get = AsyncMock(side_effect=Exception("Browser error"))

        with pytest.raises(Exception, match="Browser error"):
            await scraper.get_match_event_id("team1", "team2")

    @pytest.mark.asyncio
    async def test_generate_cookies_with_custom_base_url(
        self, scraper, mock_browser, mock_tab
    ):
        """Test cookie generation with custom base URL."""
        scraper.base_url = "https://custom-url.com"
        scraper.browser = mock_browser
        mock_browser.get = AsyncMock(return_value=mock_tab)
        mock_tab.wait_for_ready_state = AsyncMock()

        mock_cookie = Mock()
        mock_cookie.domain = "www.sofascore.com"
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"

        mock_browser.cookies = Mock()
        mock_browser.cookies.get_all = AsyncMock(return_value=[mock_cookie])

        cookies = await scraper.generate_cookies()

        assert len(cookies) == 1
        mock_browser.get.assert_called_once_with("https://custom-url.com")

    @pytest.mark.asyncio
    async def test_get_match_lineup_success_with_existing_cookies(
        self, scraper, mock_browser, mock_tab
    ):
        """Test successful lineup retrieval with existing cookies."""
        scraper.browser = mock_browser

        # Setup existing cookies
        mock_cookie = Mock()
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "www.sofascore.com"
        mock_cookie.path = "/"
        scraper.cookies = [mock_cookie]

        mock_browser.cookies = Mock()
        mock_browser.cookies.set_all = AsyncMock()
        mock_browser.get = AsyncMock(return_value=mock_tab)

        mock_lineup_data = {"lineup": {"confirmed": True, "home": {}, "away": {}}}
        mock_tab.evaluate = AsyncMock(return_value=mock_lineup_data)

        lineup = await scraper.get_match_lineup(12345)

        assert lineup == mock_lineup_data
        mock_browser.get.assert_called_once_with(
            "https://www.sofascore.com/api/v1/event/12345/lineups"
        )
        mock_browser.cookies.set_all.assert_called_once()
        mock_tab.evaluate.assert_called_once_with("JSON.parse(document.body.innerText)")

    @pytest.mark.asyncio
    async def test_get_match_lineup_with_custom_base_url(
        self, scraper, mock_browser, mock_tab
    ):
        """Test lineup retrieval with custom base URL."""
        scraper.base_url = "https://custom-url.com"
        scraper.browser = mock_browser

        mock_cookie = Mock()
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "www.sofascore.com"
        mock_cookie.path = "/"
        scraper.cookies = [mock_cookie]

        mock_browser.cookies = Mock()
        mock_browser.cookies.set_all = AsyncMock()
        mock_browser.get = AsyncMock(return_value=mock_tab)

        mock_lineup_data = {"lineup": {"confirmed": True}}
        mock_tab.evaluate = AsyncMock(return_value=mock_lineup_data)

        lineup = await scraper.get_match_lineup(12345)

        assert lineup == mock_lineup_data
        mock_browser.get.assert_called_once_with(
            "https://custom-url.com/api/v1/event/12345/lineups"
        )

    @pytest.mark.asyncio
    async def test_get_match_lineup_evaluate_error(
        self, scraper, mock_browser, mock_tab
    ):
        """Test lineup retrieval when evaluate fails."""
        scraper.browser = mock_browser

        mock_cookie = Mock()
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "www.sofascore.com"
        mock_cookie.path = "/"
        scraper.cookies = [mock_cookie]

        mock_browser.cookies = Mock()
        mock_browser.cookies.set_all = AsyncMock()
        mock_browser.get = AsyncMock(return_value=mock_tab)
        mock_tab.evaluate = AsyncMock(side_effect=Exception("Evaluate error"))

        with pytest.raises(Exception, match="Evaluate error"):
            await scraper.get_match_lineup(12345)

    @pytest.mark.asyncio
    async def test_get_match_lineup_browser_get_error(self, scraper, mock_browser):
        """Test lineup retrieval when browser.get fails."""
        scraper.browser = mock_browser

        mock_cookie = Mock()
        mock_cookie.name = "session"
        mock_cookie.value = "abc123"
        mock_cookie.domain = "www.sofascore.com"
        mock_cookie.path = "/"
        scraper.cookies = [mock_cookie]

        mock_browser.cookies = Mock()
        mock_browser.cookies.set_all = AsyncMock()
        mock_browser.get = AsyncMock(side_effect=Exception("Browser error"))

        with pytest.raises(Exception, match="Browser error"):
            await scraper.get_match_lineup(12345)

    @pytest.mark.asyncio
    async def test_get_match_lineup_multiple_cookies(
        self, scraper, mock_browser, mock_tab
    ):
        """Test lineup retrieval with multiple cookies."""
        scraper.browser = mock_browser

        mock_cookie1 = Mock()
        mock_cookie1.name = "session"
        mock_cookie1.value = "abc123"
        mock_cookie1.domain = "www.sofascore.com"
        mock_cookie1.path = "/"

        mock_cookie2 = Mock()
        mock_cookie2.name = "token"
        mock_cookie2.value = "xyz789"
        mock_cookie2.domain = "www.sofascore.com"
        mock_cookie2.path = "/"

        scraper.cookies = [mock_cookie1, mock_cookie2]

        mock_browser.cookies = Mock()
        mock_browser.cookies.set_all = AsyncMock()
        mock_browser.get = AsyncMock(return_value=mock_tab)

        mock_lineup_data = {"lineup": {"confirmed": True}}
        mock_tab.evaluate = AsyncMock(return_value=mock_lineup_data)

        lineup = await scraper.get_match_lineup(12345)

        assert lineup == mock_lineup_data
        # Verify set_all was called with a list of 2 CookieParam objects
        assert mock_browser.cookies.set_all.call_count == 1
        call_args = mock_browser.cookies.set_all.call_args[0][0]
        assert len(call_args) == 2
