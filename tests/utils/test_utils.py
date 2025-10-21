from unittest.mock import patch

import pytest

from src.utils.sport_market_constants import (
    AmericanFootballMarket,
    AmericanFootballOverUnderMarket,
    AussieRulesMarket,
    AussieRulesOverUnderMarket,
    BadmintonMarket,
    BadmintonOverUnderMarket,
    BandyMarket,
    BandyOverUnderMarket,
    BaseballMarket,
    BaseballOverUnderMarket,
    BasketballAsianHandicapMarket,
    BasketballMarket,
    BasketballOverUnderMarket,
    BoxingMarket,
    CricketMarket,
    CricketOverUnderMarket,
    DartsMarket,
    EsportsMarket,
    FloorballMarket,
    FloorballOverUnderMarket,
    FootballAsianHandicapMarket,
    FootballEuropeanHandicapMarket,
    FootballMarket,
    FootballOverUnderMarket,
    FutsalMarket,
    FutsalOverUnderMarket,
    HandballMarket,
    HandballOverUnderMarket,
    IceHockeyMarket,
    IceHockeyOverUnderMarket,
    MmaMarket,
    RugbyHandicapMarket,
    RugbyLeagueMarket,
    RugbyOverUnderMarket,
    RugbyUnionMarket,
    SnookerMarket,
    Sport,
    TableTennisMarket,
    TennisAsianHandicapGamesMarket,
    TennisAsianHandicapSetsMarket,
    TennisCorrectScoreMarket,
    TennisMarket,
    TennisOverUnderGamesMarket,
    TennisOverUnderSetsMarket,
    VolleyballMarket,
    VolleyballOverUnderMarket,
    WaterPoloMarket,
    WaterPoloOverUnderMarket,
)
from src.utils.utils import clean_html_text, get_supported_markets, is_running_in_docker

EXPECTED_MARKETS = {
    # Original sports
    Sport.FOOTBALL: [
        *[market.value for market in FootballMarket],
        *[market.value for market in FootballOverUnderMarket],
        *[market.value for market in FootballEuropeanHandicapMarket],
        *[market.value for market in FootballAsianHandicapMarket],
    ],
    Sport.TENNIS: [
        *[market.value for market in TennisMarket],
        *[market.value for market in TennisOverUnderSetsMarket],
        *[market.value for market in TennisOverUnderGamesMarket],
        *[market.value for market in TennisAsianHandicapGamesMarket],
        *[market.value for market in TennisAsianHandicapSetsMarket],
        *[market.value for market in TennisCorrectScoreMarket],
    ],
    Sport.BASKETBALL: [
        *[market.value for market in BasketballMarket],
        *[market.value for market in BasketballAsianHandicapMarket],
        *[market.value for market in BasketballOverUnderMarket],
    ],
    Sport.RUGBY_LEAGUE: [
        *[market.value for market in RugbyLeagueMarket],
        *[market.value for market in RugbyOverUnderMarket],
        *[market.value for market in RugbyHandicapMarket],
    ],
    Sport.RUGBY_UNION: [
        *[market.value for market in RugbyUnionMarket],
        *[market.value for market in RugbyOverUnderMarket],
        *[market.value for market in RugbyHandicapMarket],
    ],
    Sport.ICE_HOCKEY: [
        *[market.value for market in IceHockeyMarket],
        *[market.value for market in IceHockeyOverUnderMarket],
    ],
    Sport.BASEBALL: [
        *[market.value for market in BaseballMarket],
        *[market.value for market in BaseballOverUnderMarket],
    ],
    # New sports
    Sport.AMERICAN_FOOTBALL: [
        *[market.value for market in AmericanFootballMarket],
        *[market.value for market in AmericanFootballOverUnderMarket],
    ],
    Sport.AUSSIE_RULES: [
        *[market.value for market in AussieRulesMarket],
        *[market.value for market in AussieRulesOverUnderMarket],
    ],
    Sport.BADMINTON: [
        *[market.value for market in BadmintonMarket],
        *[market.value for market in BadmintonOverUnderMarket],
    ],
    Sport.BANDY: [
        *[market.value for market in BandyMarket],
        *[market.value for market in BandyOverUnderMarket],
    ],
    Sport.BOXING: [
        *[market.value for market in BoxingMarket],
    ],
    Sport.CRICKET: [
        *[market.value for market in CricketMarket],
        *[market.value for market in CricketOverUnderMarket],
    ],
    Sport.DARTS: [
        *[market.value for market in DartsMarket],
    ],
    Sport.ESPORTS: [
        *[market.value for market in EsportsMarket],
    ],
    Sport.FLOORBALL: [
        *[market.value for market in FloorballMarket],
        *[market.value for market in FloorballOverUnderMarket],
    ],
    Sport.FUTSAL: [
        *[market.value for market in FutsalMarket],
        *[market.value for market in FutsalOverUnderMarket],
    ],
    Sport.HANDBALL: [
        *[market.value for market in HandballMarket],
        *[market.value for market in HandballOverUnderMarket],
    ],
    Sport.MMA: [
        *[market.value for market in MmaMarket],
    ],
    Sport.SNOOKER: [
        *[market.value for market in SnookerMarket],
    ],
    Sport.TABLE_TENNIS: [
        *[market.value for market in TableTennisMarket],
    ],
    Sport.VOLLEYBALL: [
        *[market.value for market in VolleyballMarket],
        *[market.value for market in VolleyballOverUnderMarket],
    ],
    Sport.WATER_POLO: [
        *[market.value for market in WaterPoloMarket],
        *[market.value for market in WaterPoloOverUnderMarket],
    ],
}


@pytest.mark.parametrize(
    ("sport_enum", "expected"),
    [
        # Original sports
        (Sport.FOOTBALL, EXPECTED_MARKETS[Sport.FOOTBALL]),
        (Sport.TENNIS, EXPECTED_MARKETS[Sport.TENNIS]),
        (Sport.BASKETBALL, EXPECTED_MARKETS[Sport.BASKETBALL]),
        (Sport.RUGBY_LEAGUE, EXPECTED_MARKETS[Sport.RUGBY_LEAGUE]),
        (Sport.RUGBY_UNION, EXPECTED_MARKETS[Sport.RUGBY_UNION]),
        (Sport.ICE_HOCKEY, EXPECTED_MARKETS[Sport.ICE_HOCKEY]),
        (Sport.BASEBALL, EXPECTED_MARKETS[Sport.BASEBALL]),
        # New sports
        (Sport.AMERICAN_FOOTBALL, EXPECTED_MARKETS[Sport.AMERICAN_FOOTBALL]),
        (Sport.AUSSIE_RULES, EXPECTED_MARKETS[Sport.AUSSIE_RULES]),
        (Sport.BADMINTON, EXPECTED_MARKETS[Sport.BADMINTON]),
        (Sport.BANDY, EXPECTED_MARKETS[Sport.BANDY]),
        (Sport.BOXING, EXPECTED_MARKETS[Sport.BOXING]),
        (Sport.CRICKET, EXPECTED_MARKETS[Sport.CRICKET]),
        (Sport.DARTS, EXPECTED_MARKETS[Sport.DARTS]),
        (Sport.ESPORTS, EXPECTED_MARKETS[Sport.ESPORTS]),
        (Sport.FLOORBALL, EXPECTED_MARKETS[Sport.FLOORBALL]),
        (Sport.FUTSAL, EXPECTED_MARKETS[Sport.FUTSAL]),
        (Sport.HANDBALL, EXPECTED_MARKETS[Sport.HANDBALL]),
        (Sport.MMA, EXPECTED_MARKETS[Sport.MMA]),
        (Sport.SNOOKER, EXPECTED_MARKETS[Sport.SNOOKER]),
        (Sport.TABLE_TENNIS, EXPECTED_MARKETS[Sport.TABLE_TENNIS]),
        (Sport.VOLLEYBALL, EXPECTED_MARKETS[Sport.VOLLEYBALL]),
        (Sport.WATER_POLO, EXPECTED_MARKETS[Sport.WATER_POLO]),
    ],
)
def test_get_supported_markets_enum(sport_enum, expected):
    """Test getting supported markets using Sport enum."""
    assert get_supported_markets(sport_enum) == expected


@pytest.mark.parametrize(
    ("sport_str", "expected"),
    [
        # Original sports
        ("football", EXPECTED_MARKETS[Sport.FOOTBALL]),
        ("tennis", EXPECTED_MARKETS[Sport.TENNIS]),
        ("basketball", EXPECTED_MARKETS[Sport.BASKETBALL]),
        ("rugby-league", EXPECTED_MARKETS[Sport.RUGBY_LEAGUE]),
        ("rugby-union", EXPECTED_MARKETS[Sport.RUGBY_UNION]),
        ("ice-hockey", EXPECTED_MARKETS[Sport.ICE_HOCKEY]),
        ("baseball", EXPECTED_MARKETS[Sport.BASEBALL]),
        # New sports - sample testing (not all 16 to keep test file manageable)
        ("american-football", EXPECTED_MARKETS[Sport.AMERICAN_FOOTBALL]),
        ("cricket", EXPECTED_MARKETS[Sport.CRICKET]),
        ("volleyball", EXPECTED_MARKETS[Sport.VOLLEYBALL]),
        ("handball", EXPECTED_MARKETS[Sport.HANDBALL]),
        ("mma", EXPECTED_MARKETS[Sport.MMA]),
        ("esports", EXPECTED_MARKETS[Sport.ESPORTS]),
    ],
)
def test_get_supported_markets_string(sport_str, expected):
    """Test getting supported markets using string sport name."""
    assert get_supported_markets(sport_str) == expected


@pytest.mark.parametrize(
    ("sport_str_mixed_case", "expected"),
    [
        ("FooTbAlL", EXPECTED_MARKETS[Sport.FOOTBALL]),
        ("TENNIS", EXPECTED_MARKETS[Sport.TENNIS]),
        ("BaseBall", EXPECTED_MARKETS[Sport.BASEBALL]),
    ],
)
def test_get_supported_markets_case_insensitive(sport_str_mixed_case, expected):
    """Test that sport string input is case-insensitive."""
    assert get_supported_markets(sport_str_mixed_case) == expected


def test_get_supported_markets_unconfigured_sport():
    """Test handling of a sport that is a valid enum but not in the mapping."""
    with patch("src.utils.utils.SPORT_MARKETS_MAPPING", {}):
        with pytest.raises(ValueError) as excinfo:
            get_supported_markets(Sport.FOOTBALL)
        assert "Sport FOOTBALL is not configured in the market mapping" in str(excinfo.value)


def test_sport_markets_mapping_consistency():
    """Test that all sports in Sport enum are included in SPORT_MARKETS_MAPPING."""
    from src.utils.utils import SPORT_MARKETS_MAPPING

    for sport in Sport:
        assert sport in SPORT_MARKETS_MAPPING, f"Sport {sport.name} is missing from SPORT_MARKETS_MAPPING"


@patch("os.path.exists", return_value=True)
def test_is_running_in_docker_true(mock_exists):
    """Test detection of Docker environment when /.dockerenv exists."""
    assert is_running_in_docker() is True
    mock_exists.assert_called_once_with("/.dockerenv")


@patch("os.path.exists", return_value=False)
def test_is_running_in_docker_false(mock_exists):
    """Test detection of Docker environment when /.dockerenv doesn't exist."""
    assert is_running_in_docker() is False
    mock_exists.assert_called_once_with("/.dockerenv")


@patch("os.path.exists", side_effect=PermissionError("Permission denied"))
def test_is_running_in_docker_permission_error(mock_exists):
    """Test handling of permission error when checking for Docker environment."""
    # Should default to False when there's an error checking the file
    assert is_running_in_docker() is False
    mock_exists.assert_called_once_with("/.dockerenv")


def test_clean_html_text():
    # Test with None input
    assert clean_html_text(None) is None

    # Test with empty string
    assert clean_html_text("") == ""

    # Test with plain text (no HTML)
    assert clean_html_text("Simple text") == "Simple text"

    # Test with HTML tags
    assert clean_html_text("<div>Text content</div>") == "Text content"

    # Test with nested HTML tags
    assert clean_html_text("<div><p>Nested <strong>content</strong></p></div>") == "Nestedcontent"

    # Test with HTML entities
    assert clean_html_text("<div>Text &amp; content</div>") == "Text & content"

    # Test with the specific case from the issue
    html_with_sup = "6:3, 6:4, 1:6, 7:6<div><sup>4</sup></div>"
    expected_clean = "6:3, 6:4, 1:6, 7:64"
    assert clean_html_text(html_with_sup) == expected_clean

    # Test with complex HTML structure
    complex_html = """
    <div class="score">
        <span>Set 1: 6-3</span>
        <span>Set 2: 6-4</span>
        <span>Set 3: 1-6</span>
        <span>Set 4: 7-6<sup>4</sup></span>
    </div>
    """
    expected_complex = "Set 1: 6-3Set 2: 6-4Set 3: 1-6Set 4: 7-64"
    assert clean_html_text(complex_html) == expected_complex

    # Test with non-string input (should convert to string)
    assert clean_html_text(123) == "123"
    assert clean_html_text(True) == "True"
