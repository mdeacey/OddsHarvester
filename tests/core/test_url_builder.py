import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from bs4 import BeautifulSoup

from src.core.url_builder import URLBuilder
from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.sport_market_constants import Sport

# Create test discovered leagues mapping (simulating dynamic discovery results)
TEST_DISCOVERED_LEAGUES = {
    "england-premier-league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
    "la-liga": f"{ODDSPORTAL_BASE_URL}/football/spain/la-liga",
    "atp-tour": f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour",
    "mlb": f"{ODDSPORTAL_BASE_URL}/baseball/usa/mlb",
    "japan-npb": f"{ODDSPORTAL_BASE_URL}/baseball/japan/npb",
}


@pytest.fixture
def discovered_leagues():
    """Provide test discovered leagues for URLBuilder tests."""
    return TEST_DISCOVERED_LEAGUES.copy()


@pytest.mark.parametrize(
    ("sport", "league", "season", "expected_url"),
    [
        # Valid cases with specific seasons
        (
            "football",
            "england-premier-league",
            "2023-2024",
            f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2023-2024/results/",
        ),
        ("tennis", "atp-tour", "2024-2025", f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour-2024-2025/results/"),
        # Empty season cases (representing current season)
        ("football", "england-premier-league", "", f"{ODDSPORTAL_BASE_URL}/football/england/premier-league/results/"),
        ("football", "england-premier-league", None, f"{ODDSPORTAL_BASE_URL}/football/england/premier-league/results/"),
        # Single year format
        ("tennis", "atp-tour", "2024", f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour-2024/results/"),
        # Baseball special cases (should only use first year)
        ("baseball", "mlb", "2023-2024", f"{ODDSPORTAL_BASE_URL}/baseball/usa/mlb-2023/results/"),
        ("baseball", "japan-npb", "2024-2025", f"{ODDSPORTAL_BASE_URL}/baseball/japan/npb-2024/results/"),
    ],
)
def test_get_historic_matches_url(sport, league, season, expected_url, discovered_leagues):
    """Test building URLs for historical matches with various inputs."""
    assert URLBuilder.get_historic_matches_url(sport, league, season, discovered_leagues) == expected_url


@pytest.mark.parametrize(
    ("sport", "league", "season", "error_msg"),
    [
        # Invalid season format
        (
            "football",
            "england-premier-league",
            "20-2024",
            "Invalid season format: 20-2024. Expected format: 'YYYY' or 'YYYY-YYYY'",
        ),
        (
            "football",
            "england-premier-league",
            "202A-2024",
            "Invalid season format: 202A-2024. Expected format: 'YYYY' or 'YYYY-YYYY'",
        ),
        (
            "football",
            "england-premier-league",
            "2023/2024",
            "Invalid season format: 2023/2024. Expected format: 'YYYY' or 'YYYY-YYYY'",
        ),
        (
            "football",
            "england-premier-league",
            " 2023-2024 ",
            "Invalid season format:  2023-2024 . Expected format: 'YYYY' or 'YYYY-YYYY'",
        ),
        (
            "football",
            "england-premier-league",
            "Season_2023-2024",
            "Invalid season format: Season_2023-2024. Expected format: 'YYYY' or 'YYYY-YYYY'",
        ),
    ],
)
def test_get_historic_matches_url_invalid_season_format(sport, league, season, error_msg, discovered_leagues):
    """Test invalid season formats."""
    with pytest.raises(ValueError, match=error_msg):
        URLBuilder.get_historic_matches_url(sport, league, season, discovered_leagues)


@pytest.mark.parametrize(
    ("sport", "league", "season", "error_msg"),
    [
        # According to the implementation, end year must be exactly start_year + 1
        (
            "football",
            "england-premier-league",
            "2023-2025",
            "Invalid season range: 2023-2025. The second year must be exactly one year after the first.",
        ),
        (
            "football",
            "england-premier-league",
            "2024-2023",
            "Invalid season range: 2024-2023. The second year must be exactly one year after the first.",
        ),
    ],
)
def test_get_historic_matches_url_invalid_season_range(sport, league, season, error_msg, discovered_leagues):
    """Test invalid season ranges."""
    with pytest.raises(ValueError, match=error_msg):
        URLBuilder.get_historic_matches_url(sport, league, season, discovered_leagues)


def test_get_historic_matches_url_invalid_league(discovered_leagues):
    """Test error handling for invalid leagues."""
    with pytest.raises(
        ValueError,
        match="Invalid league 'random-league' for sport 'football'. Available: england-premier-league, la-liga, atp-tour, mlb, japan-npb",
    ):
        URLBuilder.get_historic_matches_url("football", "random-league", "2023-2024", discovered_leagues)


@pytest.mark.parametrize(
    ("sport", "date", "league", "expected_url"),
    [
        # With league
        ("football", "2025-02-10", "england-premier-league", f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"),
        # Without league
        ("football", "2025-02-10", None, f"{ODDSPORTAL_BASE_URL}/matches/football/2025-02-10/"),
        # Different date format (assuming implemented format handling)
        ("tennis", "2025-02-10", "atp-tour", f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour"),
        # Empty or None date should use today's date (not testing exact value to avoid test instability)
        ("football", None, None, None),  # Special case handled in test function
        ("football", "", None, None),  # Special case handled in test function
    ],
)
def test_get_upcoming_matches_url(sport, date, league, expected_url, discovered_leagues):
    """Test building URLs for upcoming matches with various inputs."""
    if date is None or date == "":
        # Don't test the exact URL since it depends on today's date
        result = URLBuilder.get_upcoming_matches_url(sport, date, league, discovered_leagues)
        assert result.startswith(f"{ODDSPORTAL_BASE_URL}/matches/")
    else:
        assert URLBuilder.get_upcoming_matches_url(sport, date, league, discovered_leagues) == expected_url


@pytest.mark.parametrize(
    ("sport", "league", "expected_url"),
    [
        ("football", "england-premier-league", f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"),
        ("tennis", "atp-tour", f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour"),
        ("baseball", "mlb", f"{ODDSPORTAL_BASE_URL}/baseball/usa/mlb"),
    ],
)
def test_get_league_url(sport, league, expected_url, discovered_leagues):
    """Test retrieving league URLs."""
    assert URLBuilder.get_league_url(sport, league, discovered_leagues) == expected_url


def test_get_league_url_invalid_league(discovered_leagues):
    """Test get_league_url raises ValueError for unsupported league."""
    with pytest.raises(
        ValueError,
        match="Invalid league 'random-league' for sport 'football'. Available: england-premier-league, la-liga",
    ):
        URLBuilder.get_league_url("football", "random-league", discovered_leagues)


# Tests for new date range URL generation methods
class TestGetUpcomingMatchesUrlsForRange:
    """Test the get_upcoming_matches_urls_for_range method."""

    def test_single_date_range(self):
        """Test generating URLs for a single date range."""
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(
            sport="football", from_date="20250101", to_date="20250101"
        )
        assert len(urls_with_dates) == 1
        url, date_str = urls_with_dates[0]
        assert url == f"{ODDSPORTAL_BASE_URL}/matches/football/2025-01-01/"
        assert date_str == "2025-01-01"

    def test_multi_date_range(self):
        """Test generating URLs for a multi-date range."""
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(
            sport="football", from_date="20250101", to_date="20250103"
        )
        assert len(urls_with_dates) == 3

        # Check all expected dates are present
        dates = [date for _, date in urls_with_dates]
        assert "2025-01-01" in dates
        assert "2025-01-02" in dates
        assert "2025-01-03" in dates

        # Check URL format
        for url, date_str in urls_with_dates:
            assert url == f"{ODDSPORTAL_BASE_URL}/matches/football/{date_str}/"
            assert date_str in ["2025-01-01", "2025-01-02", "2025-01-03"]

    def test_date_range_with_league(self, discovered_leagues):
        """Test generating URLs for date range with specific league."""
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(
            sport="football", from_date="20250101", to_date="20250102", league="england-premier-league", discovered_leagues=discovered_leagues
        )
        assert len(urls_with_dates) == 2

        for url, date_str in urls_with_dates:
            assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"
            assert date_str in ["2025-01-01", "2025-01-02"]

    def test_now_keyword(self):
        """Test generating URLs with 'now' keyword."""
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(
            sport="football", from_date="now", to_date="now"
        )
        assert len(urls_with_dates) == 1
        url, date_str = urls_with_dates[0]
        today = datetime.now().strftime("%Y-%m-%d")
        assert url == f"{ODDSPORTAL_BASE_URL}/matches/football/{today}/"
        assert date_str == today

    def test_invalid_date_format(self):
        """Test error handling for invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format: 'invalid'"):
            URLBuilder.get_upcoming_matches_urls_for_range(
                sport="football", from_date="invalid", to_date="20250102"
            )

    def test_end_date_before_start_date(self):
        """Test error handling when end date is before start date."""
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            URLBuilder.get_upcoming_matches_urls_for_range(
                sport="football", from_date="20250105", to_date="20250101"
            )


class TestGetHistoricMatchesUrlsForRange:
    """Test the get_historic_matches_urls_for_range method."""

    def test_single_season_range(self, discovered_leagues):
        """Test generating URLs for a single season."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="2023", to_date="2023", league="england-premier-league", discovered_leagues=discovered_leagues
        )
        assert len(urls_with_seasons) == 1
        url, season_str = urls_with_seasons[0]
        assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2023/results/"
        assert season_str == "2023"

    def test_multi_season_range(self, discovered_leagues):
        """Test generating URLs for multiple seasons."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="2021", to_date="2023", league="england-premier-league", discovered_leagues=discovered_leagues
        )
        assert len(urls_with_seasons) == 3

        # Check all expected seasons are present
        seasons = [season for _, season in urls_with_seasons]
        assert "2021" in seasons
        assert "2022" in seasons
        assert "2023" in seasons

        # Check URL format
        for url, season_str in urls_with_seasons:
            assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{season_str}/results/"
            assert season_str in ["2021", "2022", "2023"]

    def test_season_range_with_hyphenated_seasons(self, discovered_leagues):
        """Test generating URLs with hyphenated season format."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="tennis", from_date="2022-2023", to_date="2023-2024", league="atp-tour", discovered_leagues=discovered_leagues
        )
        assert len(urls_with_seasons) == 2

        # Should generate for 2023 and 2024 (end years of the seasons)
        seasons = [season for _, season in urls_with_seasons]
        assert "2023" in seasons
        assert "2024" in seasons

    def test_now_keyword_historic(self, discovered_leagues):
        """Test generating URLs with 'now' keyword for historic matches."""
        current_year = datetime.now().year
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="now", to_date="now", league="england-premier-league", discovered_leagues=discovered_leagues
        )
        assert len(urls_with_seasons) == 1
        url, season_str = urls_with_seasons[0]
        assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{current_year}/results/"
        assert season_str == str(current_year)

    def test_invalid_season_format(self, discovered_leagues):
        """Test error handling for invalid season format."""
        with pytest.raises(ValueError, match="Invalid season format: 'invalid'"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="invalid", to_date="2023", league="england-premier-league", discovered_leagues=discovered_leagues
            )

    def test_end_season_before_start_season(self, discovered_leagues):
        """Test error handling when end season is before start season."""
        with pytest.raises(ValueError, match="End season/year cannot be before start season/year"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="2025", to_date="2020", league="england-premier-league", discovered_leagues=discovered_leagues
            )

    def test_invalid_season_range_format(self, discovered_leagues):
        """Test error handling for invalid season range (more than 1 year apart)."""
        with pytest.raises(ValueError, match="Invalid season range"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="2022-2024", to_date="2024-2025", league="england-premier-league", discovered_leagues=discovered_leagues
            )


class TestParseSeasonForUrl:
    """Test the _parse_season_for_url helper method."""

    def test_parse_integer_year(self):
        """Test parsing integer year input."""
        season_format, end_year = URLBuilder._parse_season_for_url(2023)
        assert season_format == "2023"
        assert end_year == 2023

    def test_parse_string_year(self):
        """Test parsing string year input."""
        season_format, end_year = URLBuilder._parse_season_for_url("2023")
        assert season_format == "2023"
        assert end_year == 2023

    def test_parse_hyphenated_season(self):
        """Test parsing hyphenated season format."""
        season_format, end_year = URLBuilder._parse_season_for_url("2022-2023")
        assert season_format == "2022-2023"
        assert end_year == 2023

    def test_parse_now_keyword(self):
        """Test parsing 'now' keyword."""
        current_year = datetime.now().year
        season_format, end_year = URLBuilder._parse_season_for_url("now")
        assert season_format == str(current_year)
        assert end_year == current_year

    def test_parse_invalid_format(self):
        """Test error handling for invalid format."""
        with pytest.raises(ValueError, match="Invalid season format: 'invalid'"):
            URLBuilder._parse_season_for_url("invalid")

    def test_parse_invalid_season_range(self):
        """Test error handling for invalid season range."""
        with pytest.raises(ValueError, match="Invalid season range: '2022-2024'"):
            URLBuilder._parse_season_for_url("2022-2024")


class TestGetAllAvailableSeasonsUrlRange:
    """Test the get_all_available_seasons_url_range method."""

    def test_get_all_available_seasons_default_range(self, discovered_leagues):
        """Test generating URLs for all available seasons with new optimized default range."""
        current_year = datetime.now().year

        urls_with_seasons = URLBuilder.get_all_available_seasons_url_range(
            sport="football", league="england-premier-league", discovered_leagues=discovered_leagues
        )

        # Should generate from 2010 to current year + 1 (new optimized range)
        expected_years = current_year + 1 - 2010 + 1
        assert len(urls_with_seasons) == expected_years

        # Check first and last seasons
        first_url, first_season = urls_with_seasons[0]
        last_url, last_season = urls_with_seasons[-1]

        assert first_season == "2010"
        assert first_url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2010/results/"
        assert last_season == str(current_year + 1)
        assert last_url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{current_year + 1}/results/"

    def test_get_all_available_seasons_custom_range(self, discovered_leagues):
        """Test generating URLs with custom fallback range."""
        urls_with_seasons = URLBuilder.get_all_available_seasons_url_range(
            sport="football", league="england-premier-league",
            fallback_start_year=2020, fallback_end_year=2022, discovered_leagues=discovered_leagues
        )

        assert len(urls_with_seasons) == 3
        seasons = [season for _, season in urls_with_seasons]
        assert "2020" in seasons
        assert "2021" in seasons
        assert "2022" in seasons

        # Check URL format
        for url, season_str in urls_with_seasons:
            assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{season_str}/results/"

    def test_get_all_available_seasons_different_sports(self, discovered_leagues):
        """Test generating URLs for different sports."""
        football_urls = URLBuilder.get_all_available_seasons_url_range(
            sport="football", league="england-premier-league",
            fallback_start_year=2021, fallback_end_year=2021, discovered_leagues=discovered_leagues
        )
        tennis_urls = URLBuilder.get_all_available_seasons_url_range(
            sport="tennis", league="atp-tour",
            fallback_start_year=2021, fallback_end_year=2021, discovered_leagues=discovered_leagues
        )

        assert len(football_urls) == 1
        assert len(tennis_urls) == 1

        # Check URLs are sport-specific
        football_url, football_season = football_urls[0]
        tennis_url, tennis_season = tennis_urls[0]

        assert football_url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2021/results/"
        assert tennis_url == f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour-2021/results/"


class TestDiscoverAvailableSeasons:
    """Test the discover_available_seasons method."""

    @pytest.mark.asyncio
    async def test_discover_seasons_success(self, discovered_leagues):
        """Test successful season discovery with mock page."""
        from unittest.mock import AsyncMock, MagicMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2020-2021 Season 2021-2022</html>')

        # Test with content-based discovery
        seasons = await URLBuilder.discover_available_seasons(
            "football", "england-premier-league", mock_page, discovered_leagues
        )

        # Should find seasons 2020, 2021, and 2022 in content
        # Content has "2020-2021", "2021-2022" which matches patterns that find 2020, 2021, 2022
        expected_seasons = [2020, 2021, 2022]
        assert seasons == expected_seasons

    @pytest.mark.asyncio
    async def test_discover_seasons_no_content(self, discovered_leagues):
        """Test season discovery when no seasons found - should raise error."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>No seasons here</html>')

        with pytest.raises(ValueError, match="No seasons discovered on league page"):
            await URLBuilder.discover_available_seasons(
                "football", "england-premier-league", mock_page, discovered_leagues
            )

    @pytest.mark.asyncio
    async def test_discover_seasons_exception_handling(self, discovered_leagues):
        """Test season discovery exception handling - should re-raise."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Navigation failed"))

        with pytest.raises(Exception, match="Navigation failed"):
            await URLBuilder.discover_available_seasons(
                "football", "england-premier-league", mock_page, discovered_leagues
            )

    @pytest.mark.asyncio
    async def test_discover_seasons_real_failure(self):
        """Test that real discovery failures raise errors appropriately."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>League page exists but has no season data</html>')

        # Create custom discovered leagues with problematic league
        custom_discovered_leagues = {
            "problematic-league": "https://www.oddsportal.com/football/problematic-league"
        }

        with pytest.raises(ValueError, match="No seasons discovered on league page"):
            await URLBuilder.discover_available_seasons(
                "football", "problematic-league", mock_page, custom_discovered_leagues
            )

    @pytest.mark.asyncio
    async def test_discover_seasons_africa_cup_optimization(self):
        """Test that Africa Cup of Nations style league gets exact seasons."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])

        # Create custom discovered leagues with Africa Cup of Nations
        custom_discovered_leagues = {
            "africa-cup-of-nations": "https://www.oddsportal.com/football/africa-cup-of-nations"
        }

        # Simulate actual Africa Cup of Nations content with correct years
        html_content = """
        <html>
            <body>
                <select name='season'>
                    <option value="2025">2025</option>
                    <option value="2023">2023</option>
                    <option value="2021">2021</option>
                    <option value="2019">2019</option>
                    <option value="2017">2017</option>
                    <option value="2015">2015</option>
                    <option value="2013">2013</option>
                    <option value="2012">2012</option>
                    <option value="2010">2010</option>
                    <option value="2008">2008</option>
                </select>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        seasons = await URLBuilder.discover_available_seasons(
            "football", "africa-cup-of-nations", mock_page, custom_discovered_leagues
        )

        # Should discover exact Africa Cup seasons with no gaps
        expected_seasons = [2008, 2010, 2012, 2013, 2015, 2017, 2019, 2021, 2023, 2025]
        assert seasons == expected_seasons

        # This is much more efficient than the old 1995-2027 range
        # Old system would try 1995-2027 = 33 years of failed requests
        # New system tries only the 10 actual years = 70% reduction in failed requests!
        # Zero wasted requests - only attempts years that actually exist

    def test_get_urls_for_specific_seasons(self, discovered_leagues):
        """Test the new get_urls_for_specific_seasons method."""
        seasons = [2021, 2023, 2025]

        urls_with_seasons = URLBuilder.get_urls_for_specific_seasons(
            sport="football",
            league="england-premier-league",
            seasons=seasons,
            discovered_leagues=discovered_leagues
        )

        assert len(urls_with_seasons) == 3

        # Check that each season has a corresponding URL
        seasons_found = [int(season) for _, season in urls_with_seasons]
        assert seasons_found == seasons

        # Check URL format
        for url, season_str in urls_with_seasons:
            expected_url = f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{season_str}/results/"
            assert url == expected_url
            assert season_str in ["2021", "2023", "2025"]


class TestHistoricMatchesUrlsForRangeEdgeCases:
    """Test edge cases for get_historic_matches_urls_for_range method."""

    def test_unlimited_past_with_to_date(self, discovered_leagues):
        """Test unlimited past (None from_date) with specific to_date - now obsolete functionality."""
        # This test is obsolete since we moved to exact seasons discovery
        # Unlimited past should now be handled by exact seasons discovery, not range-based generation
        with pytest.raises(ValueError, match="get_historic_matches_urls_for_range cannot be used with None start_year"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date=None, to_date="2022", league="england-premier-league", discovered_leagues=discovered_leagues
            )

    def test_unlimited_future_with_from_date(self, discovered_leagues):
        """Test when only from_date is specified (should mirror to from_date)."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="2020", to_date=None, league="england-premier-league", discovered_leagues=discovered_leagues
        )

        # When only from_date is specified, to_date should be set to from_date (single year)
        assert len(urls_with_seasons) == 1

        first_season = urls_with_seasons[0][1]
        assert first_season == "2020"
        assert urls_with_seasons[0][0] == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2020/results/"


class TestSportsParameterUpdates:
    """Test suite for sports parameter updates to ensure consistency with FEAT-001."""

    @pytest.mark.asyncio
    async def test_discover_available_seasons_sports_parameter(self, discovered_leagues):
        """Test that discover_available_seasons correctly uses sports parameter."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2020-2021 Season 2021-2022 Season 2022-2023</html>')

        # Test with various sports values
        test_sports = ["football", "tennis", "basketball", "aussie-rules"]

        for sport in test_sports:
            # Reset mocks
            mock_page.goto.reset_mock()
            mock_page.wait_for_timeout.reset_mock()

            # Call the method under test
            seasons = await URLBuilder.discover_available_seasons(
                sport, "test-league", mock_page, discovered_leagues
            )

            # Verify page.goto was called with correct URL containing sport
            mock_page.goto.assert_called_once()
            call_args = mock_page.goto.call_args[0][0]
            assert f"/{sport}/" in call_args

            # Should find seasons 2020, 2021, 2022, and 2023 in content
            expected_seasons = [2020, 2021, 2022, 2023]
            assert seasons == expected_seasons

    @pytest.mark.asyncio
    async def test_discover_available_seasons_logging_uses_sports_parameter(self):
        """Test that logging messages use the correct sports parameter."""
        from unittest.mock import AsyncMock, patch
        import logging

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2025 Season 2024</html>')

        # Mock the logger to capture log messages
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger

            # Call the method with aussie-rules sport
            await URLBuilder.discover_available_seasons(
                "aussie-rules", "afl", mock_page
            )

            # Verify that debug log messages contain the correct sport name
            debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
            assert any("aussie-rules/afl" in call for call in debug_calls)

            # Verify that info log messages contain the correct sport name
            info_calls = [str(call) for call in mock_logger.info.call_args_list]
            assert any("aussie-rules/afl" in call for call in info_calls)

    @pytest.mark.asyncio
    async def test_discover_available_seasons_error_handling_uses_sports_parameter(self):
        """Test that error handling uses the correct sports parameter in error messages."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>No seasons here</html>')

        # Test that error messages contain the correct sport name
        with pytest.raises(ValueError, match="No seasons discovered on league page for basketball/nba"):
            await URLBuilder.discover_available_seasons(
                "basketball", "nba", mock_page
            )

    @pytest.mark.asyncio
    async def test_discover_available_seasons_exception_propagation_uses_sports_parameter(self):
        """Test that exception propagation uses the correct sports parameter."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Navigation failed for tennis"))

        # Test that exceptions are properly raised and contain sport-specific context
        with pytest.raises(Exception, match="Navigation failed for tennis"):
            await URLBuilder.discover_available_seasons(
                "tennis", "atp-tour", mock_page
            )

        # Verify the method was called with correct sport
        mock_page.goto.assert_called_once()
        call_args = mock_page.goto.call_args[0][0]
        assert "/tennis/" in call_args

    @pytest.mark.asyncio
    async def test_discover_available_seasons_with_discovered_leagues_sports_parameter(self):
        """Test discover_available_seasons works with discovered leagues and sports parameter."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2019 Season 2020 Season 2021</html>')

        # Custom discovered leagues for aussie-rules sport
        custom_discovered_leagues = {
            "afl": "https://oddsportal.com/afl/australia/afl"
        }

        # Call the method with aussie-rules sport
        seasons = await URLBuilder.discover_available_seasons(
            "aussie-rules", "afl", mock_page, custom_discovered_leagues
        )

        # Verify the correct URL was constructed and called
        expected_url = "https://oddsportal.com/afl/australia/afl/results/"
        mock_page.goto.assert_called_once_with(expected_url, timeout=15000, wait_until="domcontentloaded")

        # Should find seasons 2019, 2020, and 2021
        expected_seasons = [2019, 2020, 2021]
        assert seasons == expected_seasons

    @pytest.mark.asyncio
    async def test_discover_available_seasons_complex_sport_names(self):
        """Test discover_available_seasons with complex sport names like aussie-rules."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2022 Season 2023 Season 2024</html>')

        # Test with complex sport name
        seasons = await URLBuilder.discover_available_seasons(
            "aussie-rules", "afl", mock_page
        )

        # Verify the correct URL was constructed with complex sport name
        mock_page.goto.assert_called_once()
        call_args = mock_page.goto.call_args[0][0]
        assert "/afl/" in call_args

        # Should find seasons 2022, 2023, and 2024
        expected_seasons = [2022, 2023, 2024]
        assert seasons == expected_seasons

    @pytest.mark.asyncio
    async def test_discover_available_seasons_url_construction_various_sports(self):
        """Test that URL construction works correctly for various sports."""
        from unittest.mock import AsyncMock

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.content = AsyncMock(return_value='<html>Season 2021</html>')

        # Test data: sport -> expected URL path
        test_cases = [
            ("football", "football/england/premier-league"),
            ("tennis", "tennis/atp-tour"),
            ("basketball", "basketball/usa/nba"),
            ("baseball", "baseball/usa/mlb"),
            ("aussie-rules", "aussie-rules/australia/afl"),
        ]

        for sport, expected_path in test_cases:
            # Reset mocks
            mock_page.goto.reset_mock()

            # Create test discovered leagues for this sport
            test_discovered_leagues = {
                "test-league": f"https://oddsportal.com/{expected_path}"
            }

            # Call the method
            await URLBuilder.discover_available_seasons(
                sport, "test-league", mock_page, test_discovered_leagues
            )

            # Verify correct URL was called
            expected_url = f"https://oddsportal.com/{expected_path}/results/"
            mock_page.goto.assert_called_once_with(expected_url, timeout=15000, wait_until="domcontentloaded")
