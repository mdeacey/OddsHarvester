"""
Tests for universal market auto-discovery functionality.

This test suite validates the ACC-XXX implementation that removes hardcoded market defaults
and implements universal market auto-discovery as the default behavior.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import logging

from src.core.scraper_app import _ensure_market_auto_discovery
from src.core.sport_market_registry import SportMarketRegistry
from src.core.url_builder import URLBuilder
from src.utils.sport_market_constants import Sport


class TestUniversalMarketAutoDiscovery:
    """Test the universal market auto-discovery functionality."""

    @pytest.fixture
    def mock_page(self):
        """Create a mock Playwright page."""
        page = AsyncMock()
        page.goto = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        return page

    @pytest.fixture
    def discovered_markets(self):
        """Sample discovered markets for testing."""
        return {
            "1x2": "1X2",
            "home_away": "Home/Away",
            "over_under_2_5": "Over/Under 2.5",
            "btts": "Both Teams to Score"
        }

    @pytest.fixture
    def discovered_leagues(self):
        """Sample discovered leagues for testing."""
        return {
            "premier-league": "https://www.oddsportal.com/football/england/premier-league/",
            "championship": "https://www.oddsportal.com/football/england/championship/"
        }

    def setup_method(self):
        """Set up test environment before each test."""
        # Clear any cached discovered markets
        SportMarketRegistry.clear_discovered_markets()

    @pytest.mark.asyncio
    async def test_market_auto_discovery_with_cached_markets(self, mock_page, discovered_markets):
        """Test that cached discovered markets are used when available."""
        sport = "football"

        # Pre-populate cache with discovered markets
        SportMarketRegistry.register_discovered_markets(sport, discovered_markets)

        # Call auto-discovery
        result = await _ensure_market_auto_discovery(sport, mock_page)

        # Verify result
        assert set(result) == set(discovered_markets.keys())
        assert "1x2" in result
        assert "home_away" in result

        # Verify no network calls were made (using cached data)
        mock_page.goto.assert_not_called()

    @pytest.mark.asyncio
    async def test_market_auto_discovery_successful_discovery(self, mock_page, discovered_markets, discovered_leagues):
        """Test successful market discovery when no cached markets exist."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovered_markets

            # Call auto-discovery
            result = await _ensure_market_auto_discovery(sport, mock_page, discovered_leagues)

            # Verify discovery was called with correct parameters
            mock_discover.assert_called_once_with(sport, mock_page, discovered_leagues)

            # Verify result
            assert set(result) == set(discovered_markets.keys())

            # Verify markets were registered
            cached_markets = SportMarketRegistry.get_discovered_markets(sport)
            assert cached_markets == discovered_markets

    @pytest.mark.asyncio
    async def test_market_auto_discovery_failure_raises_error(self, mock_page):
        """Test that market discovery failure raises appropriate error."""
        sport = "nonexistent-sport"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {}  # No markets discovered

            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery(sport, mock_page)

            # Verify error message contains helpful information
            error_msg = str(exc_info.value)
            assert "No markets discovered for sport 'nonexistent-sport'" in error_msg
            assert "This could indicate" in error_msg
            assert "Please check the sport name" in error_msg

    @pytest.mark.asyncio
    async def test_market_auto_discovery_exception_handling_with_timeout(self, mock_page):
        """Test enhanced error handling for timeout exceptions."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("Timeout occurred while waiting for element")

            # Should raise ValueError with enhanced error message
            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery(sport, mock_page)

            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            # Should include timeout-specific guidance
            assert "Timeout occurred during market discovery" not in error_msg  # This is logged, not in exception

    @pytest.mark.asyncio
    async def test_market_auto_discovery_exception_handling_with_navigation_error(self, mock_page):
        """Test enhanced error handling for navigation exceptions."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("Navigation timeout exceeded")

            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery(sport, mock_page)

            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg

    @pytest.mark.asyncio
    async def test_market_auto_discovery_with_discovered_leagues(self, mock_page, discovered_markets, discovered_leagues):
        """Test that discovered leagues are properly passed to market discovery."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovered_markets

            # Call auto-discovery with discovered leagues
            result = await _ensure_market_auto_discovery(sport, mock_page, discovered_leagues)

            # Verify discovered leagues were passed through
            mock_discover.assert_called_once_with(sport, mock_page, discovered_leagues)

            # Verify result
            assert set(result) == set(discovered_markets.keys())

    @pytest.mark.asyncio
    async def test_market_auto_discovery_with_empty_discovered_leagues(self, mock_page, discovered_markets):
        """Test that empty discovered leagues are handled correctly."""
        sport = "football"
        empty_leagues = {}

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovered_markets

            # Call auto-discovery with empty leagues
            result = await _ensure_market_auto_discovery(sport, mock_page, empty_leagues)

            # Verify empty leagues were passed through
            mock_discover.assert_called_once_with(sport, mock_page, empty_leagues)

            # Verify result
            assert set(result) == set(discovered_markets.keys())

    @pytest.mark.asyncio
    async def test_market_auto_discovery_with_none_discovered_leagues(self, mock_page, discovered_markets):
        """Test that None discovered leagues are handled correctly."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovered_markets

            # Call auto-discovery with None leagues
            result = await _ensure_market_auto_discovery(sport, mock_page, None)

            # Verify None leagues were passed through
            mock_discover.assert_called_once_with(sport, mock_page, None)

            # Verify result
            assert set(result) == set(discovered_markets.keys())

    def test_cached_markets_check_avoid_unnecessary_discovery(self, mock_page, discovered_markets):
        """Test that existing cached markets prevent unnecessary discovery calls."""
        sport = "football"

        # Pre-populate cache
        SportMarketRegistry.register_discovered_markets(sport, discovered_markets)

        # Verify cached markets are detected
        assert SportMarketRegistry.has_discovered_markets(sport) is True

        cached = SportMarketRegistry.get_discovered_markets(sport)
        assert cached == discovered_markets

    @pytest.mark.asyncio
    async def test_market_auto_discovery_logs_debug_info(self, mock_page, discovered_leagues, caplog):
        """Test that appropriate debug information is logged."""
        sport = "football"

        with patch.object(URLBuilder, 'discover_available_markets', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {"1x2": "1X2"}

            # Set log level to capture debug messages
            with caplog.at_level(logging.DEBUG):
                result = await _ensure_market_auto_discovery(sport, mock_page, discovered_leagues)

            # Verify debug message about discovered leagues
            assert any("Starting market discovery" in record.message and "2 discovered leagues" in record.message
                      for record in caplog.records if record.levelno == logging.DEBUG)

            # Verify info message about successful discovery
            assert any("Successfully discovered and registered" in record.message
                      for record in caplog.records if record.levelno == logging.INFO)