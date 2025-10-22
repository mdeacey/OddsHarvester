import pytest
from datetime import datetime, timedelta

from src.utils.date_utils import (
    parse_flexible_date,
    generate_date_range,
    generate_month_range,
    generate_year_range,
    format_date_for_oddsportal,
    get_date_granularity,
    validate_date_range,
    validate_season_range,
    normalize_season,
)


class TestParseFlexibleDate:
    """Test the parse_flexible_date function."""

    def test_parse_full_date(self):
        """Test parsing full date format YYYYMMDD."""
        result = parse_flexible_date("20250101")
        expected = datetime(2025, 1, 1)
        assert result == expected

    def test_parse_month(self):
        """Test parsing month format YYYYMM."""
        result = parse_flexible_date("202501")
        expected = datetime(2025, 1, 1)
        assert result == expected

    def test_parse_year(self):
        """Test parsing year format YYYY."""
        result = parse_flexible_date("2025")
        expected = datetime(2025, 1, 1)
        assert result == expected

    def test_parse_now_keyword(self):
        """Test parsing 'now' keyword."""
        result = parse_flexible_date("now")
        expected = datetime.now()
        # Allow for small time difference (within 1 second)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_now_lowercase(self):
        """Test parsing 'now' keyword in lowercase."""
        result = parse_flexible_date("now")
        expected = datetime.now()
        # Allow for small time difference (within 1 second)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_now_uppercase(self):
        """Test parsing 'now' keyword in uppercase."""
        result = parse_flexible_date("NOW")
        expected = datetime.now()
        # Allow for small time difference (within 1 second)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_invalid_format(self):
        """Test parsing invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format: 'invalid'. Supported formats: YYYYMMDD, YYYYMM, YYYY, or 'now'"):
            parse_flexible_date("invalid")

    def test_parse_invalid_date_values(self):
        """Test parsing invalid date values."""
        with pytest.raises(ValueError):
            parse_flexible_date("20251301")  # Invalid month
        with pytest.raises(ValueError):
            parse_flexible_date("20250132")  # Invalid day

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        with pytest.raises(ValueError, match="Date string cannot be empty"):
            parse_flexible_date("")

    def test_parse_none(self):
        """Test parsing None."""
        with pytest.raises(ValueError, match="Date string cannot be empty"):
            parse_flexible_date(None)


class TestGenerateDateRange:
    """Test the generate_date_range function."""

    def test_generate_single_day_range(self):
        """Test generating range with same start and end date."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 1)
        result = generate_date_range(start, end)
        assert len(result) == 1
        assert result[0] == start

    def test_generate_multi_day_range(self):
        """Test generating range with multiple days."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 5)
        result = generate_date_range(start, end)
        assert len(result) == 5
        assert result[0] == start
        assert result[-1] == end
        # Check intermediate dates
        assert result[1] == datetime(2025, 1, 2)
        assert result[2] == datetime(2025, 1, 3)

    def test_generate_date_range_end_before_start(self):
        """Test error when end date is before start date."""
        start = datetime(2025, 1, 5)
        end = datetime(2025, 1, 1)
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            generate_date_range(start, end)


class TestGenerateMonthRange:
    """Test the generate_month_range function."""

    def test_generate_single_month_range(self):
        """Test generating range with same start and end month."""
        start = datetime(2025, 1, 15)
        end = datetime(2025, 1, 20)
        result = generate_month_range(start, end)
        assert len(result) == 1
        assert result[0] == (2025, 1)

    def test_generate_multi_month_range_same_year(self):
        """Test generating range with multiple months in same year."""
        start = datetime(2025, 1, 15)
        end = datetime(2025, 3, 20)
        result = generate_month_range(start, end)
        assert len(result) == 3
        assert result[0] == (2025, 1)
        assert result[1] == (2025, 2)
        assert result[2] == (2025, 3)

    def test_generate_multi_month_range_cross_year(self):
        """Test generating range crossing year boundary."""
        start = datetime(2025, 11, 15)
        end = datetime(2026, 2, 20)
        result = generate_month_range(start, end)
        assert len(result) == 4
        assert result[0] == (2025, 11)
        assert result[1] == (2025, 12)
        assert result[2] == (2026, 1)
        assert result[3] == (2026, 2)

    def test_generate_month_range_end_before_start(self):
        """Test error when end month is before start month."""
        start = datetime(2025, 3, 15)
        end = datetime(2025, 1, 20)
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            generate_month_range(start, end)


class TestGenerateYearRange:
    """Test the generate_year_range function."""

    def test_generate_single_year_range(self):
        """Test generating range with same start and end year."""
        start = datetime(2025, 1, 15)
        end = datetime(2025, 12, 20)
        result = generate_year_range(start, end)
        assert len(result) == 1
        assert result[0] == 2025

    def test_generate_multi_year_range(self):
        """Test generating range with multiple years."""
        start = datetime(2025, 1, 15)
        end = datetime(2028, 12, 20)
        result = generate_year_range(start, end)
        assert len(result) == 4
        assert result[0] == 2025
        assert result[1] == 2026
        assert result[2] == 2027
        assert result[3] == 2028

    def test_generate_year_range_end_before_start(self):
        """Test error when end year is before start year."""
        start = datetime(2025, 1, 15)
        end = datetime(2023, 12, 20)
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            generate_year_range(start, end)


class TestFormatDateForOddsPortal:
    """Test the format_date_for_oddsportal function."""

    def test_format_date(self):
        """Test formatting date for OddsPortal URL."""
        date_obj = datetime(2025, 1, 15)
        result = format_date_for_oddsportal(date_obj)
        assert result == "2025-01-15"

    def test_format_date_with_leading_zeros(self):
        """Test formatting date with leading zeros."""
        date_obj = datetime(2025, 3, 5)
        result = format_date_for_oddsportal(date_obj)
        assert result == "2025-03-05"


class TestGetDateGranularity:
    """Test the get_date_granularity function."""

    def test_get_day_granularity(self):
        """Test getting granularity for full date."""
        granularity = get_date_granularity("20250101")
        assert granularity == "day"

    def test_get_month_granularity(self):
        """Test getting granularity for month."""
        granularity = get_date_granularity("202501")
        assert granularity == "month"

    def test_get_year_granularity(self):
        """Test getting granularity for year."""
        granularity = get_date_granularity("2025")
        assert granularity == "year"

    def test_get_now_granularity(self):
        """Test getting granularity for 'now' keyword."""
        granularity = get_date_granularity("now")
        assert granularity == "day"

    def test_get_invalid_granularity(self):
        """Test error for invalid format."""
        with pytest.raises(ValueError, match="Invalid date format: 'invalid'"):
            get_date_granularity("invalid")


class TestValidateDateRange:
    """Test the validate_date_range function."""

    def test_validate_valid_range(self):
        """Test validating a valid date range."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 10)
        # Should not raise any exception
        validate_date_range(start, end)

    def test_validate_invalid_range(self):
        """Test error when start date is after end date."""
        start = datetime(2025, 2, 5)
        end = datetime(2025, 1, 1)
        with pytest.raises(ValueError, match="Invalid date range: start date .* is after end date .*"):
            validate_date_range(start, end)

    def test_validate_equal_dates(self):
        """Test validating range with equal start and end dates."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 1)
        # Should not raise any exception
        validate_date_range(start, end)


class TestValidateSeasonRange:
    """Test the validate_season_range function."""

    def test_validate_valid_season_range(self):
        """Test validating a valid season range."""
        validate_season_range(2020, 2025)

    def test_validate_invalid_season_range(self):
        """Test error when start year is after end year."""
        with pytest.raises(ValueError, match="Invalid season range: start year .* is after end year .*"):
            validate_season_range(2034, 2020)

    def test_validate_equal_seasons(self):
        """Test validating season range with equal start and end years."""
        validate_season_range(2020, 2020)


class TestNormalizeSeason:
    """Test the normalize_season function."""

    def test_normalize_single_year(self):
        """Test normalizing single year season."""
        result = normalize_season(2023, 2023)
        assert result == "2023"

    def test_normalize_consecutive_years(self):
        """Test normalizing consecutive year season."""
        result = normalize_season(2022, 2023)
        assert result == "2022-2023"

    def test_normalize_non_consecutive_years(self):
        """Test normalizing non-consecutive years (should return start year only)."""
        result = normalize_season(2022, 2024)
        assert result == "2022"