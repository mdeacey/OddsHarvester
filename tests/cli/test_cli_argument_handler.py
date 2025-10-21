from unittest.mock import MagicMock, patch

import pytest

from src.cli.cli_argument_handler import CLIArgumentHandler


@pytest.fixture
def cli_handler():
    return CLIArgumentHandler()


def test_parse_and_validate_args_valid(cli_handler):
    mock_args = [
        "scrape",
        "--sport",
        "football",
        "--date",
        "2024-02-25",
        "--leagues",
        "england-premier-league",
        "--storage",
        "local",
        "--format",
        "json",
        "--headless",
        "--markets",
        "1x2",
        "btts",
        "--browser-user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0 Safari/537.36",
        "--browser-locale-timezone",
        "fr-BE",
        "--browser-timezone-id",
        "Europe/Brussels",
    ]

    with (
        patch("sys.argv", ["cli_tool.py", *mock_args]),
        patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
        patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
    ):
        mock_parse_args.return_value = MagicMock(
            command="scrape",
            sport="football",
            date="2024-02-25",
            leagues=["england-premier-league"],
            storage="local",
            format="json",
            headless=True,
            markets=["1x2", "btts"],
            season=None,
            file_path=None,
            max_pages=None,
            proxies=None,
            browser_user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0 Safari/537.36",
            browser_locale_timezone="fr-BE",
            browser_timezone_id="Europe/Brussels",
            match_links=None,
            scrape_odds_history=False,
            target_bookmaker=None,
            preview_submarkets_only=False,
            all=False,
        )

        parsed_args = cli_handler.parse_and_validate_args()

        assert parsed_args == {
            "command": "scrape",
            "sport": "football",
            "date": "2024-02-25",
            "leagues": ["england-premier-league"],
            "season": None,
            "storage_type": "local",
            "storage_format": "json",
            "file_path": None,
            "headless": True,
            "markets": ["1x2", "btts"],
            "max_pages": None,
            "proxies": None,
            "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0 Safari/537.36",
            "browser_locale_timezone": "fr-BE",
            "browser_timezone_id": "Europe/Brussels",
            "match_links": None,
            "scrape_odds_history": False,
            "target_bookmaker": None,
            "preview_submarkets_only": False,
            "all": False,
        }

        mock_validate_args.assert_called_once_with(mock_parse_args.return_value)


def test_parse_and_validate_args_missing_command(cli_handler):
    with (
        patch("sys.argv", ["cli_tool.py"]),
        patch.object(cli_handler.parser, "print_help") as mock_print_help,
        patch("builtins.exit"),
        patch("builtins.print"),
        patch.object(
            cli_handler.parser,
            "parse_args",
            return_value=MagicMock(
                command=None,  # Simulate missing command
                sport=None,
                date=None,
                leagues=None,
                season=None,
                storage="local",
                format=None,
                file_path=None,
                headless=False,
                markets=None,
            ),
        ),
    ):
        cli_handler.parse_and_validate_args()

        mock_print_help.assert_called()


def test_parse_and_validate_args_invalid_args(cli_handler):
    with (
        patch("sys.argv", ["cli_tool.py", "scrape", "--sport", "invalid-sport"]),
        patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
        patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        patch("builtins.exit") as mock_exit,
    ):
        mock_parse_args.return_value = MagicMock(
            command="scrape",
            sport="invalid-sport",
            date=None,
            leagues=None,
            storage="local",
            format=None,
            headless=False,
            markets=None,
        )
        mock_validate_args.side_effect = ValueError("Invalid sport provided.")

        cli_handler.parse_and_validate_args()

        mock_exit.assert_called_once_with(1)


def test_parse_and_validate_args_with_all_flag(cli_handler):
    """Test that the all parameter is correctly passed through."""
    mock_args = [
        "scrape_upcoming",
        "--all",
        "--date",
        "2024-02-25",
        "--markets",
        "1x2",
    ]

    with (
        patch("sys.argv", ["cli_tool.py", *mock_args]),
        patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
        patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
    ):
        mock_parse_args.return_value = MagicMock(
            command="scrape_upcoming",
            all=True,
            date="2024-02-25",
            sport=None,
            leagues=None,
            markets=["1x2"],
            season=None,
            file_path=None,
            max_pages=None,
            proxies=None,
            browser_user_agent=None,
            browser_locale_timezone=None,
            browser_timezone_id=None,
            match_links=None,
            scrape_odds_history=False,
            target_bookmaker=None,
            preview_submarkets_only=False,
            storage="local",
            format="json",
            headless=False,
        )

        parsed_args = cli_handler.parse_and_validate_args()

        assert parsed_args["all"] is True
        assert parsed_args["command"] == "scrape_upcoming"
        assert parsed_args["date"] == "2024-02-25"
        assert parsed_args["markets"] == ["1x2"]

        mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
