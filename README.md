# APA Stat Scraper

A powerful CLI application for extracting player statistics from the APA (American Poolplayers Association) website poolplayers.com. Built for billiards enthusiasts who want to analyze competitor statistics and team performance data.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Zsh Tab Completion](#zsh-tab-completion)
- [Usage](#usage)
  - [Command Line Usage](#command-line-usage)
- [Actions](#actions)
  - [Login](#login)
  - [Verify Session](#verify-session)
  - [Clear State](#clear-state)
  - [Extract Player](#extract-player)
  - [Extract Team](#extract-team)
  - [Cache Manage](#cache-manage)
- [Development](#development)
  - [Caching System](#caching-system)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Setup](#setup)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
    - [Configuration Options](#configuration-options)
    - [Configuration Categories](#configuration-categories)
  - [Virtual Environment Management](#virtual-environment-management)
  - [Adding New Actions](#adding-new-actions)
- [FAQ](#faq)
  - [What should I do if I get "No valid session found"?](#what-should-i-do-if-i-get-no-valid-session-found)
  - [How do I fix browser issues?](#how-do-i-fix-browser-issues)
  - [How do I resolve configuration issues?](#how-do-i-resolve-configuration-issues)
  - [How do I fix virtual environment issues?](#how-do-i-fix-virtual-environment-issues)
  - [How do I view application logs?](#how-do-i-view-application-logs)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **🔐 Session Management**: Persistent authentication with automatic session handling
- **🔔 Notification Handling**: Automatically dismisses notification dialogues
- **⚡ CLI Interface**: Easy-to-use command-line interface with multiple actions
- **📦 Binary Installation**: Install as a system binary for easy access from anywhere
- **🖥️ Headless by Default**: Runs in headless mode by default for better performance and automation
- **👤 Player Extraction**: Extract individual player statistics and information from player pages
- **📊 Team Extraction**: Extract team statistics and player data from team pages
- **💾 Smart Caching**: 12-hour intelligent caching system with separate cache for expanded/unexpanded data
- **🔄 Retry Logic**: Automatic retry mechanism for timeout errors and network issues
- **💾 Data Export**: Export statistics to CSV and JSON formats
- **📈 Analytics Ready**: Structured data perfect for analysis and visualization
- **🔒 LSB Compliant**: Follows Linux Standard Base standards for configuration and state
- **🐍 Virtual Environment**: Isolated Python environment using venv

## Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd apa-stat-scraper-2

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install

# Login to APA site
apa-stat-scraper login

# Verify session
apa-stat-scraper verify-session

# Extract player data (interactive mode)
apa-stat-scraper extract-player

# Extract team data (uses intelligent caching)
apa-stat-scraper extract-team --team-id 12821920

# Extract team data with fresh data (skip cache)
apa-stat-scraper extract-team --team-id 12821920 --no-cache
```

## Installation

The APA Stat Scraper provides a convenient binary interface that can be installed system-wide or added to your PATH.

### Option 1: Add to PATH (Recommended)

Add the project directory to your shell PATH:
```bash
# Add to your shell configuration
echo 'export PATH="$HOME/src/apa-stat-scraper-2:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: System-wide Installation
```bash
# Copy binary to system directory
sudo cp apa-stat-scraper /usr/local/bin/
```

### Option 3: User Bin Directory
```bash
# Create user bin directory and copy binary
mkdir -p ~/bin
cp apa-stat-scraper ~/bin/
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Option 4: Create Symlink
```bash
# Create symlink to system directory
sudo ln -s $(pwd)/apa-stat-scraper /usr/local/bin/apa-stat-scraper
```

After installation, you can use `apa-stat-scraper` from anywhere in your terminal.

### Zsh Tab Completion

The APA Stat Scraper includes comprehensive zsh tab completion for all actions and options, making the CLI much more user-friendly.

#### Installation

Run the completion installation script:
```bash
./utilities/install-completion.sh
```

This will install the completion script to `~/.zsh/completions/` and add the necessary configuration to your `~/.zshrc` file.

#### Usage

After installation, reload your shell configuration:
```bash
source ~/.zshrc
```

Then you can use tab completion:
```bash
# Complete actions
apa-stat-scraper <TAB>
# Shows: login  verify-session  clear-state  extract-player  extract-team

# Complete extract-player options
apa-stat-scraper extract-player <TAB>
# Shows: --userid  --url  --output  --format  --launch-browser  --no-terminal  --no-cache

# Complete format options
apa-stat-scraper extract-player --format <TAB>
# Shows: json  csv
```

#### Features

- **Action completion**: All available actions with descriptions
- **Option completion**: All command-line options with help text
- **Value completion**: Smart completion for specific values (formats, file paths)
- **File path completion**: Intelligent file path completion for output files
- **URL completion**: URL completion for player page URLs

## Usage

### Command Line Usage
```bash
# Show all available actions
apa-stat-scraper --help

# Get help for specific action
apa-stat-scraper <action> --help
```

### Actions

### Login

**Description**: Establishes an authenticated session with the APA website. This action handles the complete login flow including form submission, authorization page navigation, and notification dismissal.

**Features**:
- Interactive credential prompting if not provided
- Multi-step authentication flow (login → authorization → dashboard)
- Automatic notification dialogue handling
- Persistent session storage for future use
- Headless operation by default for automation
- Visual debugging mode available
- Automatic retry logic for network issues

**Options**:
- `--email` (optional): Your APA website email address
  - **Input**: Email string
  - **Behavior**: Uses provided email for authentication, skips interactive prompt
- `--password` (optional): Your APA website password
  - **Input**: Password string
  - **Behavior**: Uses provided password for authentication, skips interactive prompt
- `--headless` (optional): Run in headless mode (default behavior)
  - **Behavior**: Runs browser without visible window for automation
- `--launch-browser` (optional): Launch browser in visible mode for debugging
  - **Behavior**: Opens browser window to show login process, useful for debugging

**Sample Commands**:
```bash
# Interactive login (will prompt for credentials)
apa-stat-scraper login

# Login with credentials provided
apa-stat-scraper login --email your@email.com --password yourpassword

# Login in headless mode (no browser window)
apa-stat-scraper login --headless

# Get help for login action
apa-stat-scraper login --help
```

### Verify Session

**Description**: Checks if the current session is valid and can access the APA dashboard. This action verifies authentication without requiring new credentials.

**Features**:
- Non-destructive session verification
- Uses existing session data from previous login
- Dashboard access verification
- Automatic notification dialogue handling
- Detailed session status reporting
- No credential input required

**Options**:
- `--headless` (optional): Run in headless mode (default behavior)
  - **Behavior**: Runs browser without visible window, verifies session access
- `--launch-browser` (optional): Launch browser in visible mode for debugging
  - **Behavior**: Opens browser window to show session verification process

**Sample Commands**:
```bash
# Check session status
apa-stat-scraper verify-session

# Check session in headless mode
apa-stat-scraper verify-session --headless

# Get help for verify-session action
apa-stat-scraper verify-session --help
```

### Clear State

**Description**: Clears all browser data, logs, cache, and temporary files. This action resets the application to a clean state, requiring re-authentication.

**Features**:
- Complete application state reset
- Browser data cleanup (cookies, cache, local storage)
- Application logs and cache clearing
- Temporary file removal
- Directory structure recreation
- Interactive confirmation for safety
- Non-destructive to configuration files

**Options**:
- `--confirm` (optional): Skip confirmation prompt and clear state immediately
  - **Behavior**: Immediately clears all state data without asking for confirmation
- No additional options available (confirmation required by default for safety)
  - **Behavior**: Prompts user to confirm before clearing all state data

**Sample Commands**:
```bash
# Clear state with confirmation prompt
apa-stat-scraper clear-state

# Clear state without confirmation
apa-stat-scraper clear-state --confirm

# Get help for clear-state action
apa-stat-scraper clear-state --help
```

### Extract Player

**Description**: Extracts player statistics and information from a specific player's team page on the APA website. This action can be used with either a player URL or by providing a UserId directly. It navigates to the player page, automatically clicks on the Teams tab, and extracts available data including player name, team information, current teams, past teams (with automatic scrolling to load additional data), and statistics. Data is displayed in a clean tabular format in the terminal using standard Python libraries. The system includes robust retry logic to handle timeout errors and network issues automatically.

**Features**:
- Interactive UserId prompting if not provided
- Support for both UserId and URL input methods
- Automatic Teams tab navigation and content loading
- Comprehensive player data extraction (current and past teams)
- Automatic scrolling to load additional past teams data
- Robust retry logic for timeout errors and network issues
- Multiple output formats (terminal display, JSON, CSV)
- League-specific data extraction
- Session-based authentication (no re-login required)

**Options**:
- `--userid` (optional): Player's UserId for direct lookup
  - **Input**: Numeric UserId string (e.g., "3287288")
  - **Behavior**: Directly navigates to player page using UserId, skips interactive prompt
- `--url` (optional): Full player URL for extraction
  - **Input**: Complete URL string (e.g., "https://league.poolplayers.com/Philadelphia/member/3287288")
  - **Behavior**: Parses URL to extract UserId and league, then processes player data
- `--league` (optional): Override default league setting
  - **Input**: League name string (e.g., "Philadelphia", "Los Angeles")
  - **Behavior**: Uses specified league instead of config default, affects URL construction
- `--output` (optional): Save extracted data to file
  - **Input**: File path string (e.g., "player_data.json", "data.csv")
  - **Behavior**: Saves data to specified file in addition to terminal display
- `--format` (optional): Output format for saved data
  - **Input**: Format string ("json" or "csv")
  - **Behavior**: Controls how data is formatted when saved to file
  - **Sample Output**: JSON format preserves all data structure, CSV format creates tabular data
- `--no-terminal` (optional): Suppress terminal output
  - **Behavior**: Hides formatted table output, useful for automated processing
- `--no-cache` (optional): Skip cache and force fresh data extraction
  - **Behavior**: Bypasses cache system and extracts fresh data from website
- `--launch-browser` (optional): Show browser window for debugging
  - **Behavior**: Opens browser window to show data extraction process

**Note**: The UserId is an internal identifier used by the APA system and does not reflect the player's skill level, team number, or any other visible player information. You can obtain UserIds for players by using the `extract-team` action, which displays the UserId for each team member.

**Sample Commands**:
```bash
# Interactive mode - will prompt for UserId
apa-stat-scraper extract-player

# Using UserId directly
apa-stat-scraper extract-player --userid 3287288 --league "Philadelphia"

# Using URL (supports both new and legacy formats)
apa-stat-scraper extract-player --url "https://league.poolplayers.com/Philadelphia/member/3287288"

# Extract and save to JSON file (with terminal display)
apa-stat-scraper extract-player --userid 3287288 --league "Philadelphia" --output player_data.json

# Extract and save to CSV file (suppress terminal output)
apa-stat-scraper extract-player --userid 3287288 --league "Los Angeles" --output player_data.csv --format csv --no-terminal

# Extract with browser window visible
apa-stat-scraper extract-player --userid 3287288 --league "Chicago" --launch-browser

# Extract with fresh data (skip cache)
apa-stat-scraper extract-player --userid 3287288 --no-cache

# Get help for extract-player action
apa-stat-scraper extract-player --help
```

### Extract Team

**Description**: Extracts team statistics and player data from a specific team page on the APA website. This action navigates to the team page and extracts comprehensive team information including all team members with their statistics, skill levels, match records, and performance metrics. The data is displayed in a clean tabular format showing player names, member IDs, UserIds (for individual player lookups), skill levels, match records, win percentages, PPM (Points Per Match), and PA (Points Against) values. The optional --expand parameter provides additional detailed statistics by recursively visiting each player's individual page to extract min_rank, max_rank, and seasons_played data. The system includes robust retry logic to handle timeout errors and network issues automatically.

**Features**:
- Comprehensive team roster extraction
- Player statistics and performance metrics
- Optional detailed player history expansion
- Robust retry logic for timeout errors and network issues
- Multiple output formats (terminal display, JSON, CSV)
- League-specific team data extraction
- Session-based authentication (no re-login required)
- Automatic notification dialogue handling
- Team ID reference in output headers

**Options**:
- `--team-id` (required): Team identifier for data extraction
  - **Input**: Numeric team ID string (e.g., "12821920")
  - **Behavior**: Constructs team page URL and extracts all player data from roster table
- `--league` (optional): Override default league setting
  - **Input**: League name string (e.g., "Philadelphia", "Los Angeles")
  - **Behavior**: Uses specified league instead of config default, affects URL construction
- `--expand` (optional): Extract detailed player statistics
  - **Behavior**: Recursively visits each player's individual page to extract detailed statistics
  - **Sample Output**: See "With --expand parameter" section below for enhanced table format
- `--output` (optional): Save extracted data to file
  - **Input**: File path string (e.g., "team_data.json", "roster.csv")
  - **Behavior**: Saves data to specified file in addition to terminal display
- `--format` (optional): Output format for saved data
  - **Input**: Format string ("json" or "csv")
  - **Behavior**: Controls how data is formatted when saved to file
  - **Sample Output**: JSON format preserves all data structure, CSV format creates tabular data
- `--no-terminal` (optional): Suppress terminal output
  - **Behavior**: Hides formatted table output, useful for automated processing
- `--no-cache` (optional): Skip cache and force fresh data extraction
  - **Behavior**: Bypasses cache system and extracts fresh data from website
- `--launch-browser` (optional): Show browser window for debugging
  - **Behavior**: Opens browser window to show team data extraction process

**Sample Commands**:
```bash
# Extract team data with team ID
apa-stat-scraper extract-team --team-id 12821920

# Extract team data with specific league
apa-stat-scraper extract-team --team-id 12821920 --league "Philadelphia"

# Extract with expanded player statistics (min_rank, max_rank, seasons_played)
apa-stat-scraper extract-team --team-id 12821920 --expand

# Extract and save to JSON file (with terminal display)
apa-stat-scraper extract-team --team-id 12821920 --output team_data.json

# Extract and save to CSV file (suppress terminal output)
apa-stat-scraper extract-team --team-id 12821920 --output team_data.csv --format csv --no-terminal

# Extract with browser window visible
apa-stat-scraper extract-team --team-id 12821920 --launch-browser

# Extract with fresh data (skip cache)
apa-stat-scraper extract-team --team-id 12821920 --no-cache

# Extract expanded data with fresh data (skip cache)
apa-stat-scraper extract-team --team-id 12821920 --expand --no-cache

# Get help for extract-team action
apa-stat-scraper extract-team --help
```

**Output Format**:
The extract-team action displays team data in a clean table format:

**Standard Output:**
```
📊 TEAM PLAYERS - Team ID: 12821920 (8 player(s)):
------------------------------------------------------------------------------------------------------------------------
Player Name          | Member ID  | UserId     | Skill Level | Matches Won/Played | Win %  | PPM    | PA    
------------------------------------------------------------------------------------------------------------------------
Art Carey            | 19100348   | 2762169    | 7           | 1/2                | 50.0%  | 9.0    | 45.0  
Stephen McDonald     | 19162437   | 3287288    | 6           | 2/3                | 66.7%  | 8.3    | 41.7  
...
```

**With --expand parameter:**
```
📊 TEAM PLAYERS - Team ID: 12821920 (8 player(s)):
-----------------------------------------------------------------------------------------------------------------------------------------------------------
Player Name          | Member ID  | UserId     | Skill Level | Matches Won/Played | Win %  | PPM    | PA     | Min Skill | Max Skill | Seasons
-----------------------------------------------------------------------------------------------------------------------------------------------------------
Art Carey            | 19100348   | 2762169    | 7           | 1/2                | 50.0%  | 9.0    | 45.0   | 6         | 7         | 3      
Stephen McDonald     | 19162437   | 3287288    | 3           | 1/1                | 100.0  | 15.0   | 75.0   | 2         | 4         | 3      
...
```

### Cache Manage

**Description**: Manages the application cache system including viewing statistics, clearing cache entries, and cleaning up expired files. This action provides comprehensive cache management functionality through a unified command-line interface.

**Features**:
- View detailed cache statistics and usage information
- Clear all cache files or specific cache entries
- Clean up expired cache files automatically
- Support for both player and team cache management
- LSB-compliant cache directory management
- Human-readable cache size formatting

**Options**:
- `stats`: Display cache statistics
  - **Behavior**: Shows total files, valid files, expired files, expanded/unexpanded counts, and cache directory location
- `clear --all`: Clear all cache files
  - **Behavior**: Removes all cached data files from the cache directory
- `clear --specific`: Clear specific cache entry
  - **Behavior**: Removes cache files for a specific action type and identifier
  - **Requires**: `--action-type` and `--identifier` parameters
- `cleanup`: Clean up expired cache files
  - **Behavior**: Removes cache files that have exceeded the 12-hour expiration time

**Sub-options for clear --specific**:
- `--action-type` (required): Type of action to clear cache for
  - **Input**: "player" or "team"
  - **Behavior**: Specifies which type of cached data to clear
- `--identifier` (required): Identifier to clear cache for
  - **Input**: Player ID or team ID string
  - **Behavior**: Specifies which specific cached entry to remove
- `--league` (optional): League to clear cache for
  - **Input**: League name string
  - **Behavior**: Further narrows down which cache entries to clear
- `--expand` (optional): Clear expanded cache entries only
  - **Behavior**: Only removes cache files for expanded data (with --expand flag)

**Sample Commands**:
```bash
# View cache statistics
apa-stat-scraper cache-manage stats

# Clear all cache files
apa-stat-scraper cache-manage clear --all

# Clear specific team cache
apa-stat-scraper cache-manage clear --specific --action-type team --identifier 12821920

# Clear specific player cache
apa-stat-scraper cache-manage clear --specific --action-type player --identifier 2762169

# Clear expanded team cache for specific league
apa-stat-scraper cache-manage clear --specific --action-type team --identifier 12821920 --league "Philadelphia" --expand

# Clean up expired cache files
apa-stat-scraper cache-manage cleanup
```

**Sample Output**:
```
📊 Cache Statistics
==================================================
Total cache files: 15
Valid files: 12
Expired files: 3
Expanded files: 8
Unexpanded files: 7

Cache directory: /path/to/var/apa-stat-scraper-2/cache/
Cache size: 2.3 MB
```

## Development

### Caching System

The APA Stat Scraper includes an intelligent caching system that significantly improves performance and reduces load on the APA website.

#### Features

- **12-Hour Cache Duration**: Cached data remains valid for 12 hours
- **Separate Cache Keys**: Expanded and unexpanded data are cached separately
- **Automatic Cache Management**: Cache files are automatically cleaned up when expired
- **Cache Statistics**: View cache usage and statistics
- **Skip Cache Option**: Use `--no-cache` to force fresh data extraction

#### How It Works

1. **First Request**: Data is extracted from the website and cached
2. **Subsequent Requests**: Data is served from cache if still valid
3. **Cache Expiration**: After 12 hours, cache is invalidated and fresh data is fetched
4. **Separate Caches**: 
   - `extract-team` → caches unexpanded data
   - `extract-team --expand` → caches expanded data separately

#### Cache Location

Cache files are stored in `var/apa-stat-scraper-2/cache/` following LSB standards:
- **Cache Directory**: `var/apa-stat-scraper-2/cache/`
- **File Format**: JSON files with MD5 hash names
- **Metadata**: Each cache file includes timestamp and source information

#### Cache Management

Use the `cache-manage` command to manage the application cache:

```bash
# View cache statistics
apa-stat-scraper cache-manage stats

# Clear all cache files
apa-stat-scraper cache-manage clear --all

# Clear specific cache entry
apa-stat-scraper cache-manage clear --specific --action-type team --identifier 12345

# Clean up expired cache files
apa-stat-scraper cache-manage cleanup
```

#### Cache Benefits

- **Faster Execution**: Subsequent runs use cached data (no browser automation needed)
- **Reduced Load**: Less stress on the APA website
- **Bandwidth Savings**: No need to re-download data
- **Reliability**: Works even if network is temporarily unavailable
- **Cost Efficiency**: Reduces API-like usage of the website

### Installation

#### Prerequisites
- Python 3.13.6 (recommended)

#### Setup

1. **Create and activate virtual environment:**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify Python version
python --version
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers:**
```bash
playwright install
```

4. **Verify installation:**
```bash
apa-stat-scraper --help
```

### Sample Workflow
```bash
# 1. First time setup
apa-stat-scraper login
# Enter your APA credentials when prompted

# 2. Verify everything is working
apa-stat-scraper verify-session
# Should show: "✅ SUCCESS! Dashboard is accessible"

# 3. Your session is now saved and persistent
# No need to login again unless session expires

# 4. Future sessions (coming soon)
# apa-stat-scraper scrape-team --team-id 12345678
# apa-stat-scraper export-stats --format csv --output team_stats.csv
```

### Project Structure
```
apa-stat-scraper-2/
├── app.py                 # CLI entry point
├── config.py              # Configuration management (LSB-compliant)
├── logger.py              # Logging system (LSB-compliant)
├── session_manager.py     # Session management and browser automation
├── cache_manager.py       # Intelligent caching system
├── actions/               # CLI actions
│   ├── __init__.py
│   ├── base.py           # Base action class
│   ├── login.py          # Login action
│   ├── verify_session.py # Session verification action
│   ├── clear_state.py    # Clear state action
│   ├── extract_player.py # Extract player action
│   ├── extract_team.py   # Extract team action
│   └── team_data_extractor.py # Common team data extraction logic
├── etc/                   # Configuration directory (LSB-compliant)
│   └── apa-stat-scraper-2/
│       └── config.json   # Application configuration
├── var/                   # State directory (LSB-compliant)
│   └── apa-stat-scraper-2/
│       ├── browser_data/ # Browser session data
│       ├── logs/         # Application logs
│       ├── cache/        # Application cache
│       └── tmp/          # Temporary files
├── utilities/             # Utility scripts
│   ├── _apa-stat-scraper # Zsh completion script
│   └── install-completion.sh # Completion installation script
├── requirements.txt       # Python dependencies
├── .python-version       # Python version specification
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

### Configuration

The application follows LSB (Linux Standard Base) standards for configuration and state management:

- **Configuration**: Stored in `etc/apa-stat-scraper-2/config.json`
- **State Data**: Stored in `var/apa-stat-scraper-2/` (browser data, logs, cache, temp files)
- **Logs**: Stored in `var/apa-stat-scraper-2/logs/` with automatic rotation

### League Configuration

The application supports configurable league selection for player data extraction:

- **Default League**: Set in `etc/apa-stat-scraper-2/config.json` under `league.default_league`
- **CLI Override**: Use `--league` parameter to override config default
- **Priority**: CLI parameter > config default > "Philadelphia" fallback

Example configuration:
```json
{
  "league": {
    "default_league": "Philadelphia"
  }
}
```

Supported leagues include: Philadelphia, New York, Los Angeles, Chicago, Houston, Phoenix, San Antonio, San Diego, Dallas, San Jose, Austin, Jacksonville

### Retry Logic

The application includes robust retry logic to handle common network issues and timeout errors:

- **Automatic Retries**: Up to 3 retry attempts for failed operations
- **Timeout Detection**: Automatically detects and retries timeout errors
- **Smart Delays**: Longer delays for timeout errors (3 seconds) vs other errors (2 seconds)
- **Comprehensive Coverage**: Retries apply to:
  - Player page navigation
  - Teams tab clicking
  - Team data extraction
  - Empty data scenarios

**Retry Behavior**:
- Timeout errors: 3-second delay between retries
- Other errors: 2-second delay between retries
- Maximum 3 attempts per operation
- Clear logging of retry attempts and final results
### Configuration Options

Edit `etc/apa-stat-scraper-2/config.json` to customize:
```json
{
  "browser": {
    "headless": false,
    "timeout": 30000,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
  },
  "session": {
    "persist": true,
    "timeout": 3600
  },
  "scraping": {
    "delay_between_requests": 1.0,
    "max_retries": 3,
    "timeout": 30
  },
  "output": {
    "default_format": "csv",
    "include_timestamps": true,
    "backup_previous": true
  },
  "logging": {
    "level": "INFO",
    "file": "apa-stat-scraper.log",
    "max_size": "10MB",
    "backup_count": 5
  }
}
```

### Configuration Categories

- **Browser settings**: headless mode, timeout, user agent
- **Session settings**: persistence, timeout
- **Scraping settings**: delays, retries, timeouts
- **Output settings**: format, timestamps, backups
- **Logging settings**: level, file size, rotation

### Virtual Environment Management

This project uses Python's built-in `venv` module for virtual environment management:

### Commands
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Deactivate virtual environment
deactivate

# Check if virtual environment is active
which python  # Should show path to venv/bin/python

# Remove virtual environment (if needed)
rm -rf venv  # On macOS/Linux
rmdir /s venv  # On Windows
```

### Project Structure
- Virtual environment directory: `venv/` (created locally)
- Dependencies isolated from system Python
- Cross-platform compatibility (macOS, Linux, Windows)

### Adding New Actions

The application follows a modular structure:
- `app.py`: Main CLI entry point with argument parsing
- `actions/`: Python submodules for different CLI actions
- `session_manager.py`: Handles browser automation and session persistence
- `config.py`: LSB-compliant configuration management
- `logger.py`: LSB-compliant logging system

To add a new CLI action:

1. Create a new file in `actions/` (e.g., `scrape_team.py`)
2. Inherit from `BaseAction` class
3. Implement `run()` and `_run_async()` methods
4. Add the action to `app.py` argument parser
5. Import and register in `actions/__init__.py`

## FAQ

#### What should I do if I get "No valid session found"?
```bash
# If you get "No valid session found"
apa-stat-scraper login
```

#### How do I fix browser issues?
```bash
# Reinstall Playwright browsers
playwright install

# Check browser data directory
ls -la var/apa-stat-scraper-2/browser_data/
```

#### How do I resolve configuration issues?
```bash
# Reset configuration to defaults
rm etc/apa-stat-scraper-2/config.json
apa-stat-scraper verify-session  # This will recreate default config
```

#### How do I fix virtual environment issues?
```bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

#### How do I view application logs?
```bash
# View application logs
tail -f var/apa-stat-scraper-2/logs/apa-stat-scraper.log

# Check log rotation
ls -la var/apa-stat-scraper-2/logs/
```

## Future Roadmap

### Phase 1: Core Scraping ✅
- ✅ Team member statistics extraction
- ✅ Player performance data collection
- ✅ Robust retry logic for network issues
- ✅ Team expansion with detailed player statistics
- ✅ Intelligent caching system with 12-hour duration
- Match history scraping (coming soon)

### Phase 2: Data Export ✅
- ✅ CSV export functionality
- ✅ JSON export with structured data
- ✅ Team data with expanded player statistics
- Custom field selection (coming soon)

### Phase 3: Analytics
- Player performance analysis
- Team comparison tools
- Season tracking and trends

### Phase 4: Advanced Features
- Automated reporting
- Data visualization
- Integration with external tools

## Contributing

This project follows LSB standards and best practices:

1. **Code Style**: Follow Python PEP 8 guidelines
2. **Documentation**: Update README and docstrings for new features
3. **Testing**: Test all new functionality before submitting
4. **Configuration**: Use the centralized config system
5. **Logging**: Use the logging system for all operations

## License

This project is licensed under the MIT License with additional terms specific to web scraping. See [LICENSE](LICENSE) for full details.

**Key Points:**
- Open source and free to use, modify, and distribute
- Educational and personal use encouraged
- Commercial use may violate APA website terms of service
- Users must respect APA website terms of service and rate limits
- No warranty for data accuracy or website compatibility

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the logs in `var/apa-stat-scraper-2/logs/`
3. Check the configuration in `etc/apa-stat-scraper-2/config.json`
4. Create an issue in the project repository

