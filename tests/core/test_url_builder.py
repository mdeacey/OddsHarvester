import pytest
from datetime import datetime
from unittest.mock import patch

from src.core.url_builder import URLBuilder
from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.sport_league_constants import SPORTS_LEAGUES_URLS_MAPPING
from src.utils.sport_market_constants import Sport

# Create test mapping for sports and leagues (don't modify global)
TEST_SPORTS_LEAGUES_URLS_MAPPING = {
    Sport.FOOTBALL: {
        "england-premier-league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
        "la-liga": f"{ODDSPORTAL_BASE_URL}/football/spain/la-liga",
    },
    Sport.TENNIS: {
        "atp-tour": f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour",
    },
    Sport.BASEBALL: {
        "mlb": f"{ODDSPORTAL_BASE_URL}/baseball/usa/mlb",
        "japan-npb": f"{ODDSPORTAL_BASE_URL}/baseball/japan/npb",
    },
}


@pytest.fixture(autouse=True)
def mock_sport_league_urls_mapping():
    """Mock the SPORTS_LEAGUES_URLS_MAPPING to use test data."""
    with patch('src.core.url_builder.SPORTS_LEAGUES_URLS_MAPPING', TEST_SPORTS_LEAGUES_URLS_MAPPING):
        yield


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
def test_get_historic_matches_url(sport, league, season, expected_url):
    """Test building URLs for historical matches with various inputs."""
    assert URLBuilder.get_historic_matches_url(sport, league, season) == expected_url


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
def test_get_historic_matches_url_invalid_season_format(sport, league, season, error_msg):
    """Test invalid season formats."""
    with pytest.raises(ValueError, match=error_msg):
        URLBuilder.get_historic_matches_url(sport, league, season)


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
def test_get_historic_matches_url_invalid_season_range(sport, league, season, error_msg):
    """Test invalid season ranges."""
    with pytest.raises(ValueError, match=error_msg):
        URLBuilder.get_historic_matches_url(sport, league, season)


def test_get_historic_matches_url_invalid_sport():
    """Test error handling for invalid sports."""
    with pytest.raises(ValueError, match="'nonexistent_sport' is not a valid Sport"):
        URLBuilder.get_historic_matches_url("nonexistent_sport", "champions-league", "2023-2024")


def test_get_historic_matches_url_invalid_league():
    """Test error handling for invalid leagues."""
    with pytest.raises(
        ValueError,
        match="Invalid league 'random-league' for sport 'football'. Available: england-premier-league, la-liga",
    ):
        URLBuilder.get_historic_matches_url("football", "random-league", "2023-2024")


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
def test_get_upcoming_matches_url(sport, date, league, expected_url):
    """Test building URLs for upcoming matches with various inputs."""
    if date is None or date == "":
        # Don't test the exact URL since it depends on today's date
        result = URLBuilder.get_upcoming_matches_url(sport, date, league)
        assert result.startswith(f"{ODDSPORTAL_BASE_URL}/matches/")
    else:
        assert URLBuilder.get_upcoming_matches_url(sport, date, league) == expected_url


@pytest.mark.parametrize(
    ("sport", "league", "expected_url"),
    [
        ("football", "england-premier-league", f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"),
        ("tennis", "atp-tour", f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour"),
        ("baseball", "mlb", f"{ODDSPORTAL_BASE_URL}/baseball/usa/mlb"),
    ],
)
def test_get_league_url(sport, league, expected_url):
    """Test retrieving league URLs."""
    assert URLBuilder.get_league_url(sport, league) == expected_url


def test_get_league_url_invalid_sport():
    """Test get_league_url raises ValueError for unsupported sport."""
    with pytest.raises(ValueError, match="'nonexistent_sport' is not a valid Sport"):
        URLBuilder.get_league_url("nonexistent_sport", "champions-league")


def test_get_league_url_invalid_league():
    """Test get_league_url raises ValueError for unsupported league."""
    with pytest.raises(
        ValueError,
        match="Invalid league 'random-league' for sport 'football'. Available: england-premier-league, la-liga",
    ):
        URLBuilder.get_league_url("football", "random-league")


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

    def test_date_range_with_league(self):
        """Test generating URLs for date range with specific league."""
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(
            sport="football", from_date="20250101", to_date="20250102", league="england-premier-league"
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

    def test_single_season_range(self):
        """Test generating URLs for a single season."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="2023", to_date="2023", league="england-premier-league"
        )
        assert len(urls_with_seasons) == 1
        url, season_str = urls_with_seasons[0]
        assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-2023/results/"
        assert season_str == "2023"

    def test_multi_season_range(self):
        """Test generating URLs for multiple seasons."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="2021", to_date="2023", league="england-premier-league"
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

    def test_season_range_with_hyphenated_seasons(self):
        """Test generating URLs with hyphenated season format."""
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="tennis", from_date="2022-2023", to_date="2023-2024", league="atp-tour"
        )
        assert len(urls_with_seasons) == 2

        # Should generate for 2023 and 2024 (end years of the seasons)
        seasons = [season for _, season in urls_with_seasons]
        assert "2023" in seasons
        assert "2024" in seasons

    def test_now_keyword_historic(self):
        """Test generating URLs with 'now' keyword for historic matches."""
        current_year = datetime.now().year
        urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(
            sport="football", from_date="now", to_date="now", league="england-premier-league"
        )
        assert len(urls_with_seasons) == 1
        url, season_str = urls_with_seasons[0]
        assert url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league-{current_year}/results/"
        assert season_str == str(current_year)

    def test_invalid_season_format(self):
        """Test error handling for invalid season format."""
        with pytest.raises(ValueError, match="Invalid season format: 'invalid'"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="invalid", to_date="2023", league="england-premier-league"
            )

    def test_end_season_before_start_season(self):
        """Test error handling when end season is before start season."""
        with pytest.raises(ValueError, match="End season/year cannot be before start season/year"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="2025", to_date="2020", league="england-premier-league"
            )

    def test_invalid_season_range_format(self):
        """Test error handling for invalid season range (more than 1 year apart)."""
        with pytest.raises(ValueError, match="Invalid season range"):
            URLBuilder.get_historic_matches_urls_for_range(
                sport="football", from_date="2022-2024", to_date="2024-2025", league="england-premier-league"
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
