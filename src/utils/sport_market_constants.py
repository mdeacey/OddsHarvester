from enum import Enum


class Sport(Enum):
    """Supported sports."""

    FOOTBALL = "football"
    TENNIS = "tennis"
    BASKETBALL = "basketball"
    RUGBY_LEAGUE = "rugby-league"
    RUGBY_UNION = "rugby-union"
    ICE_HOCKEY = "ice-hockey"
    BASEBALL = "baseball"
    AMERICAN_FOOTBALL = "american-football"
    AUSSIE_RULES = "aussie-rules"
    BADMINTON = "badminton"
    BANDY = "bandy"
    BOXING = "boxing"
    CRICKET = "cricket"
    DARTS = "darts"
    ESPORTS = "esports"
    FLOORBALL = "floorball"
    FUTSAL = "futsal"
    HANDBALL = "handball"
    MMA = "mma"
    SNOOKER = "snooker"
    TABLE_TENNIS = "table-tennis"
    VOLLEYBALL = "volleyball"
    WATER_POLO = "water-polo"


class FootballMarket(Enum):
    """Football-specific markets."""

    ONE_X_TWO = "1x2"
    BTTS = "btts"
    DOUBLE_CHANCE = "double_chance"
    DNB = "dnb"


class BaseballMarket(Enum):
    """Football-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class BaseballOverUnderMarket(Enum):
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_0 = "over_under_7_0"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_0 = "over_under_8_0"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_0 = "over_under_9_0"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_0 = "over_under_10_0"
    OVER_UNDER_10_5 = "over_under_10_5"
    OVER_UNDER_11_0 = "over_under_11_0"
    OVER_UNDER_11_5 = "over_under_11_5"


class FootballOverUnderMarket(Enum):
    """Over/Under market values for football."""

    OVER_UNDER_0_5 = "over_under_0_5"
    OVER_UNDER_1 = "over_under_1"
    OVER_UNDER_1_25 = "over_under_1_25"
    OVER_UNDER_1_5 = "over_under_1_5"
    OVER_UNDER_1_75 = "over_under_1_75"
    OVER_UNDER_2 = "over_under_2"
    OVER_UNDER_2_25 = "over_under_2_25"
    OVER_UNDER_2_5 = "over_under_2_5"
    OVER_UNDER_2_75 = "over_under_2_75"
    OVER_UNDER_3 = "over_under_3"
    OVER_UNDER_3_25 = "over_under_3_25"
    OVER_UNDER_3_5 = "over_under_3_5"
    OVER_UNDER_3_75 = "over_under_3_75"
    OVER_UNDER_4 = "over_under_4"
    OVER_UNDER_4_25 = "over_under_4_25"
    OVER_UNDER_4_5 = "over_under_4_5"
    OVER_UNDER_4_75 = "over_under_4_75"
    OVER_UNDER_5 = "over_under_5"
    OVER_UNDER_5_25 = "over_under_5_25"
    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_5_75 = "over_under_5_75"
    OVER_UNDER_6 = "over_under_6"
    OVER_UNDER_6_25 = "over_under_6_25"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_6_75 = "over_under_6_75"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"


class FootballEuropeanHandicapMarket(Enum):
    """European Handicap market values for football."""

    HANDICAP_MINUS_4 = "european_handicap_-4"
    HANDICAP_MINUS_3 = "european_handicap_-3"
    HANDICAP_MINUS_2 = "european_handicap_-2"
    HANDICAP_MINUS_1 = "european_handicap_-1"
    HANDICAP_PLUS_1 = "european_handicap_+1"
    HANDICAP_PLUS_2 = "european_handicap_+2"
    HANDICAP_PLUS_3 = "european_handicap_+3"
    HANDICAP_PLUS_4 = "european_handicap_+4"


class FootballAsianHandicapMarket(Enum):
    """Asian Handicap market values for football (including quarters)."""

    HANDICAP_MINUS_4 = "asian_handicap_-4"
    HANDICAP_MINUS_3_75 = "asian_handicap_-3_75"
    HANDICAP_MINUS_3_5 = "asian_handicap_-3_5"
    HANDICAP_MINUS_3_25 = "asian_handicap_-3_25"
    HANDICAP_MINUS_3 = "asian_handicap_-3"
    HANDICAP_MINUS_2_75 = "asian_handicap_-2_75"
    HANDICAP_MINUS_2_5 = "asian_handicap_-2_5"
    HANDICAP_MINUS_2_25 = "asian_handicap_-2_25"
    HANDICAP_MINUS_2 = "asian_handicap_-2"
    HANDICAP_MINUS_1_75 = "asian_handicap_-1_75"
    HANDICAP_MINUS_1_5 = "asian_handicap_-1_5"
    HANDICAP_MINUS_1_25 = "asian_handicap_-1_25"
    HANDICAP_MINUS_1 = "asian_handicap_-1"
    HANDICAP_MINUS_0_75 = "asian_handicap_-0_75"
    HANDICAP_MINUS_0_5 = "asian_handicap_-0_5"
    HANDICAP_MINUS_0_25 = "asian_handicap_-0_25"
    HANDICAP_ZERO = "asian_handicap_0"
    HANDICAP_PLUS_0_25 = "asian_handicap_+0_25"
    HANDICAP_PLUS_0_5 = "asian_handicap_+0_5"
    HANDICAP_PLUS_0_75 = "asian_handicap_+0_75"
    HANDICAP_PLUS_1 = "asian_handicap_+1"
    HANDICAP_PLUS_1_25 = "asian_handicap_+1_25"
    HANDICAP_PLUS_1_5 = "asian_handicap_+1_5"
    HANDICAP_PLUS_1_75 = "asian_handicap_+1_75"
    HANDICAP_PLUS_2 = "asian_handicap_+2"


class TennisMarket(Enum):
    """Tennis-specific markets."""

    MATCH_WINNER = "match_winner"  # Home/Away


class TennisOverUnderSetsMarket(Enum):
    """Over/Under sets betting markets."""

    OVER_UNDER_2_5 = "over_under_sets_2_5"
    OVER_UNDER_3_5 = "over_under_sets_3_5"
    OVER_UNDER_4_5 = "over_under_sets_4_5"
    OVER_UNDER_5_5 = "over_under_sets_5_5"
    OVER_UNDER_6_5 = "over_under_sets_6_5"
    OVER_UNDER_7_5 = "over_under_sets_7_5"
    OVER_UNDER_8_5 = "over_under_sets_8_5"
    OVER_UNDER_9_5 = "over_under_sets_9_5"
    OVER_UNDER_10_5 = "over_under_sets_10_5"


class TennisOverUnderGamesMarket(Enum):
    """Over/Under total games betting markets."""

    OVER_UNDER_16_5 = "over_under_games_16_5"
    OVER_UNDER_17_0 = "over_under_games_17_0"
    OVER_UNDER_17_5 = "over_under_games_17_5"
    OVER_UNDER_18_0 = "over_under_games_18_0"
    OVER_UNDER_18_5 = "over_under_games_18_5"
    OVER_UNDER_19_0 = "over_under_games_19_0"
    OVER_UNDER_19_5 = "over_under_games_19_5"
    OVER_UNDER_20_0 = "over_under_games_20_0"
    OVER_UNDER_20_5 = "over_under_games_20_5"
    OVER_UNDER_21_0 = "over_under_games_21_0"
    OVER_UNDER_21_5 = "over_under_games_21_5"
    OVER_UNDER_22_0 = "over_under_games_22_0"
    OVER_UNDER_22_5 = "over_under_games_22_5"
    OVER_UNDER_23_0 = "over_under_games_23_0"
    OVER_UNDER_23_5 = "over_under_games_23_5"
    OVER_UNDER_24_0 = "over_under_games_24_0"
    OVER_UNDER_24_5 = "over_under_games_24_5"
    OVER_UNDER_25_0 = "over_under_games_25_0"
    OVER_UNDER_25_5 = "over_under_games_25_5"
    OVER_UNDER_26_0 = "over_under_games_26_0"
    OVER_UNDER_26_5 = "over_under_games_26_5"
    OVER_UNDER_27_0 = "over_under_games_27_0"
    OVER_UNDER_27_5 = "over_under_games_27_5"
    OVER_UNDER_28_0 = "over_under_games_28_0"
    OVER_UNDER_28_5 = "over_under_games_28_5"
    OVER_UNDER_29_0 = "over_under_games_29_0"
    OVER_UNDER_29_5 = "over_under_games_29_5"
    OVER_UNDER_30_0 = "over_under_games_30_0"
    OVER_UNDER_30_5 = "over_under_games_30_5"
    OVER_UNDER_31_0 = "over_under_games_31_0"
    OVER_UNDER_31_5 = "over_under_games_31_5"
    OVER_UNDER_32_0 = "over_under_games_32_0"
    OVER_UNDER_32_5 = "over_under_games_32_5"
    OVER_UNDER_33_0 = "over_under_games_33_0"
    OVER_UNDER_33_5 = "over_under_games_33_5"
    OVER_UNDER_34_0 = "over_under_games_34_0"
    OVER_UNDER_34_5 = "over_under_games_34_5"
    OVER_UNDER_35_0 = "over_under_games_35_0"
    OVER_UNDER_35_5 = "over_under_games_35_5"
    OVER_UNDER_36_0 = "over_under_games_36_0"
    OVER_UNDER_36_5 = "over_under_games_36_5"
    OVER_UNDER_37_0 = "over_under_games_37_0"
    OVER_UNDER_37_5 = "over_under_games_37_5"
    OVER_UNDER_38_0 = "over_under_games_38_0"
    OVER_UNDER_38_5 = "over_under_games_38_5"
    OVER_UNDER_39_0 = "over_under_games_39_0"
    OVER_UNDER_39_5 = "over_under_games_39_5"
    OVER_UNDER_40_0 = "over_under_games_40_0"
    OVER_UNDER_40_5 = "over_under_games_40_5"
    OVER_UNDER_41_0 = "over_under_games_41_0"
    OVER_UNDER_41_5 = "over_under_games_41_5"
    OVER_UNDER_42_0 = "over_under_games_42_0"
    OVER_UNDER_42_5 = "over_under_games_42_5"
    OVER_UNDER_43_0 = "over_under_games_43_0"
    OVER_UNDER_43_5 = "over_under_games_43_5"
    OVER_UNDER_44_0 = "over_under_games_44_0"
    OVER_UNDER_44_5 = "over_under_games_44_5"
    OVER_UNDER_45_0 = "over_under_games_45_0"
    OVER_UNDER_45_5 = "over_under_games_45_5"
    OVER_UNDER_46_0 = "over_under_games_46_0"
    OVER_UNDER_46_5 = "over_under_games_46_5"
    OVER_UNDER_47_0 = "over_under_games_47_0"
    OVER_UNDER_47_5 = "over_under_games_47_5"
    OVER_UNDER_48_0 = "over_under_games_48_0"
    OVER_UNDER_48_5 = "over_under_games_48_5"
    OVER_UNDER_49_0 = "over_under_games_49_0"
    OVER_UNDER_49_5 = "over_under_games_49_5"
    OVER_UNDER_50_0 = "over_under_games_50_0"
    OVER_UNDER_50_5 = "over_under_games_50_5"


class TennisAsianHandicapSetsMarket(Enum):
    """Asian Handicap markets in tennis sets."""

    HANDICAP_MINUS_2_5 = "asian_handicap_-2_5_sets"
    HANDICAP_MINUS_2_0 = "asian_handicap_-2_0_sets"
    HANDICAP_MINUS_1_5 = "asian_handicap_-1_5_sets"
    HANDICAP_MINUS_1_0 = "asian_handicap_-1_0_sets"
    HANDICAP_MINUS_0_5 = "asian_handicap_-0_5_sets"
    HANDICAP_ZERO = "asian_handicap_0_sets"
    HANDICAP_PLUS_0_5 = "asian_handicap_+0_5_sets"
    HANDICAP_PLUS_1_0 = "asian_handicap_+1_0_sets"
    HANDICAP_PLUS_1_5 = "asian_handicap_+1_5_sets"
    HANDICAP_PLUS_2_0 = "asian_handicap_+2_0_sets"
    HANDICAP_PLUS_2_5 = "asian_handicap_+2_5_sets"


class TennisAsianHandicapGamesMarket(Enum):
    """Asian Handicap markets in games."""

    HANDICAP_PLUS_2_5 = "asian_handicap_+2_5_games"
    HANDICAP_PLUS_3_5 = "asian_handicap_+3_5_games"
    HANDICAP_PLUS_4_5 = "asian_handicap_+4_5_games"
    HANDICAP_PLUS_5_5 = "asian_handicap_+5_5_games"
    HANDICAP_PLUS_6_5 = "asian_handicap_+6_5_games"
    HANDICAP_PLUS_7_5 = "asian_handicap_+7_5_games"
    HANDICAP_PLUS_8_5 = "asian_handicap_+8_5_games"
    HANDICAP_MINUS_2_5 = "asian_handicap_-2_5_games"
    HANDICAP_MINUS_3_5 = "asian_handicap_-3_5_games"
    HANDICAP_MINUS_4_5 = "asian_handicap_-4_5_games"
    HANDICAP_MINUS_5_5 = "asian_handicap_-5_5_games"
    HANDICAP_MINUS_6_5 = "asian_handicap_-6_5_games"
    HANDICAP_MINUS_7_5 = "asian_handicap_-7_5_games"
    HANDICAP_MINUS_8_5 = "asian_handicap_-8_5_games"


class TennisCorrectScoreMarket(Enum):
    """Correct Score markets in tennis."""

    CORRECT_SCORE_2_0 = "correct_score_2_0"
    CORRECT_SCORE_2_1 = "correct_score_2_1"
    CORRECT_SCORE_0_2 = "correct_score_0_2"
    CORRECT_SCORE_1_2 = "correct_score_1_2"
    CORRECT_SCORE_3_0 = "correct_score_3_0"
    CORRECT_SCORE_0_3 = "correct_score_0_3"
    CORRECT_SCORE_1_3 = "correct_score_1_3"
    CORRECT_SCORE_2_3 = "correct_score_2_3"
    CORRECT_SCORE_3_1 = "correct_score_3_1"
    CORRECT_SCORE_3_2 = "correct_score_3_2"


class BasketballMarket(Enum):
    """Basketball-specific markets."""

    ONE_X_TWO = "1x2"
    home_away = "home_away"  # Match winner (FT including OT)


class BasketballOverUnderMarket(Enum):
    """Over/Under total points betting markets."""

    OVER_UNDER_180_5 = "over_under_games_180_5"
    OVER_UNDER_181_5 = "over_under_games_181_5"
    OVER_UNDER_182_5 = "over_under_games_182_5"
    OVER_UNDER_183_5 = "over_under_games_183_5"
    OVER_UNDER_184_5 = "over_under_games_184_5"
    OVER_UNDER_185_5 = "over_under_games_185_5"
    OVER_UNDER_186_5 = "over_under_games_186_5"
    OVER_UNDER_187_5 = "over_under_games_187_5"
    OVER_UNDER_188_5 = "over_under_games_188_5"
    OVER_UNDER_189_5 = "over_under_games_189_5"
    OVER_UNDER_190_5 = "over_under_games_190_5"
    OVER_UNDER_191_5 = "over_under_games_191_5"
    OVER_UNDER_192_5 = "over_under_games_192_5"
    OVER_UNDER_193_5 = "over_under_games_193_5"
    OVER_UNDER_194_5 = "over_under_games_194_5"
    OVER_UNDER_195_5 = "over_under_games_195_5"
    OVER_UNDER_196_5 = "over_under_games_196_5"
    OVER_UNDER_197_5 = "over_under_games_197_5"
    OVER_UNDER_198_5 = "over_under_games_198_5"
    OVER_UNDER_199_5 = "over_under_games_199_5"
    OVER_UNDER_200_5 = "over_under_games_200_5"
    OVER_UNDER_201_5 = "over_under_games_201_5"
    OVER_UNDER_202_5 = "over_under_games_202_5"
    OVER_UNDER_203_5 = "over_under_games_203_5"
    OVER_UNDER_204_5 = "over_under_games_204_5"
    OVER_UNDER_205_5 = "over_under_games_205_5"
    OVER_UNDER_206_5 = "over_under_games_206_5"
    OVER_UNDER_207_5 = "over_under_games_207_5"
    OVER_UNDER_208_5 = "over_under_games_208_5"
    OVER_UNDER_209_5 = "over_under_games_209_5"
    OVER_UNDER_210_5 = "over_under_games_210_5"
    OVER_UNDER_211_5 = "over_under_games_211_5"
    OVER_UNDER_212_5 = "over_under_games_212_5"
    OVER_UNDER_213_5 = "over_under_games_213_5"
    OVER_UNDER_214_5 = "over_under_games_214_5"
    OVER_UNDER_215_5 = "over_under_games_215_5"
    OVER_UNDER_216_5 = "over_under_games_216_5"
    OVER_UNDER_217_5 = "over_under_games_217_5"
    OVER_UNDER_218_5 = "over_under_games_218_5"
    OVER_UNDER_219_5 = "over_under_games_219_5"
    OVER_UNDER_220_5 = "over_under_games_220_5"
    OVER_UNDER_221_5 = "over_under_games_221_5"
    OVER_UNDER_222_5 = "over_under_games_222_5"
    OVER_UNDER_223_5 = "over_under_games_223_5"
    OVER_UNDER_224_5 = "over_under_games_224_5"
    OVER_UNDER_225_5 = "over_under_games_225_5"
    OVER_UNDER_226_5 = "over_under_games_226_5"
    OVER_UNDER_227_5 = "over_under_games_227_5"
    OVER_UNDER_228_5 = "over_under_games_228_5"
    OVER_UNDER_229_5 = "over_under_games_229_5"
    OVER_UNDER_230_5 = "over_under_games_230_5"
    OVER_UNDER_231_5 = "over_under_games_231_5"
    OVER_UNDER_232_5 = "over_under_games_232_5"
    OVER_UNDER_233_5 = "over_under_games_233_5"
    OVER_UNDER_234_5 = "over_under_games_234_5"
    OVER_UNDER_235_5 = "over_under_games_235_5"
    OVER_UNDER_236_5 = "over_under_games_236_5"
    OVER_UNDER_237_5 = "over_under_games_237_5"
    OVER_UNDER_238_5 = "over_under_games_238_5"
    OVER_UNDER_239_5 = "over_under_games_239_5"
    OVER_UNDER_240_5 = "over_under_games_240_5"
    OVER_UNDER_241_5 = "over_under_games_241_5"
    OVER_UNDER_242_5 = "over_under_games_242_5"
    OVER_UNDER_243_5 = "over_under_games_243_5"
    OVER_UNDER_244_5 = "over_under_games_244_5"
    OVER_UNDER_245_5 = "over_under_games_245_5"
    OVER_UNDER_246_5 = "over_under_games_246_5"
    OVER_UNDER_247_5 = "over_under_games_247_5"
    OVER_UNDER_248_5 = "over_under_games_248_5"
    OVER_UNDER_249_5 = "over_under_games_249_5"
    OVER_UNDER_250_5 = "over_under_games_250_5"
    OVER_UNDER_251_5 = "over_under_games_251_5"
    OVER_UNDER_252_5 = "over_under_games_252_5"
    OVER_UNDER_253_5 = "over_under_games_253_5"
    OVER_UNDER_254_5 = "over_under_games_254_5"
    OVER_UNDER_255_5 = "over_under_games_255_5"
    OVER_UNDER_256_5 = "over_under_games_256_5"
    OVER_UNDER_257_5 = "over_under_games_257_5"
    OVER_UNDER_258_5 = "over_under_games_258_5"
    OVER_UNDER_259_5 = "over_under_games_259_5"
    OVER_UNDER_260_5 = "over_under_games_260_5"


class BasketballAsianHandicapMarket(Enum):
    """Asian Handicap markets in basketball games."""

    HANDICAP_MINUS_25_5 = "asian_handicap_games_-25_5_games"
    HANDICAP_MINUS_24_5 = "asian_handicap_games_-24_5_games"
    HANDICAP_MINUS_23_5 = "asian_handicap_games_-23_5_games"
    HANDICAP_MINUS_22_5 = "asian_handicap_games_-22_5_games"
    HANDICAP_MINUS_21_5 = "asian_handicap_games_-21_5_games"
    HANDICAP_MINUS_20_5 = "asian_handicap_games_-20_5_games"
    HANDICAP_MINUS_19_5 = "asian_handicap_games_-19_5_games"
    HANDICAP_MINUS_18_5 = "asian_handicap_games_-18_5_games"
    HANDICAP_MINUS_17_5 = "asian_handicap_games_-17_5_games"
    HANDICAP_MINUS_16_5 = "asian_handicap_games_-16_5_games"
    HANDICAP_MINUS_15_5 = "asian_handicap_games_-15_5_games"
    HANDICAP_MINUS_14_5 = "asian_handicap_games_-14_5_games"
    HANDICAP_MINUS_13_5 = "asian_handicap_games_-13_5_games"
    HANDICAP_MINUS_12_5 = "asian_handicap_games_-12_5_games"
    HANDICAP_MINUS_11_5 = "asian_handicap_games_-11_5_games"
    HANDICAP_MINUS_10_5 = "asian_handicap_games_-10_5_games"
    HANDICAP_MINUS_9_5 = "asian_handicap_games_-9_5_games"
    HANDICAP_MINUS_8_5 = "asian_handicap_games_-8_5_games"
    HANDICAP_MINUS_7_5 = "asian_handicap_games_-7_5_games"
    HANDICAP_MINUS_6_5 = "asian_handicap_games_-6_5_games"
    HANDICAP_MINUS_5_5 = "asian_handicap_games_-5_5_games"
    HANDICAP_MINUS_4_5 = "asian_handicap_games_-4_5_games"
    HANDICAP_MINUS_3_5 = "asian_handicap_games_-3_5_games"
    HANDICAP_MINUS_2_5 = "asian_handicap_games_-2_5_games"
    HANDICAP_MINUS_1_5 = "asian_handicap_games_-1_5_games"
    HANDICAP_PLUS_0_5 = "asian_handicap_games_+0_5_games"
    HANDICAP_PLUS_1_5 = "asian_handicap_games_+1_5_games"
    HANDICAP_PLUS_2_5 = "asian_handicap_games_+2_5_games"
    HANDICAP_PLUS_3_5 = "asian_handicap_games_+3_5_games"
    HANDICAP_PLUS_4_5 = "asian_handicap_games_+4_5_games"
    HANDICAP_PLUS_5_5 = "asian_handicap_games_+5_5_games"
    HANDICAP_PLUS_6_5 = "asian_handicap_games_+6_5_games"
    HANDICAP_PLUS_7_5 = "asian_handicap_games_+7_5_games"
    HANDICAP_PLUS_8_5 = "asian_handicap_games_+8_5_games"
    HANDICAP_PLUS_9_5 = "asian_handicap_games_+9_5_games"
    HANDICAP_PLUS_10_5 = "asian_handicap_games_+10_5_games"
    HANDICAP_PLUS_11_5 = "asian_handicap_games_+11_5_games"
    HANDICAP_PLUS_12_5 = "asian_handicap_games_+12_5_games"
    HANDICAP_PLUS_13_5 = "asian_handicap_games_+13_5_games"
    HANDICAP_PLUS_14_5 = "asian_handicap_games_+14_5_games"
    HANDICAP_PLUS_15_5 = "asian_handicap_games_+15_5_games"
    HANDICAP_PLUS_16_5 = "asian_handicap_games_+16_5_games"
    HANDICAP_PLUS_17_5 = "asian_handicap_games_+17_5_games"
    HANDICAP_PLUS_18_5 = "asian_handicap_games_+18_5_games"
    HANDICAP_PLUS_19_5 = "asian_handicap_games_+19_5_games"
    HANDICAP_PLUS_20_5 = "asian_handicap_games_+20_5_games"
    HANDICAP_PLUS_21_5 = "asian_handicap_games_+21_5_games"
    HANDICAP_PLUS_22_5 = "asian_handicap_games_+22_5_games"
    HANDICAP_PLUS_23_5 = "asian_handicap_games_+23_5_games"
    HANDICAP_PLUS_24_5 = "asian_handicap_games_+24_5_games"
    HANDICAP_PLUS_25_5 = "asian_handicap_games_+25_5_games"


class RugbyLeagueMarket(Enum):
    """Rugby League-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"
    DNB = "dnb"
    DOUBLE_CHANCE = "double_chance"
    OVER_UNDER_32_5 = "over_under_32_5"
    OVER_UNDER_36_5 = "over_under_36_5"
    OVER_UNDER_40_5 = "over_under_40_5"
    OVER_UNDER_41_5 = "over_under_41_5"
    OVER_UNDER_42_5 = "over_under_42_5"
    OVER_UNDER_43_5 = "over_under_43_5"
    OVER_UNDER_44_5 = "over_under_44_5"
    OVER_UNDER_45_5 = "over_under_45_5"
    OVER_UNDER_46_5 = "over_under_46_5"
    OVER_UNDER_47_5 = "over_under_47_5"
    OVER_UNDER_48_5 = "over_under_48_5"
    OVER_UNDER_49_5 = "over_under_49_5"
    OVER_UNDER_50_5 = "over_under_50_5"
    OVER_UNDER_51_5 = "over_under_51_5"
    OVER_UNDER_52_5 = "over_under_52_5"
    HANDICAP_MINUS_4_5 = "handicap_-4_5"
    HANDICAP_PLUS_4_5 = "handicap_+4_5"
    HANDICAP_MINUS_8_5 = "handicap_-8_5"
    HANDICAP_PLUS_8_5 = "handicap_+8_5"
    HANDICAP_MINUS_12_5 = "handicap_-12_5"
    HANDICAP_PLUS_12_5 = "handicap_+12_5"
    HANDICAP_MINUS_16_5 = "handicap_-16_5"
    HANDICAP_PLUS_16_5 = "handicap_+16_5"


class RugbyUnionMarket(Enum):
    """Rugby Union-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"
    DNB = "dnb"
    DOUBLE_CHANCE = "double_chance"
    OVER_UNDER_35_5 = "over_under_35_5"
    OVER_UNDER_39_5 = "over_under_39_5"
    OVER_UNDER_43_5 = "over_under_43_5"
    OVER_UNDER_47_5 = "over_under_47_5"
    OVER_UNDER_51_5 = "over_under_51_5"
    OVER_UNDER_55_5 = "over_under_55_5"
    HANDICAP_MINUS_5_5 = "handicap_-5_5"
    HANDICAP_PLUS_5_5 = "handicap_+5_5"
    HANDICAP_MINUS_9_5 = "handicap_-9_5"
    HANDICAP_PLUS_9_5 = "handicap_+9_5"
    HANDICAP_MINUS_10_5 = "handicap_-10_5"
    HANDICAP_PLUS_10_5 = "handicap_+10_5"
    HANDICAP_MINUS_11_5 = "handicap_-11_5"
    HANDICAP_PLUS_11_5 = "handicap_+11_5"
    HANDICAP_MINUS_13_5 = "handicap_-13_5"
    HANDICAP_PLUS_13_5 = "handicap_+13_5"
    HANDICAP_MINUS_17_5 = "handicap_-17_5"
    HANDICAP_PLUS_17_5 = "handicap_+17_5"


class IceHockeyMarket(Enum):
    """Ice Hockey-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"
    DNB = "dnb"
    BTTS = "btts"
    DOUBLE_CHANCE = "double_chance"
    OVER_UNDER_1_5 = "over_under_1_5"
    OVER_UNDER_2_5 = "over_under_2_5"
    OVER_UNDER_3_5 = "over_under_3_5"
    OVER_UNDER_4_5 = "over_under_4_5"
    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_5 = "over_under_10_5"
    OVER_UNDER_11_5 = "over_under_11_5"


class RugbyOverUnderMarket(Enum):
    """Over/Under market values for rugby."""

    OVER_UNDER_32_5 = "over_under_32_5"
    OVER_UNDER_35_5 = "over_under_35_5"
    OVER_UNDER_36_5 = "over_under_36_5"
    OVER_UNDER_39_5 = "over_under_39_5"
    OVER_UNDER_40_5 = "over_under_40_5"
    OVER_UNDER_41_5 = "over_under_41_5"
    OVER_UNDER_42_5 = "over_under_42_5"
    OVER_UNDER_43_5 = "over_under_43_5"
    OVER_UNDER_44_5 = "over_under_44_5"
    OVER_UNDER_45_5 = "over_under_45_5"
    OVER_UNDER_46_5 = "over_under_46_5"
    OVER_UNDER_47_5 = "over_under_47_5"
    OVER_UNDER_48_5 = "over_under_48_5"
    OVER_UNDER_49_5 = "over_under_49_5"
    OVER_UNDER_50_5 = "over_under_50_5"
    OVER_UNDER_51_5 = "over_under_51_5"
    OVER_UNDER_52_5 = "over_under_52_5"
    OVER_UNDER_55_5 = "over_under_55_5"


class RugbyHandicapMarket(Enum):
    """Handicap market values for rugby."""

    HANDICAP_MINUS_17_5 = "handicap_-17_5"
    HANDICAP_MINUS_16_5 = "handicap_-16_5"
    HANDICAP_MINUS_13_5 = "handicap_-13_5"
    HANDICAP_MINUS_12_5 = "handicap_-12_5"
    HANDICAP_MINUS_11_5 = "handicap_-11_5"
    HANDICAP_MINUS_10_5 = "handicap_-10_5"
    HANDICAP_MINUS_9_5 = "handicap_-9_5"
    HANDICAP_MINUS_8_5 = "handicap_-8_5"
    HANDICAP_MINUS_5_5 = "handicap_-5_5"
    HANDICAP_MINUS_4_5 = "handicap_-4_5"
    HANDICAP_PLUS_4_5 = "handicap_+4_5"
    HANDICAP_PLUS_5_5 = "handicap_+5_5"
    HANDICAP_PLUS_8_5 = "handicap_+8_5"
    HANDICAP_PLUS_9_5 = "handicap_+9_5"
    HANDICAP_PLUS_10_5 = "handicap_+10_5"
    HANDICAP_PLUS_11_5 = "handicap_+11_5"
    HANDICAP_PLUS_12_5 = "handicap_+12_5"
    HANDICAP_PLUS_13_5 = "handicap_+13_5"
    HANDICAP_PLUS_16_5 = "handicap_+16_5"
    HANDICAP_PLUS_17_5 = "handicap_+17_5"


class IceHockeyOverUnderMarket(Enum):
    """Over/Under market values for ice hockey."""

    OVER_UNDER_1_5 = "over_under_1_5"
    OVER_UNDER_2_5 = "over_under_2_5"
    OVER_UNDER_3_5 = "over_under_3_5"
    OVER_UNDER_4_5 = "over_under_4_5"
    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_5 = "over_under_10_5"
    OVER_UNDER_11_5 = "over_under_11_5"


# New Sports Market Enums

class AmericanFootballMarket(Enum):
    """American Football-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"
    POINT_SPREAD = "point_spread"


class AmericanFootballOverUnderMarket(Enum):
    """Over/Under market values for American football."""

    OVER_UNDER_30_5 = "over_under_30_5"
    OVER_UNDER_31_5 = "over_under_31_5"
    OVER_UNDER_32_5 = "over_under_32_5"
    OVER_UNDER_33_5 = "over_under_33_5"
    OVER_UNDER_34_5 = "over_under_34_5"
    OVER_UNDER_35_5 = "over_under_35_5"
    OVER_UNDER_36_5 = "over_under_36_5"
    OVER_UNDER_37_5 = "over_under_37_5"
    OVER_UNDER_38_5 = "over_under_38_5"
    OVER_UNDER_39_5 = "over_under_39_5"
    OVER_UNDER_40_5 = "over_under_40_5"
    OVER_UNDER_41_5 = "over_under_41_5"
    OVER_UNDER_42_5 = "over_under_42_5"
    OVER_UNDER_43_5 = "over_under_43_5"
    OVER_UNDER_44_5 = "over_under_44_5"
    OVER_UNDER_45_5 = "over_under_45_5"
    OVER_UNDER_46_5 = "over_under_46_5"
    OVER_UNDER_47_5 = "over_under_47_5"
    OVER_UNDER_48_5 = "over_under_48_5"
    OVER_UNDER_49_5 = "over_under_49_5"
    OVER_UNDER_50_5 = "over_under_50_5"
    OVER_UNDER_51_5 = "over_under_51_5"
    OVER_UNDER_52_5 = "over_under_52_5"
    OVER_UNDER_53_5 = "over_under_53_5"
    OVER_UNDER_54_5 = "over_under_54_5"
    OVER_UNDER_55_5 = "over_under_55_5"
    OVER_UNDER_56_5 = "over_under_56_5"
    OVER_UNDER_57_5 = "over_under_57_5"
    OVER_UNDER_58_5 = "over_under_58_5"
    OVER_UNDER_59_5 = "over_under_59_5"
    OVER_UNDER_60_5 = "over_under_60_5"


class AussieRulesMarket(Enum):
    """Aussie Rules-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"
    HANDICAP = "handicap"


class AussieRulesOverUnderMarket(Enum):
    """Over/Under market values for Aussie Rules."""

    OVER_UNDER_150_5 = "over_under_150_5"
    OVER_UNDER_151_5 = "over_under_151_5"
    OVER_UNDER_152_5 = "over_under_152_5"
    OVER_UNDER_153_5 = "over_under_153_5"
    OVER_UNDER_154_5 = "over_under_154_5"
    OVER_UNDER_155_5 = "over_under_155_5"
    OVER_UNDER_156_5 = "over_under_156_5"
    OVER_UNDER_157_5 = "over_under_157_5"
    OVER_UNDER_158_5 = "over_under_158_5"
    OVER_UNDER_159_5 = "over_under_159_5"
    OVER_UNDER_160_5 = "over_under_160_5"
    OVER_UNDER_161_5 = "over_under_161_5"
    OVER_UNDER_162_5 = "over_under_162_5"
    OVER_UNDER_163_5 = "over_under_163_5"
    OVER_UNDER_164_5 = "over_under_164_5"
    OVER_UNDER_165_5 = "over_under_165_5"
    OVER_UNDER_166_5 = "over_under_166_5"
    OVER_UNDER_167_5 = "over_under_167_5"
    OVER_UNDER_168_5 = "over_under_168_5"
    OVER_UNDER_169_5 = "over_under_169_5"
    OVER_UNDER_170_5 = "over_under_170_5"


class BadmintonMarket(Enum):
    """Badminton-specific markets."""

    MATCH_WINNER = "match_winner"


class BadmintonOverUnderMarket(Enum):
    """Over/Under market values for badminton."""

    OVER_UNDER_30_5 = "over_under_30_5"
    OVER_UNDER_31_5 = "over_under_31_5"
    OVER_UNDER_32_5 = "over_under_32_5"
    OVER_UNDER_33_5 = "over_under_33_5"
    OVER_UNDER_34_5 = "over_under_34_5"
    OVER_UNDER_35_5 = "over_under_35_5"
    OVER_UNDER_36_5 = "over_under_36_5"
    OVER_UNDER_37_5 = "over_under_37_5"
    OVER_UNDER_38_5 = "over_under_38_5"
    OVER_UNDER_39_5 = "over_under_39_5"
    OVER_UNDER_40_5 = "over_under_40_5"
    OVER_UNDER_41_5 = "over_under_41_5"
    OVER_UNDER_42_5 = "over_under_42_5"
    OVER_UNDER_43_5 = "over_under_43_5"
    OVER_UNDER_44_5 = "over_under_44_5"
    OVER_UNDER_45_5 = "over_under_45_5"


class BandyMarket(Enum):
    """Bandy-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class BandyOverUnderMarket(Enum):
    """Over/Under market values for bandy."""

    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_5 = "over_under_10_5"
    OVER_UNDER_11_5 = "over_under_11_5"
    OVER_UNDER_12_5 = "over_under_12_5"


class BoxingMarket(Enum):
    """Boxing-specific markets."""

    MATCH_WINNER = "match_winner"


class CricketMarket(Enum):
    """Cricket-specific markets."""

    MATCH_WINNER = "match_winner"


class CricketOverUnderMarket(Enum):
    """Over/Under market values for cricket."""

    OVER_UNDER_150_5 = "over_under_150_5"
    OVER_UNDER_160_5 = "over_under_160_5"
    OVER_UNDER_170_5 = "over_under_170_5"
    OVER_UNDER_180_5 = "over_under_180_5"
    OVER_UNDER_190_5 = "over_under_190_5"
    OVER_UNDER_200_5 = "over_under_200_5"
    OVER_UNDER_210_5 = "over_under_210_5"
    OVER_UNDER_220_5 = "over_under_220_5"
    OVER_UNDER_230_5 = "over_under_230_5"
    OVER_UNDER_240_5 = "over_under_240_5"
    OVER_UNDER_250_5 = "over_under_250_5"


class DartsMarket(Enum):
    """Darts-specific markets."""

    MATCH_WINNER = "match_winner"


class EsportsMarket(Enum):
    """Esports-specific markets."""

    MATCH_WINNER = "match_winner"


class FloorballMarket(Enum):
    """Floorball-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class FloorballOverUnderMarket(Enum):
    """Over/Under market values for floorball."""

    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_5 = "over_under_10_5"


class FutsalMarket(Enum):
    """Futsal-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class FutsalOverUnderMarket(Enum):
    """Over/Under market values for futsal."""

    OVER_UNDER_3_5 = "over_under_3_5"
    OVER_UNDER_4_5 = "over_under_4_5"
    OVER_UNDER_5_5 = "over_under_5_5"
    OVER_UNDER_6_5 = "over_under_6_5"
    OVER_UNDER_7_5 = "over_under_7_5"
    OVER_UNDER_8_5 = "over_under_8_5"
    OVER_UNDER_9_5 = "over_under_9_5"
    OVER_UNDER_10_5 = "over_under_10_5"


class HandballMarket(Enum):
    """Handball-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class HandballOverUnderMarket(Enum):
    """Over/Under market values for handball."""

    OVER_UNDER_50_5 = "over_under_50_5"
    OVER_UNDER_51_5 = "over_under_51_5"
    OVER_UNDER_52_5 = "over_under_52_5"
    OVER_UNDER_53_5 = "over_under_53_5"
    OVER_UNDER_54_5 = "over_under_54_5"
    OVER_UNDER_55_5 = "over_under_55_5"
    OVER_UNDER_56_5 = "over_under_56_5"
    OVER_UNDER_57_5 = "over_under_57_5"
    OVER_UNDER_58_5 = "over_under_58_5"
    OVER_UNDER_59_5 = "over_under_59_5"
    OVER_UNDER_60_5 = "over_under_60_5"
    OVER_UNDER_61_5 = "over_under_61_5"
    OVER_UNDER_62_5 = "over_under_62_5"
    OVER_UNDER_63_5 = "over_under_63_5"
    OVER_UNDER_64_5 = "over_under_64_5"
    OVER_UNDER_65_5 = "over_under_65_5"
    OVER_UNDER_66_5 = "over_under_66_5"
    OVER_UNDER_67_5 = "over_under_67_5"
    OVER_UNDER_68_5 = "over_under_68_5"
    OVER_UNDER_69_5 = "over_under_69_5"
    OVER_UNDER_70_5 = "over_under_70_5"


class MmaMarket(Enum):
    """MMA-specific markets."""

    MATCH_WINNER = "match_winner"


class SnookerMarket(Enum):
    """Snooker-specific markets."""

    MATCH_WINNER = "match_winner"


class TableTennisMarket(Enum):
    """Table Tennis-specific markets."""

    MATCH_WINNER = "match_winner"


class VolleyballMarket(Enum):
    """Volleyball-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class VolleyballOverUnderMarket(Enum):
    """Over/Under market values for volleyball."""

    OVER_UNDER_150_5 = "over_under_150_5"
    OVER_UNDER_160_5 = "over_under_160_5"
    OVER_UNDER_170_5 = "over_under_170_5"
    OVER_UNDER_180_5 = "over_under_180_5"
    OVER_UNDER_190_5 = "over_under_190_5"
    OVER_UNDER_200_5 = "over_under_200_5"
    OVER_UNDER_210_5 = "over_under_210_5"
    OVER_UNDER_220_5 = "over_under_220_5"
    OVER_UNDER_230_5 = "over_under_230_5"
    OVER_UNDER_240_5 = "over_under_240_5"
    OVER_UNDER_250_5 = "over_under_250_5"


class WaterPoloMarket(Enum):
    """Water Polo-specific markets."""

    ONE_X_TWO = "1x2"
    HOME_AWAY = "home_away"


class WaterPoloOverUnderMarket(Enum):
    """Over/Under market values for water polo."""

    OVER_UNDER_15_5 = "over_under_15_5"
    OVER_UNDER_16_5 = "over_under_16_5"
    OVER_UNDER_17_5 = "over_under_17_5"
    OVER_UNDER_18_5 = "over_under_18_5"
    OVER_UNDER_19_5 = "over_under_19_5"
    OVER_UNDER_20_5 = "over_under_20_5"
    OVER_UNDER_21_5 = "over_under_21_5"
    OVER_UNDER_22_5 = "over_under_22_5"
    OVER_UNDER_23_5 = "over_under_23_5"
    OVER_UNDER_24_5 = "over_under_24_5"
    OVER_UNDER_25_5 = "over_under_25_5"
