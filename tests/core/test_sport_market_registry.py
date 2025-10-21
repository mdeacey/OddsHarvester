from unittest.mock import MagicMock, patch

from src.core.sport_market_registry import SportMarketRegistrar, SportMarketRegistry
from src.utils.sport_market_constants import Sport


class TestSportMarketRegistry:
    """Unit tests for the SportMarketRegistry class."""

    def setup_method(self):
        """Reset the registry before each test."""
        SportMarketRegistry._registry = {}

    def test_register_new_sport(self):
        """Test registering a new sport in the registry."""
        # Arrange
        sport = Sport.FOOTBALL
        market_mapping = {"1x2": lambda x: x}

        # Act
        SportMarketRegistry.register(sport, market_mapping)

        # Assert
        assert sport.value in SportMarketRegistry._registry
        assert "1x2" in SportMarketRegistry._registry[sport.value]
        assert SportMarketRegistry._registry[sport.value]["1x2"] == market_mapping["1x2"]

    def test_register_existing_sport(self):
        """Test adding a market to an already registered sport."""
        # Arrange
        sport = Sport.FOOTBALL
        market_mapping1 = {"1x2": lambda x: x}
        market_mapping2 = {"btts": lambda x: x * 2}

        # Act
        SportMarketRegistry.register(sport, market_mapping1)
        SportMarketRegistry.register(sport, market_mapping2)

        # Assert
        assert sport.value in SportMarketRegistry._registry
        assert "1x2" in SportMarketRegistry._registry[sport.value]
        assert "btts" in SportMarketRegistry._registry[sport.value]
        assert SportMarketRegistry._registry[sport.value]["1x2"] == market_mapping1["1x2"]
        assert SportMarketRegistry._registry[sport.value]["btts"] == market_mapping2["btts"]

    def test_get_market_mapping_existing_sport(self):
        """Test retrieving the mapping for an existing sport."""
        # Arrange
        sport = Sport.FOOTBALL
        market_mapping = {"1x2": lambda x: x}
        SportMarketRegistry.register(sport, market_mapping)

        # Act
        result = SportMarketRegistry.get_market_mapping(sport.value)

        # Assert
        assert result == market_mapping

    def test_get_market_mapping_nonexistent_sport(self):
        """Test retrieving the mapping for a non-existent sport."""
        # Act
        result = SportMarketRegistry.get_market_mapping("nonexistent_sport")

        # Assert
        assert result == {}


class TestSportMarketRegistrar:
    """Unit tests for the SportMarketRegistrar class."""

    def setup_method(self):
        """Reset the registry before each test."""
        SportMarketRegistry._registry = {}

    def test_create_market_lambda(self):
        """Test the creation of a lambda function for market extraction."""
        # Arrange
        main_market = "1X2"
        specific_market = None
        odds_labels = ["1", "X", "2"]

        extractor_mock = MagicMock()
        page_mock = MagicMock()

        # Act
        lambda_func = SportMarketRegistrar.create_market_lambda(main_market, specific_market, odds_labels)
        lambda_func(extractor_mock, page_mock)

        # Assert
        extractor_mock.extract_market_odds.assert_called_once_with(
            page=page_mock,
            main_market=main_market,
            specific_market=specific_market,
            period="FullTime",
            odds_labels=odds_labels,
            scrape_odds_history=False,
            target_bookmaker=None,
            preview_submarkets_only=False,
        )

    def test_register_football_markets(self):
        """Test registering markets for football."""
        # Act
        SportMarketRegistrar.register_football_markets()

        # Assert
        football_markets = SportMarketRegistry.get_market_mapping(Sport.FOOTBALL.value)
        assert "1x2" in football_markets
        assert "btts" in football_markets
        assert "double_chance" in football_markets
        assert "dnb" in football_markets

        # Check some Over/Under markets
        assert "over_under_2_5" in football_markets

        # Check some handicap markets
        assert "european_handicap_-1" in football_markets
        assert "asian_handicap_-1" in football_markets

    def test_register_tennis_markets(self):
        """Test registering markets for tennis."""
        # Act
        SportMarketRegistrar.register_tennis_markets()

        # Assert
        tennis_markets = SportMarketRegistry.get_market_mapping(Sport.TENNIS.value)

        # Basic markets
        assert "match_winner" in tennis_markets

        # Over/Under Sets markets
        assert "over_under_sets_2_5" in tennis_markets

        # Over/Under Games markets
        assert "over_under_games_22_5" in tennis_markets

        # Asian Handicap Games markets
        assert any(key.startswith("asian_handicap_") and key.endswith("_games") for key in tennis_markets)

        # Asian Handicap Sets markets
        assert any(key.startswith("asian_handicap_") and key.endswith("_sets") for key in tennis_markets)

        # Correct Score markets
        assert "correct_score_2_0" in tennis_markets
        assert "correct_score_0_2" in tennis_markets

    def test_register_basketball_markets(self):
        """Test registering markets for basketball."""
        # Act
        SportMarketRegistrar.register_basketball_markets()

        # Assert
        basketball_markets = SportMarketRegistry.get_market_mapping(Sport.BASKETBALL.value)

        # Basic markets
        assert "1x2" in basketball_markets
        assert "home_away" in basketball_markets

        # Over/Under markets
        assert any(key.startswith("over_under_games_") for key in basketball_markets)

        # Asian Handicap markets
        assert any(key.startswith("asian_handicap_games_") for key in basketball_markets)

    def test_register_rugby_league_markets(self):
        """Test registering markets for rugby league."""
        # Act
        SportMarketRegistrar.register_rugby_league_markets()

        # Assert
        rugby_league_markets = SportMarketRegistry.get_market_mapping(Sport.RUGBY_LEAGUE.value)

        # Basic markets
        assert "1x2" in rugby_league_markets
        assert "home_away" in rugby_league_markets
        assert "dnb" in rugby_league_markets
        assert "double_chance" in rugby_league_markets

        # Over/Under markets
        assert "over_under_43_5" in rugby_league_markets

        # Handicap markets
        assert "handicap_-13_5" in rugby_league_markets

    def test_register_rugby_union_markets(self):
        """Test registering markets for rugby union."""
        # Act
        SportMarketRegistrar.register_rugby_union_markets()

        # Assert
        rugby_union_markets = SportMarketRegistry.get_market_mapping(Sport.RUGBY_UNION.value)

        # Basic markets
        assert "1x2" in rugby_union_markets
        assert "home_away" in rugby_union_markets
        assert "dnb" in rugby_union_markets
        assert "double_chance" in rugby_union_markets

        # Over/Under markets
        assert "over_under_43_5" in rugby_union_markets

        # Handicap markets
        assert "handicap_-13_5" in rugby_union_markets

    def test_register_ice_hockey_markets(self):
        """Test registering markets for ice hockey."""
        # Act
        SportMarketRegistrar.register_ice_hockey_markets()

        # Assert
        ice_hockey_markets = SportMarketRegistry.get_market_mapping(Sport.ICE_HOCKEY.value)

        # Basic markets
        assert "1x2" in ice_hockey_markets
        assert "home_away" in ice_hockey_markets
        assert "dnb" in ice_hockey_markets
        assert "btts" in ice_hockey_markets
        assert "double_chance" in ice_hockey_markets

        # Over/Under markets
        assert "over_under_5_5" in ice_hockey_markets

    def test_register_baseball_markets(self):
        """Test registering markets for baseball."""
        # Act
        SportMarketRegistrar.register_baseball_markets()

        # Assert
        baseball_markets = SportMarketRegistry.get_market_mapping(Sport.BASEBALL.value)

        # Basic markets
        assert "1x2" in baseball_markets
        assert "home_away" in baseball_markets

        # Over/Under markets
        assert "over_under_7_5" in baseball_markets

    def test_register_american_football_markets(self):
        """Test registering markets for American football."""
        # Act
        SportMarketRegistrar.register_american_football_markets()

        # Assert
        af_markets = SportMarketRegistry.get_market_mapping(Sport.AMERICAN_FOOTBALL.value)

        # Basic markets
        assert "1x2" in af_markets
        assert "home_away" in af_markets
        assert "point_spread" in af_markets

        # Over/Under markets
        assert any(key.startswith("over_under_") for key in af_markets)

    def test_register_cricket_markets(self):
        """Test registering markets for cricket."""
        # Act
        SportMarketRegistrar.register_cricket_markets()

        # Assert
        cricket_markets = SportMarketRegistry.get_market_mapping(Sport.CRICKET.value)

        # Basic markets
        assert "match_winner" in cricket_markets

        # Over/Under markets
        assert any(key.startswith("over_under_") for key in cricket_markets)

    def test_register_handball_markets(self):
        """Test registering markets for handball."""
        # Act
        SportMarketRegistrar.register_handball_markets()

        # Assert
        handball_markets = SportMarketRegistry.get_market_mapping(Sport.HANDBALL.value)

        # Basic markets
        assert "1x2" in handball_markets
        assert "home_away" in handball_markets

        # Over/Under markets
        assert any(key.startswith("over_under_") for key in handball_markets)

    def test_register_volleyball_markets(self):
        """Test registering markets for volleyball."""
        # Act
        SportMarketRegistrar.register_volleyball_markets()

        # Assert
        volleyball_markets = SportMarketRegistry.get_market_mapping(Sport.VOLLEYBALL.value)

        # Basic markets
        assert "1x2" in volleyball_markets
        assert "home_away" in volleyball_markets

        # Over/Under markets
        assert any(key.startswith("over_under_") for key in volleyball_markets)

    def test_register_all_markets(self):
        """Test registering all markets for all sports."""
        # Act
        with patch.object(SportMarketRegistrar, "register_football_markets") as mock_football:
            with patch.object(SportMarketRegistrar, "register_tennis_markets") as mock_tennis:
                with patch.object(SportMarketRegistrar, "register_basketball_markets") as mock_basketball:
                    with patch.object(SportMarketRegistrar, "register_rugby_league_markets") as mock_rugby_league:
                        with patch.object(SportMarketRegistrar, "register_rugby_union_markets") as mock_rugby_union:
                            with patch.object(SportMarketRegistrar, "register_ice_hockey_markets") as mock_ice_hockey:
                                with patch.object(SportMarketRegistrar, "register_baseball_markets") as mock_baseball:
                                    with patch.object(SportMarketRegistrar, "register_american_football_markets") as mock_american_football:
                                        with patch.object(SportMarketRegistrar, "register_cricket_markets") as mock_cricket:
                                            with patch.object(SportMarketRegistrar, "register_volleyball_markets") as mock_volleyball:
                                                SportMarketRegistrar.register_all_markets()

        # Assert - test original sports
        mock_football.assert_called_once()
        mock_tennis.assert_called_once()
        mock_basketball.assert_called_once()
        mock_rugby_league.assert_called_once()
        mock_rugby_union.assert_called_once()
        mock_ice_hockey.assert_called_once()
        mock_baseball.assert_called_once()

        # Assert - test key new sports are called (not all 16 to keep test manageable)
        mock_american_football.assert_called_once()
        mock_cricket.assert_called_once()
        mock_volleyball.assert_called_once()

    def test_register_all_markets_integration(self):
        """Test registering all markets in an integration test"""
        # Act
        SportMarketRegistrar.register_all_markets()

        # Assert - Check that all sports have markets registered
        for sport in Sport:
            markets = SportMarketRegistry.get_market_mapping(sport.value)
            assert markets, f"No markets registered for {sport.name}"

        # Check specific markets for each sport to ensure they were properly registered
        assert "1x2" in SportMarketRegistry.get_market_mapping(Sport.FOOTBALL.value)
        assert "match_winner" in SportMarketRegistry.get_market_mapping(Sport.TENNIS.value)
        assert "home_away" in SportMarketRegistry.get_market_mapping(Sport.BASKETBALL.value)
        assert "1x2" in SportMarketRegistry.get_market_mapping(Sport.RUGBY_LEAGUE.value)
        assert "double_chance" in SportMarketRegistry.get_market_mapping(Sport.RUGBY_UNION.value)
        assert "btts" in SportMarketRegistry.get_market_mapping(Sport.ICE_HOCKEY.value)
        assert "home_away" in SportMarketRegistry.get_market_mapping(Sport.BASEBALL.value)
