import re
import logging
from datetime import datetime
from typing import List, Tuple, Optional

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
                # For --all functionality, start from earlier year to capture more historical data
                start_year = 1998  # More reasonable starting point for most sports leagues

            if to_date:
                end_season_data = URLBuilder._parse_season_for_url(to_date)
                end_year = end_season_data[1]
            else:
                # Default to current year + 1 if not specified (to include next season)
                end_year = datetime.now().year + 1
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

    @staticmethod
    async def discover_available_seasons(sport: str, league: str, page) -> Tuple[Optional[int], Optional[int]]:
        """
        Auto-discover the earliest and latest available seasons for a league.

        Args:
            sport (str): The sport name
            league (str): The league identifier
            page: Playwright page object for navigation

        Returns:
            Tuple[Optional[int], Optional[int]]: (earliest_year, latest_year) or (None, None) if discovery fails
        """
        logger = logging.getLogger(__name__)

        try:
            # Navigate to the league's main results page (current season)
            league_url = URLBuilder.get_league_url(sport, league)
            results_url = f"{league_url}/results/"

            logger.debug(f"Discovering seasons for {sport}/{league} at {results_url}")

            await page.goto(results_url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)  # Allow content to load

            # Look for season dropdown or navigation elements
            # Common patterns on OddsPortal for season selection
            season_selectors = [
                "select[name='season'] option",
                "div[role='combobox'] option",
                "a[href*='/results/']",
                "span.season",
                "div.season-selector a",
                "ul.dropdown-menu a[href*='/results/']",
                "select.form-control option"
            ]

            seasons_found = set()

            for selector in season_selectors:
                try:
                    elements = await page.query_selector_all(selector)

                    for element in elements:
                        try:
                            text = await element.inner_text()
                            # Extract season years from text
                            season_years = re.findall(r'\b(19|20)\d{2}\b', text)
                            for year in season_years:
                                seasons_found.add(int(year))
                        except:
                            # Try getting from href attribute
                            try:
                                href = await element.get_attribute('href')
                                if href and '/results/' in href:
                                    # Extract year from URLs like "/results/2024/" or "/results/2023-2024/"
                                    year_match = re.search(r'/results/(\d{4})(?:-\d{4})?/', href)
                                    if year_match:
                                        seasons_found.add(int(year_match.group(1)))
                            except:
                                continue

                    if seasons_found:
                        logger.debug(f"Found seasons using selector '{selector}': {sorted(seasons_found)}")
                        break

                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {e}")
                    continue

            # Alternative approach: look for common season patterns in page content
            if not seasons_found:
                page_content = await page.content()
                # Look for season patterns in HTML content
                season_patterns = [
                    r'(?:season|seasons?)[^\d]*((?:19|20)\d{2})(?:[-/\s]*((?:19|20)\d{2}))?',
                    r'((?:19|20)\d{2})[-/\s]((?:19|20)\d{2})',
                    r'/results/((?:19|20)\d{4})(?:-\d{4})?/',
                    r'>(\d{4})</',  # Year in tags
                ]

                for pattern in season_patterns:
                    matches = re.findall(pattern, page_content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            for year_str in match:
                                if year_str and len(year_str) == 4 and year_str.isdigit():
                                    seasons_found.add(int(year_str))
                        else:
                            if match and len(match) == 4 and match.isdigit():
                                seasons_found.add(int(match))

                logger.debug(f"Found seasons from content: {sorted(seasons_found)}")

            if seasons_found:
                earliest_year = min(seasons_found)
                latest_year = max(seasons_found)

                # Add some buffer years to ensure we don't miss data
                earliest_year = max(earliest_year - 1, 1995)  # Don't go before 1995
                latest_year = latest_year + 2  # Include potential future seasons

                logger.info(f"Discovered season range for {sport}/{league}: {earliest_year} - {latest_year}")
                return earliest_year, latest_year
            else:
                logger.warning(f"Could not discover seasons for {sport}/{league} - using default range")
                return None, None

        except Exception as e:
            logger.error(f"Error discovering seasons for {sport}/{league}: {e}")
            return None, None

    @staticmethod
    def get_all_available_seasons_url_range(sport: str, league: str, fallback_start_year: int = 1998, fallback_end_year: Optional[int] = None) -> List[Tuple[str, str]]:
        """
        Generate URLs for ALL available seasons for a league.
        Uses auto-discovery when possible, falls back to reasonable defaults.

        Args:
            sport (str): The sport name
            league (str): The league identifier
            fallback_start_year (int): Fallback start year if auto-discovery fails
            fallback_end_year (int): Fallback end year if auto-discovery fails (defaults to current year + 2)

        Returns:
            List[Tuple[str, str]]: List of (url, season_string) tuples for all available seasons
        """
        if fallback_end_year is None:
            fallback_end_year = datetime.now().year + 2  # Include current + next year

        # This is a synchronous version - the actual discovery will happen async in the scraper
        # For now, return a wide range that will be filtered by the actual scraper
        urls = []
        for year in range(fallback_start_year, fallback_end_year + 1):
            season_str = str(year)
            url = URLBuilder.get_historic_matches_url(sport, league, season_str)
            urls.append((url, season_str))

        return urls
