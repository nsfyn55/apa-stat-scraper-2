# APA Stat Scraper

A CLI application for extracting player statistics from the APA (American Poolplayers Association) website poolplayers.com.

## Features

- **Session Management**: Persistent authentication with automatic session handling
- **Notification Handling**: Automatically dismisses notification dialogues
- **CLI Interface**: Easy-to-use command-line interface with multiple actions
- **Team Scraping**: Extract player statistics from team pages (coming soon)

## Installation

### Prerequisites
- Python 3.13.6 (recommended)
- pyenv (for Python version management)

### Setup

1. **Create and activate virtual environment:**
```bash
# Create virtual environment
pyenv virtualenv 3.13.6 apa-stat-scraper-2

# Set local Python version for this project
pyenv local apa-stat-scraper-2

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

### Login
Establish a session with the APA website:
```bash
python app.py login
```

### Verify Session
Check if your current session is valid:
```bash
python app.py verify-session
```

### Help
Get help on available commands:
```bash
python app.py --help
```

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

- **Browser settings**: headless mode, timeout, user agent
- **Session settings**: persistence, timeout
- **Scraping settings**: delays, retries, timeouts
- **Output settings**: format, timestamps, backups
- **Logging settings**: level, file size, rotation

## Virtual Environment Management

This project uses pyenv for Python version management and virtual environments:

### Commands
```bash
# Check current Python version
python --version

# List available Python versions
pyenv versions

# List virtual environments
pyenv virtualenvs

# Activate virtual environment (if not using pyenv local)
pyenv activate apa-stat-scraper-2

# Deactivate virtual environment
pyenv deactivate

# Remove virtual environment (if needed)
pyenv virtualenv-delete apa-stat-scraper-2
```

### Project Structure
- `.python-version` file automatically sets the Python version for this project
- Virtual environment: `apa-stat-scraper-2` (Python 3.13.6)
- Dependencies isolated from system Python

## Development

The application follows a modular structure:
- `app.py`: Main CLI entry point with argument parsing
- `actions/`: Python submodules for different CLI actions
- `session_manager.py`: Handles browser automation and session persistence
- `config.py`: LSB-compliant configuration management
- `logger.py`: LSB-compliant logging system

## Future Actions

Additional actions will be added for:
- Team member statistics extraction
- Match history scraping
- Data export to CSV/JSON formats
