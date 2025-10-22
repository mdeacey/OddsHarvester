"""
Enhanced match fingerprinting utilities for duplicate detection.

This module provides three-layer fingerprinting for matches:
1. Identity fingerprint - identifies unique matches
2. Current odds fingerprint - identifies current odds state
3. History fingerprint - identifies odds evolution timeline
"""

import hashlib
import json
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging


class MatchFingerprint:
    """Utility class for generating match fingerprints for duplicate detection."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize MatchFingerprint with optional logger."""
        self.logger = logger or logging.getLogger(__name__)

    def generate_identity_fingerprint(self, match_data: Dict[str, Any]) -> str:
        """
        Generate identity fingerprint for a match.

        This creates a unique identifier based on match characteristics that don't change:
        - sport + match_date + home_team + away_team + league_name

        Args:
            match_data (Dict[str, Any]): Match data containing identification fields

        Returns:
            str: SHA-256 hash of the match identity
        """
        try:
            # Extract identification fields
            sport = match_data.get("sport", "")
            match_date = match_data.get("match_date", "")
            home_team = match_data.get("home_team", "")
            away_team = match_data.get("away_team", "")
            league_name = match_data.get("league_name", "")

            # Create normalized identity string
            identity_components = [
                str(sport).strip().lower(),
                str(match_date).strip(),
                str(home_team).strip().lower(),
                str(away_team).strip().lower(),
                str(league_name).strip().lower()
            ]

            identity_string = "|".join(identity_components)

            # Generate hash
            fingerprint = hashlib.sha256(identity_string.encode("utf-8")).hexdigest()

            self.logger.debug(f"Generated identity fingerprint: {fingerprint[:16]}...")
            return fingerprint

        except Exception as e:
            self.logger.error(f"Error generating identity fingerprint: {e}")
            raise

    def generate_current_odds_fingerprint(self, match_data: Dict[str, Any]) -> str:
        """
        Generate fingerprint for current odds state.

        This captures the current odds for all markets, ignoring historical data.

        Args:
            match_data (Dict[str, Any]): Match data including market data

        Returns:
            str: SHA-256 hash of current odds state
        """
        try:
            current_odds_data = {}

            # Extract current odds from each market
            for key, value in match_data.items():
                if key.endswith("_market") and value is not None:
                    market_name = key.replace("_market", "")
                    if isinstance(value, dict):
                        current_odds_data[market_name] = {
                            "current_odds": value.get("current_odds", []),
                            "bookmakers": value.get("bookmakers", [])
                        }

            # Create normalized odds string
            odds_string = json.dumps(current_odds_data, sort_keys=True, separators=(",", ":"))

            # Generate hash
            fingerprint = hashlib.sha256(odds_string.encode("utf-8")).hexdigest()

            self.logger.debug(f"Generated current odds fingerprint: {fingerprint[:16]}...")
            return fingerprint

        except Exception as e:
            self.logger.error(f"Error generating current odds fingerprint: {e}")
            raise

    def generate_history_fingerprint(self, match_data: Dict[str, Any]) -> str:
        """
        Generate fingerprint for odds history timeline.

        This captures the complete odds evolution history for all markets.

        Args:
            match_data (Dict[str, Any]): Match data including market data with history

        Returns:
            str: SHA-256 hash of odds history timeline
        """
        try:
            history_data = {}

            # Extract odds history from each market
            for key, value in match_data.items():
                if key.endswith("_market") and value is not None:
                    market_name = key.replace("_market", "")
                    if isinstance(value, dict):
                        history_data[market_name] = {
                            "odds_history": value.get("odds_history", [])
                        }

            # Create normalized history string
            history_string = json.dumps(history_data, sort_keys=True, separators=(",", ":"))

            # Generate hash
            fingerprint = hashlib.sha256(history_string.encode("utf-8")).hexdigest()

            self.logger.debug(f"Generated history fingerprint: {fingerprint[:16]}...")
            return fingerprint

        except Exception as e:
            self.logger.error(f"Error generating history fingerprint: {e}")
            raise

    def generate_complete_fingerprint_set(self, match_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate all three fingerprints for a match.

        Args:
            match_data (Dict[str, Any]): Complete match data

        Returns:
            Dict[str, str]: Dictionary containing all three fingerprints
        """
        try:
            return {
                "identity_fingerprint": self.generate_identity_fingerprint(match_data),
                "current_odds_fingerprint": self.generate_current_odds_fingerprint(match_data),
                "history_fingerprint": self.generate_history_fingerprint(match_data)
            }
        except Exception as e:
            self.logger.error(f"Error generating complete fingerprint set: {e}")
            raise

    def compare_fingerprints(self, existing: Dict[str, str], new: Dict[str, str]) -> str:
        """
        Compare existing and new fingerprints to determine change state.

        Args:
            existing (Dict[str, str]): Existing match fingerprints
            new (Dict[str, str]): New match fingerprints

        Returns:
            str: Change state - one of: "NEW", "UNCHANGED", "CURRENT_ODDS_CHANGED", "NEW_HISTORY_ENTRIES"
        """
        try:
            # Check if this is a new match (no existing identity fingerprint)
            if not existing.get("identity_fingerprint"):
                return "NEW"

            # Check if identity fingerprints match
            if existing["identity_fingerprint"] != new["identity_fingerprint"]:
                return "NEW"

            # At this point, we have the same match - check for changes

            current_odds_changed = existing["current_odds_fingerprint"] != new["current_odds_fingerprint"]
            history_changed = existing["history_fingerprint"] != new["history_fingerprint"]

            if not current_odds_changed and not history_changed:
                return "UNCHANGED"
            elif current_odds_changed and history_changed:
                return "CURRENT_ODDS_CHANGED"  # Both changed, prioritize current odds
            elif current_odds_changed:
                return "CURRENT_ODDS_CHANGED"
            else:
                return "NEW_HISTORY_ENTRIES"

        except Exception as e:
            self.logger.error(f"Error comparing fingerprints: {e}")
            raise


class ChangeSensitivityCalculator:
    """Utility class for calculating change sensitivity based on user configuration."""

    @staticmethod
    def should_skip_update(existing_odds: List[float], new_odds: List[float], sensitivity: str = "normal") -> bool:
        """
        Determine if an update should be skipped based on change sensitivity.

        Args:
            existing_odds (List[float]): Existing odds values
            new_odds (List[float]): New odds values
            sensitivity (str): Change sensitivity level ("aggressive", "normal", "conservative")

        Returns:
            bool: True if update should be skipped
        """
        if sensitivity == "conservative":
            return False  # Always scrape for known matches

        if sensitivity == "aggressive":
            # Skip if >95% of odds unchanged
            return ChangeSensitivityCalculator._calculate_odds_similarity(existing_odds, new_odds) > 0.95

        # Normal sensitivity - skip if 100% of odds unchanged
        return ChangeSensitivityCalculator._calculate_odds_similarity(existing_odds, new_odds) >= 1.0

    @staticmethod
    def _calculate_odds_similarity(odds1: List[float], odds2: List[float]) -> float:
        """
        Calculate similarity percentage between two odds arrays.

        Args:
            odds1 (List[float]): First odds array
            odds2 (List[float]): Second odds array

        Returns:
            float: Similarity percentage (0.0 to 1.0)
        """
        if not odds1 or not odds2 or len(odds1) != len(odds2):
            return 0.0

        # Count identical odds values
        identical_count = sum(1 for o1, o2 in zip(odds1, odds2) if abs(o1 - o2) < 0.01)  # Small tolerance for floating point

        return identical_count / len(odds1)