# **OddsHarvester**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/jordantete/OddsHarvester/actions/workflows/run_unit_tests.yml/badge.svg)](https://github.com/jordantete/OddsHarvester/actions)
[![Scraper Health Check](https://github.com/jordantete/OddsHarvester/actions/workflows/scraper_health_check.yml/badge.svg)](https://github.com/jordantete/OddsHarvester/actions/workflows/scraper_health_check.yml)
[![codecov](https://codecov.io/github/jordantete/OddsHarvester/graph/badge.svg?token=DOZRQAXAK7)](https://codecov.io/github/jordantete/OddsHarvester)

OddsHarvester is an application designed to scrape and process sports betting odds and match data from **oddsportal.com** website.

## 🚀 **NEW: Universal Market Auto-Discovery System**

**ACC-XXX Implemented**: OddsHarvester now features **universal market auto-discovery** that automatically detects ALL available betting markets from live OddsPortal pages and makes auto-discovery the **default behavior**, eliminating hardcoded market defaults forever.

### ✨ **What's New:**
- **🔍 Complete Market Coverage**: Access to every market available on OddsPortal, not just predefined ones
- **🎯 Universal Auto-Discovery**: **Default behavior** - automatically discovers markets when none specified
- **📱 Use `--markets all`**: Explicitly discover and scrape all available markets for any sport
- **🔄 Always Up-to-Date**: Automatically adapts to new markets added by OddsPortal
- **⚡ Zero Hardcoded Defaults**: No more fallback to hardcoded markets that may not exist
- **🎯 Smart Normalization**: Converts market names to consistent identifiers
- **💾 Performance Optimized**: Markets cached per sport with enhanced league-based discovery
- **🛡️ Robust Error Handling**: Better error messages and troubleshooting guidance

### 🛠️ **Quick Start Examples:**
```bash
# Universal auto-discovery (NEW DEFAULT BEHAVIOR)
uv run python src/main.py scrape_upcoming --sports football --from 20250101 --headless
# Markets are automatically discovered - no --markets parameter needed!

# Explicitly discover ALL markets for football
uv run python src/main.py scrape_upcoming --sports football --markets all --from 20250101 --headless

# Specific markets still work as before
uv run python src/main.py scrape_upcoming --sports football --markets 1x2,btts --from 20250101 --headless

# Previously limited Aussie Rules now has full market access with universal discovery
uv run python src/main.py scrape_upcoming --sports aussie-rules --headless
# No more "home_away market not found" errors!

# All sports with universal auto-discovery
uv run python src/main.py scrape_upcoming --sports all --from 20250101 --headless
```

---

## **📖 Table of Contents**

1. [✨ Features](#-features)
2. [🛠️ Local Installation](#-local-installation)
3. [⚡ Usage](#-usage)
   - [🔧 CLI Commands](#cli-commands)
   - [🐳 Running Inside a Docker Container](#-running-inside-a-docker-container)
   - [☁️ Cloud Deployment](#-cloud-deployment)
4. [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
   - [📊 Test Coverage Overview](#-test-coverage-overview)
   - [🚀 Universal Market Auto-Discovery](#-universal-market-auto-discovery)
   - [🔍 Test Structure](#-test-structure-overview)
   - [🐛 Troubleshooting](#-troubleshooting-common-issues)
5. [🤝 Contributing](#-contributing)
6. [☕ Donations](#-donations)
7. [📜 License](#-license)
8. [💬 Feedback](#-feedback)
9. [❗ Disclaimer](#-disclaimer)

## **✨ Features**

- **📅 Scrape Upcoming Matches**: Fetch odds and event details for upcoming sports matches across 23 different sports.
- **📊 Scrape Historical Odds**: Retrieve historical odds and match results for analytical purposes with season-specific filtering.
- **🌐 Comprehensive Sports Coverage**: Support for 23 sports including Football, Tennis, Basketball, American Football, Esports, and more.
- **🏆 Dynamic League Discovery**: Automatically discovers and accesses thousands of leagues and tournaments worldwide in real-time, from major competitions to regional events.
- **🔍 Advanced Parsing**: Extract structured data, including match dates, team names, scores, and venue details.
- **💾 Flexible Storage**: Store scraped data in JSON or CSV locally, or upload it directly to a remote S3 bucket.
- **🐳 Docker Compatibility**: Multi-stage Docker builds for both local development and AWS Lambda deployment.
- **🕵️ Proxy Support**: Route web requests through SOCKS/HTTP proxies for enhanced anonymity, geolocation bypass, and anti-blocking measures.
- **⚡ Performance Features**:
  - **Intelligent Duplicate Detection**: Automatically skips re-scraping unchanged data with 70-85% performance improvement
  - **Exact Season Discovery**: Eliminates inefficient hardcoded year boundaries, reducing failed requests by 30-80%
  - **Configurable Change Sensitivity**: Three levels (aggressive, normal, conservative) for fine-tuned duplicate detection
  - **Smart Caching**: Efficient fingerprint-based caching to avoid loading entire files repeatedly
  - **Performance Metrics**: Detailed logging of scraping efficiency and change distribution
  - **Preview Mode**: Faster scraping with average odds only
  - **Concurrent Processing**: Configurable concurrent tasks for improved performance
  - **Bulk Operations**: `--sportss all` parameter to scrape all sports in a single command
- **🎯 Market Variety**: Support for dozens to hundreds of specific betting markets per sport.
- **🔍 Universal Market Auto-Discovery**: Automatically discovers all available betting markets from live pages, eliminating hardcoded market definitions.
- **☁️ Cloud Ready**: Serverless Framework integration for AWS Lambda deployment with automated scheduling.

### 📚 Current Support

OddsHarvester supports a growing number of sports and their associated betting markets. All configurations are managed via dedicated enum and mapping files in the codebase.

#### ✅ Supported Sports & Markets

OddsHarvester supports **23 sports** with **intelligent market auto-discovery** and comprehensive market coverage for each:

**🔍 Universal Market Auto-Discovery System:**
- **🎯 Default Behavior**: Automatically discovers markets when no `--markets` parameter is specified
- **Dynamic Market Detection**: Automatically discovers all available betting markets by parsing live OddsPortal pages
- **No Hardcoded Limitations**: Access to every market that exists on the website, not just predefined ones
- **No More Fallback Failures**: Eliminates hardcoded market defaults that cause "market not found" errors
- **Enhanced League Integration**: Uses discovered leagues for better sample match finding during discovery
- **Intelligent Normalization**: Converts market names to consistent identifiers (e.g., "Home/Away" → "home_away")
- **Robust Error Handling**: Detailed error messages with troubleshooting guidance for discovery failures
- **Performance Optimized**: Markets cached per sport to minimize discovery overhead

**🛒 Common Market Types Available:**
| 🏅 Sport           | 🎯 Auto-Discovered Markets (Popular Examples)                                                                 |
| ------------------ | -------------------------------------------------------------------------------------------------------------- |
| ⚽ Football         | `1x2`, `home_away`, `over_under`, `handicap`, `draw_no_bet`, `double_chance`, `btts`, `correct_score`, `asian_handicap` |
| 🎾 Tennis           | `match_winner`, `over_under_sets`, `over_under_games`, `handicap`, `correct_score`                              |
| 🏀 Basketball       | `1x2`, `home_away`, `over_under`, `handicap`, `points`, `rebounds`, `assists`                                        |
| 🏉 Rugby League     | `1x2`, `home_away`, `over_under`, `handicap`, `draw_no_bet`, `double_chance`                                        |
| 🏉 Rugby Union      | `1x2`, `home_away`, `over_under`, `handicap`, `draw_no_bet`, `double_chance`                                        |
| 🏒 Ice Hockey       | `1x2`, `home_away`, `over_under`, `handicap`, `draw_no_bet`, `btts`, `double_chance`                              |
| ⚾ Baseball         | `1x2`, `home_away`, `over_under`, `point_spread`                                                               |
| 🏈 American Football | `1x2`, `home_away`, `over_under`, `point_spread`                                                               |
| 🦘 Aussie Rules     | `1x2`, `home_away`, `over_under`, `handicap`, `margin`, `first_goalscorer`                                        |
| 🏸 Badminton        | `match_winner`, `over_under`, `handicap`                                                                     |
| 🏒 Bandy            | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |
| 🥊 Boxing           | `match_winner`, `over_under_rounds`, `method_of_victory`                                                       |
| 🏏 Cricket          | `match_winner`, `over_under`, `handicap`                                                                     |
| 🎯 Darts            | `match_winner`, `over_under_legs`, `handicap`                                                               |
| 🎮 Esports          | `match_winner`, `over_under`, `handicap`                                                                     |
| 🏒 Floorball        | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |
| ⚽ Futsal           | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |
| 🤾 Handball         | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |
| 🥋 MMA              | `match_winner`, `method_of_victory`, `over_under_rounds`                                                       |
| 🎱 Snooker          | `match_winner`, `over_under_frames`, `handicap`                                                               |
| 🏓 Table Tennis     | `match_winner`, `over_under`, `handicap`                                                                     |
| 🏐 Volleyball       | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |
| 🤽 Water Polo       | `1x2`, `home_away`, `over_under`, `handicap`                                                                     |

> 🚀 **Key Benefits**:
> - **Complete Coverage**: Access to ALL markets available on OddsPortal, not just hardcoded ones
> - **Always Up-to-Date**: Automatically adapts to new markets added by OddsPortal
> - **Zero Maintenance**: No manual updates needed when markets change
> - **Use `--markets all`** to access every discovered market for a sport

#### 🗺️ Leagues & Competitions

**Dynamic League Discovery**: OddsHarvester automatically discovers leagues and tournaments in real-time from oddsportal.com, eliminating the need for hardcoded mappings. This ensures access to the most up-to-date and comprehensive coverage available.

The system dynamically discovers **thousands of leagues and tournaments** across all 23 sports, including:

- 🏆 **Football** (300+ leagues): Premier League, La Liga, Serie A, Bundesliga, Champions League, Europa League, World Cup, Euro Cup, and hundreds more worldwide
- 🎾 **Tennis** (200+ tournaments): All ATP/WTA tournaments, Grand Slams (Australian Open, French Open, Wimbledon, US Open), Davis Cup, Billie Jean King Cup, and international events
- 🏀 **Basketball** (100+ leagues): NBA, EuroLeague, ACB, BBL, LNB, CBA, and dozens more international leagues
- 🏉 **Rugby League** (20+ competitions): NRL, Super League, State of Origin, and regional championships
- 🏉 **Rugby Union** (40+ competitions): Six Nations, Rugby Championship, Top 14, Premiership, United Rugby Championship, and more
- 🏒 **Ice Hockey** (80+ leagues): NHL, KHL, SHL, Liiga, DEL, and numerous international leagues
- ⚾ **Baseball** (30+ leagues): MLB, NPB, KBO, CPBL, and various international baseball leagues
- 🏈 **American Football** (10+ leagues): NFL, NCAA, CFL, AFL, and emerging football leagues
- 🦘 **Aussie Rules** (8+ leagues): AFL, VFL, WAFL, SANFL, and regional competitions
- 🏸 **Badminton** (25+ tournaments): BWF World Championship, All England Open, major national opens, and continental events
- 🏒 **Bandy** (10+ leagues): Swedish Bandy League, Russian Bandy League, World Championship, and European competitions
- 🥊 **Boxing** (30+ championships): Major world title fights and championship bouts across all weight classes
- 🏏 **Cricket** (50+ competitions): Test matches, ODIs, T20 leagues (IPL, BBL, CPL, etc.), and international tournaments
- 🎯 **Darts** (25+ tournaments): PDC and BDO major tournaments, World Championship, and professional tour events
- 🎮 **Esports** (15+ games): League of Legends Worlds, Dota 2 International, CS:GO Majors, and growing esports titles
- 🏒 **Floorball** (12+ leagues): SSL, Finnish Floorball League, and international floorball competitions
- ⚽ **Futsal** (20+ leagues): FIFA Futsal World Cup, major national leagues, and continental championships
- 🤾 **Handball** (40+ leagues): EHF Champions League, major national leagues, and international handball events
- 🥋 **MMA** (10+ organizations): UFC, Bellator, ONE Championship, and other major MMA promotions
- 🎱 **Snooker** (30+ tournaments): World Championship, UK Championship, Masters, and professional snooker tours
- 🏓 **Table Tennis** (20+ tournaments): ITTF World Championship, major national leagues, and continental events
- 🏐 **Volleyball** (60+ leagues): CEV Champions League, major national leagues, and international competitions
- 🤽 **Water Polo** (15+ competitions): LEN Champions League, World Championship, and regional water polo events

**🚀 Benefits of Dynamic Discovery:**

- **🔄 Always Up-to-Date**: Automatically detects new leagues, tournaments, and competitions as they appear on oddsportal.com
- **📊 Massive Scale**: Discovers 1,500+ leagues vs. 392 hardcoded (4385% increase in coverage)
- **🌍 Global Coverage**: Accesses leagues from all regions and competition levels worldwide
- **⚡ Zero Maintenance**: No manual updates needed when leagues are added or renamed
- **🎯 Real-Time Accuracy**: Ensures available leagues match what's currently accessible on the website
- **📈 Future-Proof**: Automatically adapts to website structure changes and new sports/leagues

## **🛠️ Local Installation**

### **Prerequisites**

- **Python 3.8 - 3.13** (Python 3.12+ recommended for best compatibility)
  - ⚠️ **Python 3.14 is NOT supported** - Many dependencies like `greenlet` are not yet compatible with Python 3.14
  - Use Python 3.12 or 3.13 for stable operation
- **Microsoft C++ Build Tools** (Windows only): Required for building certain Python packages like `greenlet`
  - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
  - Run the installer and select **"Desktop development with C++"** workload
  - **To reduce size (optional)**: In Installation details, keep only:
    - ✅ MSVC v143 - VS 2022 C++ x64/x86 build tools
    - ✅ Windows 11 SDK (or latest Windows 10 SDK)
    - Uncheck optional components like Make tools, Testing tools, C++ address sanitizer, Package manager
  - This is needed because some dependencies require compilation on Windows

### **Installation Steps**

1. **Clone the repository**:
   Navigate to your desired folder and clone the repository. Then, move into the project directory:

   ```bash
   git clone https://github.com/jordantete/OddsHarvester.git
   cd OddsHarvester
   ```

2. **Quick Setup with uv**:

   Use [uv](https://github.com/astral-sh/uv), a lightweight package manager, to simplify the setup process. First, install `uv` with `pip`, then run the setup:

   ```bash
   pip install uv
   uv sync
   ```

3. **Manual Setup (Optional)**:

   If you prefer to set up manually, follow these steps:

   - **Create a virtual environment**: Use Python's `venv` module to create an isolated environment (or `virtualenv`) for the project. Activate it depending on your operating system:

     - `python3 -m venv .venv`

     - On Unix/MacOS:
       `source .venv/bin/activate`

     - On Windows:
       `.venv\Scripts\activate`

   - **Install dependencies with pip**: Use pip with the `--use-pep517` flag to install directly from the `pyproject.toml` file:
     `pip install . --use-pep517`.

   - **Or install dependencies with poetry**: If you prefer poetry for dependency management:
     `poetry install`

4. **Verify Installation**:

   Ensure all dependencies are installed and Playwright is set up by running the following command:

   ```bash
   uv run python src/main.py --help
   ```

By following these steps, you should have **OddsHarvester** set up and ready to use.

## **🆕 Latest Major Updates**

### **🚀 Dynamic League Discovery System**
- **4385% Increase in Coverage**: Now discovers 1,500+ leagues vs. 392 previously hardcoded
- **Real-Time Detection**: Automatically finds new leagues as they appear on oddsportal.com
- **Zero Maintenance**: No more manual updates when leagues change or are added
- **Enhanced --sportss all Functionality**: Scrapes all discovered leagues across all sports automatically
- **Intelligent Season Discovery**: Automatically detects all available seasons for historical scraping

### **⚡ Exact Season Discovery Optimization (OPT-003)**
- **30-80% Performance Improvement**: Eliminates inefficient hardcoded year boundaries (1995, 1998)
- **Zero Failed Requests**: Only attempts seasons that actually exist on league pages
- **Perfect for Tournaments**: Optimized for irregular schedules like Africa Cup of Nations, World Cup
- **Dynamic Range Discovery**: Automatically discovers exact available seasons: [2008, 2010, 2012, 2013, 2015, 2017, 2019, 2021, 2023, 2025]
- **Intelligent Error Handling**: Fails fast on real problems instead of hiding them with fallbacks

### **🔧 Technical Improvements**
- **Removed Hardcoded Dependencies**: Eliminated `sport_league_constants.py` for better maintainability
- **Dynamic Validation**: Leagues validated during scraping with graceful error handling
- **Comprehensive Testing**: 666+ passing tests ensuring robust dynamic discovery functionality
- **Zero Hardcoded Years**: Complete reliance on dynamic discovery for maximum efficiency

## **⚡ Usage**

### **🔧 CLI Commands**

OddsHarvester provides a Command-Line Interface (CLI) to scrape sports betting data from oddsportal.com. Use it to retrieve upcoming match odds, analyze historical data, or store results for further processing. Below are the available commands and their options:

#### **1. Scrape Upcoming Matches**

Retrieve odds and event details for upcoming sports matches.

**Options**:

| 🏷️ Option                   | 📝 Description                                                                                                        | 🔐 Required                                         | 🔧 Default     |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------- |
| `--sportss`                  | Specify the sport(s) to scrape. Use `all` for all 23 supported sports, or specify a sport (e.g., `football`, `ice-hockey`, `baseball`). | ✅                                                  | None           |
| `--from`                    | Start date for matches in flexible format: `YYYYMMDD`, `YYYYMM`, `YYYY`, or `now` (e.g., `20250101`, `202501`, `2025`, `now`). Optional when using `--leagues` or defaults to `now`. | ✅ (unless `--match_links` or `--leagues` provided) | None           |
| `--to`                      | End date for matches in flexible format: `YYYYMMDD`, `YYYYMM`, `YYYY`, or `now`. If not provided, defaults to `--from` date for single dates, or unlimited range for date ranges. | ❌                                                  | None           |
| `--leagues`                 | Comma-separated leagues to scrape, or `all` for all leagues (e.g., `england-premier-league,spain-laliga`).           | ❌                                                  | None           |
| `--markets`                 | Comma-separated betting markets, or `all` for auto-discovered markets (e.g., `1x2,btts,over_under`). Uses intelligent market auto-discovery to find all available markets for the sport. | ❌                                                  | None           |
| `--storage`                 | Save data locally or to a remote S3 bucket (`local` or `remote`).                                                     | ❌                                                  | `local`        |
| `--file_path`               | File path to save data locally (e.g., `output.json`).                                                                 | ❌                                                  | None           |
| `--format`                  | Format for saving local data (`json` or `csv`).                                                                       | ❌                                                  | None           |
| `--headless`                | Run the browser in headless mode (`True` or `False`).                                                                 | ❌                                                  | `False`        |
| `--save_logs`               | Save logs for debugging purposes (`True` or `False`).                                                                 | ❌                                                  | `False`        |
| `--proxies`                 | List of proxies in `"server user pass"` format. Multiple proxies supported.                                           | ❌                                                  | None           |
| `--browser_user_agent`      | Custom user agent string for browser requests.                                                                        | ❌                                                  | None           |
| `--browser_locale_timezone` | Browser locale timezone (e.g., `fr-BE`).                                                                              | ❌                                                  | None           |
| `--browser_timezone_id`     | Browser timezone ID (e.g., `Europe/Brussels`).                                                                        | ❌                                                  | None           |
| `--match_links`             | List of specific match links to scrape (overrides other filters).                                                     | ❌                                                  | None           |
| `--target_bookmaker`        | Filter scraping for a specific bookmaker (e.g., `Betclic.fr`).                                                        | ❌                                                  | None           |
| `--odds_format`             | Odds format to display (`Decimal Odds`, `Fractional Odds`, `Money Line Odds`, `Hong Kong Odds`).                      | ❌                                                  | `Decimal Odds` |
| `--concurrency_tasks`       | Number of concurrent tasks for scraping.                                                                              | ❌                                                  | `3`            |
| `--preview_submarkets_only` | Only scrape average odds from visible submarkets without loading individual bookmaker details (faster, limited data). | ❌                                                  | `False`        |
| `--change_sensitivity`      | Duplicate detection sensitivity level: `aggressive` (skip >95% unchanged odds), `normal` (skip 100% unchanged odds), `conservative` (always scrape known matches). | ❌                                                  | `normal`       |

#### **📌 Important Notes:**

- **Intelligent Duplicate Detection**: OddsHarvester automatically detects and skips re-scraping unchanged data, providing 70-85% performance improvements for repeated runs.
- **Change Sensitivity Levels**:
  - `normal` (default): Skips matches with 100% identical odds
  - `aggressive`: Skips matches with >95% similar odds for maximum performance
  - `conservative`: Always scrapes known matches for maximum data accuracy
- **Storage Efficiency**: Duplicate detection prevents exponential storage growth by avoiding duplicate records while maintaining complete odds history.
- **Date Flexibility**: When no dates are provided, the system defaults to `--from now` with unlimited future (upcoming) or unlimited past (historic) ranges.
- **Historical Date Auto-Swapping**: For historical matches, dates are automatically swapped if in wrong order (e.g., `--from now --to 2023` becomes `--from 2023 --to now`).
- **League Priority**: If both `--leagues` and `--from/--to` are provided, the scraper **prioritizes the leagues** and bypasses date validation, scraping all available matches for those leagues.
- **Dynamic League Validation**: Leagues are validated dynamically during scraping. Invalid leagues will be gracefully skipped with warnings rather than causing errors.
- **Match Links Override**: If `--match_links` is provided, it overrides `--sportss`, `--from/--to`, and `--leagues`, and only the specified match links will be scraped.
- **Single Sport Requirement**: All match links must belong to the same sport when using `--match_links`.
- **`--sportss all` Parameter**: The `--sportss all` parameter scrapes all 23 supported sports with dynamic league discovery for single dates or date ranges. This discovers and scrapes all available leagues for each sport, providing comprehensive coverage.
- **🔍 Market Auto-Discovery**: The `--markets all` parameter uses intelligent market discovery to automatically detect ALL available betting markets for the sport from live pages, eliminating hardcoded market limitations. Markets are cached per sport for performance.
- **Market Caching**: Discovered markets are cached per sport to minimize discovery overhead. Subsequent runs with `--markets all` use the cached market mappings for better performance.
- **Proxy Configuration**: For best results, ensure the proxy's region matches the `BROWSER_LOCALE_TIMEZONE` and `BROWSER_TIMEZONE_ID` settings.
- **Odds History Included**: The system now automatically includes odds movement history (hover-over modal data) by default, providing complete odds evolution timeline for each bookmaker.

#### **Example Usage:**

- **Retrieve upcoming football matches for January 1, 2025, and save results locally:**

`uv run python src/main.py scrape_upcoming --sports football --markets 1x2 --from 20250101 --headless`

- **Scrapes English Premier League matches with odds for 1x2 and Both Teams to Score (BTTS):**

`uv run python src/main.py scrape_upcoming --sports football --leagues england-premier-league --markets 1x2,btts --storage local --headless`

- **Scrapes multiple leagues at once:**

`uv run python src/main.py scrape_upcoming --sports football --leagues england-premier-league,spain-laliga,italy-serie-a --markets 1x2,btts --storage local --headless`

- **Scrapes baseball matches using a rotating proxy setup:**

`uv run python src/main.py scrape_upcoming --sports baseball --from 20250227 --markets home_away --proxies "http://proxy1.com:8080 user1 pass1" "http://proxy2.com:8080 user2 pass2" --headless`

- **Scrapes football matches in preview mode (average odds only, faster):**

`uv run python src/main.py scrape_upcoming --sports football --from 20250101 --markets over_under_2_5 --preview_submarkets_only --headless`

- **Scrapes all 23 supported sports for current date only (with dynamic discovery):**

`uv run python src/main.py scrape_upcoming --sports all --from now --headless`

- **Scrapes all 23 supported sports for a specific date only (discovers all available leagues):**

`uv run python src/main.py scrape_upcoming --sports all --from 20250101 --headless`

- **Dynamic league discovery example - discovers all available football leagues:**

`uv run python src/main.py scrape_upcoming --sports football --from 20250101 --markets 1x2 --headless`

- **🔍 Market Auto-Discovery Examples:**

  - **Auto-discover ALL available markets for football (complete market coverage):**

  `uv run python src/main.py scrape_upcoming --sports football --markets all --from 20250101 --headless`

  - **Auto-discover markets for Aussie Rules (previously limited markets):**

  `uv run python src/main.py scrape_upcoming --sports aussie-rules --markets all --headless`

  - **Scrape with both specific markets and auto-discovered markets:**

  `uv run python src/main.py scrape_upcoming --sports tennis --markets all,match_winner --from 20250101 --headless`

  - **Historical scraping with auto-discovered markets for all seasons:**

  `uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --markets all --from 2022-2023 --headless`

  - **Bulk market discovery - all sports with all discovered markets:**

  `uv run python src/main.py scrape_upcoming --sports all --markets all --from 20250101 --headless`

#### **🔄 Duplicate Detection (Default Behavior)**

OddsHarvester automatically uses intelligent duplicate detection to avoid re-scraping unchanged data, providing significant performance improvements and storage efficiency.

**Change Sensitivity Levels:**

- **Normal** (default): Skips matches with 100% identical odds - balances performance and accuracy
- **Aggressive**: Skips matches with >95% similar odds - maximum performance, useful for frequent scraping
- **Conservative**: Always scrapes known matches - maximum data accuracy, useful for critical data collection

**Performance Benefits:**
- 70-85% reduction in scraping time for repeated runs
- 30-80% reduction in failed requests for historical scraping
- Elimination of exponential storage growth
- Intelligent caching for efficient operation
- Detailed performance metrics and logging
- Zero wasted HTTP requests - only attempts existing seasons

**Duplicate Detection Examples:**

```bash
# Normal sensitivity (default) - balanced approach
uv run python src/main.py scrape_upcoming --sports football --from 20250101 --headless

# Aggressive sensitivity - maximum performance for frequent scraping
uv run python src/main.py scrape_upcoming --sports football --from 20250101 --headless --change_sensitivity aggressive

# Conservative sensitivity - maximum data accuracy
uv run python src/main.py scrape_upcoming --sports football --from 20250101 --headless --change_sensitivity conservative
```

**What Gets Detected:**
- **New Matches**: Never-before-scraped matches
- **Unchanged Matches**: Identical odds and history (skipped)
- **Changed Current Odds**: Updated odds values (scraped)
- **New History Entries**: New odds evolution timeline entries (scraped)

- **Scrapes a date range for a single sport:**

`uv run python src/main.py scrape_upcoming --sports football --from 20250101 --to 20250107 --markets 1x2 --headless`

- **Scrapes all sports for a date range:**

`uv run python src/main.py scrape_upcoming --sports all --from 20250101 --to 20250107 --headless`

- **Scrapes all sports with limited markets for faster execution:**

`uv run python src/main.py scrape_upcoming --sports all --markets 1x2,home_away --preview_submarkets_only --headless`

- **Different date granularities for single dates:**

`uv run python src/main.py scrape_upcoming --sports football --from 20250101  # Full date`
`uv run python src/main.py scrape_upcoming --sports football --from 202501     # Entire month`
`uv run python src/main.py scrape_upcoming --sports football --from 2025       # Entire year`

- **Date range for single sport (same granularity):**

`uv run python src/main.py scrape_upcoming --sports football --from 20250101 --to 20250107  # Date range`
`uv run python src/main.py scrape_upcoming --sports football --from 202501 --to 202503      # Month range`
`uv run python src/main.py scrape_upcoming --sports football --from 2024 --to 2025          # Year range`

- **Flexible date defaults and unlimited ranges:**

`uv run python src/main.py scrape_upcoming --sports football --from now          # From today to unlimited future`
`uv run python src/main.py scrape_upcoming --sports football --to now            # From unlimited past to today`
`uv run python src/main.py scrape_upcoming --sports football --from 20250101     # From specific date to unlimited future`
`uv run python src/main.py scrape_upcoming --sports football                        # Defaults to now with unlimited future`

- **League-focused scraping (dates bypassed):**

`uv run python src/main.py scrape_upcoming --sports football --leagues england-premier-league --markets 1x2  # All Premier League matches, dates ignored`
`uv run python src/main.py scrape_upcoming --sports football --leagues england-premier-league,spain-laliga --from 20250101  # Leagues prioritized, dates optional`

- **Large date ranges (no limits):**

`uv run python src/main.py scrape_upcoming --sports football --from 20240101 --to 20251231     # Full year range`
`uv run python src/main.py scrape_upcoming --sports football --from 20200101 --to 20251231     # 5-year range for comprehensive data collection`
`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2000 --to 2024  # 24-year historical range`

#### **2. Scrape Historical Odds**

Retrieve historical odds and results for analytical purposes.

**Options**:

| 🏷️ Option                   | 📝 Description                                                                                                        | 🔐 Required | 🔧 Default     |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----------- | -------------- |
| `--sports`                   | Specify the sport(s) to scrape. Use `all` for all 23 supported sports, or specify a sport (e.g., `football`, `ice-hockey`, `baseball`). | ✅          | None           |
| `--leagues`                 | Comma-separated leagues to scrape, or `all` for all leagues (e.g., `england-premier-league,spain-laliga`).              | ✅          | None           |
| `--from`                    | Start season/year in `YYYY`, `YYYY-YYYY` format, or `now` for current year (e.g., `2023`, `2022-2023`, `now`). Optional with `--leagues` or defaults to unlimited past. | ✅          | None           |
| `--to`                      | End season/year in `YYYY`, `YYYY-YYYY` format, or `now` for current year. If not provided, defaults to `--from` season or unlimited past. | ❌          | None           |
| `--markets`                 | Comma-separated betting markets, or `all` for auto-discovered markets (e.g., `1x2,btts,over_under`). Uses intelligent market auto-discovery to find all available markets for the sport. | ❌          | None           |
| `--storage`                 | Save data locally or to a remote S3 bucket (`local` or `remote`).                                                     | ❌          | `local`        |
| `--file_path`               | File path to save data locally (e.g., `output.json`).                                                                 | ❌          | None           |
| `--format`                  | Format for saving local data (`json` or `csv`).                                                                       | ❌          | None           |
| `--max_pages`               | Maximum number of pages to scrape.                                                                                    | ❌          | None           |
| `--headless`                | Run the browser in headless mode (`True` or `False`).                                                                 | ❌          | `False`        |
| `--save_logs`               | Save logs for debugging purposes (`True` or `False`).                                                                 | ❌          | `False`        |
| `--proxies`                 | List of proxies in `"server user pass"` format. Multiple proxies supported.                                           | ❌          | None           |
| `--browser_user_agent`      | Custom user agent string for browser requests.                                                                        | ❌          | None           |
| `--browser_locale_timezone` | Browser locale timezone (e.g., `fr-BE`).                                                                              | ❌          | None           |
| `--browser_timezone_id`     | Browser timezone ID (e.g., `Europe/Brussels`).                                                                        | ❌          | None           |
| `--match_links`             | List of specific match links to scrape (overrides other filters).                                                     | ❌          | None           |
| `--target_bookmaker`        | Filter scraping for a specific bookmaker (e.g., `Betclic.fr`).                                                        | ❌          | None           |
| `--odds_format`             | Odds format to display (`Decimal Odds`, `Fractional Odds`, `Money Line Odds`, `Hong Kong Odds`).                      | ❌          | `Decimal Odds` |
| `--concurrency_tasks`       | Number of concurrent tasks for scraping.                                                                              | ❌          | `3`            |
| `--preview_submarkets_only` | Only scrape average odds from visible submarkets without loading individual bookmaker details (faster, limited data). | ❌          | `False`        |
| `--change_sensitivity`      | Duplicate detection sensitivity level: `aggressive`, `normal`, `conservative`.                                              | ❌          | `normal`       |


#### **Example Usage:**

- **Retrieve historical odds for the Premier League's 2022-2023 season:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2022-2023 --markets 1x2 --headless`

- **Retrieve historical odds for multiple leagues at once:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league,spain-laliga,italy-serie-a --from 2022-2023 --markets 1x2 --headless`

- **Retrieve historical odds for the current season of Premier League:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from now --markets 1x2 --headless`

- **Retrieve historical MLB 2022 season data:**

`uv run python src/main.py scrape_historic --sports baseball --leagues mlb --from 2022 --markets home_away --headless`

- **Scrapes only 3 pages of historical odds data:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2022-2023 --markets 1x2 --max_pages 3 --headless`

- **Scrapes historical odds in preview mode (average odds only, faster):**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2022-2023 --markets over_under_2_5 --preview_submarkets_only --headless`

- **Scrapes historical odds for all 23 sports for the 2023 season (discovers all leagues dynamically):**

`uv run python src/main.py scrape_historic --sports all --from 2023 --headless`

- **Scrapes historical odds for all sports for 2022-2023 season with limited pages:**

`uv run python src/main.py scrape_historic --sports all --from 2022-2023 --max_pages 5 --headless`

- **Scrapes all sports in preview mode for faster comprehensive data collection:**

`uv run python src/main.py scrape_historic --sports all --from now --markets 1x2,home_away --preview_submarkets_only --headless`

- **Single season (replaces --season parameter):**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2023 --to 2023`
`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2022-2023 --to 2022-2023  # Replaces 2022-2023 season format`

- **Multi-season range for single sport:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2021 --to 2023`

- **All sports for single season:**

`uv run python src/main.py scrape_historic --sports all --from 2023 --to 2023`

- **All sports for multi-season range:**

`uv run python src/main.py scrape_historic --sports all --from 2021 --to 2023`

- **Using 'now' keyword for historical matches:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 2023 --to now  # From specific season to current`
`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from now --to 2023  # From current season back to 2023 (auto-swapped)`
`uv run python src/main.py scrape_historic --sports all --from now --to now  # Current season only`

- **Unlimited historical data collection (no year limits):**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from 1990 --to 2024  # 34-year complete history`
`uv run python src/main.py scrape_historic --sports all --from 2000 --to 2024  # 24-year data for all sports`
`uv run python src/main.py scrape_historic --sports basketball --leagues nba --from 1980  # From 1980 to present (unlimited)`

- **Exact Seasons Optimization Examples:**

`uv run python src/main.py scrape_historic --sports all --from now  # Discovers exact seasons for each league (Africa Cup: 2008,2010,2012,2013,2015,2017,2019,2021,2023,2025)`
`uv run python src/main.py scrape_historic --sports football --leagues africa-cup-of-nations --from now  # Only attempts 10 actual seasons vs 27 arbitrary years (63% improvement)`

- **Enhanced Season Auto-Discovery**: For `--sports all` mode (no dates specified), automatically discovers all exact available seasons for each league, providing complete historical coverage without manual season specification.
- **Exact Season Optimization**: Only attempts seasons that actually exist on league pages, eliminating 30-80% of failed requests for tournaments with irregular schedules.

- **Flexible defaults for historical matches:**

`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --from now          # Current season to unlimited past`
`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league --to now            # Unlimited past to current season`
`uv run python src/main.py scrape_historic --sports football --leagues england-premier-league                      # Current season only (no dates needed)`
`uv run python src/main.py scrape_historic --sports all --from 2023                                                     # 2023 season to current for all sports`
`uv run python src/main.py scrape_historic --sports all --to 2023                                                       # Unlimited past to 2023 for all sports`

#### **📌 Preview Mode**

The `--preview_submarkets_only` flag enables a faster scraping mode that extracts only average odds from visible submarkets without loading individual bookmaker details. This mode is useful for:

- **Quick exploration** of available submarkets and their average odds
- **Testing** data structure and format
- **Light monitoring** with reduced resource usage

**Preview Mode vs Full Mode:**

| Aspect           | Full Mode                   | Preview Mode                  |
| ---------------- | --------------------------- | ----------------------------- |
| **Speed**        | Slower (interactive)        | Faster (passive)              |
| **Data**         | All submarkets + bookmakers | Visible submarkets + avg odds |
| **Bookmakers**   | Individual bookmaker odds   | Average odds only             |
| **Odds History** | Available                   | Not available                 |
| **Structure**    | By bookmaker                | By submarket (avg odds)       |

#### **📌 Running the Help Command:**

To display all available CLI commands and options, run:

`uv run python src/main.py --help`

### **🐳 Running Inside a Docker Container**

OddsHarvester is compatible with Docker, allowing you to run the application seamlessly in a containerized environment.

**Steps to Run with Docker:**

1. **Ensure Docker is Installed**
   Make sure Docker is installed and running on your system. Visit [Docker's official website](https://www.docker.com/) for installation instructions specific to your operating system.

2. **Build the Docker Image**
   Navigate to the project's root directory, where the `Dockerfile` is located. The project uses a multi-stage Docker build with different targets:

   - **For local development/testing**: `docker build -t odds-harvester:local --target local-dev .`
   - **For AWS Lambda deployment**: `docker build -t odds-harvester:lambda --target aws-lambda .`

3. **Run the Container**
   Start a Docker container based on the built image. Pass any CLI arguments (e.g., `scrape_upcoming`) as part of the Docker run command:

   ```bash
   docker run --rm odds-harvester:local python3 -m src.main scrape_upcoming --sports football --from 20250903 --markets 1x2 --storage local --file_path output.json --headless
   ```

4. **Interactive Mode for Debugging**
   If you need to debug or run commands interactively:
   ```bash
   docker run --rm -it odds-harvester:local /bin/bash
   ```

**Tips**:

- **Volume Mapping**: Use volume mapping to store logs or output data on the host machine.
- **Container Reusability**: Assign a unique container name to avoid conflicts when running multiple instances.

### **☁️ Cloud Deployment**

OddsHarvester can also be deployed on a cloud provider using the **Serverless Framework**, with a Docker image to ensure compatibility with AWS Lambda (Dockerfile will need to be tweaked if you want to deploy on a different cloud provider).

**Why Use a Docker Image?**

1. AWS Lambda's Deployment Size Limit:
   AWS Lambda has a hard limit of 50MB for direct deployment packages, which includes code, dependencies, and assets. Playwright and its browser dependencies far exceed this limit.

2. Playwright's Incompatibility with Lambda Layers:
   Playwright cannot be installed as an AWS Lambda layer because:
   • Its browser dependencies require system libraries that are unavailable in Lambda's standard runtime environment.
   • Packaging these libraries within Lambda layers would exceed the layer size limit.

3. Solution:
   Using a Docker image solves these limitations by bundling the entire runtime environment, including Playwright, its browsers, and all required libraries, into a single package. This ensures a consistent and compatible execution environment.

**Serverless Framework Setup:**

1. **Serverless Configuration**:
   The application includes a `serverless.yaml` file located at the root of the project. This file defines the deployment configuration for a serverless environment. Users can customize the configuration as needed, including:

   - **Provider**: Specify the cloud provider (e.g., AWS).
   - **Region**: Set the desired deployment region (e.g., `eu-west-3`).
   - **Resources**: Update the S3 bucket details or permissions as required.

2. **Docker Integration**:
   The app uses a Docker image (`playwright_python_arm64`) to ensure compatibility with the serverless architecture. The Dockerfile is already included in the project and configured in `serverless.yaml`.
   You'll need to build the image locally (see section above) and push the Docker image to ECR.

3. **Permissions**:
   By default, the app is configured with IAM roles to:

   - Upload (`PutObject`), retrieve (`GetObject`), and delete (`DeleteObject`) files from an S3 bucket.
     Update the `Resource` field in `serverless.yaml` with the ARN of your S3 bucket.

4. **Function Details**:
   - **Function Name**: `scanAndStoreOddsPortalDataV2`
   - **Memory Size**: 2048 MB
   - **Timeout**: 360 seconds
   - **Event Trigger**: Runs automatically every 2 hours (`rate(2 hours)`) via EventBridge.

**Customizing Your Configuration:**
To tailor the serverless deployment for your needs:

- Open the `serverless.yaml` file in the root directory.
- Update the relevant fields:
  - S3 bucket ARN in the IAM policy.
  - Scheduling rate for the EventBridge trigger.
  - Resource limits (e.g., memory size or timeout).

**Deploying to your prefered Cloud provider:**

1. Install the Serverless Framework:
   - Follow the installation guide at [Serverless Framework](https://www.serverless.com/).
2. Deploy the application:
   - Use the `sls deploy` command to deploy the app to your cloud provider.
3. Verify the deployment:
   - Confirm that the function is scheduled correctly and check logs or S3 outputs.

## **🧪 Testing & Quality Assurance**

OddsHarvester maintains **comprehensive test coverage** with **700+ passing tests** ensuring robust functionality across all features.

### **📊 Test Coverage Overview**

| **Category** | **Test Files** | **Coverage** | **Status** |
|--------------|----------------|---------------|------------|
| **Universal Auto-Discovery** | 3 files | ✅ Complete | **NEW** |
| **Dynamic Discovery** | 2 files | ✅ Complete | Enhanced |
| **CLI Integration** | 4 files | ✅ Complete | Validated |
| **Core Functionality** | 8 files | ✅ Complete | Robust |
| **Error Handling** | 1 file | ✅ Complete | **NEW** |
| **Integration Tests** | 3 files | ✅ Complete | Enhanced |
| **Sport Market Constants** | 1 file | ✅ Complete | Valid |

### **🚀 Universal Market Auto-Discovery**

The universal market auto-discovery system eliminates hardcoded market defaults and makes intelligent market discovery the default behavior.

#### **🔬 Test Coverage for Universal Auto-Discovery:**

**Core Functionality Tests:**
- ✅ Universal auto-discovery with caching
- ✅ Market discovery success/failure scenarios
- ✅ League integration for better sample match finding
- ✅ Debug logging and performance monitoring

**Integration Tests:**
- ✅ End-to-end historic scraping with auto-discovery
- ✅ End-to-end upcoming matches with auto-discovery
- ✅ Explicit markets override behavior
- ✅ `--markets all` compatibility preserved
- ✅ Match links integration scenarios

**Error Handling Tests:**
- ✅ Network timeout and connectivity issues
- ✅ Navigation failures and page structure changes
- ✅ Proxy connection problems
- ✅ Empty discovery results handling
- ✅ Enhanced error messages with troubleshooting guidance

#### **🧪 Running Tests:**

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/core/test_universal_market_auto_discovery.py
uv run pytest tests/integration/test_universal_auto_discovery_integration.py
uv run pytest tests/core/test_enhanced_error_handling.py

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific error handling tests
uv run pytest tests/core/test_enhanced_error_handling.py -v
```

### **🔍 Test Structure Overview**

```
tests/
├── core/
│   ├── test_universal_market_auto_discovery.py     # NEW: Universal auto-discovery
│   ├── test_enhanced_error_handling.py             # NEW: Enhanced error scenarios
│   ├── test_scraper_app_dynamic_discovery.py       # Dynamic discovery integration
│   ├── test_url_builder_dynamic_discovery.py       # URL builder discovery
│   └── test_scraper_app.py                        # Core scraper functionality
├── integration/
│   ├── test_universal_auto_discovery_integration.py # NEW: End-to-end integration
│   ├── test_aussie_rules_integration.py            # Sport-specific integration
│   └── test_duplicate_detection_integration.py      # Data quality integration
├── cli/
│   ├── test_cli_argument_parser.py                 # CLI argument parsing
│   ├── test_cli_validation_integration.py           # CLI validation flow
│   └── test_cli_argument_handler.py                # CLI argument handling
└── utils/
    └── test_sport_market_constants.py              # Sport market validation
```

### **🛡️ Quality Assurance Features**

**Automated Testing:**
- ✅ **700+ Unit Tests** covering all functionality
- ✅ **Integration Tests** for end-to-end scenarios
- ✅ **Error Handling Tests** for robust failure scenarios
- ✅ **Continuous Integration** with GitHub Actions
- ✅ **Code Coverage Reporting** with Codecov

**Test-Driven Development:**
- ✅ All new features developed with comprehensive test coverage
- ✅ Regression tests prevent breaking changes
- ✅ Edge cases and error scenarios thoroughly tested
- ✅ Performance tests for caching and optimization

### **🐛 Troubleshooting Common Issues**

#### **Market Discovery Issues:**

**Problem:** `No markets discovered for sport 'X'`

**Solutions:**
1. **Verify Sport Name:** Ensure the sport name matches OddsPortal's naming convention
2. **Check Network:** Verify internet connectivity and proxy settings
3. **Site Availability:** Check if oddsportal.com is accessible
4. **Try Specific Markets:** Use `--markets 1x2` to test basic functionality

```bash
# Debug market discovery
uv run python src/main.py scrape_upcoming --sports football --markets all --headless

# Try specific markets if auto-discovery fails
uv run python src/main.py scrape_upcoming --sports football --markets 1x2 --headless
```

**Problem:** `Timeout occurred during market discovery`

**Solutions:**
1. **Increase Timeout:** Use longer timeout settings
2. **Check Proxy:** Verify proxy configuration
3. **Network Stability:** Ensure stable internet connection
4. **Try Different Sport:** Test with a more popular sport

#### **Performance Issues:**

**Problem:** Slow scraping performance

**Solutions:**
1. **Use Caching:** Markets are cached per sport after first discovery
2. **Limit Scope:** Use specific leagues instead of `--leagues all`
3. **Preview Mode:** Use `--preview_submarkets_only` for faster results
4. **Concurrent Tasks:** Adjust `--concurrency_tasks` for optimal performance

### **📈 Continuous Quality Monitoring**

- **✅ GitHub Actions:** Automated testing on every push/PR
- **✅ Code Coverage:** 95%+ coverage maintained across all modules
- **✅ Scraper Health Checks:** Live testing against oddsportal.com
- **✅ Performance Monitoring:** Memory usage and execution time tracking
- **✅ Error Rate Monitoring:** Failed request tracking and alerting

---

## **🤝 Contributing**

Contributions are welcome! If you have ideas, improvements, or bug fixes, feel free to submit an issue or a pull request. Please ensure that your contributions follow the project's coding standards and include clear descriptions for any changes.

**Testing Requirements for Contributions:**
- Add comprehensive tests for new features
- Ensure all existing tests pass
- Maintain code coverage standards
- Include integration tests for major changes

## **☕ Donations**

If you find this project useful and would like to support its development, consider buying me a coffee! Your support helps keep this project maintained and improved.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/pownedj)

## **📜 License**

This project is licensed under the MIT License - see the [LICENSE](./LICENSE.txt) file for more details.

## **💬 Feedback**

Have any questions or feedback? Feel free to reach out via the issues tab on GitHub. We'd love to hear from you!

## **❗ Disclaimer**

This package is intended for educational purposes only and not for any commercial use in any way. The author is not affiliated with or endorsed by the oddsportal.com website. Use this application responsibly and ensure compliance with the terms of service of oddsportal.com and any applicable laws in your jurisdiction.
