"""
Verify session action for APA Stat Scraper
Checks if current session can access the dashboard
"""

from .base import BaseAction

class VerifySessionAction(BaseAction):
    """Action to verify current session can access dashboard"""
    
    def run(self, headless=False):
        """Run the verify session action"""
        print("🚀 APA Stat Scraper - Verify Session")
        print("=" * 40)
        
        return self._run_with_session(headless=headless)
    
    async def _run_async(self, headless=False):
        """Async implementation of session verification"""
        try:
            # Start browser with existing session
            await self.session_manager.start_browser(headless=headless)
            
            # Check if authenticated
            if not await self.session_manager.is_authenticated():
                print("❌ No valid session found")
                print("💡 Run 'python app.py login' to establish a session")
                return False
            
            print("✅ Session found!")
            
            # Handle any notifications
            print("🔍 Checking for notifications...")
            await self.session_manager.handle_notifications()
            
            # Verify dashboard access
            print("🔍 Verifying dashboard access...")
            if await self.session_manager.is_authenticated():
                current_url = self.session_manager.page.url
                title = await self.session_manager.page.title()
                
                print(f"📍 Current URL: {current_url}")
                print(f"📄 Page Title: {title}")
                
                if "dashboard" in title.lower() or "welcome" in title.lower():
                    print("✅ SUCCESS! Dashboard is accessible")
                    print("🔒 Session is valid and ready for use")
                    return True
                else:
                    print("⚠️ On page but not dashboard")
                    return False
            else:
                print("❌ Session verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False
