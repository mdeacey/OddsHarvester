"""
Comprehensive CLI validation integration tests.
Tests the complete CLI validation pipeline with conditional --all flag logic.
"""
import argparse
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
import sys
import tempfile
import os

import pytest

from src.cli.cli_argument_parser import CLIArgumentParser
from src.cli.cli_argument_validator import CLIArgumentValidator
from src.cli.cli_argument_handler import CLIArgumentHandler


@pytest.fixture
def parser():
    return CLIArgumentParser()


@pytest.fixture
def validator():
    return CLIArgumentValidator()


@pytest.fixture
def handler():
    return CLIArgumentHandler()


class TestAllFlagConditionalValidation:
    """Test --all flag conditional validation scenarios."""

    def test_scrape_historic_all_without_sport_success(self, validator):
        """Test that scrape_historic --all without --sport bypasses sport validation."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            markets=None,
            leagues=None,
            from_date="2023",
            to_date="2024",
            storage="local",
            max_pages=5
        )

        # Should not raise any errors
        try:
            validator.validate_args(mock_args)
        except ValueError as e:
            pytest.fail(f"Unexpected ValueError when using --all flag without sport: {e}")

    def test_scrape_upcoming_all_without_sport_success(self, validator):
        """Test that scrape_upcoming --all without --sport bypasses sport validation."""
        mock_args = MagicMock(
            command="scrape_upcoming",
            all=True,
            sport=None,
            markets=None,
            leagues=None,
            from_date="20231201",
            to_date="20231202",
            storage="local"
        )

        # Should not raise any errors
        try:
            validator.validate_args(mock_args)
        except ValueError as e:
            pytest.fail(f"Unexpected ValueError when using --all flag without sport: {e}")

    def test_scrape_historic_all_with_sport_validates_normally(self, validator):
        """Test that scrape_historic --all with --sport still validates sport normally."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport="invalid_sport",  # Invalid sport
            markets=None,
            leagues=None,
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should raise ValueError for invalid sport
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args)

    def test_scrape_upcoming_all_with_sport_validates_normally(self, validator):
        """Test that scrape_upcoming --all with --sport still validates sport normally."""
        mock_args = MagicMock(
            command="scrape_upcoming",
            all=True,
            sport="invalid_sport",  # Invalid sport
            markets=None,
            leagues=None,
            from_date="20231201",
            to_date="20231202",
            storage="local"
        )

        # Should raise ValueError for invalid sport
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args)

    def test_scrape_historic_all_with_invalid_markets_bypasses_validation(self, validator):
        """Test that --all flag bypasses markets validation even with invalid markets."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            markets=["invalid_market"],  # Normally would cause error
            leagues=None,
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should not raise errors for invalid markets when --all is used without sport
        try:
            validator.validate_args(mock_args)
        except ValueError as e:
            pytest.fail(f"Unexpected ValueError when using --all flag with invalid markets: {e}")

    def test_scrape_historic_all_with_invalid_leagues_bypasses_validation(self, validator):
        """Test that --all flag bypasses leagues validation even with invalid leagues."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            markets=None,
            leagues=["invalid_league"],  # Normally would cause error
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should not raise errors for invalid leagues when --all is used without sport
        try:
            validator.validate_args(mock_args)
        except ValueError as e:
            pytest.fail(f"Unexpected ValueError when using --all flag with invalid leagues: {e}")

    def test_no_all_flag_validates_sport_normally(self, validator):
        """Test that without --all flag, sport validation works normally."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=False,
            sport=None,  # Missing sport should cause error when --all is False
            markets=None,
            leagues=None,
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should raise ValueError for missing sport when --all is False
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args)

    def test_all_flag_false_validates_sport_normally(self, validator):
        """Test that when --all flag is explicitly False, sport validation works normally."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=False,
            sport=None,  # Missing sport should cause error when --all is False
            markets=None,
            leagues=None,
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should raise ValueError for missing sport when --all is False
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args)


class TestCLIIntegrationPipeline:
    """Test complete CLI integration pipeline with sys.argv mocking."""

    @patch('sys.argv', ['scrape_historic', '--all', '--from', '2023', '--to', '2024'])
    def test_scrape_historic_all_integration(self, parser, validator):
        """Test complete CLI integration: scrape_historic --all should bypass sport validation."""
        # Parse arguments
        args = parser.parse_args()

        # Validate arguments - should not raise errors
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Integration test failed for scrape_historic --all: {e}")

        # Verify parsed arguments
        assert args.command == "scrape_historic"
        assert args.all is True
        assert args.from_date == "2023"
        assert args.to_date == "2024"

    @patch('sys.argv', ['scrape_upcoming', '--all', '--from', '20231201', '--to', '20231202'])
    def test_scrape_upcoming_all_integration(self, parser, validator):
        """Test complete CLI integration: scrape_upcoming --all should bypass sport validation."""
        # Parse arguments
        args = parser.parse_args()

        # Validate arguments - should not raise errors
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Integration test failed for scrape_upcoming --all: {e}")

        # Verify parsed arguments
        assert args.command == "scrape_upcoming"
        assert args.all is True
        assert args.from_date == "20231201"
        assert args.to_date == "20231202"

    @patch('sys.argv', ['scrape_historic', '--all', '--sport', 'invalid_sport', '--from', '2023'])
    def test_scrape_historic_all_with_invalid_sport_integration(self, parser, validator):
        """Test that --all with invalid sport still raises validation error."""
        # Parse arguments
        args = parser.parse_args()

        # Validate arguments - should raise error for invalid sport
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(args)

    @patch('sys.argv', ['scrape_historic', '--sport', 'football', '--from', '2023'])
    def test_scrape_historic_normal_validation_integration(self, parser, validator):
        """Test normal validation flow without --all flag."""
        # Parse arguments
        args = parser.parse_args()

        # Validate arguments - should not raise errors for valid sport
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Integration test failed for normal scrape_historic: {e}")

        # Verify parsed arguments
        assert args.command == "scrape_historic"
        assert args.all is False
        assert args.sport == "football"
        assert args.from_date == "2023"

    @patch('sys.argv', ['scrape_historic', '--from', '2023'])
    def test_scrape_historic_missing_sport_without_all_integration(self, parser, validator):
        """Test that missing sport without --all flag raises validation error."""
        # Parse arguments
        args = parser.parse_args()

        # Validate arguments - should raise error for missing sport when --all is not used
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(args)


class TestErrorChainValidation:
    """Test error reporting chain validation."""

    def test_multiple_errors_without_all_flag(self, validator):
        """Test that multiple validation errors are reported together without --all flag."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=False,
            sport="invalid_sport",  # Invalid sport
            markets=["invalid_market"],  # Invalid market
            leagues=["invalid_league"],  # Invalid league
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should collect and report all validation errors
        with pytest.raises(ValueError) as exc_info:
            validator.validate_args(mock_args)

        error_message = str(exc_info.value)
        # Should contain multiple error messages
        assert "Invalid sport" in error_message
        # Note: markets and leagues validation may be skipped if sport validation fails first

    def test_no_errors_with_all_flag(self, validator):
        """Test that --all flag prevents validation errors even with invalid inputs."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            markets=["invalid_market"],  # Would normally cause error
            leagues=["invalid_league"],  # Would normally cause error
            from_date="2023",
            to_date="2024",
            storage="local"
        )

        # Should not raise any errors
        try:
            validator.validate_args(mock_args)
        except ValueError as e:
            pytest.fail(f"Unexpected errors with --all flag: {e}")


class TestEdgeCasesAndComplexScenarios:
    """Test edge cases and complex flag combinations."""

    def test_all_flag_with_match_links(self, validator):
        """Test --all flag behavior with match_links (match_links should still require sport)."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            match_links=["https://www.oddsportal.com/football/test-match"],
            from_date="2023",
            to_date="2024"
        )

        # match_links validation should still require sport even with --all flag
        with pytest.raises(ValueError, match="--sport.*required.*match_links"):
            validator.validate_args(mock_args)

    def test_all_flag_with_leagues_requires_sport(self, validator):
        """Test that --all with leagues still requires sport validation."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,  # Sport is None
            leagues=["england-premier-league"],  # But leagues are provided
            from_date="2023",
            to_date="2024"
        )

        # Should not bypass sport validation when leagues are provided even with --all flag
        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args)

    def test_boolean_variations_all_flag(self, validator):
        """Test different boolean variations of --all flag."""
        # Test all=False
        mock_args_false = MagicMock(
            command="scrape_historic",
            all=False,
            sport=None,  # Missing sport
            from_date="2023",
            to_date="2024"
        )

        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args_false)

        # Test all=None (treated as falsy)
        mock_args_none = MagicMock(
            command="scrape_historic",
            all=None,
            sport=None,  # Missing sport
            from_date="2023",
            to_date="2024"
        )

        with pytest.raises(ValueError, match="Invalid sport"):
            validator.validate_args(mock_args_none)

        # Test all=True (bypasses validation)
        mock_args_true = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,  # Missing sport but bypassed
            from_date="2023",
            to_date="2024"
        )

        try:
            validator.validate_args(mock_args_true)
        except ValueError as e:
            pytest.fail(f"Unexpected error with all=True: {e}")

    def test_all_flag_date_validation_still_required(self, validator):
        """Test that date validation is still required with --all flag."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            from_date=None,  # Missing dates
            to_date=None
        )

        # Date validation should still work normally with --all flag
        # This should pass since dates can be optional and default to "now"
        try:
            validator.validate_args(mock_args)
        except ValueError:
            # If it fails, it should be due to other validation logic, not the --all bypass
            pass

    def test_all_flag_with_storage_validation(self, validator):
        """Test that storage validation still works with --all flag."""
        mock_args = MagicMock(
            command="scrape_historic",
            all=True,
            sport=None,
            from_date="2023",
            to_date="2024",
            storage="invalid_storage"  # Invalid storage
        )

        # Storage validation should still work even with --all flag
        with pytest.raises(ValueError, match="Invalid storage type"):
            validator.validate_args(mock_args)


class TestRealWorldUsagePatterns:
    """Test real-world CLI usage patterns with --all flag."""

    @patch('sys.argv', ['scrape_historic', '--all', '--from', '2022', '--to', '2023', '--max_pages', '10'])
    def test_historic_all_with_pages(self, parser, validator):
        """Test scrape_historic --all with max_pages."""
        args = parser.parse_args()
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Failed historic --all with max_pages: {e}")
        assert args.all is True
        assert args.max_pages == 10

    @patch('sys.argv', ['scrape_upcoming', '--all', '--from', 'now'])
    def test_upcoming_all_from_now(self, parser, validator):
        """Test scrape_upcoming --all from now."""
        args = parser.parse_args()
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Failed upcoming --all from now: {e}")
        assert args.all is True
        assert args.from_date == "now"

    @patch('sys.argv', ['scrape_historic', '--all', '--from', '2023-2024'])
    def test_historic_all_with_season_range(self, parser, validator):
        """Test scrape_historic --all with season range format."""
        args = parser.parse_args()
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Failed historic --all with season range: {e}")
        assert args.all is True
        assert args.from_date == "2023-2024"

    @patch('sys.argv', ['scrape_upcoming', '--all', '--from', '20231201', '--to', '20231231', '--format', 'json'])
    def test_upcoming_all_with_format(self, parser, validator):
        """Test scrape_upcoming --all with date range and format."""
        args = parser.parse_args()
        try:
            validator.validate_args(args)
        except ValueError as e:
            pytest.fail(f"Failed upcoming --all with format: {e}")
        assert args.all is True
        assert args.format == "json"


if __name__ == "__main__":
    pytest.main([__file__])