# APA Stat Scraper

A powerful CLI application for extracting player statistics from the APA (American Poolplayers Association) website poolplayers.com. Built for billiards enthusiasts who want to analyze competitor statistics and team performance data.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Command Line Usage](#command-line-usage)
  - [Actions](#actions)
    - [Login](#login)
    - [Verify Session](#verify-session)
    - [Clear State](#clear-state)
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
- **📊 Team Scraping**: Extract player statistics from team pages (coming soon)
- **💾 Data Export**: Export statistics to CSV and JSON formats (coming soon)
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
python app.py login

# Verify session
python app.py verify-session
```

## Usage

### Command Line Usage

```bash
# Show all available actions
python app.py --help

# Get help for specific action
python app.py <action> --help
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
python app.py login

# Login with credentials provided
python app.py login --email your@email.com --password yourpassword

# Login in headless mode (no browser window)
python app.py login --headless

# Get help for login action
python app.py login --help
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
python app.py verify-session

# Check session in headless mode
python app.py verify-session --headless

# Get help for verify-session action
python app.py verify-session --help
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
python app.py clear-state

# Clear state without confirmation
python app.py clear-state --confirm

# Get help for clear-state action
python app.py clear-state --help
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
python app.py --help
```

### Sample Workflow

```bash
# 1. First time setup
python app.py login
# Enter your APA credentials when prompted

# 2. Verify everything is working
python app.py verify-session
# Should show: "✅ SUCCESS! Dashboard is accessible"

# 3. Your session is now saved and persistent
# No need to login again unless session expires

# 4. Future sessions (coming soon)
# python app.py scrape-team --team-id 12345678
# python app.py export-stats --format csv --output team_stats.csv
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
│   └── verify_session.py # Session verification action
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
python app.py login
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
python app.py verify-session  # This will recreate default config
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

### Phase 1: Core Scraping (Coming Soon)
- Team member statistics extraction
- Player performance data collection
- Match history scraping

### Phase 2: Data Export
- CSV export functionality
- JSON export with structured data
- Custom field selection

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

