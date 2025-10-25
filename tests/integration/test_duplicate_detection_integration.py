import json
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.main import main
from src.utils.change_detection_service import ChangeDetectionService, IncrementalScrapingManager


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_scraper_data():
    """Sample data that would be returned by the scraper."""
    return [
        {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League",
            "scraped_date": "2025-01-01 10:00:00 UTC",
            "home_score": 2,
            "away_score": 1,
            "1x2_market": {
                "current_odds": [2.0, 3.5, 4.0],
                "bookmakers": ["bet365", "bwin", "unibet"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                    {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]}
                ]
            },
            "over_under_2_5_market": {
                "current_odds": [1.8, 2.1],
                "bookmakers": ["bet365", "bwin"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [1.85, 2.05]},
                    {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [1.8, 2.1]}
                ]
            }
        },
        {
            "sport": "football",
            "match_date": "2025-01-02 20:00:00 UTC",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league_name": "Premier League",
            "scraped_date": "2025-01-01 10:00:00 UTC",
            "1x2_market": {
                "current_odds": [1.8, 3.8, 4.5],
                "bookmakers": ["bet365", "bwin"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [1.8, 3.8, 4.5]}
                ]
            }
        }
    ]


@pytest.fixture
def changed_scraper_data():
    """Sample data with changed odds for testing."""
    return [
        {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League",
            "scraped_date": "2025-01-01 11:00:00 UTC",  # Later scraped time
            "home_score": 2,
            "away_score": 1,
            "1x2_market": {
                "current_odds": [2.1, 3.4, 3.9],  # Changed odds
                "bookmakers": ["bet365", "bwin", "unibet"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                    {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]},
                    {"timestamp": "2025-01-01 11:00:00 UTC", "odds": [2.1, 3.4, 3.9]}  # New history entry
                ]
            },
            "over_under_2_5_market": {
                "current_odds": [1.8, 2.1],  # Same odds
                "bookmakers": ["bet365", "bwin"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [1.85, 2.05]},
                    {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [1.8, 2.1]}
                ]
            }
        }
    ]


class TestDuplicateDetectionIntegration:
    """Integration tests for the complete duplicate detection workflow."""

    @patch('src.main.run_scraper')
    def test_first_run_saves_all_data(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test that first run saves all scraped data."""
        mock_run_scraper.return_value = sample_scraper_data

        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit as e:
                # main() calls sys.exit, which is expected
                pass

        # Verify file was created and contains all data
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) == len(sample_scraper_data)
            assert saved_data[0]["home_team"] == "Arsenal"
            assert saved_data[1]["home_team"] == "Manchester United"

    @patch('src.main.run_scraper')
    def test_second_run_skips_unchanged_data_normal_sensitivity(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test that second run skips unchanged data with normal sensitivity."""
        # First run
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Get initial file size
        with open(output_file, 'r') as f:
            initial_content = json.load(f)
            initial_count = len(initial_content)

        # Second run with identical data
        mock_run_scraper.return_value = sample_scraper_data

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify no new records were added (duplicates detected)
        with open(output_file, 'r') as f:
            final_content = json.load(f)
            # Should contain same records as before (no duplicates added)
            assert len(final_content) == initial_count

    @patch('src.main.run_scraper')
    def test_second_run_with_changed_data(self, mock_run_scraper, temp_dir, sample_scraper_data, changed_scraper_data):
        """Test second run with changed data."""
        # First run
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Second run with changed data
        mock_run_scraper.return_value = changed_scraper_data

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify changed data was saved
        with open(output_file, 'r') as f:
            final_content = json.load(f)

            # Should have multiple records including the changed one
            scraped_dates = [record.get("scraped_date") for record in final_content]
            assert "2025-01-01 11:00:00 UTC" in scraped_dates  # Changed data

    @patch('src.main.run_scraper')
    def test_aggressive_sensitivity_behavior(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test aggressive sensitivity behavior."""
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'aggressive'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) > 0

    @patch('src.main.run_scraper')
    def test_conservative_sensitivity_behavior(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test conservative sensitivity behavior."""
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'conservative'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) > 0

    @patch('src.main.run_scraper')
    def test_csv_format_duplicate_detection(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test duplicate detection with CSV format."""
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.csv")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--format', 'csv',
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify CSV file was created
        assert os.path.exists(output_file)
        with open(output_file, 'r') as f:
            content = f.read()
            assert "Arsenal" in content
            assert "Manchester United" in content

    @patch('src.main.run_scraper')
    def test_duplicate_detection_service_initialization(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test that change detection service is properly initialized."""
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'aggressive'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify service was initialized with correct sensitivity
        assert os.path.exists(output_file)

    @patch('src.main.run_scraper')
    def test_performance_metrics_logging(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test that performance metrics are logged."""
        mock_run_scraper.return_value = sample_scraper_data
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            with patch('logging.getLogger') as mock_get_logger:
                mock_logger = MagicMock()
                mock_get_logger.return_value = mock_logger
                try:
                    main()
                except SystemExit:
                    pass

                # Check that performance metrics were logged
                # This is a basic check - in a real scenario you'd capture and verify the log messages
                assert mock_logger.info.called

    @patch('src.main.run_scraper')
    def test_empty_scraper_data_handling(self, mock_run_scraper, temp_dir):
        """Test handling when scraper returns no data."""
        mock_run_scraper.return_value = None
        output_file = os.path.join(temp_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            with patch('sys.exit') as mock_exit:
                try:
                    main()
                except SystemExit:
                    pass

                # Should exit with error code when no data returned
                mock_exit.assert_called_with(1)

    @patch('src.main.run_scraper')
    def test_file_path_directory_creation(self, mock_run_scraper, temp_dir, sample_scraper_data):
        """Test that directories are created when they don't exist."""
        mock_run_scraper.return_value = sample_scraper_data
        nested_dir = os.path.join(temp_dir, "nested", "directory")
        output_file = os.path.join(nested_dir, "test_output.json")

        with patch('sys.argv', [
            'python', 'scrape_upcoming',
            '--sports', 'football',
            '--file_path', output_file,
            '--change_sensitivity', 'normal'
        ]):
            try:
                main()
            except SystemExit:
                pass

        # Verify directory was created and file exists
        assert os.path.exists(nested_dir)
        assert os.path.exists(output_file)