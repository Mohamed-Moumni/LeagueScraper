import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app


class TestMatchLineupAPI:
    """Unit tests for the match lineup API endpoint."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def match_request_payload(self):
        """Create a match request payload."""
        return {"team1": "olympic-safi", "team2": "wydad-casablanca"}

    @pytest.fixture
    def mock_lineup_data(self):
        """Create mock lineup data."""
        return {
            "confirmed": True,
            "home": {
                "players": [
                    {
                        "player": {
                            "name": "John Doe",
                            "slug": "john-doe",
                            "shortName": "J. Doe",
                            "position": "Forward",
                            "jerseyNumber": "10",
                            "height": 180,
                            "userCount": 1000,
                            "gender": "M",
                            "id": 1,
                            "country": {
                                "alpha2": "US",
                                "alpha3": "USA",
                                "name": "United States",
                                "slug": "united-states",
                            },
                            "marketValueCurrency": "USD",
                            "dateOfBirthTimestamp": 631152000,
                            "proposedMarketValueRaw": {
                                "value": 5000000,
                                "currency": "USD",
                            },
                            "fieldTranslations": {
                                "nameTranslation": {"en": "John Doe"},
                                "shortNameTranslation": {"en": "J. Doe"},
                            },
                        },
                        "teamId": 1,
                        "shirtNumber": 10,
                        "jerseyNumber": "10",
                        "position": "Forward",
                        "substitute": False,
                        "statistics": {
                            "goals": 1,
                            "assists": 0,
                            "minutesPlayed": 90,
                            "rating": 7.5,
                            "totalPass": 45,
                            "accuratePass": 38,
                        },
                    }
                ],
                "supportStaff": [],
                "formation": "4-4-2",
                "playerColor": {
                    "primary": "#FF0000",
                    "number": "#FFFFFF",
                    "outline": "#000000",
                    "fancyNumber": "#FFFFFF",
                },
                "goalkeeperColor": {
                    "primary": "#FF0000",
                    "number": "#FFFFFF",
                    "outline": "#000000",
                    "fancyNumber": "#FFFFFF",
                },
            },
            "away": {
                "players": [
                    {
                        "player": {
                            "name": "Jane Smith",
                            "slug": "jane-smith",
                            "shortName": "J. Smith",
                            "position": "Midfielder",
                            "jerseyNumber": "8",
                            "height": 175,
                            "userCount": 800,
                            "gender": "F",
                            "id": 2,
                            "country": {
                                "alpha2": "GB",
                                "alpha3": "GBR",
                                "name": "United Kingdom",
                                "slug": "united-kingdom",
                            },
                            "marketValueCurrency": "GBP",
                            "dateOfBirthTimestamp": 662688000,
                            "proposedMarketValueRaw": {
                                "value": 3000000,
                                "currency": "GBP",
                            },
                        },
                        "teamId": 2,
                        "shirtNumber": 8,
                        "jerseyNumber": "8",
                        "position": "Midfielder",
                        "substitute": False,
                        "statistics": {
                            "goals": 0,
                            "assists": 1,
                            "minutesPlayed": 90,
                            "rating": 7.0,
                            "totalPass": 60,
                            "accuratePass": 55,
                        },
                    }
                ],
                "supportStaff": [],
                "formation": "4-3-3",
                "playerColor": {
                    "primary": "#0000FF",
                    "number": "#FFFFFF",
                    "outline": "#000000",
                    "fancyNumber": "#FFFFFF",
                },
                "goalkeeperColor": {
                    "primary": "#0000FF",
                    "number": "#FFFFFF",
                    "outline": "#000000",
                    "fancyNumber": "#FFFFFF",
                },
            },
            "statisticalVersion": 1,
        }

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_success(
        self, mock_scraper_class, client, mock_lineup_data, match_request_payload
    ):
        """Test successful match lineup retrieval."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(return_value=mock_lineup_data)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "lineup" in data
        assert data["lineup"]["confirmed"] is True
        assert "home" in data["lineup"]
        assert "away" in data["lineup"]
        assert len(data["lineup"]["home"]["players"]) == 1
        assert len(data["lineup"]["away"]["players"]) == 1

        # Verify scraper methods were called
        mock_scraper.start_browser.assert_called_once()
        mock_scraper.get_match_event_id.assert_called_once_with(
            "olympic-safi", "wydad-casablanca"
        )
        mock_scraper.get_match_lineup.assert_called_once_with(12345)
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_not_found_when_event_id_is_none(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test 404 response when event_id is None."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=None)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 404
        assert "Match not found" in response.json()["detail"]
        assert "olympic-safi" in response.json()["detail"]
        assert "wydad-casablanca" in response.json()["detail"]

        # Verify scraper methods were called
        mock_scraper.start_browser.assert_called_once()
        mock_scraper.get_match_event_id.assert_called_once_with(
            "olympic-safi", "wydad-casablanca"
        )
        mock_scraper.get_match_lineup.assert_not_called()
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_not_found_when_lineup_is_none(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test 404 response when lineup is None."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(return_value=None)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 404
        assert "Lineup not found" in response.json()["detail"]

        # Verify scraper methods were called
        mock_scraper.start_browser.assert_called_once()
        mock_scraper.get_match_event_id.assert_called_once_with(
            "olympic-safi", "wydad-casablanca"
        )
        mock_scraper.get_match_lineup.assert_called_once_with(12345)
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_browser_start_error(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test handling of browser start errors."""
        # Setup mock scraper to raise an exception
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock(
            side_effect=Exception("Browser start failed")
        )
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions - should return 500 or propagate error
        assert response.status_code >= 400

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_get_event_id_error(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test handling of get_match_event_id errors."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(
            side_effect=Exception("Failed to get event ID")
        )
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions - should return 500 or propagate error
        assert response.status_code >= 400
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_get_lineup_error(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test handling of get_match_lineup errors."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(
            side_effect=Exception("Failed to get lineup")
        )
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions - should return 500 or propagate error
        assert response.status_code >= 400
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_empty_lineup_data(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test handling of empty lineup data."""
        empty_lineup = {
            "confirmed": False,
            "home": {
                "players": [],
                "supportStaff": [],
                "formation": None,
                "playerColor": None,
                "goalkeeperColor": None,
            },
            "away": {
                "players": [],
                "supportStaff": [],
                "formation": None,
                "playerColor": None,
                "goalkeeperColor": None,
            },
            "statisticalVersion": None,
        }

        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(return_value=empty_lineup)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["lineup"]["confirmed"] is False
        assert len(data["lineup"]["home"]["players"]) == 0
        assert len(data["lineup"]["away"]["players"]) == 0

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_browser_cleanup_on_error(
        self, mock_scraper_class, client, match_request_payload
    ):
        """Test that browser is properly cleaned up even when errors occur."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(side_effect=Exception("Error"))
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Verify browser cleanup was attempted in finally block
        assert response.status_code == 500
        mock_scraper.start_browser.assert_called_once()
        mock_scraper.stop_browser.assert_called_once()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_response_model_validation(
        self, mock_scraper_class, client, mock_lineup_data, match_request_payload
    ):
        """Test that response conforms to MatchResponse model."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(return_value=mock_lineup_data)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        # Validate response structure matches MatchResponse model
        assert "lineup" in data
        lineup = data["lineup"]
        assert "confirmed" in lineup
        assert "home" in lineup
        assert "away" in lineup
        assert isinstance(lineup["confirmed"], bool)
        assert isinstance(lineup["home"]["players"], list)
        assert isinstance(lineup["away"]["players"], list)

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_with_statistics(
        self, mock_scraper_class, client, mock_lineup_data, match_request_payload
    ):
        """Test lineup response includes player statistics."""
        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=12345)
        mock_scraper.get_match_lineup = AsyncMock(return_value=mock_lineup_data)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post(
            "/api/v1/football/match/lineup", json=match_request_payload
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()

        # Check that statistics are included
        home_player = data["lineup"]["home"]["players"][0]
        assert "statistics" in home_player
        assert home_player["statistics"]["goals"] == 1
        assert home_player["statistics"]["minutesPlayed"] == 90
        assert home_player["statistics"]["rating"] == 7.5

    def test_match_lineup_missing_payload(self, client):
        """Test that missing request payload returns validation error."""
        response = client.post("/api/v1/football/match/lineup")

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    def test_match_lineup_invalid_payload(self, client):
        """Test that invalid request payload returns validation error."""
        invalid_payload = {"team1": "team1"}  # Missing team2
        response = client.post("/api/v1/football/match/lineup", json=invalid_payload)

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()

    @patch("app.api.endpoints.match_lineup.MatchLineupScraper")
    def test_match_lineup_custom_teams(
        self, mock_scraper_class, client, mock_lineup_data
    ):
        """Test lineup retrieval with custom team names."""
        custom_payload = {"team1": "real-madrid", "team2": "barcelona"}

        # Setup mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.start_browser = AsyncMock()
        mock_scraper.get_match_event_id = AsyncMock(return_value=99999)
        mock_scraper.get_match_lineup = AsyncMock(return_value=mock_lineup_data)
        mock_scraper.stop_browser = AsyncMock()
        mock_scraper_class.return_value = mock_scraper

        # Make request
        response = client.post("/api/v1/football/match/lineup", json=custom_payload)

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "lineup" in data

        # Verify scraper methods were called with custom team names
        mock_scraper.get_match_event_id.assert_called_once_with(
            "real-madrid", "barcelona"
        )
        mock_scraper.get_match_lineup.assert_called_once_with(99999)
