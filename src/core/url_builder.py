import re
import warnings
import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict
from bs4 import BeautifulSoup

from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.date_utils import (
    parse_flexible_date, generate_date_range, generate_month_range,
    generate_year_range, format_date_for_oddsportal
)
from src.utils.sport_market_constants import Sport


class URLBuilder:
    """
    A utility class for constructing URLs used in scraping data from OddsPortal.
    """

    @staticmethod
    def get_historic_matches_url(sport: str, league: str, season: str | None = None, discovered_leagues: Dict[str, str] | None = None) -> str:
        """
        Constructs the URL for historical matches of a specific sport league and season.

        Args:
            sport (str): The sport for which the URL is required (e.g., "football", "tennis", "baseball").
            league (str): The league for which the URL is required (e.g., "premier-league", "mlb").
            season (Optional[str]): The season for which the URL is required. Accepts either:
                - a single year (e.g., "2024")
                - a range in 'YYYY-YYYY' format (e.g., "2023-2024")
                - None or empty string for the current season
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping.

        Returns:
            str: The constructed URL for the league and season.

        Raises:
            ValueError: If the season is provided but does not follow the expected format(s).
        """
        # Remove /results/ from the base URL since we'll add it appropriately based on season
        base_url = URLBuilder.get_league_url(sport, league, discovered_leagues).rstrip("/").replace("/results", "")

        # Treat missing season as current
        if not season:
            return f"{base_url}/results/"

        if isinstance(season, str) and season.lower() == "current":
            raise ValueError(f"Invalid season format: {season}. Expected format: 'YYYY' or 'YYYY-YYYY'")

        if re.match(r"^\d{4}$", season):
            # Check if this is the current year
            # Current year uses no year in URL, previous years use year in URL
            current_year = datetime.now().year
            if int(season) == current_year:
                return f"{base_url}/results/"  # Current year: no year in URL
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
    def get_upcoming_matches_url(sport: str, date: str, league: str | None = None, discovered_leagues: Dict[str, str] | None = None) -> str:
        """
        Constructs the URL for upcoming matches for a specific sport and date.
        If a league is provided, includes the league in the URL.

        Args:
            sport (str): The sport for which the URL is required (e.g., "football", "tennis").
            date (str): The date for which the matches are required in 'YYYY-MM-DD' format (e.g., "2025-01-15").
            league (Optional[str]): The league for which matches are required (e.g., "premier-league").
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping.

        Returns:
            str: The constructed URL for upcoming matches.
        """
        if league:
            return URLBuilder.get_league_url(sport, league, discovered_leagues)
        return f"{ODDSPORTAL_BASE_URL}/matches/{sport}/{date}/"

    @staticmethod
    def get_league_url(sport: str, league: str, discovered_leagues: Dict[str, str] | None) -> str:
        """
        Retrieves the URL associated with a specific league for a given sport.

        Args:
            sport (str): The sport name (e.g., "football", "tennis").
            league (str): The league name (e.g., "premier-league", "atp-tour").
            discovered_leagues (Dict[str, str] | None): Dynamically discovered leagues mapping.

        Returns:
            str: The URL associated with the league.

        Raises:
            ValueError: If the league is not found in the discovered leagues.
        """
        # Handle None for backward compatibility
        if discovered_leagues is None:
            # Fallback to static URL construction
            return f"{ODDSPORTAL_BASE_URL}/{sport}/{league}"

        if league not in discovered_leagues:
            raise ValueError(f"Invalid league '{league}' for sport '{sport}'. Available: {', '.join(discovered_leagues.keys())}")

        return discovered_leagues[league]

    @staticmethod
    def get_upcoming_matches_urls_for_range(sport: str, from_date: str | None, to_date: str | None, league: str | None = None, discovered_leagues: Dict[str, str] | None = None) -> List[Tuple[str, str]]:
        """
        Constructs URLs for upcoming matches across a date range.

        Args:
            sport (str): The sport for which URLs are required
            from_date (str | None): Start date in flexible format (YYYYMMDD, YYYYMM, YYYY, or 'now'), or None for "now"
            to_date (str | None): End date in flexible format (YYYYMMDD, YYYYMM, YYYY, or 'now'), or None for unlimited future
            league (Optional[str]): Specific league to filter by
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping

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
            url = URLBuilder.get_upcoming_matches_url(sport, date_str, league, discovered_leagues)
            urls.append((url, date_str))

        return urls

    @staticmethod
    def get_historic_matches_urls_for_range(sport: str, from_date: str | None, to_date: str | None, league: str, discovered_leagues: Dict[str, str]) -> List[Tuple[str, str]]:
        """
        Constructs URLs for historical matches across a season/year range.

        Args:
            sport (str): The sport for which URLs are required
            from_date (str | None): Start season/year in format YYYY, YYYY-YYYY, or 'now', or None for unlimited past
            to_date (str | None): End season/year in format YYYY, YYYY-YYYY, or 'now', or None for current year
            league (str): The league to scrape
            discovered_leagues (Dict[str, str]): Dynamically discovered leagues mapping

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
                # For --all functionality, dynamic discovery will handle the actual seasons
                # No hardcoded years needed - scraper will use exact discovered seasons
                start_year = None  # Will be handled by dynamic discovery in scraper

            if to_date:
                end_season_data = URLBuilder._parse_season_for_url(to_date)
                end_year = end_season_data[1]
            else:
                # Default to current year + 1 if not specified (to include next season)
                end_year = datetime.now().year + 1
        except ValueError as e:
            raise ValueError(f"Invalid season format: {e}")

        # For --all functionality, this method shouldn't be used anymore
        # The scraper should use exact seasons discovery instead
        if start_year is None:
            raise ValueError("get_historic_matches_urls_for_range cannot be used with None start_year. Use exact seasons discovery instead.")

        if end_year < start_year:
            raise ValueError("End season/year cannot be before start season/year")

        urls = []
        # For historical data, we generate years from start_year to end_year (inclusive)
        for year in range(start_year, end_year + 1):
            season_str = str(year)  # For historical, we use single year format
            url = URLBuilder.get_historic_matches_url(sport, league, season_str, discovered_leagues)
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
    async def discover_available_seasons(sports: str, league: str, page, discovered_leagues: Dict[str, str] | None = None) -> Optional[List[int]]:
        """
        Auto-discover the exact available seasons for a league.

        Args:
            sports (str): The sport name
            league (str): The league identifier
            page: Playwright page object for navigation
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping.

        Returns:
            Optional[List[int]]: List of discovered seasons in chronological order, or None if discovery fails
        """
        logger = logging.getLogger(__name__)

        try:
            # Navigate to the league's main results page (current season)
            league_url = URLBuilder.get_league_url(sports, league, discovered_leagues)

            # The league_url from discovered leagues already ends with /results/
            # So we use it directly instead of adding /results/ again
            results_url = league_url

            logger.debug(f"Discovering seasons for {sports}/{league} at {results_url}")

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
                            season_years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)

                            # Debug logging for aussie-rules
                            if sports == "aussie-rules" and season_years:
                                logger.debug(f"Season text: '{text}' -> extracted years: {season_years}")

                            for year in season_years:
                                seasons_found.add(int(year))
                        except:
                            # Try getting from href attribute
                            try:
                                href = await element.get_attribute('href')
                                if href and '/results/' in href:
                                    # Extract year from URLs like "/results/2024/" or "/results/2023-2024/"
                                    year_match = re.search(r'/results/(\d{4})(?:-\d{4})?/', href)

                                    # Debug logging for aussie-rules
                                    if sports == "aussie-rules" and year_match:
                                        logger.debug(f"Season href: '{href}' -> extracted year: {year_match.group(1)}")

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
                sorted_seasons = sorted(seasons_found)

                logger.info(f"Discovered {len(sorted_seasons)} exact seasons for {sports}/{league}: {sorted_seasons}")
                return sorted_seasons
            else:
                # If no seasons found on a valid league page, this indicates a real problem
                raise ValueError(f"No seasons discovered on league page for {sports}/{league}. League exists but no season data found.")

        except Exception as e:
            logger.error(f"Error discovering seasons for {sports}/{league}: {e}")
            raise  # Re-raise the exception - don't hide real problems

    @staticmethod
    async def discover_leagues_for_sport(sport: str, page) -> Dict[str, str]:
        """
        Dynamically discover all available leagues for a sport by visiting the sport's results page.

        This function replaces the hardcoded SPORTS_LEAGUES_URLS_MAPPING constants with dynamic discovery.
        It visits the /{sport}/results/ page and extracts all league links available.

        Args:
            sport (str): The sport name (e.g., "football", "tennis", "basketball")
            page: Playwright page object for navigation

        Returns:
            Dict[str, str]: Dictionary mapping league names to their URLs, or empty dict if discovery fails
        """
        logger = logging.getLogger(__name__)

        try:
            # Validate sport
            sport_enum = Sport(sport)
            logger.info(f"Discovering leagues for sport: {sport}")

            # Navigate to the sport's main results page
            sport_results_url = f"{ODDSPORTAL_BASE_URL}/{sport}/results/"
            logger.debug(f"Navigating to {sport_results_url}")

            await page.goto(sport_results_url, timeout=20000, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)  # Allow content to load

            # Get page content and parse with BeautifulSoup
            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')

            # Enhanced debug logging for aussie-rules
            if sport == "aussie-rules":
                logger.debug(f"Page content length: {len(page_content)} characters")
                logger.debug(f"Page content preview: {page_content[:1000]}...")

                # Log all links found on the page for debugging
                all_links = soup.find_all('a', href=True)
                logger.debug(f"Total links found: {len(all_links)}")
                sport_links = [link for link in all_links if f'/{sport}/' in link.get('href', '')]
                logger.debug(f"Links containing '/{sport}/': {len(sport_links)}")
                for i, link in enumerate(sport_links[:20]):  # Log first 20 links
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    logger.debug(f"  {i+1}. href='{href}' text='{text}'")

            discovered_leagues = {}

            # Multiple selector strategies to find league links
            league_selectors = [
                # Primary: Direct links to league results pages (this is the main one that works)
                f"a[href*='/{sport}/'][href*='/results/']",
                # Secondary: Direct links to league main pages (not result pages)
                f"a[href*='/{sport}/']:not([href*='/results/']):not([href*='/matches/'])",
                # Tertiary: More specific league links within the main content area
                "main ul li a[href*='/{sport}/'][href*='/results/']",
                # Additional specific selectors for aussie-rules based on known structure
                "div[id*='content'] a[href*='/{sport}/'][href*='/results/']",
                "div[class*='main'] a[href*='/{sport}/'][href*='/results/']",
                "table a[href*='/{sport}/'][href*='/results/']",
                # Fallback: any link with sport and results
                f"a[href*='/{sport}/'][href*='results']",
            ]

            leagues_found = set()

            for selector in league_selectors:
                try:
                    elements = soup.select(selector)
                    logger.debug(f"Selector '{selector}' found {len(elements)} elements")

                    for element in elements:
                        try:
                            href = element.get('href', '')
                            if not href:
                                continue

                            # Enhanced debug logging for aussie-rules
                            if sport == "aussie-rules":
                                logger.debug(f"Processing link: href='{href}' text='{element.get_text(strip=True)}'")

                            # Skip invalid or unwanted links
                            navigation_patterns = [
                                'odds', 'play', 'blocked', 'calculator', '/rules/', 'home',
                                'standings', 'footballbasketballtennisbaseballhockeyamerican', 'footballaussie',
                                'upcoming', 'live', 'today', 'yesterday', 'archived'
                            ]

                            # Additional filtering for main page links (second selector)
                            if 'results' not in href:  # This is a main page link, not a results page
                                # Main page links should have at least 3 path segments (sport, region/country, league)
                                href_parts = [part for part in href.split('/') if part]
                                if len(href_parts) < 3:
                                    if sport == "aussie-rules":
                                        logger.debug(f"  Skipped: Not enough path parts ({len(href_parts)} < 3)")
                                    continue

                            # Check each filter condition with debug logging
                            if href.startswith('#'):
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: href starts with '#'")
                                continue
                            if 'javascript:' in href:
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: contains javascript:")
                                continue
                            if '/matches/' in href:
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: contains /matches/")
                                continue
                            if href == f'/{sport}/results/':
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: is main results page")
                                continue
                            if href == f'/{sport}/':
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: is main sport page")
                                continue
                            if href.endswith('/standings/'):
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: ends with /standings/")
                                continue
                            if f'oddsportal.com/{sport}/' not in f"{ODDSPORTAL_BASE_URL}{href}":
                                if sport == "aussie-rules":
                                    logger.debug(f"  Skipped: doesn't contain oddsportal.com/{sport}/")
                                continue
                            if any(pattern in href for pattern in navigation_patterns):
                                if sport == "aussie-rules":
                                    matched_patterns = [pattern for pattern in navigation_patterns if pattern in href]
                                    logger.debug(f"  Skipped: contains navigation patterns: {matched_patterns}")
                                continue

                            # Extract league information
                            league_name, league_url = URLBuilder._extract_league_info(href, sport)

                            if sport == "aussie-rules":
                                logger.debug(f"  Extracted: league_name='{league_name}' league_url='{league_url}'")

                            if league_name and league_url and league_name not in leagues_found:
                                # Validate that this looks like a proper league URL
                                is_valid = URLBuilder._is_valid_league_url(league_url, sport)
                                if sport == "aussie-rules":
                                    logger.debug(f"  Validation result: {is_valid}")

                                if is_valid:
                                    discovered_leagues[league_name] = league_url
                                    leagues_found.add(league_name)
                                    if sport == "aussie-rules":
                                        logger.debug(f"  ✅ Added league: {league_name}")
                                else:
                                    if sport == "aussie-rules":
                                        logger.debug(f"  ❌ Rejected league: {league_name} (validation failed)")
                            elif sport == "aussie-rules":
                                if not league_name:
                                    logger.debug(f"  ❌ Rejected: no league name extracted")
                                elif not league_url:
                                    logger.debug(f"  ❌ Rejected: no league URL extracted")
                                elif league_name in leagues_found:
                                    logger.debug(f"  ❌ Rejected: league already found: {league_name}")

                        except Exception as e:
                            logger.debug(f"Error processing league link: {e}")
                            continue

                    # If we found leagues with this selector, no need to try others
                    if discovered_leagues:
                        break

                except Exception as e:
                    logger.debug(f"Selector '{selector}' failed: {e}")
                    continue

            # Disabled content-based discovery as it was returning too many invalid leagues
            # Rely on direct link discovery only for better quality control
            # if not discovered_leagues:
            #     logger.debug("Trying content-based league discovery")
            #     discovered_leagues.update(URLBuilder._discover_leagues_from_content(soup, sport))

            if discovered_leagues:
                logger.info(f"Successfully discovered {len(discovered_leagues)} leagues for sport '{sport}': {', '.join(list(discovered_leagues.keys())[:10])}{'...' if len(discovered_leagues) > 10 else ''}")
            else:
                logger.warning(f"No leagues discovered for sport '{sport}' at {sport_results_url}")

            return discovered_leagues

        except Exception as e:
            logger.error(f"Error discovering leagues for sport '{sport}': {e}")
            return {}

    @staticmethod
    def _extract_league_info(href: str, sport: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract league name and URL from a href attribute.

        Args:
            href (str): The href attribute value
            sport (str): The sport name

        Returns:
            Tuple[Optional[str], Optional[str]]: (league_name, league_url) or (None, None)
        """
        try:
            # Clean up the href
            href = href.strip()
            if href.startswith('/'):
                league_url = f"{ODDSPORTAL_BASE_URL}{href}"
            else:
                league_url = href

            # Extract league name from URL path
            # Expected pattern: /{sport}/{region}/{league-name}/
            # or /{sport}/{league-name}/
            # or /{sport}/results/ (main sport page)

            if href == f"/{sport}/results/" or href == f"/{sport}/":
                return None, None  # Skip main sport page links

            # Remove domain if present for path parsing
            path = href.replace(ODDSPORTAL_BASE_URL, '')
            path = path.strip('/')

            parts = path.split('/')

            # Find the league name in the path
            if len(parts) >= 2 and parts[0] == sport:
                # Handle URLs that end with /results/ - remove that for league name extraction
                if parts[-1] == 'results':
                    parts = parts[:-1]

                if len(parts) >= 3:
                    # Pattern: /{sport}/{region}/{league-name}/
                    league_name = parts[2]
                elif len(parts) >= 2:
                    # Pattern: /{sport}/{league-name}/
                    league_name = parts[1]
                else:
                    return None, None

                # Clean up league name
                league_name = league_name.replace('-', '_').lower()

                # Validate league name
                if (league_name and
                    len(league_name) > 1 and
                    not league_name.isdigit()):
                    return league_name, league_url

            return None, None

        except Exception:
            return None, None

    @staticmethod
    def _is_valid_league_url(url: str, sport: str) -> bool:
        """
        Validate that a URL looks like a proper league URL for the given sport.

        Args:
            url (str): The URL to validate
            sport (str): The sport name

        Returns:
            bool: True if this looks like a valid league URL
        """
        try:
            # Basic URL structure validation
            if not url.startswith(ODDSPORTAL_BASE_URL):
                return False

            # Must contain the sport name
            if f"/{sport}/" not in url:
                return False

            # Should not be the main sport page (only exclude exact matches, not league results pages)
            exclusion_patterns = [
                f"/{sport}/",           # Main sport page
                "/matches/",            # Match pages
                "/live/",               # Live pages
                "/odds/",               # Odds pages (not league odds)
                "/stats/"               # Stats pages
            ]

            for pattern in exclusion_patterns:
                if url.endswith(pattern):
                    return False

            # Specifically exclude the main sport results page
            if url == f"{ODDSPORTAL_BASE_URL}/{sport}/results/":
                return False

            # Should have a reasonable path structure
            path_parts = url.replace(ODDSPORTAL_BASE_URL, '').strip('/').split('/')
            if len(path_parts) < 2:  # Need at least /sport/league/
                return False

            return True

        except Exception:
            return False

    @staticmethod
    def _discover_leagues_from_content(soup: BeautifulSoup, sport: str) -> Dict[str, str]:
        """
        Discover leagues by analyzing page content structure.

        Args:
            soup: BeautifulSoup object of the page content
            sport (str): The sport name

        Returns:
            Dict[str, str]: Dictionary of discovered leagues
        """
        leagues = {}

        try:
            # Look for common patterns that might indicate leagues
            # This is a fallback method when direct link discovery fails

            # Look for text patterns that might be league names
            league_patterns = [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Title case words
                r'\b([a-z]+(?:-[a-z]+)*)\b',  # Lowercase with hyphens
            ]

            # Search in various content areas
            content_areas = [
                soup.find_all('div', class_=lambda x: x and 'league' in str(x).lower()),
                soup.find_all('div', class_=lambda x: x and 'competition' in str(x).lower()),
                soup.find_all('div', class_=lambda x: x and 'tournament' in str(x).lower()),
                soup.find_all('table'),
                soup.find_all('ul'),
            ]

            for area in content_areas:
                if not area:
                    continue

                # Handle both single elements and lists of elements
                if isinstance(area, list):
                    for element in area:
                        if element:
                            text = element.get_text(strip=True)
                            for pattern in league_patterns:
                                matches = re.findall(pattern, text)
                                for match in matches:
                                    league_name = match.lower().replace(' ', '-')
                                    if len(league_name) > 2 and league_name not in leagues:
                                        potential_url = f"{ODDSPORTAL_BASE_URL}/{sport}/{league_name}/"
                                        leagues[league_name] = potential_url
                else:
                    text = area.get_text(strip=True)
                for pattern in league_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        league_name = match.lower().replace(' ', '-')
                        if len(league_name) > 2 and league_name not in leagues:
                            # Construct a potential URL for this league
                            potential_url = f"{ODDSPORTAL_BASE_URL}/{sport}/{league_name}/"
                            leagues[league_name] = potential_url

        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.debug(f"Content-based league discovery failed: {e}")

        return leagues

    @staticmethod
    def get_all_available_seasons_url_range(sport: str, league: str, fallback_start_year: int = 2010, fallback_end_year: Optional[int] = None, discovered_leagues: Dict[str, str] | None = None) -> List[Tuple[str, str]]:
        """
        Generate URLs for ALL available seasons for a league.
        Uses auto-discovery when possible, falls back to reasonable defaults.

        Args:
            sport (str): The sport name
            league (str): The league identifier
            fallback_start_year (int): Fallback start year if auto-discovery fails (updated to 2010)
            fallback_end_year (int): Fallback end year if auto-discovery fails (defaults to current year + 1)
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping.

        Returns:
            List[Tuple[str, str]]: List of (url, season_string) tuples for all available seasons
        """
        if fallback_end_year is None:
            fallback_end_year = datetime.now().year + 1  # More conservative end year

        # This is a synchronous version - the actual discovery will happen async in the scraper
        # Return a reasonable range that minimizes failed requests
        urls = []
        for year in range(fallback_start_year, fallback_end_year + 1):
            season_str = str(year)
            url = URLBuilder.get_historic_matches_url(sport, league, season_str, discovered_leagues)
            urls.append((url, season_str))

        return urls

    @staticmethod
    def get_urls_for_specific_seasons(sport: str, league: str, seasons: List[int], discovered_leagues: Dict[str, str] | None = None) -> List[Tuple[str, str]]:
        """
        Generate URLs for a specific list of seasons.

        Args:
            sport (str): The sport name
            league (str): The league identifier
            seasons (List[int]): List of specific seasons to generate URLs for
            discovered_leagues (Optional[Dict[str, str]]): Dynamically discovered leagues mapping

        Returns:
            List[Tuple[str, str]]: List of (url, season_string) tuples for the specified seasons
        """
        urls = []
        for season in seasons:
            season_str = str(season)
            url = URLBuilder.get_historic_matches_url(sport, league, season_str, discovered_leagues)
            urls.append((url, season_str))
        return urls

    @staticmethod
    async def discover_available_markets(sport: str, page, discovered_leagues: Dict[str, str] | None = None) -> Dict[str, str]:
        """
        Dynamically discover all available markets for a sport by parsing match page market navigation.

        This function visits a sample match page for the sport and extracts all available market tabs
        and hidden menu markets to build a complete market mapping.

        Args:
            sport (str): The sport name (e.g., "aussie-rules", "football", "basketball")
            page: Playwright page object for navigation
            discovered_leagues (Dict[str, str] | None): Optional discovered leagues mapping

        Returns:
            Dict[str, str]: Dictionary mapping normalized market names to their display names
        """
        logger = logging.getLogger(__name__)

        try:
            # Validate sport
            sport_enum = Sport(sport)
            logger.info(f"Discovering markets for sport: {sport}")

            # Find a sample match page to analyze markets
            sample_match_url = await URLBuilder._find_sample_match_url(sport, page, discovered_leagues)
            if not sample_match_url:
                logger.warning(f"Could not find sample match URL for {sport}, returning empty markets")
                return {}

            logger.debug(f"Analyzing markets on sample match page: {sample_match_url}")

            await page.goto(sample_match_url, timeout=15000, wait_until="domcontentloaded")
            await page.wait_for_timeout(2000)  # Allow content to load

            # Extract markets from page
            markets = await URLBuilder._extract_markets_from_page(page, sport)

            logger.info(f"Discovered {len(markets)} markets for {sport}: {list(markets.keys())}")
            return markets

        except Exception as e:
            logger.error(f"Error discovering markets for {sport}: {e}")
            return {}

    @staticmethod
    async def _find_sample_match_url(sport: str, page, discovered_leagues: Dict[str, str] | None = None) -> Optional[str]:
        """
        Find a sample match URL for the given sport to analyze markets.

        Enhanced to better utilize discovered leagues for more reliable sample match finding.

        Args:
            sport (str): The sport name
            page: Playwright page object
            discovered_leagues (Dict[str, str] | None): Optional discovered leagues mapping (flat dict: league_name -> league_url)

        Returns:
            Optional[str]: URL of a sample match page, or None if not found
        """
        logger = logging.getLogger(__name__)

        try:
            # Try to use discovered leagues first (enhanced logic)
            if discovered_leagues:
                logger.debug(f"Attempting to use {len(discovered_leagues)} discovered leagues for sample match finding")

                # Try a few different leagues to find one with actual matches
                league_entries = list(discovered_leagues.items())[:3]  # Try first 3 leagues

                for league_name, league_url in league_entries:
                    try:
                        logger.debug(f"Trying discovered league '{league_name}' with URL: {league_url}")

                        await page.goto(league_url, timeout=15000, wait_until="domcontentloaded")
                        await page.wait_for_timeout(2000)  # Allow page to fully load

                        # Enhanced match selectors for better detection
                        match_selectors = [
                            "a[href*='/match/']",
                            "a[href*='/game/']",
                            "tr.deactivate[data-date] a[href*='/match/']",  # Specific OddsPortal pattern
                            "td[class*='match'] a",
                            "div[class*='match'] a",
                            "table[class*='table-main'] a[href*='/match/']",
                            "div[id*='table-matches'] a[href*='/match/']"
                        ]

                        for selector in match_selectors:
                            try:
                                matches = await page.query_selector_all(selector)
                                if matches:
                                    # Get the first non-disabled match
                                    for match in matches[:5]:  # Try first 5 matches
                                        match_href = await match.get_attribute('href')
                                        if match_href and not 'deactivate' in (await match.get_attribute('class') or ''):
                                            full_url = f"{ODDSPORTAL_BASE_URL}{match_href}" if not match_href.startswith('http') else match_href
                                            logger.debug(f"Found sample match URL from league '{league_name}': {full_url}")
                                            return full_url
                            except Exception:
                                continue

                        logger.debug(f"No matches found on league page for '{league_name}'")

                    except Exception as e:
                        logger.debug(f"Failed to access league '{league_name}': {e}")
                        continue

            # Enhanced fallback strategies
            logger.debug("No matches found in discovered leagues, trying enhanced fallback strategies")

            # Strategy 1: Try the main sport page with latest results
            fallback_urls = [
                f"{ODDSPORTAL_BASE_URL}/{sport}/results/",
                f"{ODDSPORTAL_BASE_URL}/{sport}/",
                f"{ODDSPORTAL_BASE_URL}/{sport}/australia/",  # Try Australia as common fallback
                f"{ODDSPORTAL_BASE_URL}/{sport}/england/",   # Try England as common fallback
            ]

            for fallback_url in fallback_urls:
                try:
                    logger.debug(f"Trying fallback URL: {fallback_url}")

                    await page.goto(fallback_url, timeout=15000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(2000)

                    # Same enhanced match selectors
                    match_selectors = [
                        "a[href*='/match/']",
                        "a[href*='/game/']",
                        "tr.deactivate[data-date] a[href*='/match/']",
                        "td[class*='match'] a",
                        "div[class*='match'] a",
                        "table[class*='table-main'] a[href*='/match/']",
                    ]

                    for selector in match_selectors:
                        try:
                            matches = await page.query_selector_all(selector)
                            if matches:
                                for match in matches[:3]:
                                    match_href = await match.get_attribute('href')
                                    if match_href:
                                        full_url = f"{ODDSPORTAL_BASE_URL}{match_href}" if not match_href.startswith('http') else match_href
                                        logger.debug(f"Found sample match URL from fallback: {full_url}")
                                        return full_url
                        except Exception:
                            continue

                except Exception as e:
                    logger.debug(f"Fallback URL {fallback_url} failed: {e}")
                    continue

            # Last resort: return None to indicate failure
            logger.warning(f"All strategies failed to find sample match URL for sport '{sport}'")
            return None

        except Exception as e:
            logger.error(f"Critical error finding sample match URL for {sport}: {e}")
            return None

    @staticmethod
    async def _extract_markets_from_page(page, sport: str) -> Dict[str, str]:
        """
        Extract market information from a match page.

        Args:
            page: Playwright page object loaded with a match page
            sport (str): The sport name

        Returns:
            Dict[str, str]: Dictionary mapping normalized market names to display names
        """
        logger = logging.getLogger(__name__)
        markets = {}

        try:
            # Look for market tabs in navigation
            market_tab_selectors = [
                "li[class*='odds-item'] span div",
                "div[class*='market-tab']",
                "ul[class*='markets'] li",
                "div[class*='betting-market'] span"
            ]

            for selector in market_tab_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        try:
                            market_text = await element.inner_text()
                            if market_text and len(market_text.strip()) > 0:
                                normalized_market = URLBuilder._normalize_market_name(market_text.strip())
                                markets[normalized_market] = market_text.strip()
                        except Exception:
                            continue
                except Exception:
                    continue

            # Look for hidden menu markets
            hidden_market_selectors = [
                "li[class*='snap-right'] a div",
                "div[class*='hide-menu'] a",
                "ul[class*='dropdown'] a",
                "div[class*='more-markets'] a"
            ]

            for selector in hidden_market_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        try:
                            market_text = await element.inner_text()
                            if market_text and len(market_text.strip()) > 0:
                                normalized_market = URLBuilder._normalize_market_name(market_text.strip())
                                markets[normalized_market] = market_text.strip()
                        except Exception:
                            continue
                except Exception:
                    continue

            # Add common markets if not found (fallback)
            common_markets = URLBuilder._get_common_markets_for_sport(sport)
            for market_name, display_name in common_markets.items():
                if market_name not in markets:
                    markets[market_name] = display_name

            return markets

        except Exception as e:
            logger.error(f"Error extracting markets from page for {sport}: {e}")
            # Return fallback markets on error
            return URLBuilder._get_common_markets_for_sport(sport)

    @staticmethod
    def _normalize_market_name(market_name: str) -> str:
        """
        Normalize market name to a consistent identifier format.

        Args:
            market_name (str): Raw market name from page

        Returns:
            str: Normalized market name
        """
        import re

        # Convert to lowercase and remove special characters
        normalized = market_name.lower()

        # Common replacements
        replacements = {
            'home/away': 'home_away',
            'over/under': 'over_under',
            'asian handicap': 'handicap',
            'draw no bet': 'draw_no_bet',
            'odd or even': 'odd_even',
            'double chance': 'double_chance',
            'both teams to score': 'both_teams_to_score',
            'correct score': 'correct_score',
            'half time/full time': 'half_time_full_time'
        }

        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        # Remove non-alphanumeric characters except underscore
        normalized = re.sub(r'[^a-z0-9_]', '', normalized)

        # Replace multiple underscores with single
        normalized = re.sub(r'_+', '_', normalized)

        # Remove leading/trailing underscores
        normalized = normalized.strip('_')

        return normalized if normalized else 'unknown'

    @staticmethod
    def _get_common_markets_for_sport(sport: str) -> Dict[str, str]:
        """
        Get common markets for a sport as fallback.

        Args:
            sport (str): The sport name

        Returns:
            Dict[str, str]: Dictionary of common markets for the sport
        """
        common_markets = {
            # Universal markets
            '1x2': '1X2',
            'home_away': 'Home/Away',
            'over_under': 'Over/Under',
            'handicap': 'Handicap',
            'draw_no_bet': 'Draw No Bet',
            'double_chance': 'Double Chance',
            'correct_score': 'Correct Score',
            'half_time_full_time': 'Half Time/Full Time',
            'odd_even': 'Odd or Even',

            # Team-based markets
            'both_teams_to_score': 'Both Teams to Score',
        }

        # Sport-specific common markets
        sport_specific = {
            'aussie-rules': {
                'margin': 'Winning Margin',
                'first_goalscorer': 'First Goalscorer',
            },
            'football': {
                'both_teams_to_score': 'Both Teams to Score',
                'goalscorer': 'Goalscorer',
                'cards': 'Cards',
                'corners': 'Corners',
            },
            'basketball': {
                'points': 'Points',
                'rebounds': 'Rebounds',
                'assists': 'Assists',
            },
            'tennis': {
                'set_winner': 'Set Winner',
                'game_winner': 'Game Winner',
                'total_games': 'Total Games',
            }
        }

        if sport in sport_specific:
            common_markets.update(sport_specific[sport])

        return common_markets
