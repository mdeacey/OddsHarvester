import re
from datetime import datetime
from typing import List, Tuple

from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.date_utils import (
    parse_flexible_date, generate_date_range, generate_month_range,
    generate_year_range, format_date_for_oddsportal
)
from src.utils.sport_league_constants import SPORTS_LEAGUES_URLS_MAPPING
from src.utils.sport_market_constants import Sport


class URLBuilder:
    """
    A utility class for constructing URLs used in scraping data from OddsPortal.
    """

    @staticmethod
    def get_historic_matches_url(sport: str, league: str, season: str | None = None) -> str:
        """
        Constructs the URL for historical matches of a specific sport league and season.

        Args:
            sport (str): The sport for which the URL is required (e.g., "football", "tennis", "baseball").
            league (str): The league for which the URL is required (e.g., "premier-league", "mlb").
            season (Optional[str]): The season for which the URL is required. Accepts either:
                - a single year (e.g., "2024")
                - a range in 'YYYY-YYYY' format (e.g., "2023-2024")
                - None or empty string for the current season

        Returns:
            str: The constructed URL for the league and season.

        Raises:
            ValueError: If the season is provided but does not follow the expected format(s).
        """
        base_url = URLBuilder.get_league_url(sport, league).rstrip("/")

        # Treat missing season as current
        if not season:
            return f"{base_url}/results/"

        if isinstance(season, str) and season.lower() == "current":
            raise ValueError(f"Invalid season format: {season}. Expected format: 'YYYY' or 'YYYY-YYYY'")

        if re.match(r"^\d{4}$", season):
            return f"{base_url}-{season}/results/"

        if re.match(r"^\d{4}-\d{4}$", season):
            start_year, end_year = map(int, season.split("-"))
            if end_year != start_year + 1:
                raise ValueError(
                    f"Invalid season range: {season}. The second year must be exactly one year after the first."
                )

            # Special handling for baseball leagues
            if sport.lower() == "baseball":
                return f"{base_url}-{start_year}/results/"

            return f"{base_url}-{season}/results/"

        raise ValueError(f"Invalid season format: {season}. Expected format: 'YYYY' or 'YYYY-YYYY'")

    @staticmethod
    def get_upcoming_matches_url(sport: str, date: str, league: str | None = None) -> str:
        """
        Constructs the URL for upcoming matches for a specific sport and date.
        If a league is provided, includes the league in the URL.

        Args:
            sport (str): The sport for which the URL is required (e.g., "football", "tennis").
            date (str): The date for which the matches are required in 'YYYY-MM-DD' format (e.g., "2025-01-15").
            league (Optional[str]): The league for which matches are required (e.g., "premier-league").

        Returns:
            str: The constructed URL for upcoming matches.
        """
        if league:
            return URLBuilder.get_league_url(sport, league)
        return f"{ODDSPORTAL_BASE_URL}/matches/{sport}/{date}/"

    @staticmethod
    def get_league_url(sport: str, league: str) -> str:
        """
        Retrieves the URL associated with a specific league for a given sport.

        Args:
            sport (str): The sport name (e.g., "football", "tennis").
            league (str): The league name (e.g., "premier-league", "atp-tour").

        Returns:
            str: The URL associated with the league.

        Raises:
            ValueError: If the league is not found for the specified sport.
        """
        sport_enum = Sport(sport)

        if sport_enum not in SPORTS_LEAGUES_URLS_MAPPING:
            raise ValueError(f"Unsupported sport '{sport}'. Available: {', '.join(SPORTS_LEAGUES_URLS_MAPPING.keys())}")

        leagues = SPORTS_LEAGUES_URLS_MAPPING[sport_enum]

        if league not in leagues:
            raise ValueError(f"Invalid league '{league}' for sport '{sport}'. Available: {', '.join(leagues.keys())}")

        return leagues[league]

    @staticmethod
    def get_upcoming_matches_urls_for_range(sport: str, from_date: str | None, to_date: str | None, league: str | None = None) -> List[Tuple[str, str]]:
        """
        Constructs URLs for upcoming matches across a date range.

        Args:
            sport (str): The sport for which URLs are required
            from_date (str | None): Start date in flexible format (YYYYMMDD, YYYYMM, YYYY, or 'now'), or None for "now"
            to_date (str | None): End date in flexible format (YYYYMMDD, YYYYMM, YYYY, or 'now'), or None for unlimited future
            league (Optional[str]): Specific league to filter by

        Returns:
            List[Tuple[str, str]]: List of (url, date_string) tuples for each date in the range

        Raises:
            ValueError: If date formats are invalid
        """
        # Handle default values
        if not from_date:
            from_date = "now"
        if not to_date:
            # If no to_date, default to single date (from_date only)
            to_date = from_date

        try:
            start_date = parse_flexible_date(from_date)
            # Only parse end_date if it's different from from_date
            if to_date and to_date != from_date:
                end_date = parse_flexible_date(to_date)
            else:
                end_date = start_date
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")

        if end_date < start_date:
            raise ValueError("End date cannot be before start date")

        urls = []
        dates = generate_date_range(start_date, end_date)

        for date_obj in dates:
            date_str = format_date_for_oddsportal(date_obj)
            url = URLBuilder.get_upcoming_matches_url(sport, date_str, league)
            urls.append((url, date_str))

        return urls

    @staticmethod
    def get_historic_matches_urls_for_range(sport: str, from_date: str | None, to_date: str | None, league: str) -> List[Tuple[str, str]]:
        """
        Constructs URLs for historical matches across a season/year range.

        Args:
            sport (str): The sport for which URLs are required
            from_date (str | None): Start season/year in format YYYY, YYYY-YYYY, or 'now', or None for unlimited past
            to_date (str | None): End season/year in format YYYY, YYYY-YYYY, or 'now', or None for current year
            league (str): The league to scrape

        Returns:
            List[Tuple[str, str]]: List of (url, season_string) tuples for each season in the range

        Raises:
            ValueError: If season formats are invalid
        """
        # Handle default values
        if not from_date and not to_date:
            from_date = None  # No start limit - unlimited past
            to_date = "now"    # End at current time
        elif from_date and not to_date:
            to_date = from_date
        elif not from_date and to_date:
            from_date = None  # No start limit - unlimited past

        try:
            if from_date:
                start_season_data = URLBuilder._parse_season_for_url(from_date)
                start_year = start_season_data[1]
            else:
                # For unlimited past, start from a reasonable early year
                start_year = 2000

            if to_date:
                end_season_data = URLBuilder._parse_season_for_url(to_date)
                end_year = end_season_data[1]
            else:
                # Default to current year if not specified
                end_year = datetime.now().year
        except ValueError as e:
            raise ValueError(f"Invalid season format: {e}")

        if end_year < start_year:
            raise ValueError("End season/year cannot be before start season/year")

        urls = []
        # For historical data, we generate years from start_year to end_year (inclusive)
        for year in range(start_year, end_year + 1):
            season_str = str(year)  # For historical, we use single year format
            url = URLBuilder.get_historic_matches_url(sport, league, season_str)
            urls.append((url, season_str))

        return urls

    @staticmethod
    def _parse_season_for_url(season_str: str | int) -> Tuple[str, int]:
        """
        Parse season string for URL generation and return (season_format, end_year).

        Args:
            season_str: Season string in YYYY, YYYY-YYYY, or 'now' format, or integer year

        Returns:
            Tuple of (season_format, end_year) where season_format is the string to use in URLs
        """
        # Handle integer input
        if isinstance(season_str, int):
            return str(season_str), season_str

        season_str = season_str.strip().lower()

        if season_str == "now":
            current_year = datetime.now().year
            return str(current_year), current_year

        # YYYY format
        if re.match(r"^\d{4}$", season_str):
            year = int(season_str)
            return season_str, year

        # YYYY-YYYY format
        if re.match(r"^\d{4}-\d{4}$", season_str):
            start_year, end_year = map(int, season_str.split("-"))
            if end_year != start_year + 1:
                raise ValueError(
                    f"Invalid season range: '{season_str}'. The second year must be exactly one year after the first year."
                )
            return season_str, end_year

        raise ValueError(
            f"Invalid season format: '{season_str}'. Expected format: YYYY, YYYY-YYYY, or 'now' (e.g., 2023, 2022-2023, now)."
        )
