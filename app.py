#!/usr/bin/env python3
"""
APA Stat Scraper CLI Application
Entry point for the command-line interface
"""

import argparse
import sys
from actions.login import LoginAction
from actions.verify_session import VerifySessionAction
from actions.clear_state import ClearStateAction
from actions.extract_player import ExtractPlayerAction
from actions.extract_team import ExtractTeamAction

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="APA Stat Scraper - Extract player statistics from poolplayers.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  apa-stat-scraper login                    # Login to APA site
  apa-stat-scraper verify-session          # Verify current session
  apa-stat-scraper clear-state             # Clear browser state and data
  apa-stat-scraper extract-player --userid 3287288 --league "Philadelphia"
  apa-stat-scraper extract-player --url "https://league.poolplayers.com/Philadelphia/member/3287288"
  apa-stat-scraper extract-team --team-id 12821920 --league "Philadelphia"
        """
    )
    
    subparsers = parser.add_subparsers(
        dest='action',
        help='Available actions',
        required=True
    )
    
    # Login action
    login_parser = subparsers.add_parser(
        'login',
        help='Login to APA site and establish session'
    )
    login_parser.add_argument(
        '--email',
        help='Email address for login (will prompt if not provided)'
    )
    login_parser.add_argument(
        '--password',
        help='Password for login (will prompt if not provided)'
    )
    login_parser.add_argument(
        '--launch-browser',
        action='store_true',
        help='Launch browser window (default: headless mode)'
    )
    
    # Verify session action
    verify_parser = subparsers.add_parser(
        'verify-session',
        help='Verify current session can access dashboard'
    )
    verify_parser.add_argument(
        '--launch-browser',
        action='store_true',
        help='Launch browser window (default: headless mode)'
    )
    
    # Clear state action
    clear_parser = subparsers.add_parser(
        'clear-state',
        help='Clear browser state, logs, and cache'
    )
    clear_parser.add_argument(
        '--confirm',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    # Extract player action
    extract_parser = subparsers.add_parser(
        'extract-player',
        help='Extract player statistics from a specific player page'
    )
    # Make URL optional and add userid option
    extract_parser.add_argument(
        '--url',
        help='URL of the player page to extract data from (optional if userid provided)'
    )
    extract_parser.add_argument(
        '--userid',
        help='UserId of the player to extract data from'
    )
    extract_parser.add_argument(
        '--league',
        help='League name to use (overrides config default)'
    )
    extract_parser.add_argument(
        '--output',
        help='Output file to save extracted data (optional)'
    )
    extract_parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    extract_parser.add_argument(
        '--launch-browser',
        action='store_true',
        help='Launch browser window (default: headless mode)'
    )
    extract_parser.add_argument(
        '--no-terminal',
        action='store_true',
        help='Suppress terminal output (useful when only saving to file)'
    )
    
    # Extract team action
    extract_team_parser = subparsers.add_parser(
        'extract-team',
        help='Extract team statistics from a specific team page'
    )
    extract_team_parser.add_argument(
        '--team-id',
        required=True,
        help='Team ID of the team to extract data from'
    )
    extract_team_parser.add_argument(
        '--league',
        help='League name to use (overrides config default)'
    )
    extract_team_parser.add_argument(
        '--output',
        help='Output file to save extracted data (optional)'
    )
    extract_team_parser.add_argument(
        '--format',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    extract_team_parser.add_argument(
        '--launch-browser',
        action='store_true',
        help='Launch browser window (default: headless mode)'
    )
    extract_team_parser.add_argument(
        '--no-terminal',
        action='store_true',
        help='Suppress terminal output (useful when only saving to file)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.action == 'login':
            action = LoginAction()
            success = action.run(
                email=args.email,
                password=args.password,
                headless=not args.launch_browser
            )
        elif args.action == 'verify-session':
            action = VerifySessionAction()
            success = action.run(headless=not args.launch_browser)
        elif args.action == 'clear-state':
            action = ClearStateAction()
            success = action.run(confirm=args.confirm)
        elif args.action == 'extract-player':
            action = ExtractPlayerAction()
            success = action.run(
                userid=args.userid,
                league=args.league,
                player_url=args.url,
                output_file=args.output,
                format=args.format,
                headless=not args.launch_browser,
                terminal_output=not args.no_terminal
            )
        elif args.action == 'extract-team':
            action = ExtractTeamAction()
            success = action.run(
                team_id=args.team_id,
                league=args.league,
                output_file=args.output,
                format=args.format,
                headless=not args.launch_browser,
                terminal_output=not args.no_terminal
            )
        else:
            print(f"❌ Unknown action: {args.action}")
            return 1
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())