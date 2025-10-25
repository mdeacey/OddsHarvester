import asyncio
import logging
import sys
import os

from src.cli.cli_argument_handler import CLIArgumentHandler
from src.core.scraper_app import run_scraper
from src.storage.storage_manager import store_data
from src.utils.setup_logging import setup_logger
from src.utils.change_detection_service import ChangeDetectionService, IncrementalScrapingManager


def main():
    """Main entry point for CLI usage."""
    setup_logger(log_level=logging.DEBUG, save_to_file=False)
    logger = logging.getLogger("Main")

    try:
        args = CLIArgumentHandler().parse_and_validate_args()
        logger.info(f"Parsed arguments: {args}")

        # Initialize change detection (always enabled)
        storage_dir = os.path.dirname(args["file_path"]) if args.get("file_path") else "."
        change_detection_service = ChangeDetectionService(
            storage_dir=storage_dir,
            change_sensitivity=args.get("change_sensitivity", "normal"),
            logger=logger
        )
        incremental_manager = IncrementalScrapingManager(change_detection_service, logger)
        logger.info(f"Duplicate detection enabled with sensitivity: {args.get('change_sensitivity', 'normal')}")

        scraped_data = asyncio.run(
            run_scraper(
                command=args["command"],
                match_links=args["match_links"],
                sports=args["sports"],
                from_date=args["from_date"],
                to_date=args["to_date"],
                leagues=args["leagues"],
                markets=args["markets"],
                max_pages=args["max_pages"],
                proxies=args["proxies"],
                browser_user_agent=args["browser_user_agent"],
                browser_locale_timezone=args["browser_locale_timezone"],
                browser_timezone_id=args["browser_timezone_id"],
                target_bookmaker=args["target_bookmaker"],
                scrape_odds_history=args["scrape_odds_history"],
                headless=args["headless"],
                preview_submarkets_only=args["preview_submarkets_only"],
                change_sensitivity=args.get("change_sensitivity", "normal"),
            )
        )

        if scraped_data:
            # Apply duplicate detection filtering
            filtered_data = scraped_data
            change_results = None

            if args.get("file_path"):
                filtered_data, change_results = incremental_manager.filter_matches_for_scraping(
                    scraped_data, args["file_path"]
                )

            # Store data with duplicate detection (always enabled)
            success = store_data(
                storage_type=args["storage_type"],
                data=filtered_data,
                storage_format=args["storage_format"],
                file_path=args["file_path"],
                change_results=change_results,
            )

            if success:
                logger.info(f"Successfully stored {len(filtered_data)} records.")

                # Log performance metrics
                metrics = incremental_manager.get_performance_metrics()
                logger.info(f"Duplicate detection performance: {metrics}")
            else:
                logger.error("Failed to store data.")
                sys.exit(1)
        else:
            logger.error("Scraper did not return valid data.")
            sys.exit(1)

    except ValueError as e:
        logger.error(f"Argument validation failed: {e!s}")

    except Exception as e:
        logger.error(f"Unexpected error: {e!s}", exc_info=True)


if __name__ == "__main__":
    main()
