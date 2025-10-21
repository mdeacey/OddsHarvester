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
            "--date",
            "20250225",
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
    assert args.date == "20250225"
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
            "--season",
            "2023-2024",
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
    assert args.season == "2023-2024"
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
    assert args.date is None
    assert args.all is False


def test_parse_scrape_upcoming_with_all_flag(parser):
    """Test parsing scrape_upcoming command with --all flag."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--all",
            "--date",
            "20250225",
            "--markets",
            "1x2,btts",
            "--storage",
            "local",
        ]
    )
    assert args.command == "scrape_upcoming"
    assert args.all is True
    assert args.date == "20250225"
    assert args.markets == ["1x2", "btts"]
    assert args.storage == "local"


def test_parse_scrape_upcoming_all_without_date(parser):
    """Test parsing scrape_upcoming with --all flag but no date (should default to None)."""
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
    assert args.date is None
    assert args.markets == ["1x2"]


def test_parse_scrape_historic_with_all_flag(parser):
    """Test parsing scrape_historic command with --all flag."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--all",
            "--season",
            "2023-2024",
            "--markets",
            "1x2,btts",
            "--storage",
            "remote",
            "--headless",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.all is True
    assert args.season == "2023-2024"
    assert args.markets == ["1x2", "btts"]
    assert args.storage == "remote"
    assert args.headless is True


def test_invalid_sport(parser):
    with pytest.raises(SystemExit):  # argparse raises SystemExit on invalid args
        parser.parse_args(["scrape_upcoming", "--sport", "invalid_sport", "--date", "20250225"])


def test_missing_season(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_historic"])


def test_invalid_storage(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_upcoming", "--date", "20250225", "--storage", "invalid_storage"])


def test_invalid_format(parser):
    with pytest.raises(SystemExit):
        parser.parse_args(["scrape_upcoming", "--date", "20250225", "--format", "invalid_format"])


def test_parse_multiple_leagues(parser):
    """Test parsing multiple leagues separated by commas."""
    args = parser.parse_args(
        [
            "scrape_historic",
            "--sport",
            "football",
            "--season",
            "2023-2024",
            "--leagues",
            "england-premier-league,spain-primera-division,italy-serie-a",
            "--markets",
            "1x2,btts",
        ]
    )
    assert args.command == "scrape_historic"
    assert args.sport == "football"
    assert args.season == "2023-2024"
    assert args.leagues == ["england-premier-league", "spain-primera-division", "italy-serie-a"]
    assert args.markets == ["1x2", "btts"]


def test_parse_single_league_as_list(parser):
    """Test that single league is parsed as a list for consistency."""
    args = parser.parse_args(
        [
            "scrape_upcoming",
            "--sport",
            "tennis",
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
            "--season",
            "2023",
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
            "--date",
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
            "--date",
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
                "--date",
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
                "--date",
                "20250225",
                "--concurrency_tasks",
                "invalid",
            ]
        )
