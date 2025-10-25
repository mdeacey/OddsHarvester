import logging
from typing import Any

from playwright.async_api import Page

from src.core.browser_helper import BrowserHelper
from src.core.market_extraction import (
    MarketGrouping,
    NavigationManager,
    OddsHistoryExtractor,
    OddsParser,
    SubmarketExtractor,
)
from src.core.sport_market_registry import SportMarketRegistry


class OddsPortalMarketExtractor:
    """
    Extracts betting odds data from OddsPortal using Playwright.

    This class provides methods to scrape various betting markets (e.g., 1X2, Over/Under, BTTS, ..)
    for specific match periods and bookmaker odds.
    """

    DEFAULT_TIMEOUT = 5000
    SCROLL_PAUSE_TIME = 2000
    MARKET_SWITCH_WAIT_TIME = 3000

    def __init__(self, browser_helper: BrowserHelper):
        """
        Initialize OddsPortalMarketExtractor.

        Args:
            browser_helper (BrowserHelper): Helper class for browser interactions.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser_helper = browser_helper

        # Initialize component classes
        self.navigation_manager = NavigationManager(browser_helper)
        self.odds_parser = OddsParser()
        self.submarket_extractor = SubmarketExtractor()
        self.odds_history_extractor = OddsHistoryExtractor()
        self.market_grouping = MarketGrouping()

    async def scrape_markets(
        self,
        page: Page,
        sport: str,
        markets: list[str],
        period: str = "FullTime",
        scrape_odds_history: bool = True,  # Always scrape odds history by default
        target_bookmaker: str | None = None,
        preview_submarkets_only: bool = False,
    ) -> dict[str, Any]:
        """
        Extract market data for a given match.

        Args:
            page (Page): A Playwright Page instance for this task.
            sport (str): The sport to scrape odds for.
            markets (List[str]): A list of markets to scrape (e.g., ['1x2', 'over_under_2_5']).
            period (str): The match period (e.g., "FullTime").
            scrape_odds_history (bool): Whether to extract historic odds evolution.
            target_bookmaker (str): If set, only scrape odds for this bookmaker.
            preview_submarkets_only (bool): If True, only scrape average odds from visible submarkets.

        Returns:
            Dict[str, Any]: A dictionary containing market data.
        """
        market_data = {}
        market_methods = SportMarketRegistry.get_market_mapping(sport)
        discovered_markets = SportMarketRegistry.get_discovered_markets(sport)

        # Group markets by their main market type for optimization in preview mode
        market_groups = {}

        for market in markets:
            try:
                if market in market_methods:
                    # Handle traditional markets with registered methods
                    # For preview mode, group markets by their main market type
                    if preview_submarkets_only:
                        # Get the main market info from the existing market method
                        main_market_info = self.market_grouping.get_main_market_info(market_methods[market])
                        if main_market_info:
                            main_market_name = main_market_info["main_market"]
                            if main_market_name not in market_groups:
                                market_groups[main_market_name] = []
                            market_groups[main_market_name].append(market)
                    else:
                        # Normal mode: scrape each market individually
                        self.logger.info(f"Scraping market: {market} (Period: {period})")
                        market_data[f"{market}_market"] = await market_methods[market](
                            self, page, period, scrape_odds_history, target_bookmaker, preview_submarkets_only
                        )
                elif market in discovered_markets:
                    # Handle auto-discovered markets
                    self.logger.info(f"Scraping discovered market: {market} (Period: {period})")
                    market_data[f"{market}_market"] = await self._scrape_discovered_market(
                        page, market, discovered_markets[market], sport, period, scrape_odds_history, target_bookmaker
                    )
                else:
                    self.logger.warning(f"Market '{market}' is not supported for sport '{sport}'.")

            except Exception as e:
                self.logger.error(f"Error scraping market '{market}': {e}")
                market_data[f"{market}_market"] = None

        # Handle grouped markets in preview mode
        if preview_submarkets_only and market_groups:
            for main_market_name, grouped_markets in market_groups.items():
                try:
                    self.logger.info(
                        f"Scraping main market: {main_market_name} for submarkets: {grouped_markets} (Period: {period})"
                    )

                    # Use the first market in the group to get the odds labels
                    first_market = grouped_markets[0]
                    if first_market in market_methods:
                        main_market_info = self.market_grouping.get_main_market_info(market_methods[first_market])
                        odds_labels = main_market_info["odds_labels"] if main_market_info else None

                        # Scrape the main market once
                        main_market_data = await self.extract_market_odds(
                            page=page,
                            main_market=main_market_name,
                            specific_market=None,  # No specific market, scrape all submarkets
                            period=period,
                            odds_labels=odds_labels,
                            scrape_odds_history=scrape_odds_history,
                            target_bookmaker=target_bookmaker,
                            preview_submarkets_only=preview_submarkets_only,
                        )

                        # Distribute the results to each specific market
                        for specific_market in grouped_markets:
                            market_data[f"{specific_market}_market"] = main_market_data

                except Exception as e:
                    self.logger.error(f"Error scraping grouped markets for {main_market_name}: {e}")
                    for specific_market in grouped_markets:
                        market_data[f"{specific_market}_market"] = None

        return market_data

    async def _scrape_discovered_market(
        self,
        page: Page,
        market_name: str,
        display_name: str,
        sport: str,
        period: str,
        scrape_odds_history: bool,
        target_bookmaker: str | None,
    ) -> dict[str, Any]:
        """
        Scrape a discovered market that doesn't have a registered extraction method.

        Args:
            page: Playwright page instance
            market_name: Normalized market name
            display_name: Display name from the page
            sport: Sport name
            period: Match period
            scrape_odds_history: Whether to scrape odds history
            target_bookmaker: Specific bookmaker to target

        Returns:
            Dict containing market data
        """
        try:
            # Try to determine market type and create appropriate extraction method
            main_market = self._determine_main_market_type(market_name, display_name)
            specific_market = display_name if display_name != main_market else None

            # Map to common odds labels based on market type
            odds_labels = self._get_odds_labels_for_market_type(main_market, market_name)

            # Use the existing extract_market_odds method with inferred parameters
            return await self.extract_market_odds(
                page=page,
                main_market=main_market,
                specific_market=specific_market,
                period=period,
                odds_labels=odds_labels,
                scrape_odds_history=scrape_odds_history,
                target_bookmaker=target_bookmaker,
                preview_submarkets_only=False,
            )

        except Exception as e:
            self.logger.error(f"Error scraping discovered market '{market_name}': {e}")
            return {"error": str(e), "market_name": market_name, "display_name": display_name}

    def _determine_main_market_type(self, market_name: str, display_name: str) -> str:
        """
        Determine the main market type based on normalized market name and display name.

        Args:
            market_name: Normalized market name
            display_name: Display name from page

        Returns:
            Main market type for extraction
        """
        display_lower = display_name.lower()

        # Map market patterns to main market types
        if any(pattern in display_lower for pattern in ['1x2', '1 x 2', 'win/draw/win']):
            return "1X2"
        elif any(pattern in display_lower for pattern in ['home/away', 'home away', 'match winner']):
            return "Home/Away"
        elif any(pattern in display_lower for pattern in ['over/under', 'over under', 'total']):
            return "Over/Under"
        elif any(pattern in display_lower for pattern in ['handicap', 'spread', 'point']):
            return "Handicap"
        elif any(pattern in display_lower for pattern in ['draw no bet', 'dnb']):
            return "Draw No Bet"
        elif any(pattern in display_lower for pattern in ['double chance']):
            return "Double Chance"
        elif any(pattern in display_lower for pattern in ['correct score']):
            return "Correct Score"
        elif any(pattern in display_lower for pattern in ['both teams to score', 'btts']):
            return "Both Teams to Score"
        elif any(pattern in display_lower for pattern in ['odd or even', 'odd/even']):
            return "Odd or Even"
        else:
            # Default to 1X2 for unknown markets
            self.logger.warning(f"Unknown market type for '{display_name}', defaulting to 1X2")
            return "1X2"

    def _get_odds_labels_for_market_type(self, main_market: str, market_name: str) -> list[str]:
        """
        Get appropriate odds labels for a market type.

        Args:
            main_market: Main market type
            market_name: Normalized market name

        Returns:
            List of odds labels
        """
        if main_market == "1X2":
            return ["1", "X", "2"]
        elif main_market == "Home/Away":
            return ["1", "2"]
        elif main_market in ["Over/Under", "Handicap"]:
            return ["odds_over", "odds_under"]
        elif main_market == "Draw No Bet":
            return ["dnb_team1", "dnb_team2"]
        elif main_market == "Double Chance":
            return ["1X", "12", "X2"]
        elif main_market == "Both Teams to Score":
            return ["btts_yes", "btts_no"]
        elif main_market == "Odd or Even":
            return ["odd", "even"]
        else:
            # Default to simple binary outcome
            return ["outcome1", "outcome2"]

    async def extract_market_odds(
        self,
        page: Page,
        main_market: str,
        specific_market: str | None = None,
        period: str = "FullTime",
        odds_labels: list | None = None,
        scrape_odds_history: bool = True,  # Always scrape odds history by default
        target_bookmaker: str | None = None,
        preview_submarkets_only: bool = False,
    ) -> list:
        """
        Extracts odds for a given main market and optional specific sub-market.

        Args:
            page (Page): The Playwright page instance.
            main_market (str): The main market name (e.g., "Over/Under", "European Handicap").
            specific_market (str, optional): The specific market within the main market (e.g., "Over/Under 2.5", ...)
            period (str): The match period (e.g., "FullTime").
            odds_labels (list): Labels corresponding to odds values in the extracted data.
            scrape_odds_history (bool): Whether to scrape and attach odds history.
            target_bookmaker (str): If set, only scrape odds for this bookmaker.
            preview_submarkets_only (bool): If True, only scrape average odds from visible submarkets.

        Returns:
            list[dict]: A list of dictionaries containing bookmaker odds.
        """
        self.logger.info(
            f"Scraping odds for market: {main_market}, specific: {specific_market}, period: {period}, "
            f"preview_mode: {preview_submarkets_only}"
        )

        try:
            # Navigate to the main market tab
            if not await self.navigation_manager.navigate_to_market_tab(page=page, market_tab_name=main_market):
                self.logger.error(f"Failed to find or click {main_market} tab")
                return []

            # Wait for market switch to complete
            await self.navigation_manager.wait_for_market_switch(page, main_market)

            # Handle different scraping modes
            if preview_submarkets_only:
                # For preview mode, always try passive extraction first
                self.logger.info(f"Using passive mode for {main_market} in preview mode")
                odds_data = await self.submarket_extractor.extract_visible_submarkets_passive(
                    page=page, main_market=main_market, period=period, odds_labels=odds_labels
                )

                # If no data was extracted passively, fall back to normal scraping
                if not odds_data:
                    self.logger.info(f"No data extracted passively for {main_market}, falling back to normal scraping")
                    if specific_market and not await self.navigation_manager.select_specific_market(
                        page=page, specific_market=specific_market
                    ):
                        self.logger.error(f"Failed to find or select {specific_market} within {main_market}")
                        return []

                    await self.navigation_manager.wait_for_page_load(page)
                    html_content = await page.content()

                    odds_data = self.odds_parser.parse_market_odds(
                        html_content=html_content,
                        period=period,
                        odds_labels=odds_labels,
                        target_bookmaker=target_bookmaker,
                    )
            else:
                # Active mode: click on specific submarket if provided
                if specific_market and not await self.navigation_manager.select_specific_market(
                    page=page, specific_market=specific_market
                ):
                    self.logger.error(f"Failed to find or select {specific_market} within {main_market}")
                    return []

                await self.navigation_manager.wait_for_page_load(page)
                html_content = await page.content()

                odds_data = self.odds_parser.parse_market_odds(
                    html_content=html_content, period=period, odds_labels=odds_labels, target_bookmaker=target_bookmaker
                )

            if scrape_odds_history:
                self.logger.info("Fetching odds history for all parsed bookmakers.")

                for odds_entry in odds_data:
                    bookmaker_name = odds_entry.get("bookmaker_name")

                    if not bookmaker_name or (target_bookmaker and bookmaker_name.lower() != target_bookmaker.lower()):
                        continue

                    modals = await self.odds_history_extractor.extract_odds_history_for_bookmaker(page, bookmaker_name)

                    if modals:
                        all_histories = []
                        for modal_html in modals:
                            parsed_history = self.odds_parser.parse_odds_history_modal(modal_html)
                            if parsed_history:
                                all_histories.append(parsed_history)

                        odds_entry["odds_history_data"] = all_histories

            # Close the sub-market after scraping to avoid duplicates
            if specific_market:
                await self.navigation_manager.close_specific_market(page, specific_market)

            return odds_data

        except Exception as e:
            self.logger.error(f"Error extracting odds for {main_market} {specific_market}: {e}")
            return []
