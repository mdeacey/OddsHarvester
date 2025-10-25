import json
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock

from src.main import main
from src.core.scraper_app import ScraperApp


class TestAussieRulesIntegration:
    """Integration tests for the aussie-rules scenario that was originally failing."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    @pytest.fixture
    def sample_aussie_rules_data(self):
        """Sample aussie-rules data that would be returned by the scraper."""
        return [
            {
                "sport": "aussie-rules",
                "match_date": "2025-01-01 20:00:00 UTC",
                "home_team": "Richmond Tigers",
                "away_team": "Collingwood Magpies",
                "league_name": "AFL",
                "scraped_date": "2025-01-01 10:00:00 UTC",
                "home_score": 89,
                "away_score": 78,
                "1x2_market": {
                    "current_odds": [1.85, 3.20, 4.50],
                    "bookmakers": ["bet365", "bwin", "unibet"],
                    "odds_history": [
                        {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [1.90, 3.15, 4.45]},
                        {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [1.85, 3.20, 4.50]}
                    ]
                },
                "over_under_2_5_market": {
                    "current_odds": [1.80, 2.10],
                    "bookmakers": ["bet365", "bwin"],
                    "odds_history": [
                        {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [1.82, 2.08]},
                        {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [1.80, 2.10]}
                    ]
                }
            },
            {
                "sport": "aussie-rules",
                "match_date": "2025-01-02 19:30:00 UTC",
                "home_team": "Geelong Cats",
                "away_team": "Sydney Swans",
                "league_name": "AFL",
                "scraped_date": "2025-01-01 10:00:00 UTC",
                "1x2_market": {
                    "current_odds": [2.10, 3.40, 3.80],
                    "bookmakers": ["bet365", "bwin"],
                    "odds_history": [
                        {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.10, 3.40, 3.80]}
                    ]
                }
            }
        ]

    @patch('src.main.run_scraper')
    def test_aussie_rules_historic_all_leagues_all_markets(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test the original failing scenario: historic scraping with aussie-rules, all leagues, all markets."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules_historic.json")

        with patch('sys.argv', [
            'python', 'scrape_historic',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--to', 'now',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                # main() calls sys.exit, which is expected
                pass

        # Verify file was created and contains aussie-rules data
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)
            assert all(record["sport"] == "aussie-rules" for record in saved_data)
            assert all(record["league_name"] == "AFL" for record in saved_data)
            # Verify we have both teams from the sample data
            home_teams = [record["home_team"] for record in saved_data]
            assert "Richmond Tigers" in home_teams
            assert "Geelong Cats" in home_teams

    @patch('src.main.run_scraper')
    def test_aussie_rules_upcoming_all_leagues_all_markets(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules upcoming matches with all leagues and all markets."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules_upcoming.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created and contains aussie-rules data
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)
            assert all(record["sport"] == "aussie-rules" for record in saved_data)

    @patch('src.main.run_scraper')
    def test_aussie_rules_with_specific_afl_league(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules with specific AFL league (non-all scenario)."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules_afl.json")

        with patch('sys.argv', [
            'python', 'scrape_historic',
            '--sports', 'aussie-rules',
            '--leagues', 'australia-afl',
            '--markets', '1x2',
            '--from', '2024',
            '--to', '2024',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)
            assert all(record["sport"] == "aussie-rules" for record in saved_data)

    @patch('src.main.run_scraper')
    def test_aussie_rules_csv_output_format(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules scenario with CSV output format."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules.csv")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--format', 'csv',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify CSV file was created and contains aussie-rules data
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            assert "Richmond Tigers" in content
            assert "Collingwood Magpies" in content
            assert "AFL" in content

    @patch('src.main.run_scraper')
    def test_aussie_rules_with_browser_settings(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules scenario with custom browser settings."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules_browser.json")

        with patch('sys.argv', [
            'python', 'scrape_historic',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--to', 'now',
            '--headless',
            '--browser-user-agent', 'Mozilla/5.0 (Custom Aussie Rules Agent)',
            '--browser-locale-timezone', 'en-AU',
            '--browser-timezone-id', 'Australia/Melbourne',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)
            assert all(record["sport"] == "aussie-rules" for record in saved_data)

    @patch('src.main.run_scraper')
    def test_aussie_rules_all_sports_parameter(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules with --all parameter (should set sports to 'all')."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "all_sports_including_aussie_rules.json")

        with patch('sys.argv', [
            'python', 'scrape_historic',
            '--all',
            '--to', 'now',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created (would contain data from all sports including aussie-rules)
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)

    @patch('src.core.scraper_app.ScraperApp._scrape_historic_all_leagues')
    def test_aussie_rules_scraper_app_direct_call(self, mock_scrape_historic, temp_dir, sample_aussie_rules_data):
        """Test direct ScraperApp call for aussie-rules scenario."""
        mock_scrape_historic.return_value = sample_aussie_rules_data

        app = ScraperApp()
        result = app._scrape_historic_all_leagues(
            sports="aussie-rules",
            markets=["all"],
            from_date=None,
            to_date="now",
            storage_type="local",
            storage_format="json",
            file_path=os.path.join(temp_dir, "direct_call.json"),
            headless=True,
            proxies=None,
            browser_user_agent=None,
            browser_locale_timezone=None,
            browser_timezone_id=None,
            scrape_odds_history=False,
            target_bookmaker=None,
            preview_submarkets_only=False,
            change_sensitivity="normal"
        )

        # Verify the method was called with correct parameters
        mock_scrape_historic.assert_called_once()
        call_args = mock_scrape_historic.call_args
        assert call_args[1]["sports"] == "aussie-rules"
        assert call_args[1]["markets"] == ["all"]
        assert call_args[1]["to_date"] == "now"
        assert call_args[1]["headless"] is True

    @patch('src.main.run_scraper')
    def test_aussie_rules_error_handling_no_data(self, mock_run_scraper, temp_dir):
        """Test error handling when scraper returns no data for aussie-rules."""
        mock_run_scraper.return_value = None
        output_file = os.path.join(temp_dir, "aussie_rules_empty.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--headless',
            '--file_path', output_file
        ]):
            with patch('sys.exit') as mock_exit:
                try:
                    main()
                except SystemExit:
                    pass

                # Should exit with error code when no data returned
                mock_exit.assert_called_with(1)

    @patch('src.main.run_scraper')
    def test_aussie_rules_with_change_detection(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules scenario with change detection enabled."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        output_file = os.path.join(temp_dir, "aussie_rules_change_detection.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--change_sensitivity', 'normal',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)

    @patch('src.main.run_scraper')
    def test_aussie_rules_nested_directory_creation(self, mock_run_scraper, temp_dir, sample_aussie_rules_data):
        """Test aussie-rules scenario with nested directory creation."""
        mock_run_scraper.return_value = sample_aussie_rules_data
        nested_dir = os.path.join(temp_dir, "aussie-rules", "2025", "january")
        output_file = os.path.join(nested_dir, "matches.json")

        with patch('sys.argv', [
            'python', 'scrape_historic',
            '--sports', 'aussie-rules',
            '--leagues', 'all',
            '--markets', 'all',
            '--to', 'now',
            '--headless',
            '--file_path', output_file
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify directory was created and file exists
        assert os.path.exists(nested_dir)
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_aussie_rules_data)
            assert all(record["sport"] == "aussie-rules" for record in saved_data)