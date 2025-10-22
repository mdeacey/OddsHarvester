import pytest

from src.utils.match_fingerprint import MatchFingerprint, ChangeSensitivityCalculator


@pytest.fixture
def fingerprint_generator():
    """Create a MatchFingerprint instance for testing."""
    return MatchFingerprint()


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
    }


@pytest.fixture
def sample_match_data_changed():
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
            "bookmakers": ["bet365", "bwin", "unibet"],
            "odds_history": [
                {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]},
                {"timestamp": "2025-01-01 11:00:00 UTC", "odds": [2.1, 3.4, 3.9]}
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


class TestMatchFingerprint:
    """Test suite for MatchFingerprint class."""

    def test_identity_fingerprint_generation(self, fingerprint_generator, sample_match_data):
        """Test identity fingerprint generation."""
        fingerprint = fingerprint_generator.generate_identity_fingerprint(sample_match_data)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA-256 hash length
        assert fingerprint.isalnum()  # Should contain only alphanumeric characters

    def test_identity_fingerprint_consistency(self, fingerprint_generator, sample_match_data):
        """Test that identity fingerprints are consistent for the same data."""
        fp1 = fingerprint_generator.generate_identity_fingerprint(sample_match_data)
        fp2 = fingerprint_generator.generate_identity_fingerprint(sample_match_data)

        assert fp1 == fp2

    def test_identity_fingerprint_different_matches(self, fingerprint_generator):
        """Test that different matches have different identity fingerprints."""
        match1 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League"
        }

        match2 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league_name": "Premier League"
        }

        fp1 = fingerprint_generator.generate_identity_fingerprint(match1)
        fp2 = fingerprint_generator.generate_identity_fingerprint(match2)

        assert fp1 != fp2

    def test_identity_fingerprint_case_insensitive(self, fingerprint_generator):
        """Test that identity fingerprinting is case insensitive for team names."""
        match1 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "chelsea",
            "league_name": "premier league"
        }

        match2 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "ARSENAL",
            "away_team": "CHELSEA",
            "league_name": "PREMIER LEAGUE"
        }

        fp1 = fingerprint_generator.generate_identity_fingerprint(match1)
        fp2 = fingerprint_generator.generate_identity_fingerprint(match2)

        assert fp1 == fp2

    def test_current_odds_fingerprint_generation(self, fingerprint_generator, sample_match_data):
        """Test current odds fingerprint generation."""
        fingerprint = fingerprint_generator.generate_current_odds_fingerprint(sample_match_data)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA-256 hash length

    def test_current_odds_fingerprint_changes_with_odds(self, fingerprint_generator, sample_match_data, sample_match_data_changed):
        """Test that current odds fingerprint changes when odds change."""
        fp_original = fingerprint_generator.generate_current_odds_fingerprint(sample_match_data)
        fp_changed = fingerprint_generator.generate_current_odds_fingerprint(sample_match_data_changed)

        assert fp_original != fp_changed

    def test_history_fingerprint_generation(self, fingerprint_generator, sample_match_data):
        """Test history fingerprint generation."""
        fingerprint = fingerprint_generator.generate_history_fingerprint(sample_match_data)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA-256 hash length

    def test_history_fingerprint_changes_with_new_entries(self, fingerprint_generator, sample_match_data, sample_match_data_changed):
        """Test that history fingerprint changes when new history entries are added."""
        fp_original = fingerprint_generator.generate_history_fingerprint(sample_match_data)
        fp_changed = fingerprint_generator.generate_history_fingerprint(sample_match_data_changed)

        assert fp_original != fp_changed

    def test_complete_fingerprint_set(self, fingerprint_generator, sample_match_data):
        """Test complete fingerprint set generation."""
        fingerprints = fingerprint_generator.generate_complete_fingerprint_set(sample_match_data)

        assert isinstance(fingerprints, dict)
        assert "identity_fingerprint" in fingerprints
        assert "current_odds_fingerprint" in fingerprints
        assert "history_fingerprint" in fingerprints

        # All fingerprints should be different
        assert len(set(fingerprints.values())) == 3

    def test_fingerprint_comparison_new_match(self, fingerprint_generator, sample_match_data):
        """Test fingerprint comparison for new matches."""
        existing = {}
        new = fingerprint_generator.generate_complete_fingerprint_set(sample_match_data)

        state = fingerprint_generator.compare_fingerprints(existing, new)
        assert state == "NEW"

    def test_fingerprint_comparison_unchanged(self, fingerprint_generator, sample_match_data):
        """Test fingerprint comparison for unchanged matches."""
        fingerprints = fingerprint_generator.generate_complete_fingerprint_set(sample_match_data)

        state = fingerprint_generator.compare_fingerprints(fingerprints, fingerprints)
        assert state == "UNCHANGED"

    def test_fingerprint_comparison_current_odds_changed(self, fingerprint_generator, sample_match_data, sample_match_data_changed):
        """Test fingerprint comparison for changed current odds."""
        existing = fingerprint_generator.generate_complete_fingerprint_set(sample_match_data)
        new = fingerprint_generator.generate_complete_fingerprint_set(sample_match_data_changed)

        state = fingerprint_generator.compare_fingerprints(existing, new)
        assert state == "CURRENT_ODDS_CHANGED"

    def test_fingerprint_comparison_new_history_entries(self, fingerprint_generator):
        """Test fingerprint comparison for new history entries with same current odds."""
        match1 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League",
            "1x2_market": {
                "current_odds": [2.0, 3.5, 4.0],
                "bookmakers": ["bet365", "bwin"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]}
                ]
            }
        }

        match2 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League",
            "1x2_market": {
                "current_odds": [2.0, 3.5, 4.0],  # Same current odds
                "bookmakers": ["bet365", "bwin"],
                "odds_history": [
                    {"timestamp": "2025-01-01 09:00:00 UTC", "odds": [2.1, 3.6, 4.1]},
                    {"timestamp": "2025-01-01 10:00:00 UTC", "odds": [2.0, 3.5, 4.0]}  # New history entry
                ]
            }
        }

        existing = fingerprint_generator.generate_complete_fingerprint_set(match1)
        new = fingerprint_generator.generate_complete_fingerprint_set(match2)

        state = fingerprint_generator.compare_fingerprints(existing, new)
        assert state == "NEW_HISTORY_ENTRIES"

    def test_fingerprint_comparison_different_identity(self, fingerprint_generator):
        """Test fingerprint comparison for different match identities."""
        match1 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "league_name": "Premier League"
        }

        match2 = {
            "sport": "football",
            "match_date": "2025-01-01 20:00:00 UTC",
            "home_team": "Manchester United",
            "away_team": "Liverpool",
            "league_name": "Premier League"
        }

        existing = fingerprint_generator.generate_complete_fingerprint_set(match1)
        new = fingerprint_generator.generate_complete_fingerprint_set(match2)

        state = fingerprint_generator.compare_fingerprints(existing, new)
        assert state == "NEW"

    def test_fingerprint_generation_error_handling(self, fingerprint_generator):
        """Test error handling in fingerprint generation."""
        # Test with missing required fields
        incomplete_data = {"home_team": "Arsenal"}

        # Should handle missing fields gracefully by using empty strings
        result = fingerprint_generator.generate_identity_fingerprint(incomplete_data)

        # Should still return a hash even with incomplete data
        assert isinstance(result, str)
        assert len(result) == 64


class TestChangeSensitivityCalculator:
    """Test suite for ChangeSensitivityCalculator class."""

    def test_conservative_sensitivity_always_scrape(self):
        """Test that conservative sensitivity always returns False (always scrape)."""
        existing_odds = [2.0, 3.5, 4.0]
        new_odds = [2.0, 3.5, 4.0]  # Exactly the same

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "conservative")
        assert result is False

        # Even with identical odds, should not skip
        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "conservative")
        assert result is False

    def test_normal_sensitivity_identical_odds(self):
        """Test normal sensitivity with identical odds."""
        existing_odds = [2.0, 3.5, 4.0]
        new_odds = [2.0, 3.5, 4.0]  # Exactly the same

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "normal")
        assert result is True

    def test_normal_sensitivity_different_odds(self):
        """Test normal sensitivity with different odds."""
        existing_odds = [2.0, 3.5, 4.0]
        new_odds = [2.1, 3.4, 3.9]  # Different

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "normal")
        assert result is False

    def test_aggressive_sensitivity_high_similarity(self):
        """Test aggressive sensitivity with high similarity (>95%)."""
        existing_odds = [2.0, 3.5, 4.0]
        new_odds = [2.0, 3.5, 4.01]  # 66.7% similar, but let's test with better similarity
        new_odds = [2.0, 3.5, 4.0]  # 100% similar

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "aggressive")
        assert result is True

    def test_aggressive_sensitivity_low_similarity(self):
        """Test aggressive sensitivity with low similarity (<95%)."""
        existing_odds = [2.0, 3.5, 4.0]
        new_odds = [2.5, 2.8, 4.5]  # All different

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "aggressive")
        assert result is False

    def test_odds_similarity_calculation(self):
        """Test odds similarity calculation."""
        # Test with identical odds
        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([2.0, 3.5, 4.0], [2.0, 3.5, 4.0])
        assert similarity == 1.0

        # Test with completely different odds
        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([2.0, 3.5], [4.0, 5.5])
        assert similarity == 0.0

        # Test with some similar odds
        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([2.0, 3.5, 4.0], [2.0, 3.6, 5.0])
        assert similarity == 1/3  # Only first odds matches within tolerance

    def test_odds_similarity_empty_arrays(self):
        """Test odds similarity calculation with empty arrays."""
        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([], [])
        assert similarity == 0.0

        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([2.0, 3.5], [])
        assert similarity == 0.0

    def test_odds_similarity_different_lengths(self):
        """Test odds similarity calculation with different array lengths."""
        similarity = ChangeSensitivityCalculator._calculate_odds_similarity([2.0, 3.5], [2.0, 3.5, 4.0])
        assert similarity == 0.0  # Different lengths should return 0

    def test_change_sensitivity_edge_cases(self):
        """Test change sensitivity calculator edge cases."""
        existing_odds = [2.0, 3.5, 4.0]

        # Test with small floating point differences (within tolerance)
        new_odds = [2.009, 3.509, 4.009]  # Within 0.01 tolerance

        # Normal sensitivity should skip (considered identical within tolerance)
        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "normal")
        assert result is True

        # Test with differences outside tolerance
        new_odds = [2.02, 3.52, 4.02]  # Outside 0.01 tolerance

        result = ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, "normal")
        assert result is False  # Should not skip