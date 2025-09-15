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
- [Development](#development)
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
- **👤 Player Extraction**: Extract individual player statistics and information from player pages
- **📊 Team Extraction**: Extract team statistics and player data from team pages
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

# Extract team data
apa-stat-scraper extract-team --team-id 12821920
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
# Shows: --team-id  --member-id  --url  --output  --format  --headless  --no-terminal

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

**Semantics**: 
- Prompts for credentials if not provided via command line
- Performs multi-step authentication (login → authorization → dashboard)
- Automatically handles notification dialogues
- Saves session data for future use
- Returns success/failure status

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

**Semantics**:
- Uses existing session data from previous login
- Navigates to dashboard to verify access
- Handles any notification dialogues
- Reports session status and current page information
- Returns success if authenticated, failure if not

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

**Semantics**:
- Removes browser session data (cookies, cache, local storage)
- Clears application logs and cache
- Deletes temporary files
- Recreates necessary directory structure
- Requires confirmation unless --confirm flag is used
- Returns success/failure status

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

**Description**: Extracts player statistics and information from a specific player's team page on the APA website. This action can be used with either a player URL or by providing team ID and member ID directly. It navigates to the player page and extracts available data including player name, team information, current teams, past teams (with automatic scrolling to load additional data), and statistics. Data is displayed in a clean tabular format in the terminal using standard Python libraries.

**Semantics**:
- Requires either a player URL or both team ID and member ID
- Supports --league parameter to specify league (overrides config default)
- If no arguments provided, will prompt for team ID and member ID interactively
- Uses existing session data from previous login
- Navigates to the specified player page
- Extracts player information, team details, current teams, and past teams
- Automatically scrolls to load additional past teams data
- Displays data in a formatted table in the terminal (can be suppressed with --no-terminal)
- Shows detailed teams summary with current and past teams information
- Handles any notification dialogues that appear
- Can save extracted data to JSON or CSV format
- Returns success/failure status with extracted data display

**Sample Commands**:
```bash
# Interactive mode - will prompt for team ID and member ID
apa-stat-scraper extract-player

# Using team ID and member ID directly
apa-stat-scraper extract-player --team-id 2336878 --member-id 2762169 --league "New York"

# Using URL (legacy method)
apa-stat-scraper extract-player --url "https://league.poolplayers.com/Philadelphia/member/2762169/2336878/teams"

# Extract and save to JSON file (with terminal display)
apa-stat-scraper extract-player --team-id 2336878 --member-id 2762169 --league "Philadelphia" --output player_data.json

# Extract and save to CSV file (suppress terminal output)
apa-stat-scraper extract-player --team-id 2336878 --member-id 2762169 --league "Los Angeles" --output player_data.csv --format csv --no-terminal

# Extract in headless mode
apa-stat-scraper extract-player --team-id 2336878 --member-id 2762169 --league "Chicago" --headless

# Get help for extract-player action
apa-stat-scraper extract-player --help
```

### Extract Team

**Description**: Extracts team statistics and player data from a specific team page on the APA website. This action navigates to the team page and extracts comprehensive team information including all team members with their statistics, skill levels, match records, and performance metrics. The data is displayed in a clean tabular format showing player names, member IDs, skill levels, match records, win percentages, PPM (Points Per Match), and PA (Points Against) values.

**Semantics**:
- Requires a team ID to construct the team page URL
- Supports --league parameter to specify league (overrides config default)
- Uses existing session data from previous login
- Navigates to the specified team page (https://league.poolplayers.com/team/{team_id})
- Extracts team information and all player statistics from the team roster table
- Displays data in a formatted table in the terminal (can be suppressed with --no-terminal)
- Shows team ID in the header for easy reference
- Handles any notification dialogues that appear
- Can save extracted data to JSON or CSV format
- Returns success/failure status with extracted team data display

**Sample Commands**:
```bash
# Extract team data with team ID
apa-stat-scraper extract-team --team-id 12821920

# Extract team data with specific league
apa-stat-scraper extract-team --team-id 12821920 --league "Philadelphia"

# Extract and save to JSON file (with terminal display)
apa-stat-scraper extract-team --team-id 12821920 --output team_data.json

# Extract and save to CSV file (suppress terminal output)
apa-stat-scraper extract-team --team-id 12821920 --output team_data.csv --format csv --no-terminal

# Extract in headless mode
apa-stat-scraper extract-team --team-id 12821920 --headless

# Get help for extract-team action
apa-stat-scraper extract-team --help
```

**Output Format**:
The extract-team action displays team data in a clean table format:
```
📊 TEAM PLAYERS - Team ID: 12821920 (8 player(s)):
------------------------------------------------------------------------------------------------------------------------
Player Name          | Member ID  | Skill Level | Matches Won/Played | Win %  | PPM    | PA    
------------------------------------------------------------------------------------------------------------------------
Art Carey            | 19100348   | 7           | 1/2                | 50.0%  | 9.0    | 45.0  
Stephen McDonald     | 19162437   | 6           | 2/3                | 66.7%  | 8.3    | 41.7  
...
```

## Development

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
├── actions/               # CLI actions
│   ├── __init__.py
│   ├── base.py           # Base action class
│   ├── login.py          # Login action
│   ├── verify_session.py # Session verification action
│   ├── clear_state.py    # Clear state action
│   ├── extract_player.py # Extract player action
│   └── extract_team.py   # Extract team action
├── etc/                   # Configuration directory (LSB-compliant)
│   └── apa-stat-scraper-2/
│       └── config.json   # Application configuration
├── var/                   # State directory (LSB-compliant)
│   └── apa-stat-scraper-2/
│       ├── browser_data/ # Browser session data
│       ├── logs/         # Application logs
│       ├── cache/        # Application cache
│       └── tmp/          # Temporary files
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
- Match history scraping (coming soon)

### Phase 2: Data Export ✅
- ✅ CSV export functionality
- ✅ JSON export with structured data
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

