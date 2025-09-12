"""
Login action for APA Stat Scraper
Handles authentication and session establishment
"""

import getpass
from .base import BaseAction

class LoginAction(BaseAction):
    """Action to login to APA site and establish session"""
    
    def run(self, email=None, password=None, headless=False):
        """Run the login action"""
        print("🚀 APA Stat Scraper - Login")
        print("=" * 40)
        
        # Get credentials if not provided
        if not email:
            email = input("Email: ").strip()
        if not password:
            password = getpass.getpass("Password: ").strip()
        
        if not email or not password:
            print("❌ Email and password are required")
            return False
        
        return self._run_with_session(email=email, password=password, headless=headless)
    
    async def _run_async(self, email, password, headless=False):
        """Async implementation of login"""
        try:
            # Start browser
            await self.session_manager.start_browser(headless=headless)
            
            # Check if already authenticated
            if await self.session_manager.is_authenticated():
                print("✅ Already authenticated!")
                return True
            
            # Perform login
            print("🔐 Logging in...")
            if not await self.session_manager.login(email, password):
                print("❌ Login failed")
                return False
            
            # Handle notifications
            print("🔍 Checking for notifications...")
            await self.session_manager.handle_notifications()
            
            # Verify we can access dashboard
            print("🔍 Verifying dashboard access...")
            if await self.session_manager.is_authenticated():
                print("✅ Login successful! Session established.")
                print("🔒 Session data saved for future use")
                return True
            else:
                print("❌ Login verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
