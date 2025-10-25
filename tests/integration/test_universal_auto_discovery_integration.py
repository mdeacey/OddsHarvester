"""
Integration tests for Universal Market Auto-Discovery (ACC-XXX).

This test suite validates the end-to-end functionality of universal market auto-discovery
as the default behavior when no markets are specified.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.scraper_app import run_scraper, _ensure_market_auto_discovery
from src.core.sport_market_registry import SportMarketRegistry
from src.utils.command_enum import CommandEnum


class TestUniversalAutoDiscoveryIntegration:
    """Test universal market auto-discovery in realistic scenarios."""

    @pytest.fixture
    def setup_mocks(self):
        """Set up common mocks for integration tests."""
        playwright_manager_mock = MagicMock()
        browser_helper_mock = MagicMock()
        market_extractor_mock = MagicMock()
        scraper_mock = MagicMock()

        # Configure async methods
        scraper_mock.start_playwright = AsyncMock()
        scraper_mock.stop_playwright = AsyncMock()
        scraper_mock.scrape_historic = AsyncMock(return_value=[{"match": "data"}])
        scraper_mock.scrape_upcoming = AsyncMock(return_value=[{"match": "data"}])
        scraper_mock.scrape_matches = AsyncMock(return_value=[{"match": "data"}])
        scraper_mock.playwright_manager.page = AsyncMock()

        return {
            "playwright_manager_mock": playwright_manager_mock,
            "browser_helper_mock": browser_helper_mock,
            "market_extractor_mock": market_extractor_mock,
            "scraper_mock": scraper_mock,
        }

    def setup_method(self):
        """Clean up before each test."""
        SportMarketRegistry.clear_discovered_markets()

    @pytest.mark.asyncio
    @patch("src.core.scraper_app.OddsPortalScraper")
    @patch("src.core.scraper_app.OddsPortalMarketExtractor")
    @patch("src.core.scraper_app.BrowserHelper")
    @patch("src.core.scraper_app.PlaywrightManager")
    @patch("src.core.scraper_app.ProxyManager")
    @patch("src.core.scraper_app.SportMarketRegistrar")
    async def test_historic_scraping_with_universal_auto_discovery(
        self,
        sport_market_registrar_mock,
        proxy_manager_mock,
        playwright_manager_mock,
        browser_helper_mock,
        market_extractor_mock,
        scraper_cls_mock,
        setup_mocks
    ):
        """Test historic scraping with universal auto-discovery (no markets specified)."""
        scraper_mock = setup_mocks["scraper_mock"]
        scraper_cls_mock.return_value = scraper_mock

        # Mock proxy manager
        proxy_manager_instance = MagicMock()
        proxy_manager_instance.get_current_proxy.return_value = {"server": "test-proxy"}
        proxy_manager_mock.return_value = proxy_manager_instance

        # Mock discovered markets
        discovered_markets = ["1x2", "over_under_2_5", "btts", "handicap"]

        with patch("src.core.scraper_app._ensure_market_auto_discovery", new_callable=AsyncMock) as auto_discovery_mock:
            auto_discovery_mock.return_value = discovered_markets

            with patch("src.core.scraper_app._scrape_single_league_date_range") as date_range_mock:
                date_range_mock.return_value = [{"match": "historic_data"}]

                # Run scraper without specifying markets (should trigger auto-discovery)
                result = await run_scraper(
                    command=CommandEnum.HISTORIC,
                    sports="football",
                    leagues=["premier-league"],
                    from_date="2023",
                    to_date="2023",
                    markets=None,  # No markets - should trigger universal auto-discovery
                    headless=True,
                )

                # Verify auto-discovery was called
                auto_discovery_mock.assert_called_once_with("football", scraper_mock.playwright_manager.page)

                # Verify discovered markets were used
                date_range_mock.assert_called_once()
                call_args = date_range_mock.call_args
                assert call_args[1]["markets"] == discovered_markets

                assert result == [{"match": "historic_data"}]

    @pytest.mark.asyncio
    @patch("src.core.scraper_app.OddsPortalScraper")
    @patch("src.core.scraper_app.OddsPortalMarketExtractor")
    @patch("src.core.scraper_app.BrowserHelper")
    @patch("src.core.scraper_app.PlaywrightManager")
    @patch("src.core.scraper_app.ProxyManager")
    @patch("src.core.scraper_app.SportMarketRegistrar")
    async def test_upcoming_scraping_with_universal_auto_discovery(
        self,
        sport_market_registrar_mock,
        proxy_manager_mock,
        playwright_manager_mock,
        browser_helper_mock,
        market_extractor_mock,
        scraper_cls_mock,
        setup_mocks
    ):
        """Test upcoming matches scraping with universal auto-discovery."""
        scraper_mock = setup_mocks["scraper_mock"]
        scraper_cls_mock.return_value = scraper_mock

        # Mock proxy manager
        proxy_manager_instance = MagicMock()
        proxy_manager_instance.get_current_proxy.return_value = {"server": "test-proxy"}
        proxy_manager_mock.return_value = proxy_manager_instance

        # Mock discovered markets
        discovered_markets = ["match_winner", "over_under_sets", "handicap"]

        with patch("src.core.scraper_app._ensure_market_auto_discovery", new_callable=AsyncMock) as auto_discovery_mock:
            auto_discovery_mock.return_value = discovered_markets

            with patch("src.core.scraper_app._scrape_single_league_date_range") as date_range_mock:
                date_range_mock.return_value = [{"match": "upcoming_data"}]

                # Run scraper for tennis without specifying markets
                result = await run_scraper(
                    command=CommandEnum.UPCOMING_MATCHES,
                    sports="tennis",
                    from_date="20240101",
                    to_date="20240101",
                    markets=None,  # No markets - should trigger universal auto-discovery
                    headless=True,
                )

                # Verify auto-discovery was called for tennis
                auto_discovery_mock.assert_called_once_with("tennis", scraper_mock.playwright_manager.page)

                # Verify discovered markets were used
                date_range_mock.assert_called_once()
                call_args = date_range_mock.call_args
                assert call_args[1]["markets"] == discovered_markets

                assert result == [{"match": "upcoming_data"}]

    @pytest.mark.asyncio
    @patch("src.core.scraper_app.OddsPortalScraper")
    @patch("src.core.scraper_app.OddsPortalMarketExtractor")
    @patch("src.core.scraper_app.BrowserHelper")
    @patch("src.core.scraper_app.PlaywrightManager")
    @patch("src.core.scraper_app.ProxyManager")
    @patch("src.core.scraper_app.SportMarketRegistrar")
    async def test_explicit_markets_override_auto_discovery(
        self,
        sport_market_registrar_mock,
        proxy_manager_mock,
        playwright_manager_mock,
        browser_helper_mock,
        market_extractor_mock,
        scraper_cls_mock,
        setup_mocks
    ):
        """Test that explicitly specified markets override auto-discovery."""
        scraper_mock = setup_mocks["scraper_mock"]
        scraper_cls_mock.return_value = scraper_mock

        # Mock proxy manager
        proxy_manager_instance = MagicMock()
        proxy_manager_instance.get_current_proxy.return_value = {"server": "test-proxy"}
        proxy_manager_mock.return_value = proxy_manager_instance

        explicit_markets = ["1x2", "btts"]

        with patch("src.core.scraper_app._ensure_market_auto_discovery", new_callable=AsyncMock) as auto_discovery_mock:
            # Auto-discovery should NOT be called when markets are explicitly provided
            auto_discovery_mock.return_value = ["other_markets"]

            with patch("src.core.scraper_app._scrape_single_league_date_range") as date_range_mock:
                date_range_mock.return_value = [{"match": "data"}]

                # Run scraper with explicit markets
                result = await run_scraper(
                    command=CommandEnum.HISTORIC,
                    sports="football",
                    leagues=["premier-league"],
                    from_date="2023",
                    to_date="2023",
                    markets=explicit_markets,  # Explicit markets - should NOT trigger auto-discovery
                    headless=True,
                )

                # Auto-discovery should NOT be called
                auto_discovery_mock.assert_not_called()

                # Verify explicit markets were used
                date_range_mock.assert_called_once()
                call_args = date_range_mock.call_args
                assert call_args[1]["markets"] == explicit_markets

                assert result == [{"match": "data"}]

    @pytest.mark.asyncio
    @patch("src.core.scraper_app.OddsPortalScraper")
    @patch("src.core.scraper_app.OddsPortalMarketExtractor")
    @patch("src.core.scraper_app.BrowserHelper")
    @patch("src.core.scraper_app.PlaywrightManager")
    @patch("src.core.scraper_app.ProxyManager")
    @patch("src.core.scraper_app.SportMarketRegistrar")
    async def test_markets_all_still_triggers_full_discovery(
        self,
        sport_market_registrar_mock,
        proxy_manager_mock,
        playwright_manager_mock,
        browser_helper_mock,
        market_extractor_mock,
        scraper_cls_mock,
        setup_mocks
    ):
        """Test that --markets all still triggers full market discovery."""
        scraper_mock = setup_mocks["scraper_mock"]
        scraper_cls_mock.return_value = scraper_mock

        # Mock proxy manager
        proxy_manager_instance = MagicMock()
        proxy_manager_instance.get_current_proxy.return_value = {"server": "test-proxy"}
        proxy_manager_mock.return_value = proxy_manager_instance

        all_markets = ["1x2", "over_under_2_5", "btts", "handicap", "correct_score", "double_chance"]

        with patch("src.core.scraper_app._ensure_market_auto_discovery", new_callable=AsyncMock) as auto_discovery_mock:
            auto_discovery_mock.return_value = all_markets

            with patch("src.core.scraper_app._scrape_single_league_date_range") as date_range_mock:
                date_range_mock.return_value = [{"match": "data"}]

                # Run scraper with markets=all
                result = await run_scraper(
                    command=CommandEnum.HISTORIC,
                    sports="football",
                    leagues=["premier-league"],
                    from_date="2023",
                    to_date="2023",
                    markets=["all"],  # Explicit "all" - should trigger auto-discovery
                    headless=True,
                )

                # Auto-discovery should be called
                auto_discovery_mock.assert_called_once_with("football", scraper_mock.playwright_manager.page)

                # Verify all discovered markets were used
                date_range_mock.assert_called_once()
                call_args = date_range_mock.call_args
                assert call_args[1]["markets"] == all_markets

                assert result == [{"match": "data"}]

    @pytest.mark.asyncio
    async def test_auto_discovery_error_handling_integration(self):
        """Test error handling when auto-discovery fails."""
        mock_page = AsyncMock()

        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {}  # No markets discovered

            # Should raise ValueError
            with pytest.raises(ValueError) as exc_info:
                await _ensure_market_auto_discovery("nonexistent-sport", mock_page)

            error_msg = str(exc_info.value)
            assert "No markets discovered for sport 'nonexistent-sport'" in error_msg
            assert "This could indicate" in error_msg

    @pytest.mark.asyncio
    async def test_auto_discovery_caching_integration(self, mock_page):
        """Test that discovered markets are cached for performance."""
        # First call should perform discovery
        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {"1x2": "1X2", "btts": "BTTS"}

            result1 = await _ensure_market_auto_discovery("football", mock_page)
            mock_discover.assert_called_once()
            assert set(result1) == {"1x2", "btts"}

        # Second call should use cache
        with patch("src.core.scraper_app.URLBuilder.discover_available_markets", new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {"1x2": "1X2", "btts": "BTTS"}

            result2 = await _ensure_market_auto_discovery("football", mock_page)
            mock_discover.assert_not_called()  # Should not be called due to caching
            assert set(result2) == {"1x2", "btts"}

    @pytest.mark.asyncio
    @patch("src.core.scraper_app.OddsPortalScraper")
    @patch("src.core.scraper_app.OddsPortalMarketExtractor")
    @patch("src.core.scraper_app.BrowserHelper")
    @patch("src.core.scraper_app.PlaywrightManager")
    @patch("src.core.scraper_app.ProxyManager")
    @patch("src.core.scraper_app.SportMarketRegistrar")
    async def test_match_links_with_universal_auto_discovery(
        self,
        sport_market_registrar_mock,
        proxy_manager_mock,
        playwright_manager_mock,
        browser_helper_mock,
        market_extractor_mock,
        scraper_cls_mock,
        setup_mocks
    ):
        """Test match links scraping with universal auto-discovery."""
        scraper_mock = setup_mocks["scraper_mock"]
        scraper_cls_mock.return_value = scraper_mock

        # Mock proxy manager
        proxy_manager_instance = MagicMock()
        proxy_manager_instance.get_current_proxy.return_value = {"server": "test-proxy"}
        proxy_manager_mock.return_value = proxy_manager_instance

        discovered_markets = ["1x2", "over_under"]

        with patch("src.core.scraper_app._ensure_market_auto_discovery", new_callable=AsyncMock) as auto_discovery_mock:
            auto_discovery_mock.return_value = discovered_markets

            with patch("src.core.scraper_app.retry_scrape") as retry_scrape_mock:
                retry_scrape_mock.return_value = [{"match": "data"}]

                # Run scraper with match_links but no markets
                result = await run_scraper(
                    command=CommandEnum.HISTORIC,
                    match_links=["https://oddsportal.com/match1"],
                    sports="football",
                    markets=None,  # No markets - should trigger auto-discovery
                    headless=True,
                )

                # Verify auto-discovery was called
                auto_discovery_mock.assert_called_once_with("football", scraper_mock.playwright_manager.page)

                # Verify discovered markets were used
                retry_scrape_mock.assert_called_once()
                call_args = retry_scrape_mock.call_args
                assert call_args[1]["markets"] == discovered_markets

                assert result == [{"match": "data"}]