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

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="APA Stat Scraper - Extract player statistics from poolplayers.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py login                    # Login to APA site
  python app.py verify-session          # Verify current session
  python app.py clear-state             # Clear browser state and data
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
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    # Verify session action
    verify_parser = subparsers.add_parser(
        'verify-session',
        help='Verify current session can access dashboard'
    )
    verify_parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
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
    
    args = parser.parse_args()
    
    try:
        if args.action == 'login':
            action = LoginAction()
            success = action.run(
                email=args.email,
                password=args.password,
                headless=args.headless
            )
        elif args.action == 'verify-session':
            action = VerifySessionAction()
            success = action.run(headless=args.headless)
        elif args.action == 'clear-state':
            action = ClearStateAction()
            success = action.run(confirm=args.confirm)
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