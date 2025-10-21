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
    TennisMarket,
    TennisOverUnderGamesMarket,
    TennisOverUnderSetsMarket,
    VolleyballMarket,
    VolleyballOverUnderMarket,
    WaterPoloMarket,
    WaterPoloOverUnderMarket,
)


class TestSportEnums:
    """Unit tests for sport and market enums."""

    def test_sport_enum_values(self):
        """Verify that all sports have valid and unique values."""
        # Arrange/Act
        sport_values = [sport.value for sport in Sport]

        # Assert
        assert len(sport_values) == len(set(sport_values))  # Check uniqueness

        # Test original sports are still there
        assert "football" in sport_values
        assert "tennis" in sport_values
        assert "basketball" in sport_values
        assert "rugby-league" in sport_values
        assert "rugby-union" in sport_values
        assert "ice-hockey" in sport_values
        assert "baseball" in sport_values

        # Test new sports have been added
        assert "american-football" in sport_values
        assert "aussie-rules" in sport_values
        assert "badminton" in sport_values
        assert "bandy" in sport_values
        assert "boxing" in sport_values
        assert "cricket" in sport_values
        assert "darts" in sport_values
        assert "esports" in sport_values
        assert "floorball" in sport_values
        assert "futsal" in sport_values
        assert "handball" in sport_values
        assert "mma" in sport_values
        assert "snooker" in sport_values
        assert "table-tennis" in sport_values
        assert "volleyball" in sport_values
        assert "water-polo" in sport_values

        # Assert total count is correct (7 original + 16 new = 23)
        assert len(sport_values) == 23

    def test_football_market_enum(self):
        """Verify football markets."""
        # Arrange/Act
        market_values = [market.value for market in FootballMarket]

        # Assert
        assert "1x2" in market_values
        assert "btts" in market_values
        assert "double_chance" in market_values
        assert "dnb" in market_values

    def test_football_over_under_market_enum(self):
        """Verify football Over/Under markets."""
        # Arrange/Act
        market_values = [market.value for market in FootballOverUnderMarket]

        # Assert
        assert "over_under_0_5" in market_values
        assert "over_under_1_5" in market_values
        assert "over_under_2_5" in market_values
        assert "over_under_3_5" in market_values
        assert len(market_values) >= 10  # At least 10 markets

    def test_football_handicap_market_enums(self):
        """Verify football handicap markets."""
        # Arrange/Act
        european_values = [market.value for market in FootballEuropeanHandicapMarket]
        asian_values = [market.value for market in FootballAsianHandicapMarket]

        # Assert
        assert "european_handicap_-1" in european_values
        assert "european_handicap_+1" in european_values
        assert "asian_handicap_-1" in asian_values
        assert "asian_handicap_+1" in asian_values
        assert len(european_values) >= 6  # At least 6 markets
        assert len(asian_values) >= 10  # At least 10 markets

    def test_tennis_market_enums(self):
        """Verify tennis markets."""
        # Arrange/Act
        market_values = [market.value for market in TennisMarket]
        sets_values = [market.value for market in TennisOverUnderSetsMarket]
        games_values = [market.value for market in TennisOverUnderGamesMarket]
        handicap_games_values = [market.value for market in TennisAsianHandicapGamesMarket]
        handicap_sets_values = [market.value for market in TennisAsianHandicapSetsMarket]

        # Assert
        assert "match_winner" in market_values
        assert "over_under_sets_2_5" in sets_values
        assert "over_under_games_21_5" in games_values
        assert "asian_handicap_+2_5_games" in handicap_games_values
        assert "asian_handicap_+2_5_sets" in handicap_sets_values
        assert "asian_handicap_-2_5_sets" in handicap_sets_values

    def test_basketball_market_enums(self):
        """Verify basketball markets."""
        # Arrange/Act
        market_values = [market.value for market in BasketballMarket]
        over_under_values = [market.value for market in BasketballOverUnderMarket]
        handicap_values = [market.value for market in BasketballAsianHandicapMarket]

        # Assert
        assert "1x2" in market_values
        assert "home_away" in market_values
        assert any("over_under_games_220_5" in val for val in over_under_values)
        assert any("asian_handicap_games_-10_5_games" in val for val in handicap_values)

    def test_rugby_market_enums(self):
        """Verify rugby (league and union) markets."""
        # Arrange/Act
        league_values = [market.value for market in RugbyLeagueMarket]
        union_values = [market.value for market in RugbyUnionMarket]
        over_under_values = [market.value for market in RugbyOverUnderMarket]
        handicap_values = [market.value for market in RugbyHandicapMarket]

        # Assert
        assert "1x2" in league_values
        assert "home_away" in league_values
        assert "1x2" in union_values
        assert "home_away" in union_values
        assert "over_under_40_5" in over_under_values
        assert "handicap_-10_5" in handicap_values

    def test_ice_hockey_market_enums(self):
        """Verify ice hockey markets."""
        # Arrange/Act
        market_values = [market.value for market in IceHockeyMarket]
        over_under_values = [market.value for market in IceHockeyOverUnderMarket]

        # Assert
        assert "1x2" in market_values
        assert "home_away" in market_values
        assert "dnb" in market_values
        assert "over_under_5_5" in over_under_values

    def test_baseball_market_enums(self):
        """Verify baseball markets."""
        # Arrange/Act
        market_values = [market.value for market in BaseballMarket]
        over_under_values = [market.value for market in BaseballOverUnderMarket]

        # Assert
        assert "1x2" in market_values
        assert "home_away" in market_values
        assert "over_under_8_5" in over_under_values

    def test_new_sports_market_enums(self):
        """Verify market enums for key new sports."""
        # American Football
        af_markets = [market.value for market in AmericanFootballMarket]
        af_over_under = [market.value for market in AmericanFootballOverUnderMarket]
        assert "1x2" in af_markets
        assert "home_away" in af_markets
        assert "point_spread" in af_markets
        assert "over_under_45_5" in af_over_under

        # Cricket
        cricket_markets = [market.value for market in CricketMarket]
        cricket_over_under = [market.value for market in CricketOverUnderMarket]
        assert "match_winner" in cricket_markets
        assert "over_under_200_5" in cricket_over_under

        # Handball
        handball_markets = [market.value for market in HandballMarket]
        handball_over_under = [market.value for market in HandballOverUnderMarket]
        assert "1x2" in handball_markets
        assert "home_away" in handball_markets
        assert "over_under_60_5" in handball_over_under

        # Volleyball
        volleyball_markets = [market.value for market in VolleyballMarket]
        volleyball_over_under = [market.value for market in VolleyballOverUnderMarket]
        assert "1x2" in volleyball_markets
        assert "home_away" in volleyball_markets
        assert "over_under_200_5" in volleyball_over_under

        # Individual sports (only match winner markets)
        individual_sports = [BoxingMarket, DartsMarket, EsportsMarket, MmaMarket, SnookerMarket, TableTennisMarket]
        for sport_market in individual_sports:
            market_values = [market.value for market in sport_market]
            assert "match_winner" in market_values
            assert len(market_values) == 1
