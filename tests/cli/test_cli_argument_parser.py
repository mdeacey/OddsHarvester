import pytest

from src.cli.cli_argument_parser import CLIArgumentParser


@pytest.fixture
def parser():
    return CLIArgumentParser().get_parser()


def test_parser_has_subparsers(parser):
    assert parser._subparsers is not None
    assert "scrape_upcoming" in parser._subparsers._group_actions[0].choices
    assert "scrape_historic" in parser._subparsers._group_actions[0].choices


def test_parse_scrape_upcoming(parser):
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "20250225",
            "--to",
            "20250227",
            "--leagues",
            "premier-league",
            "--markets",
            "1x2,btts",
            "--storage",
            "local",
            "--format",
            "json",
            "--file_path",
            "output.json",
            "--headless",
            "--save_logs",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.sport == "football"
    assert args.from_date == "20250225"
    assert args.to_date == "20250227"
    assert args.leagues == ["premier-league"]
    assert args.markets == ["1x2", "btts"]
    assert args.storage == "local"
    assert args.format == "json"
    assert args.file_path == "output.json"
    assert args.headless is True
    assert args.save_logs is True


def test_parse_scrape_historic(parser):
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "tennis",
            "--from",
            "2023-2024",
            "--to",
            "2024-2025",
            "--leagues",
            "atp-tour",
            "--markets",
            "match_winner,over_under",
            "--storage",
            "local",
            "--format",
            "csv",
            "--file_path",
            "historical.csv",
            "--headless",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.sport == "tennis"
    assert args.from_date == "2023-2024"
    assert args.to_date == "2024-2025"
    assert args.leagues == ["atp-tour"]
    assert args.markets == ["match_winner", "over_under"]
    assert args.storage == "local"
    assert args.format == "csv"
    assert args.file_path == "historical.csv"
    assert args.headless is True


def test_parser_defaults():
    """Test that the parser sets correct default values."""
    parser = CLIArgumentParser()
    args = parser.parse_args(["scrape_upcoming"])

    assert args.command == "scrape_upcoming"
    assert args.sport is None  # Changed from 'football' to None since we want explicit sport selection
    assert args.leagues is None
    assert args.markets is None
    assert args.storage == "local"
    assert args.file_path is None
    assert args.format == "json"
    assert args.proxies is None
    assert args.browser_user_agent is None
    assert args.browser_locale_timezone is None
    assert args.browser_timezone_id is None
    assert args.headless is False
    assert args.save_logs is False
    assert args.target_bookmaker is None
    assert args.scrape_odds_history is False
    assert args.odds_format == "Decimal Odds"
    assert args.concurrency_tasks == 3
    assert hasattr(args, 'from_date') and args.from_date is None
    assert hasattr(args, 'to_date') and args.to_date is None
    assert args.all is False


def test_parse_scrape_upcoming_with_all_flag(parser):
    """Test parsing scrape_upcoming command with --all flag."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--all",
            "--from",
            "20250225",
            "--to",
            "20250227",
            "--markets",
            "1x2,btts",
            "--storage",
            "local",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.all is True
    assert args.from_date == "20250225"
    assert args.to_date == "20250227"
    assert args.markets == ["1x2", "btts"]
    assert args.storage == "local"


def test_parse_scrape_upcoming_all_without_from_date(parser):
    """Test parsing scrape_upcoming with --all flag but no --from (should default to None)."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--all",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.all is True
    assert hasattr(args, 'from_date') and args.from_date is None
    assert hasattr(args, 'to_date') and args.to_date is None
    assert args.markets == ["1x2"]


def test_parse_scrape_historic_with_all_flag(parser):
    """Test parsing scrape_historic command with --all flag."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--all",
            "--from",
            "2023-2024",
            "--to",
            "2024-2025",
            "--markets",
            "1x2,btts",
            "--storage",
            "remote",
            "--headless",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.all is True
    assert args.from_date == "2023-2024"
    assert args.to_date == "2024-2025"
    assert args.markets == ["1x2", "btts"]
    assert args.storage == "remote"
    assert args.headless is True


def test_invalid_sport(parser):
    with pytest.raises(SystemExit):  # argparse raises SystemExit on invalid args
        parser.parse_args(["scrape_upcoming", "--sport", "invalid_sport", "--from", "20250225"])


def test_missing_from_date_for_historic(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_historic"])


def test_invalid_storage(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_upcoming", "--from", "20250225", "--storage", "invalid_storage"])


def test_invalid_format(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_upcoming", "--from", "20250225", "--format", "invalid_format"])


def test_parse_multiple_leagues(parser):
    """Test parsing multiple leagues separated by commas."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "football",
            "--from",
            "2023-2024",
            "--to",
            "2024-2025",
            "--leagues",
            "england-premier-league,spain-primera-division,italy-serie-a",
            "--markets",
            "1x2,btts",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.sport == "football"
    assert args.from_date == "2023-2024"
    assert args.to_date == "2024-2025"
    assert args.leagues == ["england-premier-league", "spain-primera-division", "italy-serie-a"]
    assert args.markets == ["1x2", "btts"]


def test_parse_single_league_as_list(parser):
    """Test that single league is parsed as a list for consistency."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "tennis",
            "--from",
            "20250225",
            "--leagues",
            "french-open",
            "--markets",
            "match_winner",
        ]
    )
    assert args.leagues == ["french-open"]


def test_parse_leagues_with_spaces(parser):
    """Test parsing leagues with spaces around commas."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "football",
            "--from",
            "2023",
            "--to",
            "2024",
            "--leagues",
            "england-premier-league, spain-primera-division, italy-serie-a",
            "--markets",
            "1x2",
        ]
    )
    # Note: Spaces will be handled by the validator, not the parser
    assert args.leagues == ["england-premier-league", " spain-primera-division", " italy-serie-a"]


def test_parse_odds_format(parser):
    """Test parsing odds format argument."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "20250225",
            "--odds_format",
            "Fractional Odds",
        ]
    )
    assert args.odds_format == "Fractional Odds"


def test_parse_concurrency_tasks(parser):
    """Test parsing concurrency tasks argument."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "20250225",
            "--concurrency_tasks",
            "5",
        ]
    )
    assert args.concurrency_tasks == 5


def test_invalid_odds_format(parser):
    """Test that invalid odds format raises SystemExit."""
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "scrape_upcoming",
                "--sport",
                "football",
                "--from",
                "20250225",
                "--odds_format",
                "Invalid Format",
            ]
        )


def test_invalid_concurrency_tasks(parser):
    """Test that invalid concurrency tasks raises SystemExit."""
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "scrape_upcoming",
                "--sport",
                "football",
                "--from",
                "20250225",
                "--concurrency_tasks",
                "invalid",
            ]
        )


# New tests for the new --from/--to functionality
def test_parse_single_date(parser):
    """Test parsing single date using only --from."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "20250101",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.from_date == "20250101"
    assert args.to_date is None
    assert args.markets == ["1x2"]


def test_parse_date_range(parser):
    """Test parsing date range using --from and --to."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "20250101",
            "--to",
            "20250107",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.from_date == "20250101"
    assert args.to_date == "20250107"
    assert args.markets == ["1x2"]


def test_parse_single_season(parser):
    """Test parsing single season using only --from."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "football",
            "--from",
            "2023",
            "--leagues",
            "premier-league",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.from_date == "2023"
    assert args.to_date is None
    assert args.leagues == ["premier-league"]


def test_parse_season_range(parser):
    """Test parsing season range using --from and --to."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "football",
            "--from",
            "2021",
            "--to",
            "2023",
            "--leagues",
            "premier-league",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.from_date == "2021"
    assert args.to_date == "2023"
    assert args.leagues == ["premier-league"]


def test_parse_now_keyword(parser):
    """Test parsing 'now' keyword."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "football",
            "--from",
            "now",
            "--markets",
            "1x2",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.from_date == "now"
    assert args.to_date is None
