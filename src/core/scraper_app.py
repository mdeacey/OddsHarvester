import asyncio
import logging
from datetime import datetime
from typing import Dict

from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.odds_portal_scraper import OddsPortalScraper
from src.core.playwright_manager import PlaywrightManager
from src.core.sport_market_registry import SportMarketRegistrar
from src.core.url_builder import URLBuilder
from src.utils.command_enum import CommandEnum
from src.utils.date_utils import parse_flexible_date, format_date_for_oddsportal
from src.utils.proxy_manager import ProxyManager
from src.utils.sport_market_constants import Sport

logger = logging.getLogger("ScraperApp")
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 20
TRANSIENT_ERRORS = (
    "ERR_CONNECTION_RESET",
    "ERR_CONNECTION_TIMED_OUT",
    "ERR_NAME_NOT_RESOLVED",
    "ERR_PROXY_CONNECTION_FAILED",
    "ERR_SOCKS_CONNECTION_FAILED",
    "ERR_CERT_AUTHORITY_INVALID",
    "ERR_TUNNEL_CONNECTION_FAILED",
    "ERR_NETWORK_CHANGED",
    "Timeout",  # generic timeout from Playwright
    "net::ERR_FAILED",
    "net::ERR_CONNECTION_ABORTED",
    "net::ERR_INTERNET_DISCONNECTED",
    "Navigation timeout",
    "TimeoutError",
    "Target closed",
)


async def run_scraper(
    command: CommandEnum,
    match_links: list | None = None,
    sport: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    leagues: list[str] | None = None,
    markets: list | None = None,
    max_pages: int | None = None,
    proxies: list | None = None,
    browser_user_agent: str | None = None,
    browser_locale_timezone: str | None = None,
    browser_timezone_id: str | None = None,
    target_bookmaker: str | None = None,
    scrape_odds_history: bool = True,  # Always scrape odds history by default
    headless: bool = True,
    preview_submarkets_only: bool = False,
    all: bool = False,
    change_sensitivity: str = "normal",
) -> dict:
    """Runs the scraping process and handles execution."""
    logger.info(
        f"Starting scraper with parameters: command={command}, match_links={match_links}, "
        f"sport={sport}, from_date={from_date}, to_date={to_date}, leagues={leagues}, markets={markets}, "
        f"max_pages={max_pages}, proxies={proxies}, browser_user_agent={browser_user_agent}, "
        f"browser_locale_timezone={browser_locale_timezone}, browser_timezone_id={browser_timezone_id}, "
        f"scrape_odds_history={scrape_odds_history}, target_bookmaker={target_bookmaker}, "
        f"headless={headless}, preview_submarkets_only={preview_submarkets_only}, all={all}, "
        f"change_sensitivity={change_sensitivity}"
    )

    proxy_manager = ProxyManager(cli_proxies=proxies)
    SportMarketRegistrar.register_all_markets()
    playwright_manager = PlaywrightManager()
    browser_helper = BrowserHelper()
    market_extractor = OddsPortalMarketExtractor(browser_helper=browser_helper)

    scraper = OddsPortalScraper(
        playwright_manager=playwright_manager,
        browser_helper=browser_helper,
        market_extractor=market_extractor,
        preview_submarkets_only=preview_submarkets_only,
    )

    try:
        proxy_config = proxy_manager.get_current_proxy()
        await scraper.start_playwright(
            headless=headless,
            browser_user_agent=browser_user_agent,
            browser_locale_timezone=browser_locale_timezone,
            browser_timezone_id=browser_timezone_id,
            proxy=proxy_config,
        )

        if match_links and sport:
            logger.info(f"""
                Scraping specific matches: {match_links} for sport: {sport}, markets={markets},
                scrape_odds_history={scrape_odds_history}, target_bookmaker={target_bookmaker}
            """)
            return await retry_scrape(
                scraper.scrape_matches,
                match_links=match_links,
                sport=sport,
                markets=markets,
                scrape_odds_history=scrape_odds_history,
                target_bookmaker=target_bookmaker,
            )

        if command == CommandEnum.HISTORIC:
            # Handle default behavior for historic matches
            if not from_date and not to_date:
                from_date = None  # No start limit - all historical going backwards
                to_date = "now"    # End at current time
            elif from_date and not to_date:
                to_date = from_date
            elif not from_date and to_date:
                from_date = None  # No start limit - all historical going backwards

            if all:
                # When --all flag is used, scrape all sports for the provided season range
                logger.info(
                    f"\n                Scraping historical odds for all 23 sports from {from_date} to {to_date}, "
                    f"markets={markets}, scrape_odds_history={scrape_odds_history}, "
                    f"target_bookmaker={target_bookmaker}, max_pages={max_pages}\n            "
                )

                return await _scrape_all_sports_date_range(
                    scraper=scraper,
                    command=command,
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                    max_pages=max_pages,
                )

            # Regular historic scraping (single sport)
            if not sport:
                raise ValueError("Sport must be provided for historic scraping.")

            logger.info(
                "\n                Scraping historical odds for "
                f"sport={sport}, leagues={leagues}, from {from_date} to {to_date}, "
                f"markets={markets}, scrape_odds_history={scrape_odds_history}, "
                f"target_bookmaker={target_bookmaker}, max_pages={max_pages}\n            "
            )

            if leagues is None:
                # No leagues specified - use auto-discovery for all leagues
                return await _scrape_single_league_date_range(
                    scraper=scraper,
                    command=command,
                    sport=sport,
                    league=None,  # This will trigger auto-discovery
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                    max_pages=max_pages,
                )
            elif len(leagues) == 1:
                return await _scrape_single_league_date_range(
                    scraper=scraper,
                    command=command,
                    sport=sport,
                    league=leagues[0],
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                    max_pages=max_pages,
                )
            else:
                return await _scrape_multiple_leagues_date_range(
                    scraper=scraper,
                    command=command,
                    leagues=leagues,
                    sport=sport,
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                    max_pages=max_pages,
                )

        elif command == CommandEnum.UPCOMING_MATCHES:
            # Default to_date to from_date if not provided
            if not to_date:
                to_date = from_date

            if all:
                # When --all flag is used, scrape all sports with provided date range
                logger.info(
                    f"\n                Scraping upcoming matches for all 23 sports from {from_date} to {to_date}, "
                    f"markets={markets}, scrape_odds_history={scrape_odds_history}, "
                    f"target_bookmaker={target_bookmaker}\n            "
                )

                return await _scrape_all_sports_date_range(
                    scraper=scraper,
                    command=command,
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                )

            # Regular upcoming matches scraping (single sport)
            # If no from_date and no leagues, use default "now" (all upcoming matches)
            if not from_date and not leagues:
                from_date = "now"
                to_date = None  # No end limit for all upcoming

            if leagues:
                logger.info(f"""
                    Scraping upcoming matches for sport={sport}, from {from_date} to {to_date}, leagues={leagues}, markets={markets},
                    scrape_odds_history={scrape_odds_history}, target_bookmaker={target_bookmaker}
                """)

                if len(leagues) == 1:
                    return await _scrape_single_league_date_range(
                        scraper=scraper,
                        command=command,
                        sport=sport,
                        league=leagues[0],
                        from_date=from_date,
                        to_date=to_date,
                        markets=markets,
                        scrape_odds_history=scrape_odds_history,
                        target_bookmaker=target_bookmaker,
                    )
                else:
                    return await _scrape_multiple_leagues_date_range(
                        scraper=scraper,
                        command=command,
                        leagues=leagues,
                        sport=sport,
                        from_date=from_date,
                        to_date=to_date,
                        markets=markets,
                        scrape_odds_history=scrape_odds_history,
                        target_bookmaker=target_bookmaker,
                    )
            else:
                logger.info(f"""
                    Scraping upcoming matches for sport={sport}, from {from_date} to {to_date}, markets={markets},
                    scrape_odds_history={scrape_odds_history}, target_bookmaker={target_bookmaker}
                """)
                return await _scrape_single_sport_date_range(
                    scraper=scraper,
                    command=command,
                    sport=sport,
                    from_date=from_date,
                    to_date=to_date,
                    markets=markets,
                    scrape_odds_history=scrape_odds_history,
                    target_bookmaker=target_bookmaker,
                )

        else:
            raise ValueError(f"Unknown command: {command}. Supported commands are 'upcoming-matches' and 'historic'.")

    except Exception as e:
        logger.error(f"An error occured: {e}")
        return None

    finally:
        await scraper.stop_playwright()


async def _scrape_multiple_leagues(scraper, scrape_func, leagues: list[str], sport: str, **kwargs) -> list[dict]:
    """
    Helper function to handle multi-league scraping with error handling and logging.

    Args:
        scraper: The scraper instance
        scrape_func: The function to call for each league (scrape_historic or scrape_upcoming)
        leagues: List of leagues to scrape
        sport: The sport being scraped
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all leagues
    """
    all_results = []
    failed_leagues = []

    logger.info(f"Starting multi-league scraping for {len(leagues)} leagues: {leagues}")

    for i, league in enumerate(leagues, 1):
        try:
            logger.info(f"[{i}/{len(leagues)}] Processing league: {league}")

            league_data = await retry_scrape(scrape_func, sport=sport, league=league, **kwargs)

            if league_data:
                all_results.extend(league_data)
                logger.info(f"Successfully scraped {len(league_data)} matches from league: {league}")
            else:
                logger.warning(f"No data returned for league: {league}")

        except Exception as e:
            logger.error(f"Failed to scrape league '{league}': {e}")
            failed_leagues.append(league)
            continue

    total_matches = len(all_results)
    successful_leagues = len(leagues) - len(failed_leagues)

    if failed_leagues:
        logger.warning(f"Failed to scrape {len(failed_leagues)} leagues: {failed_leagues}")

    logger.info(
        f"Multi-league scraping completed: {successful_leagues}/{len(leagues)} leagues successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results


async def _scrape_all_sports(scraper, scrape_func, **kwargs) -> list[dict]:
    """
    Helper function to handle multi-sport scraping with error handling and logging.

    Args:
        scraper: The scraper instance
        scrape_func: The function to call for each sport (scrape_historic or scrape_upcoming)
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all sports
    """
    all_results = []
    failed_sports = []

    # Get all 23 supported sports
    all_sports = list(Sport)

    logger.info(f"Starting multi-sport scraping for {len(all_sports)} sports")

    for i, sport in enumerate(all_sports, 1):
        try:
            logger.info(f"[{i}/{len(all_sports)}] Processing sport: {sport.value}")

            # For both upcoming and historic scraping, pass league=None to scrape all available leagues
            # This allows the scraper to discover and scrape all leagues for each sport
            sport_data = await retry_scrape(scrape_func, sport=sport.value, league=None, **kwargs)

            if sport_data:
                all_results.extend(sport_data)
                logger.info(f"Successfully scraped {len(sport_data)} matches from sport: {sport.value}")
            else:
                logger.warning(f"No data returned for sport: {sport.value}")

        except Exception as e:
            logger.error(f"Failed to scrape sport '{sport.value}': {e}")
            failed_sports.append(sport.value)
            continue

    total_matches = len(all_results)
    successful_sports = len(all_sports) - len(failed_sports)

    if failed_sports:
        logger.warning(f"Failed to scrape {len(failed_sports)} sports: {failed_sports}")

    logger.info(
        f"Multi-sport scraping completed: {successful_sports}/{len(all_sports)} sports successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results


async def retry_scrape(scrape_func, *args, **kwargs):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return await scrape_func(*args, **kwargs)
        except Exception as e:
            if any(keyword in str(e) for keyword in TRANSIENT_ERRORS):
                logger.warning(
                    f"[Attempt {attempt}] Transient error detected: {e}. Retrying in {RETRY_DELAY_SECONDS}s..."
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error(f"Non-retryable error encountered: {e}")
                raise
    logger.error("Max retries exceeded.")
    return None


async def _scrape_all_sports_date_range(scraper, command: CommandEnum, from_date: str, to_date: str, **kwargs) -> list[dict]:
    """
    Helper function to handle multi-sport scraping across a date range with error handling and logging.

    Args:
        scraper: The scraper instance
        command: CommandEnum (UPCOMING_MATCHES or HISTORIC)
        from_date: Start date/season string
        to_date: End date/season string
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all sports and dates/seasons
    """
    all_results = []
    failed_operations = []

    all_sports = list(Sport)

    logger.info(f"Starting multi-sport date range scraping for {len(all_sports)} sports from {from_date} to {to_date}")

    for i, sport in enumerate(all_sports, 1):
        try:
            logger.info(f"[{i}/{len(all_sports)}] Processing sport: {sport.value}")

            if command == CommandEnum.UPCOMING_MATCHES:
                # For upcoming matches, scrape all leagues for each date in range
                sport_data = await _scrape_single_sport_date_range(
                    scraper, command, sport.value, from_date, to_date, **kwargs
                )
            else:  # HISTORIC
                # For historic matches, we need to pass league=None to discover all leagues
                sport_data = await _scrape_single_sport_date_range(
                    scraper, command, sport.value, from_date, to_date, league=None, **kwargs
                )

            if sport_data:
                all_results.extend(sport_data)
                logger.info(f"Successfully scraped {len(sport_data)} matches from sport: {sport.value}")
            else:
                logger.warning(f"No data returned for sport: {sport.value}")

        except Exception as e:
            logger.error(f"Failed to scrape sport '{sport.value}': {e}")
            failed_operations.append(f"{sport.value}: {str(e)}")
            continue

    total_matches = len(all_results)
    successful_sports = len(all_sports) - len(failed_operations)

    if failed_operations:
        logger.warning(f"Failed operations: {failed_operations}")

    logger.info(
        f"Multi-sport date range scraping completed: {successful_sports}/{len(all_sports)} sports successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results


async def _scrape_multiple_leagues_date_range(scraper, command: CommandEnum, leagues: list[str], sport: str, from_date: str, to_date: str, **kwargs) -> list[dict]:
    """
    Helper function to handle multi-league scraping across a date range with error handling and logging.

    Args:
        scraper: The scraper instance
        command: CommandEnum (UPCOMING_MATCHES or HISTORIC)
        leagues: List of leagues to scrape
        sport: The sport being scraped
        from_date: Start date/season string
        to_date: End date/season string
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all leagues and dates/seasons
    """
    all_results = []
    failed_leagues = []

    logger.info(f"Starting multi-league date range scraping for {len(leagues)} leagues: {leagues}")

    for i, league in enumerate(leagues, 1):
        try:
            logger.info(f"[{i}/{len(leagues)}] Processing league: {league}")

            league_data = await _scrape_single_league_date_range(
                scraper, command, sport, league, from_date, to_date, **kwargs
            )

            if league_data:
                all_results.extend(league_data)
                logger.info(f"Successfully scraped {len(league_data)} matches from league: {league}")
            else:
                logger.warning(f"No data returned for league: {league}")

        except Exception as e:
            logger.error(f"Failed to scrape league '{league}': {e}")
            failed_leagues.append(league)
            continue

    total_matches = len(all_results)
    successful_leagues = len(leagues) - len(failed_leagues)

    if failed_leagues:
        logger.warning(f"Failed to scrape {len(failed_leagues)} leagues: {failed_leagues}")

    logger.info(
        f"Multi-league date range scraping completed: {successful_leagues}/{len(leagues)} leagues successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results


async def _scrape_single_league_date_range(scraper, command: CommandEnum, sport: str, league: str | None, from_date: str, to_date: str, **kwargs) -> list[dict]:
    """
    Helper function to handle single league scraping across a date range.

    Args:
        scraper: The scraper instance
        command: CommandEnum (UPCOMING_MATCHES or HISTORIC)
        sport: The sport being scraped
        league: The league being scraped (None for auto-discovery of all leagues)
        from_date: Start date/season string
        to_date: End date/season string
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all dates/seasons
    """
    if command == CommandEnum.UPCOMING_MATCHES:
        # For upcoming matches with specific league, discover leagues if needed
        discovered_leagues = None
        if league:
            try:
                logger.info(f"Discovering leagues for upcoming matches in sport '{sport}'")
                discovered_leagues = await URLBuilder.discover_leagues_for_sport(sport, scraper.playwright_manager.page)
                if not discovered_leagues:
                    logger.warning(f"No leagues discovered for sport '{sport}', upcoming matches may be limited")
            except Exception as e:
                logger.error(f"Failed to discover leagues for upcoming matches: {e}")

        return await _scrape_upcoming_date_range(scraper, sport, from_date, to_date, league, discovered_leagues, **kwargs)
    else:  # HISTORIC
        if league:
            return await _scrape_historic_date_range(scraper, sport, league, from_date, to_date, **kwargs)
        else:
            # For historic scraping without specific league, iterate through all available leagues
            return await _scrape_historic_all_leagues(scraper, sport, from_date, to_date, **kwargs)


async def _scrape_single_sport_date_range(scraper, command: CommandEnum, sport: str, from_date: str, to_date: str, league: str | None = None, **kwargs) -> list[dict]:
    """
    Helper function to handle single sport scraping across a date range.

    Args:
        scraper: The scraper instance
        command: CommandEnum (UPCOMING_MATCHES or HISTORIC)
        sport: The sport being scraped
        from_date: Start date/season string
        to_date: End date/season string
        league: Optional league to filter by
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all dates/seasons
    """
    if command == CommandEnum.UPCOMING_MATCHES:
        # For upcoming matches with specific league, discover leagues if needed
        discovered_leagues = None
        if league:
            try:
                logger.info(f"Discovering leagues for upcoming matches in sport '{sport}'")
                discovered_leagues = await URLBuilder.discover_leagues_for_sport(sport, scraper.playwright_manager.page)
                if not discovered_leagues:
                    logger.warning(f"No leagues discovered for sport '{sport}', upcoming matches may be limited")
            except Exception as e:
                logger.error(f"Failed to discover leagues for upcoming matches: {e}")

        return await _scrape_upcoming_date_range(scraper, sport, from_date, to_date, league, discovered_leagues, **kwargs)
    else:  # HISTORIC
        if league:
            return await _scrape_historic_date_range(scraper, sport, league, from_date, to_date, **kwargs)
        else:
            # For historic scraping without specific league, iterate through all available leagues
            return await _scrape_historic_all_leagues(scraper, sport, from_date, to_date, **kwargs)


async def _scrape_upcoming_date_range(scraper, sport: str, from_date: str, to_date: str, league: str | None = None, discovered_leagues: Dict[str, str] | None = None, **kwargs) -> list[dict]:
    """
    Scrape upcoming matches across a date range.

    Args:
        scraper: The scraper instance
        sport: The sport being scraped
        from_date: Start date string
        to_date: End date string
        league: Optional league to filter by
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all dates
    """
    try:
        urls_with_dates = URLBuilder.get_upcoming_matches_urls_for_range(sport, from_date, to_date, league)
    except ValueError as e:
        logger.error(f"Error generating URLs for date range: {e}")
        raise

    all_results = []
    failed_dates = []

    logger.info(f"Starting upcoming matches date range scraping for {len(urls_with_dates)} dates")

    for i, (url, date_str) in enumerate(urls_with_dates, 1):
        try:
            logger.info(f"[{i}/{len(urls_with_dates)}] Processing date: {date_str}")

            date_data = await retry_scrape(
                scraper.scrape_upcoming,
                sport=sport,
                date=date_str.replace("-", ""),  # Convert back to YYYYMMDD format
                league=league,
                discovered_leagues=discovered_leagues,
                **kwargs
            )

            if date_data:
                all_results.extend(date_data)
                logger.info(f"Successfully scraped {len(date_data)} matches from date: {date_str}")
            else:
                logger.warning(f"No data returned for date: {date_str}")

        except Exception as e:
            logger.error(f"Failed to scrape date '{date_str}': {e}")
            failed_dates.append(date_str)
            continue

    total_matches = len(all_results)
    successful_dates = len(urls_with_dates) - len(failed_dates)

    if failed_dates:
        logger.warning(f"Failed to scrape {len(failed_dates)} dates: {failed_dates}")

    logger.info(
        f"Upcoming matches date range scraping completed: {successful_dates}/{len(urls_with_dates)} dates successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results


async def _scrape_historic_all_leagues(scraper, sport: str, from_date: str, to_date: str, **kwargs) -> list[dict]:
    """
    Scrape historic matches across all available leagues for a sport using dynamic discovery.

    Args:
        scraper: The scraper instance
        sport: The sport being scraped
        from_date: Start season/year string
        to_date: End season/year string
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all leagues and seasons
    """
    try:
        sport_enum = Sport(sport)
    except ValueError:
        logger.error(f"Unsupported sport '{sport}' for league discovery")
        return []

    # Use dynamic league discovery instead of hardcoded constants
    logger.info(f"Dynamically discovering leagues for sport '{sport}'")
    try:
        leagues = await URLBuilder.discover_leagues_for_sport(sport, scraper.playwright_manager.page)

        if not leagues:
            logger.error(f"No leagues discovered for sport '{sport}'")
            return []

        logger.info(f"Discovered {len(leagues)} leagues for sport '{sport}': {', '.join(list(leagues.keys())[:10])}{'...' if len(leagues) > 10 else ''}")

    except Exception as e:
        logger.error(f"Failed to discover leagues for sport '{sport}': {str(e)}")
        return []

    all_results = []
    failed_leagues = []

    for league_name, league_url in leagues.items():
        try:
            logger.info(f"Scraping league '{league_name}' for sport '{sport}' from {from_date} to {to_date}")
            league_results = await _scrape_historic_date_range(scraper, sport, league_name, from_date, to_date, leagues, **kwargs)
            all_results.extend(league_results)
            logger.info(f"Successfully scraped {len(league_results)} matches from league '{league_name}'")
        except Exception as e:
            logger.error(f"Failed to scrape league '{league_name}' for sport '{sport}': {str(e)}")
            failed_leagues.append(league_name)
            continue

    if failed_leagues:
        logger.warning(f"Failed to scrape {len(failed_leagues)} leagues for sport '{sport}': {', '.join(failed_leagues)}")

    successful_leagues = len(leagues) - len(failed_leagues)
    logger.info(
        f"Completed historic scraping for sport '{sport}': "
        f"{len(all_results)} total matches scraped from {successful_leagues}/{len(leagues)} leagues"
    )

    # Log successful discovery completion
    logger.info(f"Dynamic league discovery completed for sport '{sport}': found {len(leagues)} total leagues")

    return all_results


async def _scrape_historic_date_range(scraper, sport: str, league: str, from_date: str, to_date: str, discovered_leagues: Dict[str, str] | None = None, **kwargs) -> list[dict]:
    """
    Scrape historic matches across a season/year range.

    Args:
        scraper: The scraper instance
        sport: The sport being scraped
        league: The league being scraped
        from_date: Start season/year string (None for --all = all available seasons)
        to_date: End season/year string (None for --all = all available seasons)
        **kwargs: Additional arguments to pass to the scrape function

    Returns:
        List of combined results from all seasons
    """
    # Check if this is --all functionality (no specific date range)
    is_all_mode = from_date is None and to_date is None

    if is_all_mode:
        logger.info(f"Auto-discovering exact available seasons for {sport}/{league}")
        try:
            # Try to auto-discover exact seasons
            discovered_seasons = await URLBuilder.discover_available_seasons(
                sport, league, scraper.page, discovered_leagues
            )

            # Generate URLs for discovered seasons (no wasted requests)
            urls_with_seasons = URLBuilder.get_urls_for_specific_seasons(sport, league, discovered_seasons, discovered_leagues)
        except Exception as e:
            logger.error(f"Season auto-discovery failed for {sport}/{league}: {e}")
            # No fallback - if discovery fails on a valid league, there's a real problem
            raise
    else:
        # Use specified date range
        try:
            urls_with_seasons = URLBuilder.get_historic_matches_urls_for_range(sport, from_date, to_date, league)
        except ValueError as e:
            logger.error(f"Error generating URLs for season range: {e}")
            raise

    all_results = []
    failed_seasons = []

    logger.info(f"Starting historic matches season range scraping for {len(urls_with_seasons)} seasons")

    for i, (url, season_str) in enumerate(urls_with_seasons, 1):
        try:
            logger.info(f"[{i}/{len(urls_with_seasons)}] Processing season: {season_str}")

            season_data = await retry_scrape(
                scraper.scrape_historic,
                sport=sport,
                league=league,
                season=season_str,
                discovered_leagues=discovered_leagues,
                **kwargs
            )

            if season_data:
                all_results.extend(season_data)
                logger.info(f"Successfully scraped {len(season_data)} matches from season: {season_str}")
            else:
                logger.warning(f"No data returned for season: {season_str}")

        except Exception as e:
            logger.error(f"Failed to scrape season '{season_str}': {e}")
            failed_seasons.append(season_str)
            continue

    total_matches = len(all_results)
    successful_seasons = len(urls_with_seasons) - len(failed_seasons)

    if failed_seasons:
        logger.warning(f"Failed to scrape {len(failed_seasons)} seasons: {failed_seasons}")

    logger.info(
        f"Historic matches season range scraping completed: {successful_seasons}/{len(urls_with_seasons)} seasons successful, "
        f"{total_matches} total matches scraped"
    )

    return all_results
