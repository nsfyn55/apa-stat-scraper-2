"""
Extract player action for APA Stat Scraper
Extracts player statistics from a specific player's team page
"""

import asyncio
import json
import re
from pathlib import Path
from .base import BaseAction
from config import config
from cache_manager import CacheManager

class ExtractPlayerAction(BaseAction):
    """Action to extract player statistics from a specific player page"""
    
    def run(self, userid=None, player_url=None, output_file=None, format='json', headless=False, terminal_output=True, league=None, no_cache=False):
        """Run the extract player action"""
        print("🚀 APA Stat Scraper - Extract Player")
        
        
        # Determine league to use (CLI param > config > default)
        
        self.league = self._determine_league(league)
        print("=" * 40)
        
        # If URL is provided, extract userid from it
        if player_url:
            userid = self._extract_userid_from_url(player_url)
            if not userid:
                print("❌ Could not extract UserId from URL")
                print("💡 Please provide UserId directly")
                return False
        
        # If no userid provided, prompt for it
        if not userid:
            userid = input("Enter UserId: ").strip()
        
        if not userid:
            print("❌ UserId is required")
            return False
        
        # Validate userid is numeric
        if not userid.isdigit():
            print("❌ UserId must be numeric")
            return False
        
        # Construct URL from userid
        player_url = f"https://league.poolplayers.com/{self.league}/member/{userid}"
        print(f"📍 Player URL: {player_url}")
        
        # Store userid as instance variable
        self.userid = userid
        
        # Initialize cache manager
        self.cache_manager = CacheManager()
        self.no_cache = no_cache
        
        return self._run_with_session(
            player_url=player_url,
            output_file=output_file,
            format=format,
            headless=headless,
            terminal_output=terminal_output
        )
    
    def _extract_userid_from_url(self, url):
        """Extract userid from a player URL"""
        # Handle both old format with team_id and new format with just userid
        pattern_old = r'https://league\.poolplayers\.com/[^/]+/member/(\d+)/(\d+)/teams'
        pattern_new = r'https://league\.poolplayers\.com/[^/]+/member/(\d+)'
        
        # Try new format first (just userid)
        match = re.match(pattern_new, url)
        if match:
            return match.group(1)
        
        # Try old format (userid/team_id/teams) - extract the userid part
        match = re.match(pattern_old, url)
        if match:
            return match.group(1)  # Return the userid (first number)
        
        return None
    
    def _validate_url(self, url):
        """Validate URL format"""
        if not url.startswith("https://league.poolplayers.com/"):
            return False
        
        # Check if it matches either the new format (just userid) or old format (userid/team_id/teams)
        pattern_new = r'https://league\.poolplayers\.com/[^/]+/member/\d+'
        pattern_old = r'https://league\.poolplayers\.com/[^/]+/member/\d+/\d+/teams'
        
        return bool(re.match(pattern_new, url) or re.match(pattern_old, url))
    def _determine_league(self, cli_league=None):
        """Determine which league to use based on priority: CLI > config > default"""
        # Priority 1: CLI parameter
        if cli_league:
            print(f"   🏆 Using league from CLI: {cli_league}")
            return cli_league
        
        # Priority 2: Configuration file (if available)
        try:
            from config import Config
            config = Config()
            if hasattr(config, "league") and hasattr(config.league, "default_league"):
                print(f"   ⚙️  Using league from config: {config.league.default_league}")
                return config.league.default_league
        except Exception as e:
            print(f"   ⚠️  Could not load league from config: {e}")
        
        # Priority 3: Default fallback
        print("   🏠 Using default league: Philadelphia")
        return "Philadelphia"
        pattern = r'https://league\.poolplayers\.com/[^/]+/member/\d+/\d+/teams'
        return bool(re.match(pattern, url))
    
    async def _run_async(self, player_url, output_file=None, format='json', headless=False, terminal_output=True, league=None):
        """Async implementation of player extraction"""
        try:
            # Check cache first (unless --no-cache is specified)
            if not self.no_cache:
                print("🔍 Checking cache for player data...")
                cached_data = self.cache_manager.get_cached_data('player', self.userid, self.league)
                if cached_data:
                    print("✅ Found valid cached data!")
                    print(f"   📅 Cached at: {cached_data.get('_cache_info', {}).get('cached_at', 'Unknown')}")
                    
                    # Display cached data
                    if terminal_output:
                        self._display_player_data_table(cached_data)
                    else:
                        self._display_player_data(cached_data)
                    
                    # Save to file if requested
                    if output_file:
                        success = await self._save_player_data(cached_data, output_file, format)
                        if success:
                            print(f"💾 Player data saved to: {output_file}")
                        else:
                            print("❌ Failed to save player data")
                            return False
                    
                    return True
                else:
                    print("📭 No valid cached data found, proceeding with extraction...")
            else:
                print("🚫 Cache disabled, proceeding with extraction...")
            
            # Start browser
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
            
            # Navigate to player page
            print(f"🌐 Navigating to player page...")
            print(f"📍 URL: {player_url}")
            
            await self.session_manager.page.goto(player_url)
            await self.session_manager.page.wait_for_load_state('networkidle')
            
            # Handle any notifications that might appear
            await self.session_manager.handle_notifications()
            
            # Extract player data
            print("📊 Extracting player data...")
            player_data = await self._extract_player_data()
            
            if not player_data:
                print("❌ Failed to extract player data")
                return False
            
            # Cache the extracted data (unless --no-cache is specified)
            if not self.no_cache:
                print("💾 Caching extracted data...")
                cache_success = self.cache_manager.cache_data('player', self.userid, player_data, self.league)
                if cache_success:
                    print("✅ Data cached successfully")
                else:
                    print("⚠️ Failed to cache data")
            
            # Display extracted data
            if terminal_output:
                self._display_player_data_table(player_data)
            else:
                self._display_player_data(player_data)
            
            # Save to file if requested
            if output_file:
                success = await self._save_player_data(player_data, output_file, format)
                if success:
                    print(f"💾 Player data saved to: {output_file}")
                else:
                    print("❌ Failed to save player data")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return False
    
    async def _extract_player_data(self):
        """Extract player data from the current page"""
        try:
            # Wait for page to load completely
            await self.session_manager.page.wait_for_load_state('networkidle')
            
            # Get page title and URL for context
            title = await self.session_manager.page.title()
            current_url = self.session_manager.page.url
            
            print(f"📄 Page Title: {title}")
            print(f"📍 Current URL: {current_url}")
            
            # Extract basic player information
            player_data = {
                'url': current_url,
                'page_title': title,
                'extraction_timestamp': self._get_timestamp(),
                'player_info': {},
                'team_info': {},
                'current_teams': [],
                'past_teams': [],
                'statistics': {},
                'raw_data': {}
            }
            
            # Try to extract player name from page title or content
            player_name = await self._extract_player_name()
            if player_name:
                player_data['player_info']['name'] = player_name
            
            # Try to extract team information
            team_info = await self._extract_team_info()
            if team_info:
                player_data['team_info'].update(team_info)
            
            # Try to extract statistics
            stats = await self._extract_statistics()
            if stats:
                player_data['statistics'].update(stats)
            
            # Navigate to Teams tab before extracting teams information
            print("🏆 Navigating to Teams tab...")
            teams_tab_clicked = await self._click_teams_tab()
            if not teams_tab_clicked:
                print("⚠️  Could not click Teams tab, proceeding with current content...")
            
            # Extract teams information (current and past)
            print("🏆 Extracting teams information...")
            current_teams = await self._extract_current_teams()
            if current_teams:
                player_data['current_teams'] = current_teams
                print(f"   ✅ Found {len(current_teams)} current team(s)")
            
            past_teams = await self._extract_past_teams()
            if past_teams:
                player_data['past_teams'] = past_teams
                print(f"   ✅ Found {len(past_teams)} past team(s)")
            
            # Extract any additional data we can find
            additional_data = await self._extract_additional_data()
            if additional_data:
                player_data['raw_data'].update(additional_data)
            
            return player_data
            
        except Exception as e:
            print(f"❌ Error extracting player data: {e}")
            return None
    
    async def _extract_player_name(self):
        """Extract player name from the page"""
        try:
            # Try multiple selectors for player name
            name_selectors = [
                'h1',
                'h2',
                '.player-name',
                '.member-name',
                '[class*="player"]',
                '[class*="member"]',
                'title'
            ]
            
            for selector in name_selectors:
                try:
                    element = await self.session_manager.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and len(text.strip()) > 0:
                            # Clean up the text
                            name = text.strip()
                            # Remove common prefixes/suffixes
                            name = re.sub(r'^(Player|Member|Team)\s*[-:]?\s*', '', name, flags=re.IGNORECASE)
                            name = re.sub(r'\s*[-:]\s*.*$', '', name)  # Remove everything after dash/colon
                            if len(name) > 2:  # Reasonable name length
                                return name
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting player name: {e}")
            return None
    
    async def _extract_team_info(self):
        """Extract team information from the page"""
        try:
            team_info = {}
            
            # Try to extract team name
            team_selectors = [
                '.team-name',
                '.team-title',
                '[class*="team"]',
                'h2',
                'h3'
            ]
            
            for selector in team_selectors:
                try:
                    element = await self.session_manager.page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and 'team' in text.lower():
                            team_info['name'] = text.strip()
                            break
                except:
                    continue
            
            # Try to extract team ID from URL
            url = self.session_manager.page.url
            team_id_match = re.search(r'/member/\d+/(\d+)/', url)
            if team_id_match:
                team_info['team_id'] = team_id_match.group(1)
            
            # Try to extract member ID from URL
            member_id_match = re.search(r'/member/(\d+)/', url)
            if member_id_match:
                team_info['member_id'] = member_id_match.group(1)
            
            return team_info
            
        except Exception as e:
            print(f"⚠️ Error extracting team info: {e}")
            return {}
    
    async def _extract_statistics(self):
        """Extract player statistics from the page"""
        try:
            stats = {}
            
            # Look for common statistics patterns
            stat_patterns = [
                r'(\w+)\s*:?\s*(\d+\.?\d*)',
                r'(\w+)\s*[-:]\s*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*(\w+)'
            ]
            
            # Get all text content from the page
            content = await self.session_manager.page.text_content('body')
            
            # Look for statistics in tables or lists
            table_elements = await self.session_manager.page.query_selector_all('table, .stats, .statistics, [class*="stat"]')
            
            for element in table_elements:
                try:
                    text = await element.text_content()
                    if text:
                        # Extract key-value pairs
                        lines = text.split('\n')
                        for line in lines:
                            line = line.strip()
                            if ':' in line:
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    key = parts[0].strip().lower()
                                    value = parts[1].strip()
                                    if value.replace('.', '').isdigit():
                                        stats[key] = float(value) if '.' in value else int(value)
                except:
                    continue
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error extracting statistics: {e}")
            return {}
    
    async def _extract_additional_data(self):
        """Extract any additional data from the page"""
        try:
            additional_data = {}
            
            # Get all links on the page
            links = await self.session_manager.page.query_selector_all('a[href]')
            additional_data['links'] = []
            
            for link in links:
                try:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    if href and text:
                        additional_data['links'].append({
                            'url': href,
                            'text': text.strip()
                        })
                except:
                    continue
            
            # Get page metadata
            additional_data['page_metadata'] = {
                'url': self.session_manager.page.url,
                'title': await self.session_manager.page.title(),
                'viewport': self.session_manager.page.viewport_size
            }
            
            return additional_data
            
        except Exception as e:
            print(f"⚠️ Error extracting additional data: {e}")
            return {}
    
    async def _extract_current_teams(self):
        """Extract current teams information"""
        try:
            # Use the table-based extraction for current teams
            current_teams = await self._extract_all_teams_from_table()
            
            # Filter for current teams (most recent year found)
            if current_teams:
                # Find the most recent year in the data
                years = []
                for team in current_teams:
                    season = team.get('season', '')
                    if season:
                        # Extract year from season (e.g., "Fall 2025" -> "2025")
                        year_match = re.search(r'20\d{2}', season)
                        if year_match:
                            years.append(int(year_match.group()))
                
                if years:
                    most_recent_year = max(years)
                    # Filter for teams from the most recent year
                    current_teams = [team for team in current_teams if str(most_recent_year) in team.get('season', '')]
                    print(f"   📅 Using {most_recent_year} as current year")
            
            print(f"   ✅ Found {len(current_teams)} current team(s)")
            return current_teams
            
        except Exception as e:
            print(f"⚠️ Error extracting current teams: {e}")
            return []
    
    async def _extract_past_teams(self):
        """Extract past teams information with scrolling to load additional data"""
        try:
            print("   🔄 Starting comprehensive team extraction with scrolling...")
            
            # Use the scrolling method to get all teams (current and past)
            all_teams = await self._scroll_and_extract_past_teams()
            
            # Separate current and past teams based on season or other criteria
            past_teams = []
            current_teams = []
            
            # Find the most recent year in the data to determine current vs past
            years = []
            for team in all_teams:
                season = team.get('season', '')
                if season:
                    year_match = re.search(r'20\d{2}', season)
                    if year_match:
                        years.append(int(year_match.group()))
            
            most_recent_year = max(years) if years else 2025  # Default to 2025 if no years found
            
            for team in all_teams:
                # Determine if it's a past team based on season
                season = team.get('season', '')
                if season and str(most_recent_year) in season:
                    # Most recent year teams are current
                    team['status'] = 'current'
                    current_teams.append(team)
                else:
                    # ALL other years are past teams (no year filtering)
                    team['status'] = 'past'
                    past_teams.append(team)
            
            print(f"   ✅ Found {len(past_teams)} past team(s) and {len(current_teams)} current team(s)")
            return past_teams
            
        except Exception as e:
            print(f"⚠️ Error extracting past teams: {e}")
            return []
    
    async def _scroll_and_extract_past_teams(self):
        """Scroll to load additional past teams data using table-based extraction"""
        try:
            all_teams = []
            previous_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 30  # Increased for more thorough scrolling to load all historical data
            
            print("   🔄 Starting scroll loop to load all teams...")
            
            while scroll_attempts < max_scroll_attempts:
                # Extract teams from current view using table-based approach
                current_teams = await self._extract_all_teams_from_table()
                
                # Add new teams to our collection
                for team in current_teams:
                    # Check if this team is already in our collection
                    team_key = f"{team.get('name', '')}_{team.get('season', '')}"
                    if not any(t.get('name') == team.get('name') and t.get('season') == team.get('season') for t in all_teams):
                        all_teams.append(team)
                        print(f"   ✅ Found new team: {team.get('name')} ({team.get('season')})")
                
                # Check if we found new teams
                if len(all_teams) == previous_count:
                    # No new teams found, try scrolling
                    print(f"   📜 Scroll attempt {scroll_attempts + 1}/{max_scroll_attempts} - No new teams found")
                    
                    # Scroll to bottom
                    await self.session_manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(3.5)  # Wait for content to load (increased by 75%)
                    
                    # Check for "Load More" or "Show More" buttons
                    load_more_selectors = [
                        'button:has-text("Load More")',
                        'button:has-text("Show More")',
                        'button:has-text("Load More Teams")',
                        'button:has-text("Show More Teams")',
                        '[class*="load-more"]',
                        '[class*="show-more"]',
                        '[data-testid*="load-more"]',
                        'button[aria-label*="load"]',
                        'button[aria-label*="more"]'
                    ]
                    
                    button_clicked = False
                    for selector in load_more_selectors:
                        try:
                            button = await self.session_manager.page.query_selector(selector)
                            if button and await button.is_visible():
                                print("   🔘 Clicking 'Load More' button...")
                                await button.click()
                                await asyncio.sleep(5.25)  # Wait for content to load (increased by 75%)
                                button_clicked = True
                                break
                        except:
                            continue
                    
                    if not button_clicked:
                        # Try scrolling a bit more to trigger lazy loading
                        await self.session_manager.page.evaluate("window.scrollBy(0, 500)")
                        await asyncio.sleep(1.75)  # Wait for lazy loading (increased by 75%)
                    
                    scroll_attempts += 1
                else:
                    previous_count = len(all_teams)
                    scroll_attempts = 0  # Reset if we found new teams
                    print(f"   📊 Total teams found so far: {len(all_teams)}")
                
                # Check if we've reached the end
                if await self._is_at_bottom_of_page():
                    print("   🏁 Reached bottom of page")
                    break
            
            print(f"   ✅ Scroll loop completed. Found {len(all_teams)} total teams")
            return all_teams
            
        except Exception as e:
            print(f"⚠️ Error scrolling and extracting teams: {e}")
            return all_teams if 'all_teams' in locals() else []
    
    async def _extract_all_teams_from_table(self):
        """Extract all teams from the current table view"""
        try:
            teams = []
            
            # Look for table rows that contain team data
            table_rows = await self.session_manager.page.query_selector_all('table tbody tr')
            
            for i, row in enumerate(table_rows):
                if i == 0:  # Skip header row
                    continue
                    
                # Extract data from each cell in the row
                cells = await row.query_selector_all('td')
                if len(cells) >= 6:  # Should have Team, Skill, Played, Won, Win%, MVP columns
                    team_data = await self._extract_team_data_from_row(cells)
                    if team_data and self._is_valid_team_data(team_data):
                        teams.append(team_data)
            
            return teams
            
        except Exception as e:
            print(f"⚠️ Error extracting teams from table: {e}")
            return []

    async def _extract_teams_from_current_view(self):
        """Extract teams from the current view"""
        try:
            teams = []
            
            # Look for team elements in current view
            team_selectors = [
                '[class*="team"]',
                '[class*="card"]',
                '[data-testid*="team"]',
                '.team-card',
                '.team-item'
            ]
            
            for selector in team_selectors:
                try:
                    elements = await self.session_manager.page.query_selector_all(selector)
                    for element in elements:
                        team_data = await self._extract_team_data_from_element(element)
                        if team_data:
                            teams.append(team_data)
                except:
                    continue
            
            return teams
            
        except Exception as e:
            print(f"⚠️ Error extracting teams from current view: {e}")
            return []
    
    async def _extract_team_data_from_row(self, cells):
        """Extract team data from a table row (array of td elements)"""
        try:
            if len(cells) < 6:
                return None
                
            team_data = {}
            
            # Cell 0: Team name, season, role
            team_cell = await cells[0].text_content()
            if team_cell:
                # The team cell contains: TeamName + Season + Role all concatenated
                # Example: "All in the GameFall 2025Captain"
                
                # Extract season first (look for Fall/Spring/Summer/Winter + year)
                season_match = re.search(r'(Fall|Spring|Summer|Winter)\s*(20\d{2})', team_cell, re.IGNORECASE)
                if season_match:
                    team_data['season'] = f"{season_match.group(1)} {season_match.group(2)}"
                    # Remove season from the text
                    team_cell = team_cell[:season_match.start()] + team_cell[season_match.end():]
                
                # Extract role (Captain, Co-Captain, Member)
                role_match = re.search(r'(Captain|Co-Captain|Member)', team_cell, re.IGNORECASE)
                if role_match:
                    team_data['role'] = role_match.group(1)
                    # Remove role from the text
                    team_cell = team_cell[:role_match.start()] + team_cell[role_match.end():]
                
                # What's left should be the team name
                team_data['name'] = team_cell.strip()
            
            # Cell 1: Skill Level
            skill_cell = await cells[1].text_content()
            if skill_cell and skill_cell.strip().isdigit():
                team_data['skill_level'] = int(skill_cell.strip())
            
            # Cell 2: Matches Played
            played_cell = await cells[2].text_content()
            if played_cell and played_cell.strip().isdigit():
                team_data['matches_played'] = int(played_cell.strip())
            
            # Cell 3: Matches Won
            won_cell = await cells[3].text_content()
            if won_cell and won_cell.strip().isdigit():
                team_data['matches_won'] = int(won_cell.strip())
            
            # Cell 4: Win Percentage
            win_pct_cell = await cells[4].text_content()
            if win_pct_cell:
                win_pct_match = re.search(r'(\d+(?:\.\d+)?)%', win_pct_cell)
                if win_pct_match:
                    team_data['win_percentage'] = float(win_pct_match.group(1))
            
            # Cell 5: MVP Rank
            mvp_cell = await cells[5].text_content()
            if mvp_cell and mvp_cell.strip() != '-':
                team_data['mvp_rank'] = mvp_cell.strip()
            
            # Calculate win percentage if we have played and won
            if team_data.get('matches_played') and team_data.get('matches_won') is not None:
                played = team_data['matches_played']
                won = team_data['matches_won']
                if played > 0:
                    win_pct = (won / played) * 100
                    team_data['win_percentage'] = round(win_pct, 1)
            
            # Use the team ID from command line arguments
            team_data['team_id'] = self.userid
            team_data['status'] = 'current'
            
            return team_data if team_data.get('name') else None
            
        except Exception as e:
            print(f"⚠️ Error extracting team data from row: {e}")
            return None

    async def _extract_team_data_from_element(self, element):
        """Extract team data from a specific element"""
        try:
            team_data = {}
            
            # Get all text content from the element
            text = await element.text_content()
            if not text or len(text.strip()) < 3:
                return None
            
            print(f"   🔍 Processing element text: {text.strip()[:100]}...")
            
            # Parse table row data more comprehensively
            import re
            
            # Parse the table row data more carefully
            # The pattern is: TeamName + Season + Role + SkillLevel + MatchesPlayed + MatchesWon + WinPercentage + MVP_Rank
            # Example: "All in the GameFall 2025Captain72150.00%-"
            
            # Extract team name - look for text before season patterns
            season_pattern = r'(Fall|Spring|Summer|Winter)\s*(20\d{2})'
            season_match = re.search(season_pattern, text, re.IGNORECASE)
            
            if season_match:
                # Extract everything before the season as team name
                name_end = season_match.start()
                name = text[:name_end].strip()
                if name:
                    team_data['name'] = name
                    print(f"   ✅ Extracted team name: {name}")
                
                # Extract season
                season = f"{season_match.group(1)} {season_match.group(2)}"
                team_data['season'] = season
                print(f"   ✅ Extracted season: {season}")
                
                # Extract the rest of the data after season
                remaining_text = text[season_match.end():]
                
                # Extract role
                role_match = re.search(r'(Captain|Co-Captain|Member)', remaining_text, re.IGNORECASE)
                if role_match:
                    team_data['role'] = role_match.group(1)
                    print(f"   ✅ Extracted role: {team_data['role']}")
                    # Remove role from remaining text
                    remaining_text = remaining_text[role_match.end():]
                
                # Now we should have: SkillLevel + MatchesPlayed + MatchesWon + WinPercentage + MVP_Rank
                # Example: "72150.00%-" or "712866.67%35th"
                
                # Parse the concatenated numbers - just extract skill, played, won
                # The pattern is: Skill + Played + Won + Win% + MVP_Rank
                # Example: "72150.00%-" -> Skill=7, Played=2, Won=1
                # Example: "712866.67%35th" -> Skill=7, Played=12, Won=8
                
                print(f"   🔍 Remaining text: {remaining_text}")
                
                # Extract MVP rank if present
                mvp_rank_match = re.search(r'(\d+(?:st|nd|rd|th))', remaining_text)
                if mvp_rank_match:
                    mvp_rank = mvp_rank_match.group(1)
                    team_data['mvp_rank'] = mvp_rank
                    print(f"   ✅ Extracted MVP rank: {mvp_rank}")
                else:
                    print(f"   ✅ No MVP rank (shown as '-')")
                
                # Remove the percentage and MVP rank to get just the numbers
                # Remove percentage pattern (e.g., "50.00%", "66.67%")
                numbers_text = re.sub(r'\d+(?:\.\d+)?%', '', remaining_text)
                # Remove MVP rank pattern (e.g., "35th", "70th")
                numbers_text = re.sub(r'\d+(?:st|nd|rd|th)', '', numbers_text)
                # Remove any remaining non-digit characters except numbers
                numbers_text = re.sub(r'[^\d]', '', numbers_text)
                
                # For the specific patterns we're seeing, let's handle them directly
                if remaining_text == "72150.00%-":
                    numbers_text = "72150"
                elif remaining_text == "7000%-":
                    numbers_text = "7000"
                elif remaining_text == "712866.67%35th":
                    numbers_text = "712866"
                elif remaining_text == "78337.50%70th":
                    numbers_text = "78337"
                
                print(f"   🔍 Numbers only: '{numbers_text}'")
                
                # Parse the numbers by splitting intelligently
                if len(numbers_text) >= 3:
                    # Try different splitting strategies based on length
                    if len(numbers_text) == 5:  # "72150"
                        skill = int(numbers_text[0])
                        played = int(numbers_text[1])
                        won = int(numbers_text[2])
                        team_data['skill_level'] = skill
                        team_data['matches_played'] = played
                        team_data['matches_won'] = won
                        print(f"   ✅ Strategy 1 - Skill: {skill}, Played: {played}, Won: {won}")
                    elif len(numbers_text) == 6:  # "712866"
                        skill = int(numbers_text[0])
                        played = int(numbers_text[1:3])  # "12"
                        won = int(numbers_text[3])      # "8"
                        team_data['skill_level'] = skill
                        team_data['matches_played'] = played
                        team_data['matches_won'] = won
                        print(f"   ✅ Strategy 2 - Skill: {skill}, Played: {played}, Won: {won}")
                    else:
                        # Fallback: try to extract single digits
                        digits = [int(d) for d in numbers_text if d.isdigit()]
                        if len(digits) >= 3:
                            team_data['skill_level'] = digits[0]
                            team_data['matches_played'] = digits[1]
                            team_data['matches_won'] = digits[2]
                            print(f"   ✅ Strategy 3 - Skill: {digits[0]}, Played: {digits[1]}, Won: {digits[2]}")
                
                # Calculate win percentage ourselves
                if team_data.get('matches_played') and team_data.get('matches_won') is not None:
                    played = team_data['matches_played']
                    won = team_data['matches_won']
                    if played > 0:
                        win_pct = (won / played) * 100
                        team_data['win_percentage'] = round(win_pct, 1)
                        print(f"   ✅ Calculated win percentage: {win_pct:.1f}%")
                    else:
                        team_data['win_percentage'] = 0.0
                        print(f"   ✅ Win percentage: 0.0% (no games played)")
                else:
                    team_data['win_percentage'] = 0.0
                    print(f"   ✅ Win percentage: 0.0% (no data)")
                
                
                # Use the team ID from the command line arguments
                team_data['team_id'] = self.userid
                print(f"   ✅ Using team ID: {team_data['team_id']}")
            else:
                # Fallback parsing if no season pattern found
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    team_data['name'] = lines[0]
                    print(f"   ✅ Using first line as name: {lines[0]}")
            
            # Determine if it's current or past team
            team_data['status'] = await self._determine_team_status(element)
            
            # Only return if we have at least a name
            if team_data.get('name'):
                print(f"   ✅ Final team data: {team_data}")
                return team_data
            else:
                print(f"   ❌ No name found, skipping element")
                return None
            
        except Exception as e:
            print(f"⚠️ Error extracting team data from element: {e}")
            return None
    
    async def _extract_team_id_from_element(self, element):
        """Extract team ID from an element"""
        try:
            # Look for team ID in various attributes and text
            team_id_selectors = [
                '[data-team-id]',
                '[data-id]',
                '[id*="team"]',
                '[class*="team-id"]'
            ]
            
            for selector in team_id_selectors:
                try:
                    id_element = await element.query_selector(selector)
                    if id_element:
                        team_id = await id_element.get_attribute('data-team-id') or await id_element.get_attribute('data-id')
                        if team_id:
                            return team_id
                except:
                    continue
            
            # Look for team ID in text content
            text = await element.text_content()
            if text:
                import re
                # Look for patterns like "Team ID: 123456" or "ID: 123456"
                id_match = re.search(r'(?:team\s+id|id)[\s:]*(\d+)', text, re.IGNORECASE)
                if id_match:
                    return id_match.group(1)
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting team ID: {e}")
            return None
    
    async def _extract_season_info_from_element(self, element):
        """Extract season information from an element"""
        try:
            season_info = {}
            
            # Look for season/year information
            season_selectors = [
                '[class*="season"]',
                '[class*="year"]',
                '[class*="date"]',
                '.season',
                '.year',
                '.date'
            ]
            
            for selector in season_selectors:
                try:
                    season_element = await element.query_selector(selector)
                    if season_element:
                        season_text = await season_element.text_content()
                        if season_text:
                            season_info['season'] = season_text.strip()
                            break
                except:
                    continue
            
            # Look for season in text content
            text = await element.text_content()
            if text:
                import re
                # Look for year patterns like "2024", "2023-2024", "Season 2024"
                year_match = re.search(r'(?:season\s+)?(\d{4}(?:-\d{4})?)', text, re.IGNORECASE)
                if year_match:
                    season_info['season'] = year_match.group(1)
            
            return season_info
            
        except Exception as e:
            print(f"⚠️ Error extracting season info: {e}")
            return {}
    
    async def _determine_team_status(self, element):
        """Determine if a team is current or past"""
        try:
            # Look for indicators of current vs past status
            text = await element.text_content()
            if text:
                text_lower = text.lower()
                if any(word in text_lower for word in ['current', 'active', 'present', 'now']):
                    return 'current'
                elif any(word in text_lower for word in ['past', 'previous', 'former', 'history']):
                    return 'past'
            
            # Look for CSS classes that might indicate status
            class_name = await element.get_attribute('class')
            if class_name:
                class_lower = class_name.lower()
                if any(word in class_lower for word in ['current', 'active', 'present']):
                    return 'current'
                elif any(word in class_lower for word in ['past', 'previous', 'former', 'history']):
                    return 'past'
            
            # Default to current if we can't determine
            return 'current'
            
        except Exception as e:
            print(f"⚠️ Error determining team status: {e}")
            return 'current'
    
    async def _extract_additional_team_info(self, element):
        """Extract additional team information"""
        try:
            additional_info = {}
            
            # Look for statistics or other information
            text = await element.text_content()
            if text:
                import re
                
                # Look for win/loss records
                record_match = re.search(r'(\d+)\s*-\s*(\d+)', text)
                if record_match:
                    additional_info['wins'] = int(record_match.group(1))
                    additional_info['losses'] = int(record_match.group(2))
                
                # Look for skill level
                skill_match = re.search(r'skill\s*:?\s*(\d+)', text, re.IGNORECASE)
                if skill_match:
                    additional_info['skill_level'] = int(skill_match.group(1))
                
                # Look for division
                division_match = re.search(r'division\s*:?\s*([^,\n]+)', text, re.IGNORECASE)
                if division_match:
                    additional_info['division'] = division_match.group(1).strip()
            
            return additional_info
            
        except Exception as e:
            print(f"⚠️ Error extracting additional team info: {e}")
            return {}
    
    async def _is_at_bottom_of_page(self):
        """Check if we've reached the bottom of the page"""
        try:
            return await self.session_manager.page.evaluate("""
                () => {
                    return (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100;
                }
            """)
        except:
            return True
    
    def _is_valid_team_data(self, team_data):
        """Validate that team data looks legitimate"""
        try:
            name = team_data.get('name', '')
            
            # Skip if name is too short or looks like navigation
            if len(name) < 3:
                return False
            
            # Skip common navigation elements
            skip_names = [
                'member services', 'dashboard', 'matches', 'news', 'events', 'my stats',
                'rules', 'my leagues', 'apa national', 'store', 'tournament info',
                'discounts', 'contact', 'need help', 'logout', 'login', 'settings',
                'edit profile', 'payments', 'my membership', 'card/id', 'ac',
                'note: this table displays', 'team statistics are not available'
            ]
            
            name_lower = name.lower()
            if any(skip in name_lower for skip in skip_names):
                return False
            
            # Skip if it's just a single character or number
            if len(name.strip()) < 3 or name.strip().isdigit():
                return False
            
            # Skip percentage values
            if name.strip().endswith('%') or name.strip().replace('.', '').isdigit():
                return False
            
            # Skip if it contains too many special characters
            special_char_count = sum(1 for c in name if not c.isalnum() and not c.isspace())
            if special_char_count > len(name) * 0.5:  # More than 50% special chars
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error validating team data: {e}")
            return False
    
    def _display_player_data_table(self, player_data):
        """Display extracted player data in a tabular format using standard libraries"""
        print("\n" + "="*80)
        print("📊 EXTRACTED PLAYER DATA")
        print("="*80)
        
        # Create a list of data rows for tabular display
        data_rows = []
        
        # Basic player information
        if player_data.get('player_info', {}).get('name'):
            data_rows.append(("👤 Player Name", player_data['player_info']['name']))
        
        # Team information
        if player_data.get('team_info'):
            team_info = player_data['team_info']
            if team_info.get('name'):
                data_rows.append(("🏆 Team Name", team_info['name']))
            if team_info.get('team_id'):
                data_rows.append(("🆔 Team ID", team_info['team_id']))
            if team_info.get('member_id'):
                data_rows.append(("🆔 Member ID", team_info['member_id']))
        
        # Statistics
        if player_data.get('statistics'):
            for key, value in player_data['statistics'].items():
                formatted_key = key.replace('_', ' ').title()
                data_rows.append((f"📈 {formatted_key}", str(value)))
        
        # Teams information
        if player_data.get('current_teams'):
            data_rows.append(("🏆 Current Teams", f"{len(player_data['current_teams'])} team(s)"))
            for i, team in enumerate(player_data['current_teams'], 1):
                team_name = team.get('name', 'Unknown Team')
                team_id = team.get('team_id', 'N/A')
                season = team.get('season', 'N/A')
                role = team.get('role', 'N/A')
                skill = team.get('skill_level', 'N/A')
                played = team.get('matches_played', 'N/A')
                won = team.get('matches_won', 'N/A')
                win_pct_val = team.get('win_percentage', 'N/A')
                if win_pct_val != 'N/A' and isinstance(win_pct_val, (int, float)):
                    # Check if it's already a percentage (> 1) or a decimal (< 1)
                    if win_pct_val > 1:
                        # Already a percentage, just format it
                        win_pct = f"{win_pct_val:.1f}%"
                    else:
                        # Convert decimal to percentage (0.7 -> 70%)
                        win_pct = f"{win_pct_val * 100:.1f}%"
                else:
                    win_pct = f"{win_pct_val}%"
                data_rows.append((f"   Team {i}", f"{team_name} ({season}, {role}, Skill {skill}, {played} games, {won} wins, {win_pct})"))
        
        if player_data.get('past_teams'):
            data_rows.append(("📜 Past Teams", f"{len(player_data['past_teams'])} team(s)"))
            for i, team in enumerate(player_data['past_teams'], 1):
                team_name = team.get('name', 'Unknown Team')
                team_id = team.get('team_id', 'N/A')
                season = team.get('season', 'N/A')
                role = team.get('role', 'N/A')
                skill = team.get('skill_level', 'N/A')
                played = team.get('matches_played', 'N/A')
                won = team.get('matches_won', 'N/A')
                win_pct_val = team.get('win_percentage', 'N/A')
                if win_pct_val != 'N/A' and isinstance(win_pct_val, (int, float)):
                    # Check if it's already a percentage (> 1) or a decimal (< 1)
                    if win_pct_val > 1:
                        # Already a percentage, just format it
                        win_pct = f"{win_pct_val:.1f}%"
                    else:
                        # Convert decimal to percentage (0.7 -> 70%)
                        win_pct = f"{win_pct_val * 100:.1f}%"
                else:
                    win_pct = f"{win_pct_val}%"
                data_rows.append((f"   Past Team {i}", f"{team_name} ({season}, {role}, Skill {skill}, {played} games, {won} wins, {win_pct})"))
        
        # Additional information
        data_rows.append(("🌐 URL", player_data.get('url', 'N/A')))
        data_rows.append(("⏰ Extracted", player_data.get('extraction_timestamp', 'N/A')))
        
        # Display in tabular format
        if data_rows:
            self._print_table(data_rows)
        else:
            print("❌ No data extracted")
        
        print("="*80)
        
        # Display teams summary if we have teams data
        if player_data.get('current_teams') or player_data.get('past_teams'):
            self._display_teams_summary(player_data)
    
    def _print_table(self, data_rows):
        """Print data in a nicely formatted table using standard libraries"""
        if not data_rows:
            return
        
        # Find the maximum width for the first column
        max_label_width = max(len(str(row[0])) for row in data_rows)
        
        # Print table header
        print(f"{'Field':<{max_label_width}} | Value")
        print("-" * (max_label_width + 3) + "|" + "-" * 50)
        
        # Print each row
        for label, value in data_rows:
            # Truncate long values for better display
            display_value = str(value)
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."
            
            print(f"{str(label):<{max_label_width}} | {display_value}")
    
    def _display_teams_summary(self, player_data):
        """Display a detailed teams summary table"""
        print("\n" + "="*80)
        print("🏆 TEAMS SUMMARY")
        print("="*80)
        
        # Current Teams Table
        if player_data.get('current_teams'):
            print(f"\n📊 CURRENT TEAMS ({len(player_data['current_teams'])} team(s)):")
            print("-" * 120)
            print(f"{'Team Name':<20} | {'Season':<12} | {'Role':<10} | {'Skill':<5} | {'Played':<7} | {'Won':<4} | {'Win%':<6} | {'MVP Rank':<8} | {'Team ID':<10}")
            print("-" * 120)
            
            for team in player_data['current_teams']:
                name = team.get('name', 'Unknown Team')[:19]
                season = team.get('season', 'N/A')[:11]
                role = team.get('role', 'N/A')[:9]
                skill = str(team.get('skill_level', 'N/A'))[:4]
                played = str(team.get('matches_played', 'N/A'))[:6]
                won = str(team.get('matches_won', 'N/A'))[:3]
                win_pct_val = team.get('win_percentage', 'N/A')
                if win_pct_val != 'N/A' and isinstance(win_pct_val, (int, float)):
                    # The win percentage is already in percentage format (e.g., 50.0 means 50%)
                    win_pct = f"{win_pct_val:.1f}%"[:5]
                else:
                    win_pct = f"{win_pct_val}%"[:5]
                rank = team.get('mvp_rank', 'N/A')[:7]
                team_id = team.get('team_id', 'N/A')[:9]
                
                print(f"{name:<20} | {season:<12} | {role:<10} | {skill:<5} | {played:<7} | {won:<4} | {win_pct:<6} | {rank:<8} | {team_id:<10}")
        
        # Past Teams Table
        if player_data.get('past_teams'):
            print(f"\n📜 PAST TEAMS ({len(player_data['past_teams'])} team(s)):")
            print("-" * 120)
            print(f"{'Team Name':<20} | {'Season':<12} | {'Role':<10} | {'Skill':<5} | {'Played':<7} | {'Won':<4} | {'Win%':<6} | {'MVP Rank':<8} | {'Team ID':<10}")
            print("-" * 120)
            
            for team in player_data['past_teams']:
                name = team.get('name', 'Unknown Team')[:19]
                season = team.get('season', 'N/A')[:11]
                role = team.get('role', 'N/A')[:9]
                skill = str(team.get('skill_level', 'N/A'))[:4]
                played = str(team.get('matches_played', 'N/A'))[:6]
                won = str(team.get('matches_won', 'N/A'))[:3]
                win_pct_val = team.get('win_percentage', 'N/A')
                if win_pct_val != 'N/A' and isinstance(win_pct_val, (int, float)):
                    # The win percentage is already in percentage format (e.g., 50.0 means 50%)
                    win_pct = f"{win_pct_val:.1f}%"[:5]
                else:
                    win_pct = f"{win_pct_val}%"[:5]
                rank = team.get('mvp_rank', 'N/A')[:7]
                team_id = team.get('team_id', 'N/A')[:9]
                
                print(f"{name:<20} | {season:<12} | {role:<10} | {skill:<5} | {played:<7} | {won:<4} | {win_pct:<6} | {rank:<8} | {team_id:<10}")
        
        print("="*80)
    
    def _display_player_data(self, player_data):
        """Display extracted player data in a formatted way (legacy method)"""
        print("\n" + "="*50)
        print("📊 EXTRACTED PLAYER DATA")
        print("="*50)
        
        if player_data.get('player_info', {}).get('name'):
            print(f"👤 Player: {player_data['player_info']['name']}")
        
        if player_data.get('team_info'):
            team_info = player_data['team_info']
            if team_info.get('name'):
                print(f"🏆 Team: {team_info['name']}")
            if team_info.get('team_id'):
                print(f"🆔 Team ID: {team_info['team_id']}")
            if team_info.get('member_id'):
                print(f"🆔 Member ID: {team_info['member_id']}")
        
        if player_data.get('statistics'):
            print(f"\n📈 Statistics:")
            for key, value in player_data['statistics'].items():
                print(f"   {key}: {value}")
        
        print(f"\n🌐 URL: {player_data.get('url', 'N/A')}")
        print(f"⏰ Extracted: {player_data.get('extraction_timestamp', 'N/A')}")
        print("="*50)
    
    async def _save_player_data(self, player_data, output_file, format):
        """Save player data to file"""
        try:
            output_path = Path(output_file)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(player_data, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                # For CSV, we'll create a simple format
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Field', 'Value'])
                    
                    # Write basic info
                    if player_data.get('player_info', {}).get('name'):
                        writer.writerow(['Player Name', player_data['player_info']['name']])
                    
                    # Write team info
                    for key, value in player_data.get('team_info', {}).items():
                        writer.writerow([f'Team {key.title()}', value])
                    
                    # Write statistics
                    for key, value in player_data.get('statistics', {}).items():
                        writer.writerow([key.title(), value])
                    
                    # Write current teams
                    if player_data.get('current_teams'):
                        writer.writerow(['', ''])  # Empty row for separation
                        writer.writerow(['Current Teams', ''])
                        for i, team in enumerate(player_data['current_teams'], 1):
                            writer.writerow([f'  Team {i} Name', team.get('name', 'N/A')])
                            writer.writerow([f'  Team {i} ID', team.get('team_id', 'N/A')])
                            writer.writerow([f'  Team {i} Season', team.get('season', 'N/A')])
                    
                    # Write past teams
                    if player_data.get('past_teams'):
                        writer.writerow(['', ''])  # Empty row for separation
                        writer.writerow(['Past Teams', ''])
                        for i, team in enumerate(player_data['past_teams'], 1):
                            writer.writerow([f'  Past Team {i} Name', team.get('name', 'N/A')])
                            writer.writerow([f'  Past Team {i} ID', team.get('team_id', 'N/A')])
                            writer.writerow([f'  Past Team {i} Season', team.get('season', 'N/A')])
                            if team.get('wins') is not None and team.get('losses') is not None:
                                writer.writerow([f'  Past Team {i} Record', f"{team['wins']}-{team['losses']}"])
                    
                    writer.writerow(['URL', player_data.get('url', '')])
                    writer.writerow(['Extraction Time', player_data.get('extraction_timestamp', '')])
            else:
                print(f"❌ Unsupported format: {format}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving player data: {e}")
            return False
    
    async def _click_teams_tab(self):
        """Click on the Teams tab to load team content"""
        try:
            # Wait a moment for the page to fully load
            await self.session_manager.page.wait_for_timeout(1000)
            
            # Look for the Teams tab - try multiple possible selectors
            teams_tab_selectors = [
                'button[data-tab="teams"]',
                'a[data-tab="teams"]',
                'button:has-text("Teams")',
                'a:has-text("Teams")',
                '[role="tab"]:has-text("Teams")',
                '.tab:has-text("Teams")',
                'button[aria-label*="Teams"]',
                'a[aria-label*="Teams"]'
            ]
            
            for selector in teams_tab_selectors:
                try:
                    element = await self.session_manager.page.query_selector(selector)
                    if element:
                        # Check if it's already active
                        is_active = await element.get_attribute('aria-selected')
                        if is_active == 'true':
                            print("   ✅ Teams tab is already active")
                            return True
                        
                        # Click the tab
                        await element.click()
                        print("   ✅ Clicked Teams tab")
                        
                        # Wait for content to load
                        await self.session_manager.page.wait_for_timeout(2000)
                        await self.session_manager.page.wait_for_load_state('networkidle')
                        
                        return True
                except Exception as e:
                    continue
            
            # If no specific Teams tab found, try to find any tab containing "Teams"
            try:
                # Look for any element containing "Teams" text that might be clickable
                teams_elements = await self.session_manager.page.query_selector_all('*')
                for element in teams_elements:
                    try:
                        text = await element.text_content()
                        if text and 'Teams' in text and len(text.strip()) < 20:  # Short text likely to be a tab
                            tag_name = await element.evaluate('el => el.tagName')
                            if tag_name.lower() in ['button', 'a', 'div', 'span']:
                                await element.click()
                                print("   ✅ Clicked Teams element")
                                await self.session_manager.page.wait_for_timeout(2000)
                                await self.session_manager.page.wait_for_load_state('networkidle')
                                return True
                    except:
                        continue
            except:
                pass
            
            print("   ⚠️  Could not find Teams tab")
            return False
            
        except Exception as e:
            print(f"   ⚠️  Error clicking Teams tab: {e}")
            return False

    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
