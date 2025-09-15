"""
Extract team action for APA Stat Scraper
Extracts team statistics from a specific team page
"""

import asyncio
import json
import re
from pathlib import Path
from .base import BaseAction
from .team_data_extractor import TeamDataExtractor
from config import config
from cache_manager import CacheManager

class ExtractTeamAction(BaseAction):
    """Action to extract team statistics from a specific team page"""
    
    def run(self, team_id=None, output_file=None, format='json', headless=False, terminal_output=True, league=None, expand=False, no_cache=False):
        """Run the extract team action"""
        print("🚀 APA Stat Scraper - Extract Team")
        
        # Determine league to use (CLI param > config > default)
        self.league = self._determine_league(league)
        print("=" * 40)
        
        # If no team_id provided, prompt for it
        if not team_id:
            team_id = input("Enter Team ID: ").strip()
        
        if not team_id:
            print("❌ Team ID is required")
            return False
        
        # Validate team_id is numeric
        if not team_id.isdigit():
            print("❌ Team ID must be numeric")
            return False
        
        # Construct URL from team_id
        team_url = f"https://league.poolplayers.com/team/{team_id}"
        print(f"📍 Team URL: {team_url}")
        
        # Store team_id as instance variable
        self.team_id = team_id
        
        # Initialize cache manager
        self.cache_manager = CacheManager()
        self.no_cache = no_cache
        self.expand = expand
        
        return self._run_with_session(
            team_url=team_url,
            output_file=output_file,
            format=format,
            headless=headless,
            terminal_output=terminal_output,
            expand=expand
        )
    
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
    
    async def _run_async(self, team_url, output_file=None, format='json', headless=False, terminal_output=True, expand=False):
        """Async implementation of team extraction"""
        try:
            # Check cache first (unless --no-cache is specified)
            if not self.no_cache:
                print("🔍 Checking cache for team data...")
                cached_data = self.cache_manager.get_cached_data('team', self.team_id, self.league, self.expand)
                if cached_data:
                    print("✅ Found valid cached data!")
                    print(f"   📅 Cached at: {cached_data.get('_cache_info', {}).get('cached_at', 'Unknown')}")
                    
                    # Display cached data
                    if terminal_output:
                        self._display_team_data_table(cached_data)
                    else:
                        self._display_team_data(cached_data)
                    
                    # Save to file if requested
                    if output_file:
                        success = await self._save_team_data(cached_data, output_file, format)
                        if success:
                            print(f"💾 Team data saved to: {output_file}")
                        else:
                            print("❌ Failed to save team data")
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
            
            # Navigate to team page
            print(f"🌐 Navigating to team page...")
            print(f"📍 URL: {team_url}")
            
            await self.session_manager.page.goto(team_url)
            await self.session_manager.page.wait_for_load_state('networkidle')
            
            # Handle any notifications that might appear
            await self.session_manager.handle_notifications()
            
            # Extract team data
            print("📊 Extracting team data...")
            team_data = await self._extract_team_data()
            
            if not team_data:
                print("❌ Failed to extract team data")
                return False
            
            # Expand player data if requested
            if expand:
                print("🔍 Expanding player data with detailed statistics...")
                team_data = await self._expand_player_data(team_data)
            
            # Cache the extracted data (unless --no-cache is specified)
            if not self.no_cache:
                print("💾 Caching extracted data...")
                cache_success = self.cache_manager.cache_data('team', self.team_id, team_data, self.league, self.expand)
                if cache_success:
                    print("✅ Data cached successfully")
                else:
                    print("⚠️ Failed to cache data")
            
            # Display extracted data
            if terminal_output:
                self._display_team_data_table(team_data)
            else:
                self._display_team_data(team_data)
            
            # Save to file if requested
            if output_file:
                success = await self._save_team_data(team_data, output_file, format)
                if success:
                    print(f"💾 Team data saved to: {output_file}")
                else:
                    print("❌ Failed to save team data")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return False
    
    async def _extract_team_data(self):
        """Extract team data from the current page"""
        try:
            # Wait for page to load completely
            await self.session_manager.page.wait_for_load_state('networkidle')
            
            # Get page title and URL for context
            title = await self.session_manager.page.title()
            current_url = self.session_manager.page.url
            
            print(f"📄 Page Title: {title}")
            print(f"📍 Current URL: {current_url}")
            
            # Extract basic team information
            team_data = {
                'url': current_url,
                'page_title': title,
                'extraction_timestamp': self._get_timestamp(),
                'team_info': {},
                'players': [],
                'raw_data': {}
            }
            
            # Try to extract team name from page title or content
            team_name = await self._extract_team_name()
            if team_name:
                team_data['team_info']['name'] = team_name
            
            # Extract team ID from URL
            team_id_match = re.search(r'/team/(\d+)', current_url)
            if team_id_match:
                team_data['team_info']['team_id'] = team_id_match.group(1)
            
            # Extract players information
            print("👥 Extracting players information...")
            players = await self._extract_players()
            if players:
                team_data['players'] = players
                print(f"   ✅ Found {len(players)} player(s)")
            
            # Extract any additional data we can find
            additional_data = await self._extract_additional_data()
            if additional_data:
                team_data['raw_data'].update(additional_data)
            
            return team_data
            
        except Exception as e:
            print(f"❌ Error extracting team data: {e}")
            return None
    
    async def _extract_team_name(self):
        """Extract team name from the page"""
        try:
            # Try multiple selectors for team name
            name_selectors = [
                'h1',
                'h2',
                '.team-name',
                '.team-title',
                '[class*="team"]',
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
                            name = re.sub(r'^(Team|Member|Player)\s*[-:]?\s*', '', name, flags=re.IGNORECASE)
                            name = re.sub(r'\s*[-:]\s*.*$', '', name)  # Remove everything after dash/colon
                            if len(name) > 2:  # Reasonable name length
                                return name
                except:
                    continue
            
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting team name: {e}")
            return None
    
    async def _extract_players(self):
        """Extract players data from the team page"""
        try:
            players = []
            
            # Look for table rows that contain player data
            table_rows = await self.session_manager.page.query_selector_all('table tbody tr')
            
            for i, row in enumerate(table_rows):
                # Skip header rows (those with 0 cells or th elements)
                cells = await row.query_selector_all('td')
                if len(cells) == 0:
                    continue  # Skip header rows with no td cells
                    
                if len(cells) >= 6:  # Should have Player Name, Skill Level, Matches Won/Played, Win %, PPM, PA columns
                    player_data = await self._extract_player_data_from_row(cells)
                    if player_data and self._is_valid_player_data(player_data):
                        players.append(player_data)
            
            return players
            
        except Exception as e:
            print(f"⚠️ Error extracting players: {e}")
            return []
    
    async def _extract_player_data_from_row(self, cells):
        """Extract player data from a table row (array of td elements)"""
        try:
            if len(cells) < 6:
                return None
                
            player_data = {}
            
            # Cell 0: Player Name, Member ID, and UserId from URL
            name_cell = await cells[0].text_content()
            if name_cell:
                name_text = name_cell.strip()
                
                # Extract member ID from patterns like "#19162437" at the end
                member_id_match = re.search(r'#(\d+)$', name_text)
                if member_id_match:
                    player_data['member_id'] = member_id_match.group(1)
                    # Remove member ID from name
                    name = re.sub(r'#\d+$', '', name_text).strip()
                else:
                    # No member ID found, use the full text as name
                    name = name_text
                
                player_data['name'] = name
                
                # Extract UserId from the player's URL (if it's a link)
                try:
                    # Look for a link within the name cell
                    link_element = await cells[0].query_selector('a')
                    if link_element:
                        href = await link_element.get_attribute('href')
                        if href:
                            # Extract UserId from URL pattern like /Philadelphia/member/3287288
                            userid_match = re.search(r'/member/(\d+)', href)
                            if userid_match:
                                player_data['userid'] = userid_match.group(1)
                except Exception as e:
                    # If URL extraction fails, continue without userid
                    pass
            
            # Cell 1: Skill Level
            skill_cell = await cells[1].text_content()
            if skill_cell and skill_cell.strip().isdigit():
                player_data['skill_level'] = int(skill_cell.strip())
            
            # Cell 2: Matches Won/Played (format: "Won/Played")
            matches_cell = await cells[2].text_content()
            if matches_cell and '/' in matches_cell:
                parts = matches_cell.strip().split('/')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    player_data['matches_won'] = int(parts[0])
                    player_data['matches_played'] = int(parts[1])
            
            # Cell 3: Win %
            win_pct_cell = await cells[3].text_content()
            if win_pct_cell:
                win_pct_match = re.search(r'(\d+(?:\.\d+)?)%', win_pct_cell)
                if win_pct_match:
                    player_data['win_percentage'] = float(win_pct_match.group(1))
            
            # Cell 4: PPM (Points Per Match)
            ppm_cell = await cells[4].text_content()
            if ppm_cell:
                ppm_match = re.search(r'(\d+(?:\.\d+)?)', ppm_cell)
                if ppm_match:
                    player_data['ppm'] = float(ppm_match.group(1))
            
            # Cell 5: PA (Points Against)
            pa_cell = await cells[5].text_content()
            if pa_cell:
                pa_match = re.search(r'(\d+(?:\.\d+)?)', pa_cell)
                if pa_match:
                    player_data['pa'] = float(pa_match.group(1))
            
            # Calculate win percentage if we have played and won
            if player_data.get('matches_played') and player_data.get('matches_won') is not None:
                played = player_data['matches_played']
                won = player_data['matches_won']
                if played > 0:
                    win_pct = (won / played) * 100
                    player_data['win_percentage'] = round(win_pct, 1)
            
            return player_data if player_data.get('name') else None
            
        except Exception as e:
            print(f"⚠️ Error extracting player data from row: {e}")
            return None
    
    def _is_valid_player_data(self, player_data):
        """Validate that player data looks legitimate"""
        try:
            name = player_data.get('name', '')
            
            # Skip if name is too short or looks like navigation
            if len(name) < 3:
                return False
            
            # Skip common navigation elements
            skip_names = [
                'member services', 'dashboard', 'matches', 'news', 'events', 'my stats',
                'rules', 'my leagues', 'apa national', 'store', 'tournament info',
                'discounts', 'contact', 'need help', 'logout', 'login', 'settings',
                'edit profile', 'payments', 'my membership', 'card/id', 'ac',
                'note: this table displays', 'team statistics are not available',
                'player name', 'skill level', 'matches won/played', 'win %', 'ppm', 'pa'
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
            print(f"⚠️ Error validating player data: {e}")
            return False
    
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
    
    def _display_team_data_table(self, team_data):
        """Display extracted team data in a tabular format"""
        print("\n" + "="*80)
        print("📊 EXTRACTED TEAM DATA")
        print("="*80)
        
        # Create a list of data rows for tabular display
        data_rows = []
        
        # Basic team information
        if team_data.get('team_info', {}).get('name'):
            data_rows.append(("🏆 Team Name", team_data['team_info']['name']))
        
        if team_data.get('team_info', {}).get('team_id'):
            data_rows.append(("🆔 Team ID", team_data['team_info']['team_id']))
        
        # Players information
        if team_data.get('players'):
            data_rows.append(("👥 Players", f"{len(team_data['players'])} player(s)"))
        
        # Additional information
        data_rows.append(("🌐 URL", team_data.get('url', 'N/A')))
        data_rows.append(("⏰ Extracted", team_data.get('extraction_timestamp', 'N/A')))
        
        # Display in tabular format
        if data_rows:
            self._print_table(data_rows)
        else:
            print("❌ No data extracted")
        
        print("="*80)
        
        # Display players summary if we have players data
        if team_data.get('players'):
            self._display_players_summary(team_data)
    
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
    
    def _display_players_summary(self, team_data):
        """Display a detailed players summary table"""
        print("\n" + "="*80)
        print("👥 PLAYERS SUMMARY")
        print("="*80)
        
        # Players Table
        if team_data.get('players'):
            team_id = team_data.get('team_info', {}).get('team_id', 'Unknown')
            print(f"\n📊 TEAM PLAYERS - Team ID: {team_id} ({len(team_data['players'])} player(s)):")
            
            # Check if we have expanded data
            has_expanded_data = any(player.get('min_skill') is not None for player in team_data['players'])
            
            if has_expanded_data:
                print("-" * 180)
                print(f"{'Player Name':<20} | {'Member ID':<10} | {'UserId':<10} | {'Skill Level':<11} | {'Matches Won/Played':<18} | {'Win %':<6} | {'PPM':<6} | {'PA':<6} | {'Min Skill':<9} | {'Max Skill':<9} | {'Seasons':<7}")
                print("-" * 180)
            else:
                print("-" * 140)
                print(f"{'Player Name':<20} | {'Member ID':<10} | {'UserId':<10} | {'Skill Level':<11} | {'Matches Won/Played':<18} | {'Win %':<6} | {'PPM':<6} | {'PA':<6}")
                print("-" * 140)
            
            for player in team_data['players']:
                name = player.get('name', 'Unknown Player')[:19]
                member_id = player.get('member_id', 'N/A')[:9]
                userid = player.get('userid', 'N/A')[:9]
                skill = str(player.get('skill_level', 'N/A'))[:10]
                
                # Format matches won/played
                won = player.get('matches_won', 'N/A')
                played = player.get('matches_played', 'N/A')
                if won != 'N/A' and played != 'N/A':
                    matches = f"{won}/{played}"[:17]
                else:
                    matches = f"{won}/{played}"[:17]
                
                # Format win percentage
                win_pct_val = player.get('win_percentage', 'N/A')
                if win_pct_val != 'N/A' and isinstance(win_pct_val, (int, float)):
                    win_pct = f"{win_pct_val:.1f}%"[:5]
                else:
                    win_pct = f"{win_pct_val}%"[:5]
                
                # Format PPM
                ppm_val = player.get('ppm', 'N/A')
                if ppm_val != 'N/A' and isinstance(ppm_val, (int, float)):
                    ppm = f"{ppm_val:.1f}"[:5]
                else:
                    ppm = f"{ppm_val}"[:5]
                
                # Format PA
                pa_val = player.get('pa', 'N/A')
                if pa_val != 'N/A' and isinstance(pa_val, (int, float)):
                    pa = f"{pa_val:.1f}"[:5]
                else:
                    pa = f"{pa_val}"[:5]
                
                if has_expanded_data:
                    # Format expanded data
                    min_skill = str(player.get('min_skill', 'N/A'))[:8]
                    max_skill = str(player.get('max_skill', 'N/A'))[:8]
                    seasons = str(player.get('seasons_played', 'N/A'))[:6]
                    
                    print(f"{name:<20} | {member_id:<10} | {userid:<10} | {skill:<11} | {matches:<18} | {win_pct:<6} | {ppm:<6} | {pa:<6} | {min_skill:<9} | {max_skill:<9} | {seasons:<7}")
                else:
                    print(f"{name:<20} | {member_id:<10} | {userid:<10} | {skill:<11} | {matches:<18} | {win_pct:<6} | {ppm:<6} | {pa:<6}")
        
        print("="*80)
    
    def _display_team_data(self, team_data):
        """Display extracted team data in a formatted way (legacy method)"""
        print("\n" + "="*50)
        print("📊 EXTRACTED TEAM DATA")
        print("="*50)
        
        if team_data.get('team_info', {}).get('name'):
            print(f"🏆 Team: {team_data['team_info']['name']}")
        
        if team_data.get('team_info', {}).get('team_id'):
            print(f"🆔 Team ID: {team_data['team_info']['team_id']}")
        
        if team_data.get('players'):
            print(f"\n👥 Players ({len(team_data['players'])} player(s)):")
            for i, player in enumerate(team_data['players'], 1):
                name = player.get('name', 'Unknown Player')
                member_id = player.get('member_id', 'N/A')
                userid = player.get('userid', 'N/A')
                skill = player.get('skill_level', 'N/A')
                won = player.get('matches_won', 'N/A')
                played = player.get('matches_played', 'N/A')
                win_pct = player.get('win_percentage', 'N/A')
                ppm = player.get('ppm', 'N/A')
                pa = player.get('pa', 'N/A')
                
                print(f"   {i}. {name} (Member ID: {member_id}, UserId: {userid}, Skill: {skill}, {won}/{played}, {win_pct}%, PPM: {ppm}, PA: {pa})")
        
        print(f"\n🌐 URL: {team_data.get('url', 'N/A')}")
        print(f"⏰ Extracted: {team_data.get('extraction_timestamp', 'N/A')}")
        print("="*50)
    
    async def _save_team_data(self, team_data, output_file, format):
        """Save team data to file"""
        try:
            output_path = Path(output_file)
            
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(team_data, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                # For CSV, we'll create a simple format
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Field', 'Value'])
                    
                    # Write basic info
                    if team_data.get('team_info', {}).get('name'):
                        writer.writerow(['Team Name', team_data['team_info']['name']])
                    
                    if team_data.get('team_info', {}).get('team_id'):
                        writer.writerow(['Team ID', team_data['team_info']['team_id']])
                    
                    # Write players
                    if team_data.get('players'):
                        writer.writerow(['', ''])  # Empty row for separation
                        writer.writerow(['Players', ''])
                        for i, player in enumerate(team_data['players'], 1):
                            writer.writerow([f'  Player {i} Name', player.get('name', 'N/A')])
                            writer.writerow([f'  Player {i} Member ID', player.get('member_id', 'N/A')])
                            writer.writerow([f'  Player {i} UserId', player.get('userid', 'N/A')])
                            writer.writerow([f'  Player {i} Skill Level', player.get('skill_level', 'N/A')])
                            writer.writerow([f'  Player {i} Matches Won', player.get('matches_won', 'N/A')])
                            writer.writerow([f'  Player {i} Matches Played', player.get('matches_played', 'N/A')])
                            writer.writerow([f'  Player {i} Win %', player.get('win_percentage', 'N/A')])
                            writer.writerow([f'  Player {i} PPM', player.get('ppm', 'N/A')])
                            writer.writerow([f'  Player {i} PA', player.get('pa', 'N/A')])
                            
                            # Add expanded data if available
                            if player.get('min_skill') is not None:
                                writer.writerow([f'  Player {i} Min Skill', player.get('min_skill', 'N/A')])
                                writer.writerow([f'  Player {i} Max Skill', player.get('max_skill', 'N/A')])
                                writer.writerow([f'  Player {i} Seasons Played', player.get('seasons_played', 'N/A')])
                    
                    writer.writerow(['URL', team_data.get('url', '')])
                    writer.writerow(['Extraction Time', team_data.get('extraction_timestamp', '')])
            else:
                print(f"❌ Unsupported format: {format}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving team data: {e}")
            return False
    
    async def _expand_player_data(self, team_data):
        """Expand player data with detailed statistics by visiting each player's page"""
        try:
            if not team_data.get('players'):
                return team_data
            
            print(f"   📊 Processing {len(team_data['players'])} players for detailed statistics...")
            
            # Create team data extractor instance
            team_extractor = TeamDataExtractor(self.session_manager)
            
            for i, player in enumerate(team_data['players'], 1):
                userid = player.get('userid')
                if not userid:
                    print(f"   ⚠️  Player {i}: No UserId found, skipping expansion")
                    continue
                
                print(f"   🔍 Player {i}/{len(team_data['players'])}: {player.get('name', 'Unknown')} (UserId: {userid})")
                
                try:
                    # Use the common team data extractor
                    player_stats = await team_extractor.extract_player_team_history(userid, self.league)
                    
                    if player_stats:
                        # Add the expanded data to the player
                        player.update(player_stats)
                        print(f"   ✅ Expanded data: Min Skill: {player_stats.get('min_skill', 'N/A')}, Max Skill: {player_stats.get('max_skill', 'N/A')}, Seasons: {player_stats.get('seasons_played', 'N/A')}")
                    else:
                        print(f"   ⚠️  No team history found for {player.get('name', 'Unknown')}")
                        # Set default values
                        player['min_skill'] = 'N/A'
                        player['max_skill'] = 'N/A'
                        player['seasons_played'] = 'N/A'
                
                except Exception as e:
                    print(f"   ❌ Error processing {player.get('name', 'Unknown')}: {e}")
                    # Set default values on error
                    player['min_skill'] = 'N/A'
                    player['max_skill'] = 'N/A'
                    player['seasons_played'] = 'N/A'
            
            print("   ✅ Player data expansion completed")
            return team_data
            
        except Exception as e:
            print(f"❌ Error expanding player data: {e}")
            return team_data


    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
