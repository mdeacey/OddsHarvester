import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
from bs4 import BeautifulSoup

from src.core.url_builder import URLBuilder
from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.sport_market_constants import Sport


class TestDiscoverLeaguesForSport:
    """Test the discover_leagues_for_sport method and its helper functions."""

    @pytest.mark.asyncio
    async def test_discover_leagues_success_with_links(self):
        """Test successful league discovery with direct links."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Mock HTML content with league links
        html_content = f"""
        <html>
            <body>
                <a href="/football/england/premier-league/">Premier League</a>
                <a href="/football/england/championship/">Championship</a>
                <a href="/football/spain/laliga/">La Liga</a>
                <a href="/football/italy/serie-a/">Serie A</a>
                <a href="/matches/football/2025-01-01/">Today's Matches</a>
                <a href="/football/results/">All Football Results</a>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should discover 4 valid leagues (exclude matches and main results page)
        assert len(leagues) == 4
        assert "premier_league" in leagues
        assert "championship" in leagues
        assert "laliga" in leagues
        assert "serie_a" in leagues

        # Check URL format
        for league_name, league_url in leagues.items():
            assert league_url.startswith(ODDSPORTAL_BASE_URL)
            assert "/football/" in league_url

    @pytest.mark.asyncio
    async def test_discover_leagues_with_results_links(self):
        """Test league discovery with /results/ links."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        html_content = f"""
        <html>
            <body>
                <a href="/football/england/premier-league/results/">Premier League Results</a>
                <a href="/football/germany/bundesliga/results/">Bundesliga Results</a>
                <a href="/football/france/ligue-1/results/">Ligue 1 Results</a>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should discover 3 leagues
        assert len(leagues) == 3
        assert "premier_league" in leagues
        assert "bundesliga" in leagues
        assert "ligue_1" in leagues

    @pytest.mark.asyncio
    async def test_discover_leagues_no_links_found_returns_empty(self):
        """Test that discovery returns empty when no leagues found."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>No league links here</body></html>")

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should return empty when no leagues discovered
        assert leagues == {}

    @pytest.mark.asyncio
    async def test_discover_leagues_navigation_error_returns_empty(self):
        """Test that discovery returns empty on navigation error."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Navigation failed"))

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should return empty when navigation fails
        assert leagues == {}

    @pytest.mark.asyncio
    async def test_discover_leagues_invalid_sport(self):
        """Test handling of invalid sport names."""
        mock_page = AsyncMock()

        leagues = await URLBuilder.discover_leagues_for_sport("invalid_sport", mock_page)

        # Should return empty dict for invalid sport
        assert leagues == {}

    @pytest.mark.asyncio
    async def test_discover_leagues_content_based_discovery(self):
        """Test content-based league discovery when no links found."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        html_content = """
        <html>
            <body>
                <div class="leagues">
                    <div>Premier League</div>
                    <div>Championship</div>
                    <div>La Liga</div>
                </div>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should discover some leagues from content (this is a fallback method)
        assert len(leagues) > 0

    @pytest.mark.asyncio
    async def test_discover_leagues_excludes_invalid_links(self):
        """Test that invalid links are properly excluded."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        html_content = f"""
        <html>
            <body>
                <a href="/football/england/premier-league/">Valid League</a>
                <a href="#anchor">Anchor Link</a>
                <a href="javascript:void(0)">JavaScript Link</a>
                <a href="/matches/football/2025-01-01/">Matches Link</a>
                <a href="/football/results/">Main Results Page</a>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should only discover the valid league
        assert len(leagues) == 1
        assert "premier_league" in leagues


class TestExtractLeagueInfo:
    """Test the _extract_league_info helper method."""

    def test_extract_league_info_standard_path(self):
        """Test extracting league info from standard /sport/region/league/ path."""
        href = "/football/england/premier-league/"
        league_name, league_url = URLBuilder._extract_league_info(href, "football")

        assert league_name == "premier_league"
        assert league_url == f"{ODDSPORTAL_BASE_URL}/football/england/premier-league/"

    def test_extract_league_info_direct_path(self):
        """Test extracting league info from /sport/league/ path."""
        href = "/tennis/wimbledon/"
        league_name, league_url = URLBuilder._extract_league_info(href, "tennis")

        assert league_name == "wimbledon"
        assert league_url == f"{ODDSPORTAL_BASE_URL}/tennis/wimbledon/"

    def test_extract_league_info_full_url(self):
        """Test extracting league info from full URL."""
        full_url = f"{ODDSPORTAL_BASE_URL}/basketball/usa/nba/"
        league_name, league_url = URLBuilder._extract_league_info(full_url, "basketball")

        assert league_name == "nba"
        assert league_url == full_url

    def test_extract_league_info_main_sport_page(self):
        """Test that main sport pages are excluded."""
        href = "/football/results/"
        league_name, league_url = URLBuilder._extract_league_info(href, "football")

        assert league_name is None
        assert league_url is None

        href = "/football/"
        league_name, league_url = URLBuilder._extract_league_info(href, "football")

        assert league_name is None
        assert league_url is None

    def test_extract_league_info_wrong_sport(self):
        """Test that links for other sports are excluded."""
        href = "/tennis/wimbledon/"
        league_name, league_url = URLBuilder._extract_league_info(href, "football")

        assert league_name is None
        assert league_url is None

    def test_extract_league_info_invalid_format(self):
        """Test handling of invalid href formats."""
        invalid_hrefs = [
            "/",
            "",
            "invalid",
            "/football/",
            "random text"
        ]

        for href in invalid_hrefs:
            league_name, league_url = URLBuilder._extract_league_info(href, "football")
            assert league_name is None
            assert league_url is None

    def test_extract_league_info_numeric_league_name(self):
        """Test that numeric league names are excluded."""
        href = "/football/2024/"
        league_name, league_url = URLBuilder._extract_league_info(href, "football")

        assert league_name is None
        assert league_url is None


class TestIsValidLeagueUrl:
    """Test the _is_valid_league_url helper method."""

    def test_is_valid_league_url_valid_urls(self):
        """Test validation of valid league URLs."""
        valid_urls = [
            f"{ODDSPORTAL_BASE_URL}/football/england/premier-league",
            f"{ODDSPORTAL_BASE_URL}/tennis/atp-tour/",
            f"{ODDSPORTAL_BASE_URL}/basketball/usa/nba/results",
            f"{ODDSPORTAL_BASE_URL}/baseball/japan/npb/2024"
        ]

        for url in valid_urls:
            sport = url.split("/")[3]  # Extract sport from URL
            assert URLBuilder._is_valid_league_url(url, sport) is True

    def test_is_valid_league_url_invalid_domain(self):
        """Test rejection of URLs with wrong domain."""
        invalid_url = "https://www.example.com/football/england/premier-league"
        assert URLBuilder._is_valid_league_url(invalid_url, "football") is False

    def test_is_valid_league_url_wrong_sport(self):
        """Test rejection of URLs with wrong sport."""
        url = f"{ODDSPORTAL_BASE_URL}/football/england/premier-league"
        assert URLBuilder._is_valid_league_url(url, "tennis") is False

    def test_is_valid_league_url_main_pages(self):
        """Test rejection of main sport pages."""
        exclusion_patterns = [
            f"{ODDSPORTAL_BASE_URL}/football/results/",
            f"{ODDSPORTAL_BASE_URL}/football/",
            f"{ODDSPORTAL_BASE_URL}/tennis/matches/",
            f"{ODDSPORTAL_BASE_URL}/basketball/live/"
        ]

        for url in exclusion_patterns:
            sport = url.split("/")[3]  # Extract sport from URL
            assert URLBuilder._is_valid_league_url(url, sport) is False

    def test_is_valid_league_url_insufficient_path(self):
        """Test rejection of URLs with insufficient path structure."""
        insufficient_urls = [
            f"{ODDSPORTAL_BASE_URL}/football",
            f"{ODDSPORTAL_BASE_URL}/"
        ]

        for url in insufficient_urls:
            assert URLBuilder._is_valid_league_url(url, "football") is False


class TestDiscoverLeaguesFromContent:
    """Test the _discover_leagues_from_content helper method."""

    def test_discover_leagues_from_content_basic(self):
        """Test basic content-based league discovery."""
        html = """
        <div class="leagues">
            <div>Premier League</div>
            <div>Championship</div>
            <div>La Liga</div>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        leagues = URLBuilder._discover_leagues_from_content(soup, "football")

        assert len(leagues) > 0
        # Should find some leagues from the content

    def test_discover_leagues_from_content_with_classes(self):
        """Test content discovery with specific HTML classes."""
        html = """
        <div class="league-section">
            <h3>English Premier League</h3>
        </div>
        <div class="competition-list">
            <span>La Liga</span>
            <span>Bundesliga</span>
        </div>
        """
        soup = BeautifulSoup(html, 'html.parser')
        leagues = URLBuilder._discover_leagues_from_content(soup, "football")

        assert len(leagues) > 0

    def test_discover_leagues_from_content_no_content(self):
        """Test content discovery with no relevant content."""
        html = "<div>No leagues here</div>"
        soup = BeautifulSoup(html, 'html.parser')
        leagues = URLBuilder._discover_leagues_from_content(soup, "football")

        # Should return empty dict when no leagues found
        assert leagues == {}

    def test_discover_leagues_from_content_error_handling(self):
        """Test error handling in content discovery."""
        # Pass invalid soup object (should handle gracefully)
        leagues = URLBuilder._discover_leagues_from_content(None, "football")
        assert leagues == {}


class TestDynamicLeagueDiscoveryIntegration:
    """Integration tests for the complete dynamic league discovery system."""

    @pytest.mark.asyncio
    async def test_complete_discovery_workflow(self):
        """Test the complete workflow from sport to discovered leagues."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Simulate realistic OddsPortal page structure
        html_content = f"""
        <html>
            <body>
                <div class="main-menu">
                    <a href="/football/results/">All Football</a>
                    <a href="/football/england/premier-league/">Premier League</a>
                    <a href="/football/england/championship/">Championship</a>
                    <a href="/football/spain/laliga/">La Liga</a>
                    <a href="/football/italy/serie-a/">Serie A</a>
                </div>
                <div class="other-content">
                    <a href="/matches/football/2025-01-01/">Today</a>
                    <a href="/football/live/">Live</a>
                </div>
            </body>
        </html>
        """
        mock_page.content = AsyncMock(return_value=html_content)

        # Test the discovery
        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should discover exactly the valid leagues
        assert len(leagues) == 4
        expected_leagues = ["premier_league", "championship", "laliga", "serie_a"]
        for league in expected_leagues:
            assert league in leagues

        # Verify URL construction
        for league_name, league_url in leagues.items():
            assert league_url.startswith(ODDSPORTAL_BASE_URL)
            assert "/football/" in league_url
            assert league_url.endswith("/")

    @pytest.mark.asyncio
    async def test_discovery_with_different_sports(self):
        """Test discovery works for different sports."""
        sports_to_test = ["football", "tennis", "basketball"]

        for sport in sports_to_test:
            mock_page = AsyncMock()
            mock_page.goto = AsyncMock()
            mock_page.wait_for_timeout = AsyncMock()
            mock_page.content = AsyncMock(return_value=f"<html><body>No {sport} leagues</body></html>")

            leagues = await URLBuilder.discover_leagues_for_sport(sport, mock_page)

            # Should return empty when no leagues found
            assert leagues == {}

    @pytest.mark.asyncio
    async def test_discovery_performance_with_many_leagues(self):
        """Test discovery performance with a large number of leagues."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()

        # Generate HTML with many league links
        leagues_html = ""
        for i in range(100):
            leagues_html += f'<a href="/football/region/league-{i}/">League {i}</a>\n'

        html_content = f"<html><body>{leagues_html}</body></html>"
        mock_page.content = AsyncMock(return_value=html_content)

        leagues = await URLBuilder.discover_leagues_for_sport("football", mock_page)

        # Should discover all valid leagues
        assert len(leagues) == 100

        # Verify all have proper naming and URL structure
        for i in range(100):
            expected_name = f"league_{i}"
            assert expected_name in leagues
            assert leagues[expected_name] == f"{ODDSPORTAL_BASE_URL}/football/region/league-{i}/"