import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from src.utils.change_detection_service import (
    ChangeDetectionService,
    ChangeDetectionResult,
    IncrementalScrapingManager
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def change_detection_service(temp_dir):
    """Create a ChangeDetectionService instance for testing."""
    return ChangeDetectionService(storage_dir=temp_dir, change_sensitivity="normal")


@pytest.fixture
def incremental_scraping_manager(change_detection_service):
    """Create an IncrementalScrapingManager instance for testing."""
    return IncrementalScrapingManager(change_detection_service)


@pytest.fixture
def sample_match_data():
    """Sample match data for testing."""
    return {
        "sport": "football",
        "match_date": "2025-01-01 20:00:00 UTC",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "league_name": "Premier League",
        "scraped_date": "2025-01-01 10:00:00 UTC",
        "1x2_market": {
            "current_odds": [2.0, 3.5, 4.0],
            "bookmakers": ["bet365", "bwin"],
            "odds_history": [
                {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]}
            ]
        }
    }


@pytest.fixture
def changed_match_data():
    """Sample match data with changed odds for testing."""
    return {
        "sport": "football",
        "match_date": "2025-01-01 20:00:00 UTC",
        "home_team": "Arsenal",
        "away_team": "Chelsea",
        "league_name": "Premier League",
        "scraped_date": "2025-01-01 11:00:00 UTC",
        "1x2_market": {
            "current_odds": [2.1, 3.4, 3.9],  # Changed odds
            "bookmakers": ["bet365", "bwin"],
            "odds_history": [
                {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]},
                {"timestamp": "2025-01-01 11:00:00 UTC", "odds": [2.1, 3.4, 3.9]}
            ]
        }
    }


class TestChangeDetectionResult:
    """Test suite for ChangeDetectionResult class."""

    def test_new_match_result(self):
        """Test NEW match result."""
        result = ChangeDetectionResult("NEW")

        assert result.state == "NEW"
        assert result.should_scrape is True
        assert result.should_update_history is False
        assert result.existing_data is None

    def test_unchanged_match_result(self):
        """Test UNCHANGED match result."""
        existing_data = {"test": "data"}
        result = ChangeDetectionResult("UNCHANGED", existing_data)

        assert result.state == "UNCHANGED"
        assert result.should_scrape is False
        assert result.should_update_history is False
        assert result.existing_data == existing_data

    def test_current_odds_changed_result(self):
        """Test CURRENT_ODDS_CHANGED result."""
        existing_data = {"test": "data"}
        result = ChangeDetectionResult("CURRENT_ODDS_CHANGED", existing_data)

        assert result.state == "CURRENT_ODDS_CHANGED"
        assert result.should_scrape is True
        assert result.should_update_history is True
        assert result.existing_data == existing_data

    def test_new_history_entries_result(self):
        """Test NEW_HISTORY_ENTRIES result."""
        existing_data = {"test": "data"}
        result = ChangeDetectionResult("NEW_HISTORY_ENTRIES", existing_data)

        assert result.state == "NEW_HISTORY_ENTRIES"
        assert result.should_scrape is True
        assert result.should_update_history is True
        assert result.existing_data == existing_data


class TestChangeDetectionService:
    """Test suite for ChangeDetectionService class."""

    def test_service_initialization(self, temp_dir):
        """Test ChangeDetectionService initialization."""
        service = ChangeDetectionService(temp_dir, "aggressive")

        assert service.storage_dir == Path(temp_dir)
        assert service.change_sensitivity == "aggressive"
        assert service._fingerprint_cache == {}
        assert service._data_cache == {}

    def test_analyze_new_match(self, change_detection_service, sample_match_data, temp_dir):
        """Test analysis of a new match."""
        file_path = os.path.join(temp_dir, "test.json")

        result = change_detection_service.analyze_match(sample_match_data, file_path)

        assert isinstance(result, ChangeDetectionResult)
        assert result.state == "NEW"
        assert result.should_scrape is True

    def test_analyze_unchanged_match(self, change_detection_service, sample_match_data, temp_dir):
        """Test analysis of an unchanged match."""
        file_path = os.path.join(temp_dir, "test.json")

        # First, create an existing file with the match data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        result = change_detection_service.analyze_match(sample_match_data, file_path)

        assert isinstance(result, ChangeDetectionResult)
        assert result.state == "UNCHANGED"
        assert result.should_scrape is False

    def test_analyze_changed_match(self, change_detection_service, sample_match_data, changed_match_data, temp_dir):
        """Test analysis of a changed match."""
        file_path = os.path.join(temp_dir, "test.json")

        # First, create an existing file with the original match data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        result = change_detection_service.analyze_match(changed_match_data, file_path)

        assert isinstance(result, ChangeDetectionResult)
        assert result.state == "CURRENT_ODDS_CHANGED"
        assert result.should_scrape is True

    def test_load_existing_data_json_file_not_exists(self, change_detection_service, temp_dir):
        """Test loading existing data when file doesn't exist."""
        file_path = os.path.join(temp_dir, "nonexistent.json")

        result = change_detection_service._load_existing_data(file_path, "test_fingerprint")

        assert result is None

    def test_load_existing_data_json_file_exists(self, change_detection_service, sample_match_data, temp_dir):
        """Test loading existing data from existing JSON file."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create file with test data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        # Generate the actual fingerprint for the test data
        actual_fingerprint = change_detection_service.fingerprint_generator.generate_identity_fingerprint(sample_match_data)

        result = change_detection_service._load_existing_data(
            file_path,
            actual_fingerprint  # Use the actual fingerprint
        )

        assert result is not None
        assert result == sample_match_data

    def test_fingerprint_caching(self, change_detection_service, sample_match_data, temp_dir):
        """Test that fingerprints are cached properly."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create file with test data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        # First call should populate cache
        result1 = change_detection_service.analyze_match(sample_match_data, file_path)

        # Check cache is populated
        assert len(change_detection_service._fingerprint_cache) > 0

        # Second call should use cache
        result2 = change_detection_service.analyze_match(sample_match_data, file_path)

        assert result1.state == result2.state

    def test_clear_cache(self, change_detection_service, sample_match_data, temp_dir):
        """Test cache clearing functionality."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create file and analyze to populate cache
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        change_detection_service.analyze_match(sample_match_data, file_path)

        # Verify cache is populated
        assert len(change_detection_service._fingerprint_cache) > 0
        assert len(change_detection_service._data_cache) > 0

        # Clear cache
        change_detection_service.clear_cache()

        # Verify cache is empty
        assert len(change_detection_service._fingerprint_cache) == 0
        assert len(change_detection_service._data_cache) == 0

    def test_get_cache_stats(self, change_detection_service, sample_match_data, temp_dir):
        """Test cache statistics functionality."""
        file_path = os.path.join(temp_dir, "test.json")

        # Initial stats should be empty
        stats = change_detection_service.get_cache_stats()
        assert stats["fingerprint_cache_size"] == 0
        assert stats["data_cache_size"] == 0

        # Analyze to populate cache
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        change_detection_service.analyze_match(sample_match_data, file_path)

        # Stats should show cache usage
        stats = change_detection_service.get_cache_stats()
        assert stats["fingerprint_cache_size"] > 0
        assert stats["data_cache_size"] > 0

    def test_error_handling_in_analysis(self, change_detection_service, temp_dir):
        """Test error handling in match analysis."""
        file_path = os.path.join(temp_dir, "test.json")

        # Test with invalid match data (missing required fields)
        invalid_data = {"home_team": "Arsenal"}  # Missing required fields

        result = change_detection_service.analyze_match(invalid_data, file_path)

        # Should default to NEW state when detection fails
        assert result.state == "NEW"
        assert result.should_scrape is True

    def test_csv_file_not_implemented(self, change_detection_service, temp_dir):
        """Test that CSV files return None (not fully implemented)."""
        file_path = os.path.join(temp_dir, "test.csv")
        sample_data = {"home_team": "Arsenal", "away_team": "Chelsea"}

        result = change_detection_service._load_existing_data(file_path, "test_fp")

        assert result is None  # CSV change detection not implemented


class TestIncrementalScrapingManager:
    """Test suite for IncrementalScrapingManager class."""

    def test_manager_initialization(self, change_detection_service):
        """Test IncrementalScrapingManager initialization."""
        manager = IncrementalScrapingManager(change_detection_service)

        assert manager.change_detection_service == change_detection_service
        assert manager.metrics["total_matches_analyzed"] == 0
        assert manager.metrics["new_matches"] == 0

    def test_filter_matches_all_new(self, incremental_scraping_manager, sample_match_data, temp_dir):
        """Test filtering when all matches are new."""
        file_path = os.path.join(temp_dir, "test.json")
        matches = [sample_match_data]

        filtered_matches, results = incremental_scraping_manager.filter_matches_for_scraping(
            matches, file_path
        )

        assert len(filtered_matches) == 1
        assert len(results) == 1
        assert results["match_0"].state == "NEW"

        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["new_matches"] == 1
        assert metrics["total_matches_analyzed"] == 1

    def test_filter_matches_all_unchanged(self, incremental_scraping_manager, sample_match_data, temp_dir):
        """Test filtering when all matches are unchanged."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create existing file with match data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        matches = [sample_match_data]

        filtered_matches, results = incremental_scraping_manager.filter_matches_for_scraping(
            matches, file_path
        )

        assert len(filtered_matches) == 0  # Should be filtered out
        assert len(results) == 1
        assert results["match_0"].state == "UNCHANGED"

        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["unchanged_matches"] == 1
        assert metrics["scrapes_skipped"] == 1

    def test_filter_mixed_matches(self, incremental_scraping_manager, sample_match_data, changed_match_data, temp_dir):
        """Test filtering with mixed new and unchanged matches."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create existing file with original match data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        # Test with original (unchanged) and changed match
        new_match = {
            "sport": "football",
            "match_date": "2025-01-02 20:00:00 UTC",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league_name": "Premier League",
            "scraped_date": "2025-01-01 10:00:00 UTC"
        }

        matches = [sample_match_data, changed_match_data, new_match]

        filtered_matches, results = incremental_scraping_manager.filter_matches_for_scraping(
            matches, file_path
        )

        # Should include changed and new matches, but not unchanged
        assert len(filtered_matches) == 2
        assert len(results) == 3

        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["unchanged_matches"] == 1
        assert metrics["current_odds_changed_matches"] == 1
        assert metrics["new_matches"] == 1
        assert metrics["scrapes_skipped"] == 1

    def test_performance_metrics_calculation(self, incremental_scraping_manager, sample_match_data, temp_dir):
        """Test performance metrics calculation."""
        file_path = os.path.join(temp_dir, "test.json")

        # Create existing file with match data
        with open(file_path, 'w') as f:
            json.dump([sample_match_data], f)

        matches = [sample_match_data] * 2  # 2 unchanged matches

        incremental_scraping_manager.filter_matches_for_scraping(matches, file_path)

        metrics = incremental_scraping_manager.get_performance_metrics()

        assert metrics["total_matches_analyzed"] == 2
        assert metrics["unchanged_matches"] == 2
        assert metrics["scrapes_skipped"] == 2
        assert metrics["scraping_efficiency"] == 100.0  # 2/2 * 100

        # Check change distribution
        distribution = metrics["change_distribution"]
        assert distribution["unchanged_matches_percent"] == 100.0
        assert distribution["new_matches_percent"] == 0.0

    def test_reset_metrics(self, incremental_scraping_manager, sample_match_data, temp_dir):
        """Test metrics reset functionality."""
        file_path = os.path.join(temp_dir, "test.json")

        # Generate some metrics
        incremental_scraping_manager.filter_matches_for_scraping([sample_match_data], file_path)

        # Verify metrics exist
        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["total_matches_analyzed"] > 0

        # Reset metrics
        incremental_scraping_manager.reset_metrics()

        # Verify metrics are reset
        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["total_matches_analyzed"] == 0
        assert metrics["new_matches"] == 0

    def test_empty_matches_list(self, incremental_scraping_manager, temp_dir):
        """Test filtering with empty matches list."""
        file_path = os.path.join(temp_dir, "test.json")

        filtered_matches, results = incremental_scraping_manager.filter_matches_for_scraping(
            [], file_path
        )

        assert len(filtered_matches) == 0
        assert len(results) == 0

        metrics = incremental_scraping_manager.get_performance_metrics()
        assert metrics["total_matches_analyzed"] == 0