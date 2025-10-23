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
            from_date="20240225",
            to_date=None,
            leagues=["england-premier-league"],
            storage="local",
            format="json",
            headless=True,
            markets=["1x2", "btts"],
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
            "from_date": "20240225",
            "to_date": None,
            "leagues": ["england-premier-league"],
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
            "change_sensitivity": "normal",
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
                from_date=None,
                to_date=None,
                leagues=None,
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
            from_date=None,
            to_date=None,
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
            from_date="20240225",
            to_date=None,
            sport=None,
            leagues=None,
            markets=["1x2"],
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
        assert parsed_args["from_date"] == "20240225"
        assert parsed_args["to_date"] is None
        assert parsed_args["markets"] == ["1x2"]

        mock_validate_args.assert_called_once_with(mock_parse_args.return_value)


class TestAllFlagValidationFailureScenarios:
    """Enhanced validation failure testing for --all flag scenarios."""

    def test_parse_and_validate_args_all_flag_with_invalid_sport_validation_failure(self, cli_handler):
        """Test that --all flag with invalid sport properly handles validation failure."""
        mock_args = [
            "scrape_historic",
            "--all",
            "--sport", "invalid_sport",
            "--from", "2023",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
            patch("builtins.exit") as mock_exit,
            patch("builtins.print") as mock_print,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_historic",
                all=True,
                sport="invalid_sport",  # Invalid sport
                from_date="2023",
                to_date=None,
                leagues=None,
                markets=None,
                storage="local",
                format="json",
                headless=False,
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
            )

            # Simulate validation failure for invalid sport
            mock_validate_args.side_effect = ValueError("Invalid sport: 'invalid_sport'. Supported sports are: [...]")

            cli_handler.parse_and_validate_args()

            # Verify the handler properly handles validation failure
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            mock_exit.assert_called_once_with(1)

            # Verify error message was printed
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Invalid sport" in call for call in print_calls)

    def test_parse_and_validate_args_all_flag_with_storage_validation_failure(self, cli_handler):
        """Test that --all flag with invalid storage properly handles validation failure."""
        mock_args = [
            "scrape_historic",
            "--all",
            "--from", "2023",
            "--storage", "invalid_storage",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
            patch("builtins.exit") as mock_exit,
            patch("builtins.print") as mock_print,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_historic",
                all=True,
                sport=None,  # Should be bypassed
                from_date="2023",
                to_date=None,
                leagues=None,
                markets=None,
                storage="invalid_storage",  # Invalid storage
                format="json",
                headless=False,
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
            )

            # Simulate validation failure for invalid storage
            mock_validate_args.side_effect = ValueError("Invalid storage type: 'invalid_storage'. Supported storage types are: [...]")

            cli_handler.parse_and_validate_args()

            # Verify the handler properly handles validation failure
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            mock_exit.assert_called_once_with(1)

            # Verify error message was printed
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Invalid storage" in call for call in print_calls)

    def test_parse_and_validate_args_all_flag_successful_validation_bypass(self, cli_handler):
        """Test that --all flag with normally invalid args bypasses sport validation successfully."""
        mock_args = [
            "scrape_historic",
            "--all",
            "--from", "2023",
            "--leagues", "invalid_league",  # Normally would fail
            "--markets", "invalid_market",   # Normally would fail
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_historic",
                all=True,
                sport=None,  # Triggers bypass
                from_date="2023",
                to_date=None,
                leagues=["invalid_league"],  # Should be bypassed
                markets=["invalid_market"],   # Should be bypassed
                storage="local",
                format="json",
                headless=False,
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
            )

            # No validation failure - should succeed due to --all flag bypass
            parsed_args = cli_handler.parse_and_validate_args()

            # Verify validation was called and succeeded
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            assert parsed_args["all"] is True
            assert parsed_args["command"] == "scrape_historic"
            assert parsed_args["from_date"] == "2023"
            assert parsed_args["leagues"] == ["invalid_league"]  # Passed through as-is
            assert parsed_args["markets"] == ["invalid_market"]   # Passed through as-is

    def test_parse_and_validate_args_all_flag_multiple_validation_errors(self, cli_handler):
        """Test that --all flag with multiple validation errors properly handles them."""
        mock_args = [
            "scrape_historic",
            "--all",
            "--from", "invalid_date",
            "--storage", "invalid_storage",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
            patch("builtins.exit") as mock_exit,
            patch("builtins.print") as mock_print,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_historic",
                all=True,
                sport=None,  # Should be bypassed
                from_date="invalid_date",  # Invalid
                to_date=None,
                leagues=None,
                markets=None,
                storage="invalid_storage",  # Invalid
                format="json",
                headless=False,
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
            )

            # Simulate multiple validation errors
            mock_validate_args.side_effect = ValueError(
                "Invalid date format: 'invalid_date'.\n"
                "Invalid storage type: 'invalid_storage'."
            )

            cli_handler.parse_and_validate_args()

            # Verify the handler properly handles validation failure
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            mock_exit.assert_called_once_with(1)

            # Verify error messages were printed
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Invalid date" in call for call in print_calls)
            assert any("Invalid storage" in call for call in print_calls)
