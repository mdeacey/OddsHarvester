from unittest.mock import MagicMock, patch

import pytest

from src.cli.cli_argument_handler import CLIArgumentHandler


@pytest.fixture
def cli_handler():
    return CLIArgumentHandler()


def test_parse_and_validate_args_valid(cli_handler):
    mock_args = [
        "scrape",
        "--sports",
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
            sports="football",
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
        )

        parsed_args = cli_handler.parse_and_validate_args()

        assert parsed_args == {
            "command": "scrape",
            "sports": "football",
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
        patch("sys.argv", ["cli_tool.py", "scrape", "--sports", "invalid-sport"]),
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
            sports="all",
            from_date="20240225",
            to_date=None,
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
            "--sports", "invalid_sport",
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
                sports="all",
                  # Invalid sport
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
                sports="all",
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
                sports="all",
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
                sports="all",
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


class TestMarketsAllParameter:
    """Test --markets all parameter functionality and validation."""

    def test_parse_and_validate_args_markets_all_flag(self, cli_handler):
        """Test that --markets all flag is properly parsed and passed through."""
        mock_args = [
            "scrape_upcoming",
            "--sports", "football",
            "--markets", "all",
            "--date", "2024-02-25",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="football",
                from_date="20240225",
                to_date=None,
                leagues=None,
                markets=["all"],  # Single item list with "all"
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

            # Verify --markets all is passed through correctly
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["command"] == "scrape_upcoming"
            assert parsed_args["sports"] == "football"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_markets_all_with_multiple_sports(self, cli_handler):
        """Test --markets all with multiple sports."""
        mock_args = [
            "scrape_historic",
            "--sports", "football,basketball,tennis",
            "--markets", "all",
            "--from", "2023",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_historic",
                sports="football,basketball,tennis",
                from_date="2023",
                to_date=None,
                leagues=None,
                markets=["all"],
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

            assert parsed_args["markets"] == ["all"]
            assert parsed_args["sports"] == "football,basketball,tennis"
            assert parsed_args["from_date"] == "2023"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_markets_all_with_leagues_all(self, cli_handler):
        """Test --markets all combined with --leagues all."""
        mock_args = [
            "scrape_upcoming",
            "--all",
            "--markets", "all",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="all",
                from_date=None,
                to_date=None,
                leagues=["all"],
                markets=["all"],
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
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["leagues"] == ["all"]

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_markets_all_validation_failure(self, cli_handler):
        """Test that --markets all with invalid other args handles validation properly."""
        mock_args = [
            "scrape_historic",
            "--markets", "all",
            "--storage", "invalid_storage",
            "--from", "invalid_date",
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
                sports=None,
                from_date="invalid_date",  # Invalid date
                to_date=None,
                leagues=None,
                markets=["all"],
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

            # Simulate validation failure for invalid storage and date
            mock_validate_args.side_effect = ValueError(
                "Invalid date format: 'invalid_date'.\n"
                "Invalid storage type: 'invalid_storage'."
            )

            cli_handler.parse_and_validate_args()

            # Verify validation was called and failed
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            mock_exit.assert_called_once_with(1)

            # Verify error messages were printed
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Invalid date" in call for call in print_calls)
            assert any("Invalid storage" in call for call in print_calls)

    def test_parse_and_validate_args_markets_all_with_specific_markets(self, cli_handler):
        """Test --markets all can be combined with specific markets in the same parameter."""
        mock_args = [
            "scrape_upcoming",
            "--sports", "football",
            "--markets", "all", "1x2", "btts", "over_under_2_5",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="football",
                from_date=None,
                to_date=None,
                leagues=None,
                markets=["all", "1x2", "btts", "over_under_2_5"],  # Mixed list
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

            # Verify all market values are passed through as-is
            assert parsed_args["markets"] == ["all", "1x2", "btts", "over_under_2_5"]
            assert parsed_args["command"] == "scrape_upcoming"
            assert parsed_args["sports"] == "football"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_markets_all_with_other_parameters(self, cli_handler):
        """Test --markets all works with other CLI parameters."""
        mock_args = [
            "scrape",
            "--sports", "basketball",
            "--markets", "all",
            "--date", "2024-02-25",
            "--leagues", "nba,ncaa",
            "--format", "csv",
            "--headless",
            "--file_path", "/path/to/output.csv",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape",
                sports="basketball",
                from_date="20240225",
                to_date=None,
                leagues=["nba", "ncaa"],
                storage="local",
                format="csv",
                headless=True,
                markets=["all"],
                file_path="/path/to/output.csv",
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

            parsed_args = cli_handler.parse_and_validate_args()

            # Verify all parameters are correctly parsed
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["sports"] == "basketball"
            assert parsed_args["leagues"] == ["nba", "ncaa"]
            assert parsed_args["format"] == "csv"
            assert parsed_args["headless"] is True
            assert parsed_args["file_path"] == "/path/to/output.csv"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)


class TestLeaguesAllUpcomingMatchesParameter:
    """Test --leagues all parameter functionality specifically with upcoming matches."""

    def test_parse_and_validate_args_leagues_all_upcoming_basic(self, cli_handler):
        """Test basic --leagues all functionality with upcoming matches."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all",
            "--sports", "football",
            "--date", "2024-02-25",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="football",
                from_date="20240225",
                to_date=None,
                leagues=["all"],  # Single item list with "all"
                markets=None,
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

            # Verify --leagues all is passed through correctly
            assert parsed_args["leagues"] == ["all"]
            assert parsed_args["command"] == "scrape_upcoming"
            assert parsed_args["sports"] == "football"
            assert parsed_args["from_date"] == "20240225"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_leagues_all_upcoming_with_markets_all(self, cli_handler):
        """Test --leagues all combined with --markets all for upcoming matches."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all",
            "--markets", "all",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="all",
                from_date=None,
                to_date=None,
                leagues=["all"],
                markets=["all"],
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

            assert parsed_args["leagues"] == ["all"]
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["command"] == "scrape_upcoming"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_leagues_all_upcoming_multiple_sports(self, cli_handler):
        """Test --leagues all with multiple sports for upcoming matches."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all",
            "--sports", "football,basketball,tennis",
            "--markets", "1x2", "btts",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="football,basketball,tennis",
                from_date=None,
                to_date=None,
                leagues=["all"],
                markets=["1x2", "btts"],
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

            assert parsed_args["leagues"] == ["all"]
            assert parsed_args["sports"] == "football,basketball,tennis"
            assert parsed_args["markets"] == ["1x2", "btts"]

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_leagues_all_upcoming_with_specific_leagues(self, cli_handler):
        """Test --leagues all combined with specific league names."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all", "england-premier-league", "spain-la-liga",
            "--sports", "football",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="football",
                from_date=None,
                to_date=None,
                leagues=["all", "england-premier-league", "spain-la-liga"],  # Mixed list
                markets=None,
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

            # Verify all league values are passed through as-is
            assert parsed_args["leagues"] == ["all", "england-premier-league", "spain-la-liga"]
            assert parsed_args["sports"] == "football"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_leagues_all_upcoming_validation_failure(self, cli_handler):
        """Test --leagues all with invalid parameters handles validation properly."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all",
            "--sports", "invalid_sport",
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
                command="scrape_upcoming",
                sports="invalid_sport",  # Invalid sport
                from_date=None,
                to_date=None,
                leagues=["all"],
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

            # Simulate validation failure for invalid sport and storage
            mock_validate_args.side_effect = ValueError(
                "Invalid sport: 'invalid_sport'. Supported sports are: [...]\n"
                "Invalid storage type: 'invalid_storage'."
            )

            cli_handler.parse_and_validate_args()

            # Verify validation was called and failed
            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
            mock_exit.assert_called_once_with(1)

            # Verify error messages were printed
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("Invalid sport" in call for call in print_calls)
            assert any("Invalid storage" in call for call in print_calls)

    def test_parse_and_validate_args_leagues_all_upcoming_with_all_parameters(self, cli_handler):
        """Test --leagues all with comprehensive upcoming match parameters."""
        mock_args = [
            "scrape_upcoming",
            "--leagues", "all",
            "--markets", "all",
            "--headless",
            "--format", "csv",
            "--file_path", "/path/to/upcoming_matches.csv",
            "--browser-user-agent", "Mozilla/5.0 (Custom Agent)",
            "--browser-locale-timezone", "en-AU",
            "--browser-timezone-id", "Australia/Sydney",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="all",
                from_date=None,
                to_date=None,
                leagues=["all"],
                markets=["all"],
                storage="local",
                format="csv",
                headless=True,
                file_path="/path/to/upcoming_matches.csv",
                max_pages=None,
                proxies=None,
                browser_user_agent="Mozilla/5.0 (Custom Agent)",
                browser_locale_timezone="en-AU",
                browser_timezone_id="Australia/Sydney",
                match_links=None,
                scrape_odds_history=False,
                target_bookmaker=None,
                preview_submarkets_only=False,
            )

            parsed_args = cli_handler.parse_and_validate_args()

            # Verify all parameters are correctly parsed
            assert parsed_args["leagues"] == ["all"]
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["format"] == "csv"
            assert parsed_args["headless"] is True
            assert parsed_args["file_path"] == "/path/to/upcoming_matches.csv"
            assert parsed_args["browser_user_agent"] == "Mozilla/5.0 (Custom Agent)"
            assert parsed_args["browser_locale_timezone"] == "en-AU"
            assert parsed_args["browser_timezone_id"] == "Australia/Sydney"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)

    def test_parse_and_validate_args_leagues_all_upcoming_aussie_rules_scenario(self, cli_handler):
        """Test --leagues all with aussie-rules scenario (the original failing case)."""
        mock_args = [
            "scrape_upcoming",
            "--sports", "aussie-rules",
            "--leagues", "all",
            "--markets", "all",
            "--headless",
        ]

        with (
            patch("sys.argv", ["cli_tool.py", *mock_args]),
            patch.object(cli_handler.parser, "parse_args") as mock_parse_args,
            patch.object(cli_handler.validator, "validate_args") as mock_validate_args,
        ):
            mock_parse_args.return_value = MagicMock(
                command="scrape_upcoming",
                sports="aussie-rules",
                from_date=None,
                to_date=None,
                leagues=["all"],
                markets=["all"],
                storage="local",
                format="json",
                headless=True,
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

            parsed_args = cli_handler.parse_and_validate_args()

            # Verify the exact scenario that was failing now works
            assert parsed_args["sports"] == "aussie-rules"
            assert parsed_args["leagues"] == ["all"]
            assert parsed_args["markets"] == ["all"]
            assert parsed_args["headless"] is True
            assert parsed_args["command"] == "scrape_upcoming"

            mock_validate_args.assert_called_once_with(mock_parse_args.return_value)
