import asyncio
from datetime import UTC, datetime
import json
import logging
import re
from typing import Any

from bs4 import BeautifulSoup
from playwright.async_api import Page, TimeoutError

from src.core.browser_helper import BrowserHelper
from src.core.odds_portal_market_extractor import OddsPortalMarketExtractor
from src.core.playwright_manager import PlaywrightManager
from src.utils.constants import ODDSPORTAL_BASE_URL
from src.utils.odds_format_enum import OddsFormat
from src.utils.utils import clean_html_text


class BaseScraper:
    """
    Base class for scraping match data from OddsPortal.
    """

    def __init__(
        self,
        playwright_manager: PlaywrightManager,
        browser_helper: BrowserHelper,
        market_extractor: OddsPortalMarketExtractor,
        preview_submarkets_only: bool = False,
    ):
        """
        Args:
            playwright_manager (PlaywrightManager): Handles Playwright lifecycle.
            browser_helper (BrowserHelper): Helper class for browser interactions.
            market_extractor (OddsPortalMarketExtractor): Handles market scraping.
            preview_submarkets_only (bool): If True, only scrape average odds from visible submarkets without loading individual bookmaker details.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.playwright_manager = playwright_manager
        self.browser_helper = browser_helper
        self.market_extractor = market_extractor
        self.preview_submarkets_only = preview_submarkets_only

    async def set_odds_format(self, page: Page, odds_format: OddsFormat = OddsFormat.DECIMAL_ODDS):
        """
        Sets the odds format on the page.

        Args:
            page (Page): The Playwright page instance.
            odds_format (OddsFormat): The desired odds format.
        """
        try:
            self.logger.info(f"Setting odds format: {odds_format.value}")
            button_selector = "div.group > button.gap-2"
            await page.wait_for_selector(button_selector, state="attached", timeout=8000)
            dropdown_button = await page.query_selector(button_selector)

            # Check if the desired format is already selected
            current_format = await dropdown_button.inner_text()
            self.logger.info(f"Current odds format detected: {current_format}")

            if current_format == odds_format.value:
                self.logger.info(f"Odds format is already set to '{odds_format.value}'. Skipping.")
                return

            await dropdown_button.click()
            await page.wait_for_timeout(10000)
            format_option_selector = "div.group > div.dropdown-content > ul > li > a"
            format_options = await page.query_selector_all(format_option_selector)

            for option in format_options:
                option_text = await option.inner_text()

                if odds_format.value.lower() in option_text.lower():
                    self.logger.info(f"Selecting odds format: {option_text}")
                    await option.click()
                    await page.wait_for_timeout(10000)
                    self.logger.info(f"Odds format changed to '{odds_format.value}'.")
                    return

            self.logger.warning(f"Desired odds format '{odds_format.value}' not found in dropdown options.")

        except TimeoutError:
            self.logger.error("Timeout while setting odds format. Dropdown may not have loaded.")

        except Exception as e:
            self.logger.error(f"Error while setting odds format: {e}", exc_info=True)

    async def extract_match_links(self, page: Page) -> list[str]:
        """
        Extract and parse match links from the current page.

        Args:
            page (Page): A Playwright Page instance for this task.

        Returns:
            List[str]: A list of unique match links found on the page.
        """
        try:
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "lxml")
            event_rows = soup.find_all(class_=re.compile("^eventRow"))
            self.logger.info(f"Found {len(event_rows)} event rows.")

            match_links = {
                f"{ODDSPORTAL_BASE_URL}{link['href']}"
                for row in event_rows
                for link in row.find_all("a", href=True)
                if len(link["href"].strip("/").split("/")) > 3
            }

            self.logger.info(f"Extracted {len(match_links)} unique match links.")
            return list(match_links)

        except Exception as e:
            self.logger.error(f"Error extracting match links: {e}", exc_info=True)
            return []

    async def extract_match_odds(
        self,
        sport: str,
        match_links: list[str],
        markets: list[str] | None = None,
        scrape_odds_history: bool = True,  # Always scrape odds history by default
        target_bookmaker: str | None = None,
        concurrent_scraping_task: int = 3,
        preview_submarkets_only: bool = False,
    ) -> list[dict[str, Any]]:
        """
        Extract odds for a list of match links concurrently.

        Args:
            sport (str): The sport to scrape odds for.
            match_links (List[str]): A list of match links to scrape odds for.
            markets (Optional[List[str]]: The list of markets to scrape.
            scrape_odds_history (bool): Whether to scrape and attach odds history.
            target_bookmaker (str): If set, only scrape odds for this bookmaker.
            concurrent_scraping_task (int): Controls how many pages are processed simultaneously.
            preview_submarkets_only (bool): If True, only scrape average odds from visible submarkets without loading individual bookmaker details.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing scraped odds data.
        """
        self.logger.info(f"Starting to scrape odds for {len(match_links)} match links...")
        semaphore = asyncio.Semaphore(concurrent_scraping_task)
        failed_links = []

        async def scrape_with_semaphore(link):
            async with semaphore:
                tab = None

                try:
                    tab = await self.playwright_manager.context.new_page()
                    data = await self._scrape_match_data(
                        page=tab,
                        sport=sport,
                        match_link=link,
                        markets=markets,
                        scrape_odds_history=scrape_odds_history,
                        target_bookmaker=target_bookmaker,
                        preview_submarkets_only=preview_submarkets_only,
                    )
                    self.logger.info(f"Successfully scraped match link: {link}")
                    return data

                except Exception as e:
                    self.logger.error(f"Error scraping link {link}: {e}")
                    failed_links.append(link)
                    return None

                finally:
                    if tab:
                        await tab.close()

        tasks = [scrape_with_semaphore(link) for link in match_links]
        results = await asyncio.gather(*tasks)
        odds_data = [result for result in results if result is not None]
        self.logger.info(f"Successfully scraped odds data for {len(odds_data)} matches.")

        if failed_links:
            self.logger.warning(f"Failed to scrape data for {len(failed_links)} links: {failed_links}")

        return odds_data

    async def _scrape_match_data(
        self,
        page: Page,
        sport: str,
        match_link: str,
        markets: list[str] | None = None,
        scrape_odds_history: bool = True,  # Always scrape odds history by default
        target_bookmaker: str | None = None,
        preview_submarkets_only: bool = False,
    ) -> dict[str, Any] | None:
        """
        Scrape data for a specific match based on the desired markets.

        Args:
            page (Page): A Playwright Page instance for this task.
            sport (str): The sport to scrape odds for.
            match_link (str): The link to the match page.
            markets (Optional[List[str]]): A list of markets to scrape (e.g., ['1x2', 'over_under_2_5']).
            scrape_odds_history (bool): Whether to scrape and attach odds history.
            target_bookmaker (str): If set, only scrape odds for this bookmaker.
            preview_submarkets_only (bool): If True, only scrape average odds from visible submarkets without loading individual bookmaker details.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing scraped data, or None if scraping fails.
        """
        self.logger.info(f"Scraping match: {match_link}")

        try:
            # Navigate to the match page with extended timeout
            await page.goto(match_link, timeout=15000, wait_until="domcontentloaded")

            # Wait a bit for dynamic content to load
            await page.wait_for_timeout(2000)

            match_details = await self._extract_match_details_event_header(page)

            if not match_details:
                self.logger.warning(
                    f"No match details found for {match_link} - page may be unavailable or structure changed"
                )
                return None

            if markets:
                self.logger.info(f"Scraping markets: {markets}")
                try:
                    market_data = await self.market_extractor.scrape_markets(
                        page=page,
                        sport=sport,
                        markets=markets,
                        period="FullTime",
                        scrape_odds_history=scrape_odds_history,
                        target_bookmaker=target_bookmaker,
                        preview_submarkets_only=preview_submarkets_only,
                    )
                    if market_data:
                        match_details.update(market_data)
                    else:
                        self.logger.warning(f"No market data found for {match_link}")
                except Exception as market_error:
                    self.logger.error(f"Error scraping markets for {match_link}: {market_error}")
                    # Continue without market data rather than failing completely

            return match_details

        except Exception as e:
            self.logger.error(f"Error scraping match data from {match_link}: {e}")
            return None

    async def _extract_match_details_event_header(self, page: Page) -> dict[str, Any] | None:
        """
        Extract match details such as date, teams, and scores from the react event header.

        Args:
            page (Page): A Playwright Page instance for this task.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing match details, or None if header is not found.
        """
        try:
            # Wait for the react event header to be loaded
            try:
                await page.wait_for_selector("#react-event-header", timeout=10000)
            except Exception:
                # If we can't find the selector, try to get the content anyway
                self.logger.warning("React event header selector not found, attempting to parse existing content")

            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            event_header_div = soup.find("div", id="react-event-header")

            if not event_header_div:
                self.logger.warning("React event header div not found in page content")
                return None

            # Check if the div has the 'data' attribute
            data_attribute = event_header_div.get("data")
            if not data_attribute:
                self.logger.warning("React event header div found but 'data' attribute is missing")
                return None

            try:
                json_data = json.loads(data_attribute)
            except (TypeError, json.JSONDecodeError) as e:
                self.logger.error(f"Failed to parse JSON data from react event header: {e}")
                return None

            event_body = json_data.get("eventBody", {})
            event_data = json_data.get("eventData", {})
            unix_timestamp = event_body.get("startDate")

            match_date = (
                datetime.fromtimestamp(unix_timestamp, tz=UTC).strftime("%Y-%m-%d %H:%M:%S %Z")
                if unix_timestamp
                else None
            )

            return {
                "scraped_date": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S %Z"),
                "match_date": match_date,
                "home_team": event_data.get("home"),
                "away_team": event_data.get("away"),
                "league_name": event_data.get("tournamentName"),
                "sport": sport,  # Added sport field for better match identification
                "home_score": event_body.get("homeResult"),
                "away_score": event_body.get("awayResult"),
                "partial_results": clean_html_text(event_body.get("partialresult")),
                "venue": event_body.get("venue"),
                "venue_town": event_body.get("venueTown").encode("ascii", "ignore").decode("ascii")
                if event_body.get("venueTown")
                else None,
                "venue_country": event_body.get("venueCountry"),
            }

        except Exception as e:
            self.logger.error(f"Error extracting match details while parsing React event header: {e}")
            return None
