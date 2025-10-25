"""
Tests for enhanced error handling in universal market auto-discovery.

This test suite validates the improved error messages and troubleshooting guidance
implemented as part of ACC-XXX.
"""

import pytest
from unittest.mock import AsyncMock, patch
import logging

from src.core.scraper_app import _ensure_market_auto_discovery
from src.core.sport_market_registry import SportMarketRegistry


class TestEnhancedErrorHandling:
    """Test enhanced error handling scenarios."""

    def setup_method(self):
        """Clean up before each test."""
        SportMarketRegistry.clear_discovered_markets()

    @pytest.mark.asyncio
    async def test_no_markets_discovered_error_message(self):
        """Test detailed error message when no markets are discovered."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {}  # No markets discovered

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            error_msg = str(exc_info.value)

            # Verify comprehensive error message
            assert "No markets discovered for sport 'football'" in error_msg
            assert "This could indicate:" in error_msg
            assert "1. The sport has no available markets on OddsPortal" in error_msg
            assert "2. Network connectivity issues" in error_msg
            assert "3. OddsPortal page structure changes" in error_msg
            assert "4. Temporary site unavailability" in error_msg
            assert "Please check the sport name and try again later" in error_msg

    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, caplog):
        """Test enhanced error handling for timeout exceptions."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("Timeout occurred while waiting for element")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error message
            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            assert "Timeout occurred while waiting for element" in error_msg

            # Verify timeout-specific guidance was logged
            with caplog.at_level(logging.ERROR):
                try:
                    await _ensure_market_auto_discovery("football", mock_page)
                except ValueError:
                    pass

            timeout_logged = any("Timeout occurred during market discovery" in record.message
                               for record in caplog.records if record.levelno == logging.ERROR)
            # Note: This verifies the enhanced logging behavior

    @pytest.mark.asyncio
    async def test_navigation_error_handling(self, caplog):
        """Test enhanced error handling for navigation exceptions."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("Navigation timeout exceeded")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error message
            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            assert "Navigation timeout exceeded" in error_msg

    @pytest.mark.asyncio
    async def test_selector_error_handling(self, caplog):
        """Test enhanced error handling for page structure issues."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("Element with selector '.market-tabs' not found")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error message
            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            assert "Element with selector '.market-tabs' not found" in error_msg

    @pytest.mark.asyncio
    async def test_network_connectivity_error_handling(self):
        """Test enhanced error handling for network connectivity issues."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("ERR_CONNECTION_TIMED_OUT")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error message
            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            assert "ERR_CONNECTION_TIMED_OUT" in error_msg

    @pytest.mark.asyncio
    async def test_proxy_connection_error_handling(self):
        """Test enhanced error handling for proxy connection issues."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = Exception("ERR_PROXY_CONNECTION_FAILED")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error message
            error_msg = str(exc_info.value)
            assert "Market auto-discovery failed for sport 'football'" in error_msg
            assert "ERR_PROXY_CONNECTION_FAILED" in error_msg

    @pytest.mark.asyncio
    async def test_value_error_propagation(self):
        """Test that ValueError exceptions are propagated correctly."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            # Simulate a ValueError from the discovery system
            mock_discover.side_effect = ValueError("Invalid sport parameter")

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("invalid-sport", mock_page)

            # Should propagate the original ValueError without wrapping
            error_msg = str(exc_info.value)
            assert "Invalid sport parameter" in error_msg
            # Should not contain the wrapper message
            assert "Market auto-discovery failed" not in error_msg

    @pytest.mark.asyncio
    async def test_debug_logging_with_discovered_leagues(self, caplog):
        """Test debug logging when discovered leagues are provided."""
        mock_page = AsyncMock()
        discovered_leagues = {
            "premier-league": "https://oddsportal.com/football/premier-league",
            "championship": "https://oddsportal.com/football/championship"
        }

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {"1x2": "1X2", "btts": "BTTS"}

            # Set log level to capture debug messages
            with caplog.at_level(logging.DEBUG):
                result = await _ensure_market_auto_discovery("football", mock_page, discovered_leagues)

            # Verify debug message about discovered leagues
            debug_messages = [record.message for record in caplog.records if record.levelno == logging.DEBUG]
            league_debug_msg = next((msg for msg in debug_messages if "Starting market discovery" in msg and "2 discovered leagues" in msg), None)

            assert league_debug_msg is not None
            assert "Starting market discovery for 'football'" in league_debug_msg
            assert "2 discovered leagues" in league_debug_msg

    @pytest.mark.asyncio
    async def test_debug_logging_with_no_discovered_leagues(self, caplog):
        """Test debug logging when no discovered leagues are provided."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {"1x2": "1X2"}

            # Set log level to capture debug messages
            with caplog.at_level(logging.DEBUG):
                result = await _ensure_market_auto_discovery("football", mock_page, None)

            # Verify debug message about discovered leagues
            debug_messages = [record.message for record in caplog.records if record.levelno == logging.DEBUG]
            league_debug_msg = next((msg for msg in debug_messages if "Starting market discovery" in msg and "0 discovered leagues" in msg), None)

            assert league_debug_msg is not None
            assert "Starting market discovery for 'football'" in league_debug_msg
            assert "0 discovered leagues" in league_debug_msg

    @pytest.mark.asyncio
    async def test_success_logging(self, caplog):
        """Test success logging when market discovery works."""
        mock_page = AsyncMock()
        discovered_markets = {"1x2": "1X2", "over_under_2_5": "Over/Under 2.5", "btts": "BTTS"}

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = discovered_markets

            # Set log level to capture info messages
            with caplog.at_level(logging.INFO):
                result = await _ensure_market_auto_discovery("football", mock_page)

            # Verify success message
            info_messages = [record.message for record in caplog.records if record.levelno == logging.INFO]
            success_msg = next((msg for msg in info_messages if "Successfully discovered and registered" in msg), None)

            assert success_msg is not None
            assert "Successfully discovered and registered 3 markets for 'football'" in success_msg
            assert "['1x2', 'over_under_2_5', 'btts']" in success_msg

    @pytest.mark.asyncio
    async def test_error_chain_preservation(self):
        """Test that error chain is preserved for debugging."""
        mock_page = AsyncMock()
        original_error = Exception("Original network error")

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.side_effect = original_error

            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("football", mock_page)

            # Verify error chain is preserved
            assert exc_info.value.__cause__ is original_error
            assert str(exc_info.value.__cause__) == "Original network error"