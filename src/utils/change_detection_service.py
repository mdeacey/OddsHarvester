"""
Enhanced change detection service for identifying duplicate and changed matches.

This service provides four-state change detection:
- NEW: Match identity not found
- UNCHANGED: Match found + current odds same + history same
- CURRENT_ODDS_CHANGED: Match found + current odds different
- NEW_HISTORY_ENTRIES: Match found + current odds same + new history entries
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple, Set
from datetime import datetime
import logging
from pathlib import Path

from src.utils.match_fingerprint import MatchFingerprint, ChangeSensitivityCalculator


class ChangeDetectionResult:
    """Result of change detection analysis for a match."""

    def __init__(self, state: str, existing_data: Optional[Dict[str, Any]] = None):
        self.state = state  # NEW, UNCHANGED, CURRENT_ODDS_CHANGED, NEW_HISTORY_ENTRIES
        self.existing_data = existing_data
        self.should_scrape = state in ["NEW", "CURRENT_ODDS_CHANGED", "NEW_HISTORY_ENTRIES"]
        self.should_update_history = state in ["CURRENT_ODDS_CHANGED", "NEW_HISTORY_ENTRIES"]


class ChangeDetectionService:
    """Service for detecting changes and duplicates in match data."""

    def __init__(self, storage_dir: str, change_sensitivity: str = "normal", logger: Optional[logging.Logger] = None):
        """
        Initialize change detection service.

        Args:
            storage_dir (str): Directory containing stored data files
            change_sensitivity (str): Change sensitivity level ("aggressive", "normal", "conservative")
            logger (Optional[logging.Logger]): Logger instance
        """
        self.storage_dir = Path(storage_dir)
        self.change_sensitivity = change_sensitivity
        self.logger = logger or logging.getLogger(__name__)
        self.fingerprint_generator = MatchFingerprint(logger)

        # Cache for existing fingerprints to avoid repeated file loading
        self._fingerprint_cache: Dict[str, Dict[str, str]] = {}
        self._data_cache: Dict[str, Dict[str, Any]] = {}

    def analyze_match(self, match_data: Dict[str, Any], file_path: str) -> ChangeDetectionResult:
        """
        Analyze a match for changes and duplicates.

        Args:
            match_data (Dict[str, Any]): New match data to analyze
            file_path (str): Path to the storage file for existing data

        Returns:
            ChangeDetectionResult: Analysis result with change state and recommendations
        """
        try:
            # Generate fingerprints for new match
            new_fingerprints = self.fingerprint_generator.generate_complete_fingerprint_set(match_data)
            identity_fingerprint = new_fingerprints["identity_fingerprint"]

            # Load existing data and fingerprints
            existing_data = self._load_existing_data(file_path, identity_fingerprint)

            if not existing_data:
                self.logger.debug(f"New match detected: {identity_fingerprint[:16]}...")
                return ChangeDetectionResult("NEW")

            # Generate fingerprints for existing match
            existing_fingerprints = self._get_or_generate_fingerprints(existing_data, file_path)

            # Compare fingerprints to determine change state
            change_state = self.fingerprint_generator.compare_fingerprints(existing_fingerprints, new_fingerprints)

            # Apply change sensitivity if this is a current odds change
            if change_state == "CURRENT_ODDS_CHANGED" and self.change_sensitivity != "conservative":
                existing_odds = self._extract_current_odds(existing_data)
                new_odds = self._extract_current_odds(match_data)

                if ChangeSensitivityCalculator.should_skip_update(existing_odds, new_odds, self.change_sensitivity):
                    change_state = "UNCHANGED"
                    self.logger.debug(f"Odds change below sensitivity threshold for match {identity_fingerprint[:16]}...")

            self.logger.debug(f"Change analysis complete for match {identity_fingerprint[:16]}...: {change_state}")
            return ChangeDetectionResult(change_state, existing_data)

        except Exception as e:
            self.logger.error(f"Error analyzing match change detection: {e}")
            # Default to scraping if detection fails
            return ChangeDetectionResult("NEW")

    def _load_existing_data(self, file_path: str, identity_fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Load existing data for a specific match from storage file.

        Args:
            file_path (str): Path to storage file
            identity_fingerprint (str): Identity fingerprint to find

        Returns:
            Optional[Dict[str, Any]]: Existing match data if found
        """
        try:
            # Check cache first
            cache_key = f"{file_path}:{identity_fingerprint}"
            if cache_key in self._data_cache:
                return self._data_cache[cache_key]

            # Load file if it exists
            if not os.path.exists(file_path):
                return None

            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Find matching record by identity fingerprint
                        for record in data:
                            if self._matches_identity_fingerprint(record, identity_fingerprint):
                                self._data_cache[cache_key] = record
                                return record
                    else:
                        # Single record - check if it matches
                        if self._matches_identity_fingerprint(data, identity_fingerprint):
                            self._data_cache[cache_key] = data
                            return data

            elif file_ext == '.csv':
                # For CSV files, we'd need to parse and find the matching row
                # This is more complex and might be implemented later
                self.logger.warning("CSV change detection not fully implemented - treating as new match")
                return None

            return None

        except Exception as e:
            self.logger.error(f"Error loading existing data from {file_path}: {e}")
            return None

    def _get_or_generate_fingerprints(self, match_data: Dict[str, Any], file_path: str) -> Dict[str, str]:
        """
        Get cached fingerprints or generate new ones for existing match data.

        Args:
            match_data (Dict[str, Any]): Existing match data
            file_path (str): Path to storage file

        Returns:
            Dict[str, str]: Fingerprints for the existing match
        """
        identity_fingerprint = self.fingerprint_generator.generate_identity_fingerprint(match_data)
        cache_key = f"{file_path}:{identity_fingerprint}"

        if cache_key in self._fingerprint_cache:
            return self._fingerprint_cache[cache_key]

        fingerprints = self.fingerprint_generator.generate_complete_fingerprint_set(match_data)
        self._fingerprint_cache[cache_key] = fingerprints
        return fingerprints

    def _matches_identity_fingerprint(self, match_data: Dict[str, Any], target_fingerprint: str) -> bool:
        """
        Check if match data matches the target identity fingerprint.

        Args:
            match_data (Dict[str, Any]): Match data to check
            target_fingerprint (str): Target identity fingerprint

        Returns:
            bool: True if match data matches target fingerprint
        """
        try:
            existing_fingerprint = self.fingerprint_generator.generate_identity_fingerprint(match_data)
            return existing_fingerprint == target_fingerprint
        except Exception:
            return False

    def _extract_current_odds(self, match_data: Dict[str, Any]) -> List[float]:
        """
        Extract current odds values from match data.

        Args:
            match_data (Dict[str, Any]): Match data

        Returns:
            List[float]: Current odds values
        """
        odds_values = []

        for key, value in match_data.items():
            if key.endswith("_market") and isinstance(value, dict):
                current_odds = value.get("current_odds", [])
                if isinstance(current_odds, list):
                    odds_values.extend(current_odds)

        return odds_values

    def clear_cache(self):
        """Clear fingerprint and data caches."""
        self._fingerprint_cache.clear()
        self._data_cache.clear()
        self.logger.debug("Change detection cache cleared")

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get statistics about cache usage.

        Returns:
            Dict[str, int]: Cache statistics
        """
        return {
            "fingerprint_cache_size": len(self._fingerprint_cache),
            "data_cache_size": len(self._data_cache)
        }


class IncrementalScrapingManager:
    """Manager for coordinating incremental scraping with change detection."""

    def __init__(self, change_detection_service: ChangeDetectionService, logger: Optional[logging.Logger] = None):
        """
        Initialize incremental scraping manager.

        Args:
            change_detection_service (ChangeDetectionService): Change detection service
            logger (Optional[logging.Logger]): Logger instance
        """
        self.change_detection_service = change_detection_service
        self.logger = logger or logging.getLogger(__name__)

        # Performance metrics
        self.metrics = {
            "total_matches_analyzed": 0,
            "new_matches": 0,
            "unchanged_matches": 0,
            "current_odds_changed_matches": 0,
            "new_history_entries_matches": 0,
            "scrapes_skipped": 0
        }

    def filter_matches_for_scraping(self, matches: List[Dict[str, Any]], file_path: str) -> Tuple[List[Dict[str, Any]], Dict[str, ChangeDetectionResult]]:
        """
        Filter matches to determine which ones need scraping.

        Args:
            matches (List[Dict[str, Any]]): List of matches to analyze
            file_path (str): Path to storage file

        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, ChangeDetectionResult]]:
                - List of matches that need scraping
                - Dictionary of all analysis results
        """
        matches_to_scrape = []
        analysis_results = {}

        for i, match in enumerate(matches):
            self.metrics["total_matches_analyzed"] += 1

            # Analyze match for changes
            result = self.change_detection_service.analyze_match(match, file_path)
            analysis_results[f"match_{i}"] = result

            # Update metrics
            metric_key = result.state.lower() + "_matches"
            if metric_key in self.metrics:
                self.metrics[metric_key] += 1

            if result.should_scrape:
                matches_to_scrape.append(match)
                self.logger.debug(f"Match {i} needs scraping: {result.state}")
            else:
                self.metrics["scrapes_skipped"] += 1
                self.logger.debug(f"Skipping match {i}: {result.state}")

        self.logger.info(f"Scraping analysis complete: {len(matches_to_scrape)}/{len(matches)} matches need scraping")
        return matches_to_scrape, analysis_results

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the scraping session.

        Returns:
            Dict[str, Any]: Performance metrics
        """
        total = self.metrics["total_matches_analyzed"]
        if total == 0:
            return self.metrics

        metrics = self.metrics.copy()
        metrics["scraping_efficiency"] = (metrics["scrapes_skipped"] / total) * 100
        metrics["change_distribution"] = {
            "new_matches_percent": (metrics["new_matches"] / total) * 100,
            "unchanged_matches_percent": (metrics["unchanged_matches"] / total) * 100,
            "current_odds_changed_percent": (metrics["current_odds_changed_matches"] / total) * 100,
            "new_history_entries_percent": (metrics["new_history_entries_matches"] / total) * 100
        }

        return metrics

    def reset_metrics(self):
        """Reset performance metrics."""
        for key in self.metrics:
            self.metrics[key] = 0