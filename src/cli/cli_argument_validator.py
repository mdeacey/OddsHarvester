import argparse
from datetime import datetime
import re

from src.storage.storage_format import StorageFormat
from src.storage.storage_type import StorageType
from src.utils.command_enum import CommandEnum
from src.utils.date_utils import (
    parse_flexible_date, get_date_granularity, validate_date_range,
    validate_season_range, normalize_season
)
from src.utils.odds_format_enum import OddsFormat
from src.utils.sport_league_constants import SPORTS_LEAGUES_URLS_MAPPING
from src.utils.sport_market_constants import Sport
from src.utils.utils import get_supported_markets


class CLIArgumentValidator:
    def validate_args(self, args: argparse.Namespace):
        """Validates parsed CLI arguments."""
        self._validate_command(command=args.command)

        if isinstance(args.markets, str):
            args.markets = [market.strip() for market in args.markets.split(",")]

        if isinstance(args.leagues, str):
            args.leagues = [league.strip() for league in args.leagues.split(",")]

        errors = []

        if hasattr(args, "match_links"):
            errors.extend(self._validate_match_links(match_links=args.match_links, sport=args.sport))

        # Conditional validation: bypass sport/markets/leagues validation when --all flag is used without sport
        should_bypass_validation = (
            hasattr(args, "all") and args.all and
            (not hasattr(args, "sport") or args.sport is None)
        )

        if not should_bypass_validation:
            if hasattr(args, "sport"):
                errors.extend(self._validate_sport(sport=args.sport))

            if hasattr(args, "markets"):
                errors.extend(self._validate_markets(sport=args.sport, markets=args.markets))

            if hasattr(args, "leagues"):
                errors.extend(self._validate_leagues(sport=args.sport, leagues=args.leagues))

        if hasattr(args, "from_date") and hasattr(args, "to_date"):
            errors.extend(
                self._validate_date_range(
                    command=args.command,
                    from_date=args.from_date,
                    to_date=args.to_date,
                    match_links=args.match_links,
                    leagues=getattr(args, "leagues", None),
                    all_flag=getattr(args, "all", False),
                )
            )

        if hasattr(args, "file_path") or hasattr(args, "format"):
            errors.extend(self._validate_file_args(args=args))

        if hasattr(args, "max_pages"):
            errors.extend(self._validate_max_pages(command=args.command, max_pages=args.max_pages))

        if hasattr(args, "proxies"):
            errors.extend(self._validate_proxies(args.proxies))

        if hasattr(args, "target_bookmaker") and args.target_bookmaker and not isinstance(args.target_bookmaker, str):
            errors.append("Target bookmaker must be a string if specified.")

  
        if hasattr(args, "odds_format"):
            errors.extend(self._validate_odds_format(odds_format=args.odds_format))

        if hasattr(args, "concurrency_tasks"):
            errors.extend(self._validate_concurrency_tasks(concurrency_tasks=args.concurrency_tasks))

        errors.extend(
            self._validate_browser_settings(
                user_agent=args.browser_user_agent,
                locale_timezone=args.browser_locale_timezone,
                timezone_id=args.browser_timezone_id,
            )
        )
        errors.extend(self._validate_storage(storage=args.storage))

        if errors:
            raise ValueError("\n".join(errors))

    def _validate_command(self, command: str | None):
        """Validates the command argument."""
        if command not in CommandEnum.__members__.values():
            raise ValueError(
                f"Invalid command '{command}'. Supported commands are: {', '.join(e.value for e in CommandEnum)}."
            )

    def _validate_match_links(self, match_links: list[str] | None, sport: str | None) -> list[str]:
        """Validates the format of match links."""
        errors = []
        url_pattern = re.compile(r"https?://www\.oddsportal\.com/.+")

        if match_links:
            if not sport:
                errors.append("The '--sport' argument is required when using '--match_links'.")

            for link in match_links:
                if not url_pattern.match(link):
                    errors.append(f"Invalid match link format: {link}")

        return errors

    def _validate_sport(self, sport: str | None) -> list[str]:
        """Validates the sport argument."""
        errors = []
        supported_sports = ", ".join(s.value for s in Sport)

        if not sport:
            error_msg = f"Invalid sport: None. Expected one of {[s.value for s in Sport]}."
            errors.append(error_msg)
            raise ValueError(error_msg)

        try:
            Sport(str(sport).lower())
        except (ValueError, AttributeError):
            if isinstance(sport, str):
                error_msg = f"Invalid sport: '{sport}'. Supported sports are: {supported_sports}."
            else:
                error_msg = f"Invalid sport: {sport}. Expected one of {[s.value for s in Sport]}."
            errors.append(error_msg)
            raise ValueError(error_msg) from None

        return errors

    def _validate_markets(self, sport: Sport, markets: list[str]) -> list[str]:
        """Validates markets against the selected sport."""
        errors = []

        if isinstance(sport, str):
            try:
                sport = Sport(sport.lower())
            except ValueError:
                return [f"Invalid sport: '{sport}'. Supported sports are: {', '.join(s.value for s in Sport)}."]

        supported_markets = get_supported_markets(sport)

        if markets:
            for market in markets:
                if market not in supported_markets:
                    errors.append(
                        f"Invalid market: {market}. Supported markets for {sport.value}: "
                        f"{', '.join(supported_markets)}."
                    )

        return errors

    def _validate_leagues(self, sport: str, leagues: list[str] | None) -> list[str]:
        """Validates the leagues argument based on the sport."""
        errors = []

        if not leagues:
            return errors

        try:
            sport_enum = Sport(sport.lower()) if isinstance(sport, str) else sport
        except ValueError:
            return [f"Invalid sport: '{sport}'. Supported sports are: {', '.join(s.value for s in Sport)}."]

        if sport_enum not in SPORTS_LEAGUES_URLS_MAPPING:
            errors.append(f"Sport '{sport}' is not supported for league validation.")
            return errors

        supported_leagues = SPORTS_LEAGUES_URLS_MAPPING[sport_enum]
        for league in leagues:
            if league not in supported_leagues:
                errors.append(f"Invalid league: '{league}' for sport '{sport_enum.value}'.")

        return errors

    def _validate_date_range(
        self, command: str, from_date: str | None, to_date: str | None, match_links: list[str] | None, leagues: list[str] | None = None, all_flag: bool = False
    ) -> list[str]:
        """Validates the from/to date range arguments for both upcoming and historic commands."""
        errors = []

        # Date range not required when match_links or leagues is provided, but is required for --all flag
        if match_links or (leagues and not all_flag):
            return errors

        if command == "scrape_upcoming":
            return self._validate_upcoming_date_range(from_date, to_date)
        elif command == "scrape_historic":
            return self._validate_historic_date_range(from_date, to_date)
        else:
            # Date ranges shouldn't be provided for other commands
            if from_date or to_date:
                errors.append(f"Date ranges should not be provided for the '{command}' command.")
            return errors

    def _validate_upcoming_date_range(self, from_date: str | None, to_date: str | None) -> list[str]:
        """Validates date range for upcoming matches."""
        errors = []

        # Default to "now" if neither from_date nor to_date is provided (all upcoming)
        if not from_date and not to_date:
            from_date = "now"
            to_date = None  # No end limit for all upcoming matches

        # Default to_date to from_date if only from_date is provided (single date)
        elif from_date and not to_date:
            to_date = from_date

        # Default from_date to "now" if only to_date is provided
        elif not from_date and to_date:
            from_date = "now"

        try:
            start_date = parse_flexible_date(from_date)
            # Only parse end_date if it's provided (not None)
            if to_date:
                end_date = parse_flexible_date(to_date)
            else:
                # For unlimited future, use a very distant future date
                end_date = None
        except ValueError as e:
            errors.append(str(e))
            return errors

        # Validate date range order (only if end_date is specified)
        if end_date and end_date < start_date:
            errors.append("--to date cannot be before --from date.")
            return errors

        # Validate that start date is not too far in the past for upcoming matches
        if start_date.date() < datetime.now().date():
            errors.append("--from date must be today or in the future for upcoming matches.")

        # Validate date range size (only if both dates are specified and end_date is not None)
        if end_date:
            try:
                validate_date_range(start_date, end_date)
            except ValueError as e:
                errors.append(str(e))

        return errors

    def _validate_historic_date_range(self, from_date: str | None, to_date: str | None) -> list[str]:
        """Validates season/year range for historical matches."""
        errors = []

        # Default to "now" if neither from_date nor to_date is provided (all historical)
        if not from_date and not to_date:
            from_date = "now"
            to_date = None  # No start limit for all historical (going backwards)

        # Default to_date to from_date if only from_date is provided (single season)
        elif from_date and not to_date:
            to_date = from_date

        # Default to_date to "now" if only to_date is provided (from past to now)
        elif not from_date and to_date:
            # This means from earliest available data up to the specified end
            from_date = None  # No start limit for all historical (going backwards)

        # Validate season formats (YYYY or YYYY-YYYY)
        try:
            if from_date:
                start_season = self._parse_season(from_date)
            else:
                # For unlimited past, use a very early year
                start_season = (None, 1900)  # (format, year)

            if to_date:
                end_season = self._parse_season(to_date)
            else:
                # Default to current year for end if not specified
                end_season = (str(datetime.now().year), datetime.now().year)
        except ValueError as e:
            errors.append(str(e))
            return errors

        # Validate season range order (only if both dates are specified)
        if from_date and end_season[1] < start_season[1]:
            # For historical matches, automatically swap dates if they're in wrong order
            # This handles cases like --from now --to 2023, treating it as --from 2023 --to now
            start_season, end_season = end_season, start_season

        # Validate season range size (only if both dates are specified)
        if from_date:
            try:
                validate_season_range(start_season[1], end_season[1])
            except ValueError as e:
                errors.append(str(e))

        return errors

    def _parse_season(self, season_str: str) -> tuple[str, int]:
        """
        Parse season string and return (season_format, end_year).

        Args:
            season_str: Season string in YYYY, YYYY-YYYY, or 'now' format

        Returns:
            Tuple of (season_format, end_year) where season_format is the string to use in URLs
        """
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

    def _validate_storage(self, storage: str) -> list[str]:
        """Validates the storage argument."""
        try:
            StorageType(storage)
        except ValueError:
            return [
                f"Invalid storage type: '{storage}'. Supported storage types are: "
                f"{', '.join([e.value for e in StorageType])}"
            ]
        return []

    def _validate_file_args(self, args: argparse.Namespace) -> list[str]:
        """Validates the file_path and file_format arguments."""
        errors = []

        extracted_format = None
        if args.file_path:
            if "." in args.file_path:
                extracted_format = args.file_path.split(".")[-1].lower()
            else:
                errors.append(
                    f"File path '{args.file_path}' must include a valid file extension (e.g., '.csv' or '.json')."
                )

        if args.format:
            if args.format not in [f.value for f in StorageFormat]:
                errors.append(
                    f"Invalid file format: '{args.format}'. Supported formats are: "
                    f"{', '.join(f.value for f in StorageFormat)}."
                )
            elif extracted_format and args.format != extracted_format:
                errors.append(
                    f"Mismatch between file format '{args.format}' and file path extension '{extracted_format}'."
                )

        elif extracted_format:
            if extracted_format not in [f.value for f in StorageFormat]:
                errors.append(
                    f"Invalid file extension in file path: '{extracted_format}'. Supported formats are: "
                    f"{', '.join(f.value for f in StorageFormat)}."
                )
            args.format = extracted_format

        if args.file_path and args.format and not args.file_path.endswith(f".{args.format}"):
            errors.append(f"File path '{args.file_path}' must end with '.{args.format}'.")

        return errors

    def _validate_max_pages(self, command: str, max_pages: int | None) -> list[str]:
        """Validates the max_pages argument (only for scrape_historic)."""
        errors = []

        if command != "scrape_historic":
            return errors  # max_pages is only valid for scrape_historic

        if max_pages is not None and (not isinstance(max_pages, int) or max_pages <= 0):
            errors.append(f"Invalid max-pages value: '{max_pages}'. It must be a positive integer.")

        return errors

    def _validate_proxies(self, proxies: list[str] | None) -> list[str]:
        """Validates proxy format (supports http, https, socks5 with optional auth)."""
        errors = []
        if not proxies:
            return errors

        proxy_pattern = re.compile(
            r"^(?P<scheme>https?|socks5|socks4)://(?P<host>[\w\.-]+):(?P<port>\d+)(?:\s+(?P<user>\S+)\s+(?P<pass>\S+))?$"
        )

        for proxy in proxies:
            if not proxy_pattern.match(proxy):
                errors.append(
                    f"Invalid proxy format: '{proxy}'. Expected format: "
                    f"'http[s]://host:port [user pass]' or 'socks5://host:port [user pass]'."
                )

        return errors

    def _validate_browser_settings(
        self, user_agent: str | None, locale_timezone: str | None, timezone_id: str | None
    ) -> list[str]:
        """Validates the browser-related CLI arguments."""
        errors = []

        if user_agent and not isinstance(user_agent, str):
            errors.append("Invalid browser user agent format.")

        if locale_timezone and not isinstance(locale_timezone, str):
            errors.append("Invalid browser locale timezone format.")

        if timezone_id and not isinstance(timezone_id, str):
            errors.append("Invalid browser timezone ID format.")

        return errors

    def _validate_odds_format(self, odds_format: str) -> list[str]:
        """Validates the odds format argument."""
        errors = []
        try:
            OddsFormat(odds_format)
        except ValueError:
            supported_formats = ", ".join([f.value for f in OddsFormat])
            errors.append(f"Invalid odds format: '{odds_format}'. Supported formats are: {supported_formats}.")
        return errors

    def _validate_concurrency_tasks(self, concurrency_tasks: int) -> list[str]:
        """Validates the concurrency tasks argument."""
        errors = []
        if not isinstance(concurrency_tasks, int) or concurrency_tasks <= 0:
            errors.append(f"Invalid concurrency tasks value: '{concurrency_tasks}'. It must be a positive integer.")
        return errors
