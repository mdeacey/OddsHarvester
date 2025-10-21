from datetime import datetime, timedelta
from typing import List, Tuple, Optional


def parse_flexible_date(date_str: str) -> datetime:
    """
    Parse flexible date formats into datetime objects.

    Supports:
    - YYYYMMDD for specific dates
    - YYYYMM for entire months (returns first day of month)
    - YYYY for entire years (returns January 1st of that year)
    - "now" keyword for current date

    Args:
        date_str: Date string in various formats

    Returns:
        datetime: Parsed datetime object

    Raises:
        ValueError: If date format is not recognized
    """
    if not date_str:
        raise ValueError("Date string cannot be empty")

    date_str = date_str.strip().lower()

    if date_str == "now":
        return datetime.now()

    # YYYYMMDD format
    if len(date_str) == 8 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            pass

    # YYYYMM format
    if len(date_str) == 6 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y%m")
        except ValueError:
            pass

    # YYYY format
    if len(date_str) == 4 and date_str.isdigit():
        try:
            return datetime.strptime(date_str, "%Y")
        except ValueError:
            pass

    raise ValueError(
        f"Invalid date format: '{date_str}'. "
        "Supported formats: YYYYMMDD, YYYYMM, YYYY, or 'now'"
    )


def generate_date_range(start_date: datetime, end_date: datetime) -> List[datetime]:
    """
    Generate a list of dates from start_date to end_date (inclusive).

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        List of datetime objects representing each day in the range

    Raises:
        ValueError: If end_date is before start_date
    """
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")

    dates = []
    current_date = start_date

    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    return dates


def generate_month_range(start_date: datetime, end_date: datetime) -> List[Tuple[int, int]]:
    """
    Generate a list of (year, month) tuples from start_date to end_date (inclusive).

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        List of (year, month) tuples

    Raises:
        ValueError: If end_date is before start_date
    """
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")

    months = []
    current_year = start_date.year
    current_month = start_date.month
    end_year = end_date.year
    end_month = end_date.month

    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
        months.append((current_year, current_month))
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    return months


def generate_year_range(start_date: datetime, end_date: datetime) -> List[int]:
    """
    Generate a list of years from start_date to end_date (inclusive).

    Args:
        start_date: Starting date
        end_date: Ending date

    Returns:
        List of years

    Raises:
        ValueError: If end_date is before start_date
    """
    if end_date < start_date:
        raise ValueError("End date cannot be before start date")

    years = []
    for year in range(start_date.year, end_date.year + 1):
        years.append(year)

    return years


def format_date_for_oddsportal(date_obj: datetime) -> str:
    """
    Format datetime object as YYYY-MM-DD string for OddsPortal URLs.

    Args:
        date_obj: datetime object

    Returns:
        Formatted date string
    """
    return date_obj.strftime("%Y-%m-%d")


def get_date_granularity(date_str: str) -> str:
    """
    Determine the granularity of a date string.

    Args:
        date_str: Date string in various formats

    Returns:
        String indicating granularity: 'day', 'month', or 'year'

    Raises:
        ValueError: If date format is not recognized
    """
    date_str = date_str.strip().lower()

    if date_str == "now":
        return "day"

    if len(date_str) == 8 and date_str.isdigit():
        return "day"
    elif len(date_str) == 6 and date_str.isdigit():
        return "month"
    elif len(date_str) == 4 and date_str.isdigit():
        return "year"
    else:
        raise ValueError(
            f"Invalid date format: '{date_str}'. "
            "Supported formats: YYYYMMDD, YYYYMM, YYYY, or 'now'"
        )


def validate_date_range(start_date: datetime, end_date: datetime, max_days: int = 30) -> None:
    """
    Validate that a date range doesn't exceed maximum allowed days.

    Args:
        start_date: Starting date
        end_date: Ending date
        max_days: Maximum number of days allowed

    Raises:
        ValueError: If date range exceeds maximum allowed days
    """
    days_diff = (end_date - start_date).days + 1  # Include both start and end dates

    if days_diff > max_days:
        raise ValueError(
            f"Date range too large: {days_diff} days. "
            f"Maximum allowed is {max_days} days for upcoming matches."
        )


def validate_season_range(start_year: int, end_year: int, max_years: int = 10) -> None:
    """
    Validate that a season range doesn't exceed maximum allowed years.

    Args:
        start_year: Starting year
        end_year: Ending year
        max_years: Maximum number of years allowed

    Raises:
        ValueError: If season range exceeds maximum allowed years
    """
    years_diff = end_year - start_year + 1

    if years_diff > max_years:
        raise ValueError(
            f"Season range too large: {years_diff} years. "
            f"Maximum allowed is {max_years} years for historical matches."
        )


def normalize_season(start_year: int, end_year: int) -> str:
    """
    Normalize season format to either single year or year-year format.

    Args:
        start_year: Starting year
        end_year: Ending year

    Returns:
        Season string in format "YYYY" or "YYYY-YYYY"
    """
    if start_year == end_year:
        return str(start_year)
    elif end_year == start_year + 1:
        return f"{start_year}-{end_year}"
    else:
        # For non-consecutive years, return start year only
        # This could be extended to support custom season ranges if needed
        return str(start_year)