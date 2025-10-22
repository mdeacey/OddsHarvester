from typing import ClassVar

from src.utils.sport_market_constants import (
    AmericanFootballMarket,
    AmericanFootballOverUnderMarket,
    AussieRulesMarket,
    AussieRulesOverUnderMarket,
    BadmintonMarket,
    BadmintonOverUnderMarket,
    BandyMarket,
    BandyOverUnderMarket,
    BaseballOverUnderMarket,
    BasketballAsianHandicapMarket,
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
    FootballOverUnderMarket,
    FutsalMarket,
    FutsalOverUnderMarket,
    HandballMarket,
    HandballOverUnderMarket,
    IceHockeyOverUnderMarket,
    MmaMarket,
    RugbyHandicapMarket,
    RugbyOverUnderMarket,
    SnookerMarket,
    Sport,
    TableTennisMarket,
    TennisAsianHandicapGamesMarket,
    TennisAsianHandicapSetsMarket,
    TennisCorrectScoreMarket,
    TennisOverUnderGamesMarket,
    TennisOverUnderSetsMarket,
    VolleyballMarket,
    VolleyballOverUnderMarket,
    WaterPoloMarket,
    WaterPoloOverUnderMarket,
)


class SportMarketRegistry:
    """Registry to dynamically store market mappings for each sport."""

    _registry: ClassVar[dict] = {}

    @classmethod
    def register(cls, sport: Sport, market_mapping: dict):
        """Register a market mapping for a sport."""
        if sport.value not in cls._registry:
            cls._registry[sport.value] = {}
        cls._registry[sport.value].update(market_mapping)

    @classmethod
    def get_market_mapping(cls, sport: str) -> dict:
        """Retrieve market mappings for a given sport."""
        return cls._registry.get(sport, {})


class SportMarketRegistrar:
    """Handles the registration of betting markets for different sports."""

    @staticmethod
    def create_market_lambda(main_market, specific_market=None, odds_labels=None):
        """
        Creates a lambda function for market extraction.
        """
        return (
            lambda extractor,
            page,
            period="FullTime",
            scrape_odds_history=True,  # Always scrape odds history by default
            target_bookmaker=None,
            preview_submarkets_only=False: extractor.extract_market_odds(
                page=page,
                main_market=main_market,
                specific_market=specific_market,
                period=period,
                odds_labels=odds_labels,
                scrape_odds_history=scrape_odds_history,
                target_bookmaker=target_bookmaker,
                preview_submarkets_only=preview_submarkets_only,
            )
        )

    @classmethod
    def register_football_markets(cls):
        """Registers all football betting markets."""
        SportMarketRegistry.register(
            Sport.FOOTBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "btts": cls.create_market_lambda("Both Teams to Score", odds_labels=["btts_yes", "btts_no"]),
                "double_chance": cls.create_market_lambda("Double Chance", odds_labels=["1X", "12", "X2"]),
                "dnb": cls.create_market_lambda("Draw No Bet", odds_labels=["dnb_team1", "dnb_team2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in FootballOverUnderMarket:
            SportMarketRegistry.register(
                Sport.FOOTBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{over_under.value.replace('over_under_', '').replace('_', '.')}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Register European Handicap Markets
        for handicap in FootballEuropeanHandicapMarket:
            SportMarketRegistry.register(
                Sport.FOOTBALL,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="European Handicap",
                        specific_market=f"European Handicap {handicap.value.split('_')[-1]}",
                        odds_labels=["team1_handicap", "draw_handicap", "team2_handicap"],
                    )
                },
            )

        # Register Asian Handicap Markets
        for handicap in FootballAsianHandicapMarket:
            raw_handicap = handicap.value.replace("asian_handicap_", "")
            formatted_handicap = raw_handicap.replace("_", ".")
            SportMarketRegistry.register(
                Sport.FOOTBALL,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Asian Handicap",
                        specific_market=f"Asian Handicap {formatted_handicap}",
                        odds_labels=["team1_handicap", "team2_handicap"],
                    )
                },
            )

    @classmethod
    def register_tennis_markets(cls):
        """Registers all tennis betting markets."""
        SportMarketRegistry.register(
            Sport.TENNIS,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["player_1", "player_2"]),
            },
        )

        # Register Over/Under Sets Markets
        for over_under in TennisOverUnderSetsMarket:
            numeric_part = over_under.value.replace("over_under_sets_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.TENNIS,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part} Sets",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Register Over/Under Games Markets
        for over_under in TennisOverUnderGamesMarket:
            numeric_part = over_under.value.replace("over_under_games_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.TENNIS,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part} Games",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Register Asian Handicap Games Markets
        for handicap in TennisAsianHandicapGamesMarket:
            numeric_part = handicap.value.replace("asian_handicap_", "").replace("_games", "").replace("_", ".")
            specific_market = f"Asian Handicap {numeric_part} Games"
            SportMarketRegistry.register(
                Sport.TENNIS,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Asian Handicap",
                        specific_market=specific_market,
                        odds_labels=["games_handicap_player_1", "games_handicap_player_2"],
                    )
                },
            )

        # Register Asian Handicap Sets Markets
        for handicap in TennisAsianHandicapSetsMarket:
            numeric_part = handicap.value.replace("asian_handicap_", "").replace("_sets", "").replace("_", ".")
            specific_market = f"Asian Handicap {numeric_part} Sets"
            SportMarketRegistry.register(
                Sport.TENNIS,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Asian Handicap",
                        specific_market=specific_market,
                        odds_labels=["sets_handicap_player_1", "sets_handicap_player_2"],
                    )
                },
            )

        # Register Correct Score Markets
        for correct_score in TennisCorrectScoreMarket:
            numeric_part = correct_score.value.replace("correct_score_", "").replace("_", ":")
            specific_market = f"{numeric_part}"
            SportMarketRegistry.register(
                Sport.TENNIS,
                {
                    correct_score.value: cls.create_market_lambda(
                        main_market="Correct Score", specific_market=specific_market, odds_labels=["correct_score"]
                    )
                },
            )

    @classmethod
    def register_basketball_markets(cls):
        """Registers all basketball betting markets."""
        SportMarketRegistry.register(
            Sport.BASKETBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Games Markets
        for over_under in BasketballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_games_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.BASKETBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Register Asian Handicap Markets
        for handicap in BasketballAsianHandicapMarket:
            numeric_part = handicap.value.replace("asian_handicap_games_", "").replace("_games", "").replace("_", ".")
            specific_market = f"Asian Handicap {numeric_part}"
            SportMarketRegistry.register(
                Sport.BASKETBALL,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Asian Handicap",
                        specific_market=specific_market,
                        odds_labels=["handicap_team_1", "handicap_team_2"],
                    )
                },
            )

    @classmethod
    def register_rugby_league_markets(cls):
        """Registers all rugby league betting markets."""
        SportMarketRegistry.register(
            Sport.RUGBY_LEAGUE,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
                "dnb": cls.create_market_lambda("Draw No Bet", odds_labels=["dnb_team1", "dnb_team2"]),
                "double_chance": cls.create_market_lambda("Double Chance", odds_labels=["1X", "12", "X2"]),
            },
        )

        # Over/Under Markets
        for over_under in RugbyOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.RUGBY_LEAGUE,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Handicap Markets
        for handicap in RugbyHandicapMarket:
            numeric_part = handicap.value.replace("handicap_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.RUGBY_LEAGUE,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Handicap",
                        specific_market=f"Handicap {numeric_part}",
                        odds_labels=["handicap_team_1", "handicap_team_2"],
                    )
                },
            )

    @classmethod
    def register_rugby_union_markets(cls):
        """Registers all rugby union betting markets."""
        SportMarketRegistry.register(
            Sport.RUGBY_UNION,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
                "dnb": cls.create_market_lambda("Draw No Bet", odds_labels=["dnb_team1", "dnb_team2"]),
                "double_chance": cls.create_market_lambda("Double Chance", odds_labels=["1X", "12", "X2"]),
            },
        )

        # Over/Under Markets
        for over_under in RugbyOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.RUGBY_UNION,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

        # Handicap Markets
        for handicap in RugbyHandicapMarket:
            numeric_part = handicap.value.replace("handicap_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.RUGBY_UNION,
                {
                    handicap.value: cls.create_market_lambda(
                        main_market="Handicap",
                        specific_market=f"Handicap {numeric_part}",
                        odds_labels=["handicap_team_1", "handicap_team_2"],
                    )
                },
            )

    @classmethod
    def register_ice_hockey_markets(cls):
        """Registers all ice hockey betting markets."""
        SportMarketRegistry.register(
            Sport.ICE_HOCKEY,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
                "dnb": cls.create_market_lambda("Draw No Bet", odds_labels=["dnb_team1", "dnb_team2"]),
                "btts": cls.create_market_lambda("Both Teams to Score", odds_labels=["btts_yes", "btts_no"]),
                "double_chance": cls.create_market_lambda("Double Chance", odds_labels=["1X", "12", "X2"]),
            },
        )

        # Over/Under Markets
        for over_under in IceHockeyOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.ICE_HOCKEY,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_baseball_markets(cls):
        """Registers all baseball betting markets."""
        SportMarketRegistry.register(
            Sport.BASEBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Over/Under Markets
        for over_under in BaseballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.BASEBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_american_football_markets(cls):
        """Registers all American football betting markets."""
        SportMarketRegistry.register(
            Sport.AMERICAN_FOOTBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
                "point_spread": cls.create_market_lambda("Point Spread", odds_labels=["point_spread_team1", "point_spread_team2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in AmericanFootballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.AMERICAN_FOOTBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_aussie_rules_markets(cls):
        """Registers all Aussie Rules betting markets."""
        SportMarketRegistry.register(
            Sport.AUSSIE_RULES,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
                "handicap": cls.create_market_lambda("Handicap", odds_labels=["handicap_team1", "handicap_team2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in AussieRulesOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.AUSSIE_RULES,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_badminton_markets(cls):
        """Registers all badminton betting markets."""
        SportMarketRegistry.register(
            Sport.BADMINTON,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["player_1", "player_2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in BadmintonOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.BADMINTON,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_bandy_markets(cls):
        """Registers all bandy betting markets."""
        SportMarketRegistry.register(
            Sport.BANDY,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in BandyOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.BANDY,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_boxing_markets(cls):
        """Registers all boxing betting markets."""
        SportMarketRegistry.register(
            Sport.BOXING,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["fighter_1", "fighter_2"]),
            },
        )

    @classmethod
    def register_cricket_markets(cls):
        """Registers all cricket betting markets."""
        SportMarketRegistry.register(
            Sport.CRICKET,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["team_1", "team_2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in CricketOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.CRICKET,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_darts_markets(cls):
        """Registers all darts betting markets."""
        SportMarketRegistry.register(
            Sport.DARTS,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["player_1", "player_2"]),
            },
        )

    @classmethod
    def register_esports_markets(cls):
        """Registers all esports betting markets."""
        SportMarketRegistry.register(
            Sport.ESPORTS,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["team_1", "team_2"]),
            },
        )

    @classmethod
    def register_floorball_markets(cls):
        """Registers all floorball betting markets."""
        SportMarketRegistry.register(
            Sport.FLOORBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in FloorballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.FLOORBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_futsal_markets(cls):
        """Registers all futsal betting markets."""
        SportMarketRegistry.register(
            Sport.FUTSAL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in FutsalOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.FUTSAL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_handball_markets(cls):
        """Registers all handball betting markets."""
        SportMarketRegistry.register(
            Sport.HANDBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in HandballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.HANDBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_mma_markets(cls):
        """Registers all MMA betting markets."""
        SportMarketRegistry.register(
            Sport.MMA,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["fighter_1", "fighter_2"]),
            },
        )

    @classmethod
    def register_snooker_markets(cls):
        """Registers all snooker betting markets."""
        SportMarketRegistry.register(
            Sport.SNOOKER,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["player_1", "player_2"]),
            },
        )

    @classmethod
    def register_table_tennis_markets(cls):
        """Registers all table tennis betting markets."""
        SportMarketRegistry.register(
            Sport.TABLE_TENNIS,
            {
                "match_winner": cls.create_market_lambda("Home/Away", odds_labels=["player_1", "player_2"]),
            },
        )

    @classmethod
    def register_volleyball_markets(cls):
        """Registers all volleyball betting markets."""
        SportMarketRegistry.register(
            Sport.VOLLEYBALL,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in VolleyballOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.VOLLEYBALL,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_water_polo_markets(cls):
        """Registers all water polo betting markets."""
        SportMarketRegistry.register(
            Sport.WATER_POLO,
            {
                "1x2": cls.create_market_lambda("1X2", odds_labels=["1", "X", "2"]),
                "home_away": cls.create_market_lambda("Home/Away", odds_labels=["1", "2"]),
            },
        )

        # Register Over/Under Markets
        for over_under in WaterPoloOverUnderMarket:
            numeric_part = over_under.value.replace("over_under_", "").replace("_", ".")
            SportMarketRegistry.register(
                Sport.WATER_POLO,
                {
                    over_under.value: cls.create_market_lambda(
                        main_market="Over/Under",
                        specific_market=f"Over/Under +{numeric_part}",
                        odds_labels=["odds_over", "odds_under"],
                    )
                },
            )

    @classmethod
    def register_all_markets(cls):
        """Registers all sports markets."""
        cls.register_football_markets()
        cls.register_tennis_markets()
        cls.register_basketball_markets()
        cls.register_rugby_league_markets()
        cls.register_rugby_union_markets()
        cls.register_ice_hockey_markets()
        cls.register_baseball_markets()
        cls.register_american_football_markets()
        cls.register_aussie_rules_markets()
        cls.register_badminton_markets()
        cls.register_bandy_markets()
        cls.register_boxing_markets()
        cls.register_cricket_markets()
        cls.register_darts_markets()
        cls.register_esports_markets()
        cls.register_floorball_markets()
        cls.register_futsal_markets()
        cls.register_handball_markets()
        cls.register_mma_markets()
        cls.register_snooker_markets()
        cls.register_table_tennis_markets()
        cls.register_volleyball_markets()
        cls.register_water_polo_markets()
