# APA Stat Scraper

A powerful CLI application for extracting player statistics from the APA (American Poolplayers Association) website poolplayers.com. Built for billiards enthusiasts who want to analyze competitor statistics and team performance data.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Available Commands](#available-commands)
  - [Sample Workflow](#sample-workflow)
- [Capabilities](#capabilities)
  - [Current Features](#current-features)
  - [Coming Soon Features](#coming-soon-features)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
  - [Configuration Options](#configuration-options)
  - [Configuration Categories](#configuration-categories)
- [Virtual Environment Management](#virtual-environment-management)
- [Development](#development)
  - [Adding New Actions](#adding-new-actions)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
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

## Installation

### Prerequisites
- Python 3.13.6 (recommended)

### Setup

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

## Usage

### Available Commands

#### Login
Establish a session with the APA website:
```bash
# Interactive login (will prompt for credentials)
python app.py login

# Login with credentials provided
python app.py login --email your@email.com --password yourpassword

# Login in headless mode (no browser window)
python app.py login --headless
```

#### Verify Session
Check if your current session is valid:
```bash
# Check session status
python app.py verify-session

# Check session in headless mode
python app.py verify-session --headless
```

```bash
# Clear state with confirmation prompt
python app.py clear-state

# Clear state without confirmation
python app.py clear-state --confirm
```

```bash
# Clear state with confirmation prompt
python app.py clear-state

# Clear state without confirmation
python app.py clear-state --confirm
``````

#### Help
Get help on available commands:
```bash
# General help
python app.py --help

# Help for specific action
python app.py login --help
python app.py verify-session --help
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

## Capabilities

### Current Features

#### 🔐 **Authentication & Session Management**
- **Persistent Login**: Once logged in, your session is saved and reused
- **Automatic Re-authentication**: Handles session expiration gracefully
- **Notification Handling**: Automatically dismisses APA notification popups
- **Secure Storage**: Session data stored in LSB-compliant `var/` directory

#### ⚡ **CLI Interface**
- **Intuitive Commands**: Simple, memorable command structure
- **Help System**: Comprehensive help for all commands and options
- **Error Handling**: Clear error messages and troubleshooting guidance
- **Progress Feedback**: Real-time status updates during operations

#### 🔒 **LSB Compliance**
- **Configuration Management**: Centralized config in `etc/apa-stat-scraper-2/`
- **State Management**: All runtime data in `var/apa-stat-scraper-2/`
- **Logging**: Professional logging with automatic rotation
- **Clean Separation**: Code vs. state data properly separated

### Coming Soon Features

#### 📊 **Team Statistics Extraction**
```bash
# Extract all team member statistics
python app.py scrape-team --team-id 12345678

# Extract with specific options
python app.py scrape-team --team-id 12345678 --format json --output team_data.json
```

#### 💾 **Data Export**
```bash
# Export to CSV
python app.py export-stats --format csv --output team_stats.csv

# Export to JSON
python app.py export-stats --format json --output team_stats.json

# Export with custom fields
python app.py export-stats --fields name,skill_level,win_percentage,matches_played
```

#### 📈 **Analytics Features**
- **Player Performance Analysis**: Win rates, skill progression, match history
- **Team Comparison**: Compare multiple teams side-by-side
- **Season Tracking**: Track performance across different seasons
- **Custom Reports**: Generate reports with specific metrics

## Project Structure

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

## Configuration

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

## Virtual Environment Management

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

## Development

The application follows a modular structure:
- `app.py`: Main CLI entry point with argument parsing
- `actions/`: Python submodules for different CLI actions
- `session_manager.py`: Handles browser automation and session persistence
- `config.py`: LSB-compliant configuration management
- `logger.py`: LSB-compliant logging system

### Adding New Actions

To add a new CLI action:

1. Create a new file in `actions/` (e.g., `scrape_team.py`)
2. Inherit from `BaseAction` class
3. Implement `run()` and `_run_async()` methods
4. Add the action to `app.py` argument parser
5. Import and register in `actions/__init__.py`

## Troubleshooting

### Common Issues

#### Session Not Found
```bash
# If you get "No valid session found"
python app.py login
```

#### Browser Issues
```bash
# Reinstall Playwright browsers
playwright install

# Check browser data directory
ls -la var/apa-stat-scraper-2/browser_data/
```

#### Configuration Issues
```bash
# Reset configuration to defaults
rm etc/apa-stat-scraper-2/config.json
python app.py verify-session  # This will recreate default config
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

#### Logs
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