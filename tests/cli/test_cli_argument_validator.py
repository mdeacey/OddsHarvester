from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from src.cli.cli_argument_validator import CLIArgumentValidator
from src.utils.sport_market_constants import Sport


@pytest.fixture
def validator():
    return CLIArgumentValidator()


@pytest.fixture
def mock_args():
    return MagicMock(
        command="scrape_upcoming",
        sport="football",
        leagues=["england-premier-league"],
        from_date=(datetime.now() + timedelta(days=1)).strftime("%Y%m%d"),  # Corrected format (YYYYMMDD)
        to_date=None,
        storage="local",
        format="json",
        file_path="data.json",
        headless=True,
        markets=["1x2", "btts"],
        proxies=None,
        browser_user_agent=None,
        browser_locale_timezone=None,
        browser_timezone_id=None,
        match_links=None,
        scrape_odds_history=False,
        target_bookmaker=None,
        odds_format="Decimal Odds",
        concurrency_tasks=3,
        max_pages=None,  # Add max_pages to avoid mock issues
    )


def test_validate_args_valid(validator, mock_args):
    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError: {e}")


def test_validate_command_invalid(validator, mock_args):
    mock_args.command = "invalid_command"
    with pytest.raises(
        ValueError, match="Invalid command 'invalid_command'. Supported commands are: scrape_upcoming, scrape_historic."
    ):
        validator.validate_args(mock_args)


@pytest.mark.parametrize("invalid_sport", ["invalid_sport", "invalid_sport_name", 123, None])
def test_validate_sport_invalid(invalid_sport):
    validator = CLIArgumentValidator()

    with pytest.raises(ValueError) as exc_info:
        validator._validate_sport(sport=invalid_sport)

    expected_sports = ", ".join(s.value for s in Sport)
    if isinstance(invalid_sport, str):
        assert f"Invalid sport: '{invalid_sport}'. Supported sports are: {expected_sports}." in str(exc_info.value)
    else:
        assert f"Invalid sport: {invalid_sport}. Expected one of {[s.value for s in Sport]}." in str(exc_info.value)


def test_validate_sport_valid():
    validator = CLIArgumentValidator()
    valid_sports = [s.value for s in Sport]

    for sport in valid_sports:
        errors = validator._validate_sport(sport=sport)
        assert not errors, f"Validation failed for valid sport: {sport}"


def test_validate_markets_invalid(validator, mock_args):
    mock_args.markets = ["invalid_market"]
    with pytest.raises(ValueError, match="Invalid market: invalid_market. Supported markets for football: "):
        validator.validate_args(mock_args)


def test_validate_league_invalid(validator, mock_args):
    mock_args.leagues = ["invalid_league"]
    with pytest.raises(ValueError, match="Invalid league: 'invalid_league' for sport 'football'."):
        validator.validate_args(mock_args)


def test_validate_date_range_invalid_format(validator, mock_args):
    mock_args.from_date = "25-02-2025"
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = None

    with pytest.raises(
        ValueError, match="Invalid date format: '25-02-2025'. Supported formats: YYYYMMDD, YYYYMM, YYYY, or 'now'"
    ):
        validator.validate_args(mock_args)


def test_validate_date_range_past_date_upcoming(validator, mock_args):
    """Test that past dates are still rejected for upcoming matches when leagues are not provided."""
    mock_args.command = "scrape_upcoming"
    mock_args.from_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = None

    with pytest.raises(ValueError, match="--from date must be today or in the future for upcoming matches."):
        validator.validate_args(mock_args)


def test_validate_date_range_past_date_with_leagues(validator, mock_args):
    """Test that past dates are allowed when leagues are provided (date validation is bypassed)."""
    mock_args.command = "scrape_upcoming"
    mock_args.from_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = ["england-premier-league"]  # When leagues are provided, date validation is bypassed

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError when leagues are provided: {e}")


def test_validate_date_range_to_before_from(validator, mock_args):
    future_date = datetime.now() + timedelta(days=7)
    past_date = datetime.now() + timedelta(days=1)
    mock_args.from_date = future_date.strftime("%Y%m%d")
    mock_args.to_date = past_date.strftime("%Y%m%d")
    mock_args.match_links = None
    mock_args.leagues = None

    with pytest.raises(ValueError, match="--to date cannot be before --from date."):
        validator.validate_args(mock_args)


def test_validate_date_range_large_range(validator, mock_args):
    """Test that large date ranges are now allowed."""
    start_date = datetime.now() + timedelta(days=1)
    end_date = datetime.now() + timedelta(days=365)  # 1 year range - should be allowed now
    mock_args.from_date = start_date.strftime("%Y%m%d")
    mock_args.to_date = end_date.strftime("%Y%m%d")
    mock_args.match_links = None
    mock_args.leagues = None

    # Should not raise any exception now that limits are removed
    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError: {e}")


def test_validate_storage_invalid(validator, mock_args):
    mock_args.storage = "invalid_storage"
    with pytest.raises(ValueError, match="Invalid storage type: 'invalid_storage'. Supported storage types are: "):
        validator.validate_args(mock_args)


def test_validate_file_path_invalid_extension(validator, mock_args):
    mock_args.file_path = "data.invalid"
    with pytest.raises(ValueError, match="Mismatch between file format 'json' and file path extension 'invalid'."):
        validator.validate_args(mock_args)


def test_validate_file_format_mismatch(validator, mock_args):
    mock_args.file_path = "data.json"
    mock_args.format = "csv"
    with pytest.raises(ValueError, match="Mismatch between file format 'csv' and file path extension 'json'."):
        validator.validate_args(mock_args)


def test_validate_markets_rugby_union():
    validator = CLIArgumentValidator()

    # Test valid markets
    valid_markets = ["1x2", "home_away", "over_under_43_5", "handicap_-13_5"]
    errors = validator._validate_markets(sport=Sport.RUGBY_UNION, markets=valid_markets)
    assert not errors, "Validation failed for valid Rugby Union markets"

    # Test invalid markets
    invalid_markets = ["invalid_market", "btts"]
    errors = validator._validate_markets(sport=Sport.RUGBY_UNION, markets=invalid_markets)
    assert len(errors) == 2, "Validation should fail for invalid Rugby Union markets"


def test_validate_league_rugby_union():
    validator = CLIArgumentValidator()

    # Test valid leagues (single league)
    valid_leagues = ["six-nations", "france-top-14", "world-cup"]
    for league in valid_leagues:
        errors = validator._validate_leagues(sport=Sport.RUGBY_UNION, leagues=[league])
        assert not errors, f"Validation failed for valid Rugby Union league: {league}"

    # Test multiple valid leagues
    errors = validator._validate_leagues(sport=Sport.RUGBY_UNION, leagues=valid_leagues)
    assert not errors, "Validation should succeed for multiple valid Rugby Union leagues"

    # Test invalid league
    errors = validator._validate_leagues(sport=Sport.RUGBY_UNION, leagues=["invalid-league"])
    assert len(errors) == 1, "Validation should fail for invalid Rugby Union league"
    assert "Invalid league: 'invalid-league' for sport 'rugby-union'" in errors[0]

    # Test mixed valid and invalid leagues
    mixed_leagues = ["six-nations", "invalid-league", "france-top-14"]
    errors = validator._validate_leagues(sport=Sport.RUGBY_UNION, leagues=mixed_leagues)
    assert len(errors) == 1, "Validation should fail for invalid league in mixed list"
    assert "Invalid league: 'invalid-league' for sport 'rugby-union'" in errors[0]


def test_validate_empty_leagues_list():
    validator = CLIArgumentValidator()

    # Empty list should be treated as None
    errors = validator._validate_leagues(sport=Sport.FOOTBALL, leagues=[])
    assert not errors, "Empty leagues list should not cause validation errors"

    # None should also not cause errors
    errors = validator._validate_leagues(sport=Sport.FOOTBALL, leagues=None)
    assert not errors, "None leagues should not cause validation errors"


@pytest.mark.parametrize(
    ("command", "from_date", "to_date", "expected_errors"),
    [
        # Historic matches
        ("scrape_historic", "2023-2024", "2024-2025", []),  # Valid format YYYY-YYYY range
        ("scrape_historic", "2023", "2023", []),  # Valid format YYYY single year
        ("scrape_historic", "2023", None, []),  # Valid format YYYY without to_date
        ("scrape_historic", "now", None, []),  # Valid "now" keyword
        ("scrape_historic", None, "2023", []),  # Valid only to_date
        ("scrape_historic", None, None, []),  # Valid - defaults to now and unlimited past
        (
            "scrape_historic",
            "invalid",
            None,
            ["Invalid season format: 'invalid'. Expected format: YYYY, YYYY-YYYY, or 'now' (e.g., 2023, 2022-2023, now)."],
        ),  # Invalid format
        # Upcoming matches
        ("scrape_upcoming", (datetime.now() + timedelta(days=1)).strftime("%Y%m%d"), (datetime.now() + timedelta(days=2)).strftime("%Y%m%d"), []),  # Valid range
        ("scrape_upcoming", "now", None, []),  # Valid "now" keyword for upcoming
        ("scrape_upcoming", None, "now", []),  # Valid only to_date with now
        ("scrape_upcoming", None, None, []),  # Valid - defaults to now and unlimited future
        ("scrape_upcoming", (datetime.now() + timedelta(days=1)).strftime("%Y%m%d"), None, []),  # Valid single date
    ],
)
def test_validate_date_range(validator, command, from_date, to_date, expected_errors):
    errors = validator._validate_date_range(
        command=command, from_date=from_date, to_date=to_date, match_links=None, leagues=None
    )
    assert errors == expected_errors


def test_validate_date_range_with_match_links(validator):
    errors = validator._validate_date_range(
        command="scrape_upcoming", from_date=None, to_date=None,
        match_links=["https://www.oddsportal.com/match/123456"], leagues=None
    )
    assert not errors, "Validation should succeed when match_links is provided, even without from_date"


def test_validate_date_range_with_leagues(validator):
    errors = validator._validate_date_range(
        command="scrape_upcoming", from_date=None, to_date=None,
        match_links=None, leagues=["england-premier-league"]
    )
    assert not errors, "Validation should succeed when leagues are provided, even without from_date"

    errors = validator._validate_date_range(
        command="scrape_upcoming", from_date=None, to_date=None,
        match_links=None, leagues=["england-premier-league", "spain-la-liga"]
    )
    assert not errors, "Validation should succeed when multiple leagues are provided, even without from_date"


def test_validate_date_range_wrong_command(validator):
    """Test date range validation for a command other than scrape_upcoming/scrape_historic."""
    errors = validator._validate_date_range(
        command="invalid_command", from_date="20250101", to_date=None, match_links=None, leagues=None
    )
    assert len(errors) == 1
    assert "Date ranges should not be provided for the 'invalid_command' command." in errors[0]


def test_validate_historic_season_range_large_range(validator):
    """Test that large season ranges are now allowed."""
    errors = validator._validate_date_range(
        command="scrape_historic", from_date="1900", to_date="2025", match_links=None, leagues=None
    )
    # Should not have any errors now that limits are removed
    assert len(errors) == 0


def test_validate_historic_season_date_swapping(validator):
    """Test that historical dates are automatically swapped when in wrong order."""
    errors = validator._validate_date_range(
        command="scrape_historic", from_date="now", to_date="2023", match_links=None, leagues=None
    )
    # Should not have any errors - dates should be automatically swapped
    assert len(errors) == 0


def test_validate_historic_season_to_before_from(validator):
    """Test that historical dates are automatically swapped when in wrong order."""
    errors = validator._validate_date_range(
        command="scrape_historic", from_date="2025", to_date="2020", match_links=None, leagues=None
    )
    # Should not have any errors now - dates should be automatically swapped
    assert len(errors) == 0


def test_parse_season_format_validation(validator):
    """Test the _parse_season helper function."""
    # Test valid season formats
    result = validator._parse_season("2023")
    assert result == ("2023", 2023)

    result = validator._parse_season("2022-2023")
    assert result == ("2022-2023", 2023)

    result = validator._parse_season("now")
    season_format, end_year = result
    assert season_format == str(datetime.now().year)
    assert end_year == datetime.now().year

    # Test invalid season format
    with pytest.raises(ValueError, match="Invalid season format: 'invalid'"):
        validator._parse_season("invalid")

    # Test invalid season range
    with pytest.raises(ValueError, match="Invalid season range: '2022-2024'"):
        validator._parse_season("2022-2024")


@pytest.mark.parametrize(
    ("proxies", "expected_errors"),
    [
        (None, []),
        ([], []),
        (["http://proxy.com:8080 user pass"], []),
        (["socks5://proxy.com:1080"], []),
        (
            ["invalid_proxy_format"],
            [
                "Invalid proxy format: 'invalid_proxy_format'. Expected format: "
                "'http[s]://host:port [user pass]' or 'socks5://host:port [user pass]'."
            ],
        ),
        (
            ["http://proxy.com:8080", "invalid_proxy"],
            [
                "Invalid proxy format: 'invalid_proxy'. Expected format: "
                "'http[s]://host:port [user pass]' or 'socks5://host:port [user pass]'."
            ],
        ),
    ],
)
def test_validate_proxies(validator, proxies, expected_errors):
    """Test validation of proxy settings."""
    errors = validator._validate_proxies(proxies=proxies)
    assert errors == expected_errors


@pytest.mark.parametrize(
    ("user_agent", "locale_timezone", "timezone_id", "expected_errors"),
    [
        ("Mozilla/5.0", "fr-FR", "Europe/Paris", []),
        (None, None, None, []),
        (123, "fr-FR", "Europe/Paris", ["Invalid browser user agent format."]),
        ("Mozilla/5.0", 123, "Europe/Paris", ["Invalid browser locale timezone format."]),
        ("Mozilla/5.0", "fr-FR", 123, ["Invalid browser timezone ID format."]),
        (
            123,
            456,
            789,
            [
                "Invalid browser user agent format.",
                "Invalid browser locale timezone format.",
                "Invalid browser timezone ID format.",
            ],
        ),
    ],
)
def test_validate_browser_settings(validator, user_agent, locale_timezone, timezone_id, expected_errors):
    errors = validator._validate_browser_settings(
        user_agent=user_agent, locale_timezone=locale_timezone, timezone_id=timezone_id
    )
    assert errors == expected_errors


@pytest.mark.parametrize(
    ("match_links", "sport", "expected_errors"),
    [
        (None, "football", []),
        ([], "football", []),
        (["https://www.oddsportal.com/football/match/123456"], "football", []),
        (
            ["https://www.oddsportal.com/football/match/123456"],
            None,
            ["The '--sport' argument is required when using '--match_links'."],
        ),
        (["invalid_url_format"], "football", ["Invalid match link format: invalid_url_format"]),
    ],
)
def test_validate_match_links(validator, match_links, sport, expected_errors):
    errors = validator._validate_match_links(match_links=match_links, sport=sport)
    assert errors == expected_errors


@pytest.mark.parametrize(
    ("command", "max_pages", "expected_errors"),
    [
        ("scrape_historic", 5, []),
        ("scrape_historic", 1, []),
        ("scrape_historic", None, []),
        ("scrape_historic", 0, ["Invalid max-pages value: '0'. It must be a positive integer."]),
        (
            "scrape_historic",
            -1,
            ["Invalid max-pages value: '-1'. It must be a positive integer."],
        ),
        (
            "scrape_historic",
            "5",
            ["Invalid max-pages value: '5'. It must be a positive integer."],
        ),
        ("scrape_upcoming", 5, []),
    ],
)
def test_validate_max_pages(validator, command, max_pages, expected_errors):
    errors = validator._validate_max_pages(command=command, max_pages=max_pages)
    assert errors == expected_errors


def test_validate_file_args_no_extension(validator):
    args = MagicMock(file_path="data_file", format=None)
    errors = validator._validate_file_args(args=args)
    assert len(errors) == 1
    assert "File path 'data_file' must include a valid file extension" in errors[0]


def test_validate_file_args_format_only(validator):
    args = MagicMock(file_path=None, format="json")
    errors = validator._validate_file_args(args=args)
    assert not errors


def test_validate_args_with_match_links(validator, mock_args):
    mock_args.match_links = ["https://www.oddsportal.com/football/match/123456"]
    mock_args.sport = "football"
    mock_args.from_date = None
    mock_args.to_date = None

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError: {e}")


def test_validate_target_bookmaker(validator, mock_args):
    mock_args.target_bookmaker = "Bookmaker1"
    validator.validate_args(mock_args)

    mock_args.target_bookmaker = 123
    with pytest.raises(ValueError, match="Target bookmaker must be a string if specified."):
        validator.validate_args(mock_args)




@pytest.mark.parametrize(
    ("odds_format", "expected_errors"),
    [
        ("Decimal Odds", []),
        ("Fractional Odds", []),
        ("Money Line Odds", []),
        ("Hong Kong Odds", []),
        (
            "Invalid Format",
            [
                "Invalid odds format: 'Invalid Format'. Supported formats are: "
                "Decimal Odds, Fractional Odds, Money Line Odds, Hong Kong Odds."
            ],
        ),
    ],
)
def test_validate_odds_format(validator, odds_format, expected_errors):
    """Test validation of odds format parameter."""
    errors = validator._validate_odds_format(odds_format=odds_format)
    assert errors == expected_errors


@pytest.mark.parametrize(
    ("concurrency_tasks", "expected_errors"),
    [
        (1, []),
        (3, []),
        (10, []),
        (0, ["Invalid concurrency tasks value: '0'. It must be a positive integer."]),
        (-1, ["Invalid concurrency tasks value: '-1'. It must be a positive integer."]),
        ("3", ["Invalid concurrency tasks value: '3'. It must be a positive integer."]),
    ],
)
def test_validate_concurrency_tasks(validator, concurrency_tasks, expected_errors):
    errors = validator._validate_concurrency_tasks(concurrency_tasks=concurrency_tasks)
    assert errors == expected_errors


def test_validate_args_with_new_arguments(validator, mock_args):
    mock_args.odds_format = "Fractional Odds"
    mock_args.concurrency_tasks = 5

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError: {e}")

    mock_args.odds_format = "Invalid Format"
    with pytest.raises(
        ValueError,
        match="Invalid odds format: 'Invalid Format'. Supported formats are: "
        "Decimal Odds, Fractional Odds, Money Line Odds, Hong Kong Odds.",
    ):
        validator.validate_args(mock_args)

    mock_args.odds_format = "Decimal Odds"
    mock_args.concurrency_tasks = 0
    with pytest.raises(ValueError, match="Invalid concurrency tasks value: '0'. It must be a positive integer."):
        validator.validate_args(mock_args)


def test_validate_now_keyword_upcoming(validator, mock_args):
    """Test validation with 'now' keyword for upcoming matches."""
    mock_args.command = "scrape_upcoming"
    mock_args.from_date = "now"
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = None

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError with 'now' keyword: {e}")


def test_validate_now_keyword_historic(validator, mock_args):
    """Test validation with 'now' keyword for historic matches."""
    mock_args.command = "scrape_historic"
    mock_args.from_date = "now"
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = ["england-premier-league"]

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError with 'now' keyword: {e}")


def test_validate_only_to_date_now(validator, mock_args):
    """Test validation with only --to date set to 'now'."""
    mock_args.command = "scrape_upcoming"
    mock_args.from_date = None
    mock_args.to_date = "now"
    mock_args.match_links = None
    mock_args.leagues = None

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError with only --to=now: {e}")


def test_validate_date_range_with_unlimited_future(validator, mock_args):
    """Test validation with from_date but no to_date (unlimited future)."""
    mock_args.command = "scrape_upcoming"
    future_date = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    mock_args.from_date = future_date
    mock_args.to_date = None
    mock_args.match_links = None
    mock_args.leagues = None

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError with unlimited future: {e}")


def test_validate_date_range_with_unlimited_past(validator, mock_args):
    """Test validation with only to_date for historic (unlimited past)."""
    mock_args.command = "scrape_historic"
    mock_args.from_date = None
    mock_args.to_date = "2023"
    mock_args.match_links = None
    mock_args.leagues = ["england-premier-league"]

    try:
        validator.validate_args(mock_args)
    except ValueError as e:
        pytest.fail(f"Unexpected ValueError with unlimited past: {e}")
