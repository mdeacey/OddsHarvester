import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.core.scraper_app import _scrape_historic_all_leagues, _scrape_historic_date_range
from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.sport_market_constants import Sport


class TestDynamicLeagueDiscoveryScraperApp:
    """Test the integration of dynamic league discovery in scraper_app."""

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_dynamic_discovery(self):
        """Test that _scrape_historic_all_leagues uses dynamic discovery."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Mock the URLBuilder.discover_leagues_for_sport to return discovered leagues
        discovered_leagues = {
            "premier_league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
            "championship": f"{ODDSPORTAL_BASE_URL}/football/england/championship",
            "laliga": f"{ODDSPORTAL_BASE_URL}/football/spain/laliga"
        }

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues) as mock_discover:
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       return_value=[{"match": "data1"}, {"match": "data2"}]) as mock_scrape_range:

                # Mock the logger to capture log messages
                with patch('src.core.scraper_app.logger') as mock_logger:
                    result = await _scrape_historic_all_leagues(
                        mock_scraper, "football", "2023", "2023"
                    )

                    # Should call dynamic discovery
                    mock_discover.assert_called_once_with("football", mock_scraper.playwright_manager.page)

                    # Should call _scrape_historic_date_range for each discovered league
                    assert mock_scrape_range.call_count == 3

                    # Verify the calls were made with correct parameters
                    calls = mock_scrape_range.call_args_list
                    league_names = [call[0][2] for call in calls]  # Get league_name from each call
                    assert "premier_league" in league_names
                    assert "championship" in league_names
                    assert "laliga" in league_names

                    # Should return combined results
                    assert len(result) == 6  # 3 leagues * 2 matches each
                    mock_logger.info.assert_called()

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_empty_discovery_result(self):
        """Test handling when dynamic discovery returns no leagues."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Mock discovery to return empty (simulating no leagues found)
        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value={}) as mock_discover:

            result = await _scrape_historic_all_leagues(
                mock_scraper, "football", "2023", "2023"
            )

            # Should call dynamic discovery
            mock_discover.assert_called_once_with("football", mock_scraper.playwright_manager.page)

            # Should return empty when no leagues discovered
            assert result == []

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_discovery_exception(self):
        """Test handling when discovery throws an exception."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Mock discovery to raise an exception
        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   side_effect=Exception("Discovery failed")) as mock_discover:

            result = await _scrape_historic_all_leagues(
                mock_scraper, "football", "2023", "2023"
            )

            # Should call dynamic discovery
            mock_discover.assert_called_once_with("football", mock_scraper.playwright_manager.page)

            # Should return empty when discovery fails
            assert result == []

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_invalid_sport(self):
        """Test handling of invalid sport names."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        result = await _scrape_historic_all_leagues(
            mock_scraper, "invalid_sport", "2023", "2023"
        )

        # Should return empty for invalid sport
        assert result == []

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_league_failure_handling(self):
        """Test that individual league failures don't stop the entire process."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        discovered_leagues = {
            "premier_league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
            "championship": f"{ODDSPORTAL_BASE_URL}/football/england/championship",
            "laliga": f"{ODDSPORTAL_BASE_URL}/football/spain/laliga"
        }

        def mock_scrape_range_side_effect(scraper, sport, league, from_date, to_date, discovered_leagues, **kwargs):
            if league == "championship":
                raise Exception("Failed to scrape championship")
            return [{"match": f"data_{league}"}]

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues):
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       side_effect=mock_scrape_range_side_effect) as mock_scrape_range:

                with patch('src.core.scraper_app.logger') as mock_logger:
                    result = await _scrape_historic_all_leagues(
                        mock_scraper, "football", "2023", "2023"
                    )

                    # Should still succeed for the working leagues
                    assert len(result) == 2  # Only 2 leagues succeeded
                    assert mock_logger.error.call_count == 1  # One error logged for failed league
                    assert mock_logger.warning.call_count == 1  # One warning for failed leagues summary

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_logs_improvement(self):
        """Test that improvements over hardcoded constants are logged."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Mock discovery to return more leagues than hardcoded constants
        discovered_leagues = {
            "premier_league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
            "championship": f"{ODDSPORTAL_BASE_URL}/football/england/championship",
            "laliga": f"{ODDSPORTAL_BASE_URL}/football/spain/laliga",
            "new_league": f"{ODDSPORTAL_BASE_URL}/football/england/new-league"  # Additional league
        }

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues):
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       return_value=[{"match": "data"}]):

                with patch('src.core.scraper_app.logger') as mock_logger:
                    await _scrape_historic_all_leagues(
                        mock_scraper, "football", "2023", "2023"
                    )

                    # Should log successful discovery completion
                    completion_logged = any(
                        "Dynamic league discovery completed" in call.args[0]
                        for call in mock_logger.info.call_args_list
                    )
                    assert completion_logged

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_all_sports_supported(self):
        """Test that dynamic discovery works for all supported sports."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Test a few different sports
        sports_to_test = ["football", "tennis", "basketball", "baseball"]

        for sport in sports_to_test:
            discovered_leagues = {
                f"test_league_{sport}": f"{ODDSPORTAL_BASE_URL}/{sport}/region/test-league"
            }

            with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                       return_value=discovered_leagues):
                with patch('src.core.scraper_app._scrape_historic_date_range',
                           return_value=[{"match": "data"}]):

                    result = await _scrape_historic_all_leagues(
                        mock_scraper, sport, "2023", "2023"
                    )

                    # Should succeed for each sport
                    assert len(result) == 1
                    assert result[0]["match"] == "data"

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_large_number_of_leagues(self):
        """Test handling of large number of discovered leagues."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        # Generate many discovered leagues
        discovered_leagues = {}
        for i in range(50):
            discovered_leagues[f"league_{i}"] = f"{ODDSPORTAL_BASE_URL}/football/region/league-{i}"

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues):
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       return_value=[{"match": "data"}]):

                result = await _scrape_historic_all_leagues(
                    mock_scraper, "football", "2023", "2023"
                )

                # Should handle all leagues
                assert len(result) == 50  # 50 leagues * 1 match each

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_kwargs_passed_through(self):
        """Test that kwargs are properly passed to _scrape_historic_date_range."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        discovered_leagues = {
            "premier_league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"
        }

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues):
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       return_value=[{"match": "data"}]) as mock_scrape_range:

                test_kwargs = {"headless": True, "timeout": 30, "custom_param": "value"}

                await _scrape_historic_all_leagues(
                    mock_scraper, "football", "2023", "2023", **test_kwargs
                )

                # Should pass kwargs through to the scrape range function
                call_kwargs = mock_scrape_range.call_args[1]  # Get kwargs from the call
                assert call_kwargs["headless"] is True
                assert call_kwargs["timeout"] == 30
                assert call_kwargs["custom_param"] == "value"

    @pytest.mark.asyncio
    async def test_scrape_historic_all_leagues_logs_discovery_info(self):
        """Test that discovery process is properly logged."""
        mock_scraper = MagicMock()
        mock_scraper.playwright_manager = MagicMock()
        mock_scraper.playwright_manager.page = AsyncMock()

        discovered_leagues = {
            "premier_league": f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
            "championship": f"{ODDSPORTAL_BASE_URL}/football/england/championship"
        }

        with patch('src.core.scraper_app.URLBuilder.discover_leagues_for_sport',
                   return_value=discovered_leagues):
            with patch('src.core.scraper_app._scrape_historic_date_range',
                       return_value=[{"match": "data"}]):

                with patch('src.core.scraper_app.logger') as mock_logger:
                    await _scrape_historic_all_leagues(
                        mock_scraper, "football", "2023", "2023"
                    )

                    # Should log discovery start
                    discovery_start_logged = any(
                        "Dynamically discovering leagues" in call.args[0]
                        for call in mock_logger.info.call_args_list
                    )
                    assert discovery_start_logged

                    # Should log discovered leagues
                    discovery_result_logged = any(
                        "Discovered 2 leagues" in call.args[0]
                        for call in mock_logger.info.call_args_list
                    )
                    assert discovery_result_logged

                    # Should log completion
                    completion_logged = any(
                        "Completed historic scraping" in call.args[0]
                        for call in mock_logger.info.call_args_list
                    )
                    assert completion_logged