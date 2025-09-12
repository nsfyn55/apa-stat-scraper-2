#!/usr/bin/env python3
"""
Session Manager for APA Scraper
Handles authentication and session persistence
"""

import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext
from config import config

class APASessionManager:
    def __init__(self):
        self.session_file = config.get_session_file()
        self.user_data_dir = config.get_browser_data_dir()
        self.browser = None
        self.context = None
        self.page = None
        
    async def start_browser(self, headless=None):
        """Start browser with persistent user data directory"""
        playwright = await async_playwright().start()
        
        # Use config value if headless not specified
        if headless is None:
            headless = config.get('browser.headless', False)
        
        # Create user data directory for persistence
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        # Get browser configuration
        timeout = config.get('browser.timeout', 30000)
        user_agent = config.get('browser.user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                f'--user-agent={user_agent}'
            ]
        )
        
        # Get the first page or create a new one
        pages = self.browser.pages
        if pages:
            self.page = pages[0]
        else:
            self.page = await self.browser.new_page()
            
        return self.page
    
    async def is_authenticated(self):
        """Check if we're already authenticated by visiting the dashboard"""
        try:
            print("🔍 Checking if already authenticated...")
            await self.page.goto("https://league.poolplayers.com/")
            await self.page.wait_for_load_state('networkidle')
            
            current_url = self.page.url
            title = await self.page.title()
            
            # Check if we're on the dashboard (not login page)
            if "login" not in current_url.lower() and "dashboard" in title.lower():
                print("✅ Already authenticated!")
                return True
            else:
                print("❌ Not authenticated, need to login")
                return False
                
        except Exception as e:
            print(f"⚠️ Error checking authentication: {e}")
            return False
    
    async def login(self, email, password):
        """Perform login if not already authenticated"""
        if await self.is_authenticated():
            return True
            
        try:
            print("🌐 Going to login page...")
            await self.page.goto("https://league.poolplayers.com/login")
            await self.page.wait_for_load_state('networkidle')
            
            print("🔐 Logging in...")
            await self.page.fill('#email', email)
            await self.page.fill('#password', password)
            await self.page.click('button:has-text("Log In")')
            
            print("⏳ Waiting for authorization page...")
            await asyncio.sleep(3)
            
            print("🖱️ Clicking Continue...")
            await self.page.click('button:has-text("Continue")')
            
            print("⏳ Waiting for dashboard to load...")
            await asyncio.sleep(5)
            await self.page.wait_for_load_state('networkidle')
            
            # Check if login was successful
            current_url = self.page.url
            title = await self.page.title()
            
            if "login" not in current_url.lower():
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    async def handle_notifications(self):
        """Check for and handle any notification dialogues"""
        try:
            print("🔍 Checking for notifications dialogue...")
            
            # Wait a bit for notifications to appear
            await asyncio.sleep(2)
            
            # Look for the specific "No Thanks" button first
            no_thanks_selectors = [
                'a:has-text("No Thanks")',
                'button:has-text("No Thanks")',
                'button:has-text("No thanks")',
                'button:has-text("no thanks")',
                '[role="button"]:has-text("No Thanks")',
                'input[type="button"]:has-text("No Thanks")'
            ]
            
            for selector in no_thanks_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button and await button.is_visible():
                        text = await button.text_content()
                        if text and "no thanks" in text.lower():
                            print(f"✅ Found 'No Thanks' button: '{text.strip()}'")
                            print(f"🖱️ Clicking 'No Thanks' button...")
                            await button.click()
                            await asyncio.sleep(2)
                            print("✅ Notification dismissed!")
                            return True
                except:
                    continue
            
            # If no "No Thanks" button found, look for other notification patterns
            notification_selectors = [
                '[class*="notification"]',
                '[class*="alert"]',
                '[class*="modal"]',
                '[class*="dialog"]',
                '[class*="popup"]',
                '[class*="toast"]',
                '[role="dialog"]',
                '[role="alert"]',
                '.modal',
                '.dialog',
                '.popup',
                '.notification',
                '.alert'
            ]
            
            for selector in notification_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        print(f"✅ Found notification dialogue: {selector}")
                        
                        # Look for close buttons
                        close_selectors = [
                            'button:has-text("Close")',
                            'button:has-text("Dismiss")',
                            'button:has-text("OK")',
                            'button:has-text("Got it")',
                            'button:has-text("×")',
                            'button:has-text("✕")',
                            '[aria-label="Close"]',
                            '[aria-label="Dismiss"]',
                            '.close',
                            '.dismiss',
                            '.btn-close'
                        ]
                        
                        for close_selector in close_selectors:
                            try:
                                close_btn = await element.query_selector(close_selector)
                                if close_btn and await close_btn.is_visible():
                                    print(f"🖱️ Clicking close button: {close_selector}")
                                    await close_btn.click()
                                    await asyncio.sleep(1)
                                    return True
                            except:
                                continue
                        
                        # Try clicking any button in the notification
                        buttons = await element.query_selector_all('button')
                        if buttons:
                            print("🖱️ Clicking first available button...")
                            await buttons[0].click()
                            await asyncio.sleep(1)
                            return True
                            
                except:
                    continue
            
            print("ℹ️ No notification dialogue found")
            return False
            
        except Exception as e:
            print(f"⚠️ Error handling notifications: {e}")
            return False
    
    async def navigate_to_team(self, team_id):
        """Navigate to a specific team page"""
        try:
            team_url = f"https://league.poolplayers.com/team/{team_id}"
            print(f"🌐 Navigating to team {team_id}: {team_url}")
            
            await self.page.goto(team_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Handle any notifications that might appear
            await self.handle_notifications()
            
            current_url = self.page.url
            title = await self.page.title()
            
            print(f"📍 Current URL: {current_url}")
            print(f"📄 Page Title: {title}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error navigating to team: {e}")
            return False
    
    async def get_page_content(self):
        """Get current page content"""
        try:
            html = await self.page.content()
            return html
        except Exception as e:
            print(f"❌ Error getting page content: {e}")
            return None
    
    async def take_screenshot(self, filename="screenshot.png"):
        """Take a screenshot of current page"""
        try:
            await self.page.screenshot(path=filename)
            print(f"📸 Screenshot saved as '{filename}'")
            return True
        except Exception as e:
            print(f"❌ Error taking screenshot: {e}")
            return False
    
    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
            print("🔒 Browser closed")

async def main():
    """Test the session manager"""
    session = APASessionManager()
    
    try:
        # Start browser
        await session.start_browser(headless=False)
        
        # Check if already authenticated
        if not await session.is_authenticated():
            # Get credentials
            print("📝 Please enter your login credentials:")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            
            # Login
            if not await session.login(email, password):
                print("❌ Failed to login")
                return
        
        # Handle notifications
        await session.handle_notifications()
        
        # Test navigation to a team
        team_id = input("Enter team ID to test (or press Enter to skip): ").strip()
        if team_id:
            await session.navigate_to_team(team_id)
            await session.take_screenshot("team_page.png")
        
        print("✅ Session manager working! Browser will stay open...")
        print("⏳ Press Ctrl+C to close when done testing...")
        
        # Keep browser open
        try:
            await asyncio.sleep(3600)  # Keep open for 1 hour
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
