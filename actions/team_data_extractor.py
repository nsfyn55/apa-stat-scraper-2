"""
Common module for extracting team data from player pages.
This module contains shared logic used by both extract-player and extract-team actions.
"""

import re
import asyncio


class TeamDataExtractor:
    """Common team data extraction logic"""
    
    def __init__(self, session_manager):
        self.session_manager = session_manager
    
    async def extract_player_team_history(self, userid, league, max_retries=3):
        """Extract team history for a single player to calculate min_rank, max_rank, seasons_played"""
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid detection
                import random
                delay = random.uniform(2, 4)
                await asyncio.sleep(delay)
                
                # Navigate to player's teams page directly
                teams_url = f"https://league.poolplayers.com/{league}/member/{userid}/teams"
                await self.session_manager.page.goto(teams_url)
                await self.session_manager.page.wait_for_load_state('networkidle')
                await self.session_manager.handle_notifications()
                
                # Add another delay
                await asyncio.sleep(random.uniform(1, 2))
                
                # Click on Teams tab
                teams_tab_clicked = await self._click_teams_tab()
                if not teams_tab_clicked:
                    print(f"   ⚠️  Could not click Teams tab for userid {userid}")
                    if attempt < max_retries - 1:
                        print(f"   🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    return None
                
                # Extract current and past teams using the same logic as extract-player
                current_teams = await self._extract_current_teams()
                past_teams = await self._extract_past_teams()
                
                all_teams = []
                if current_teams:
                    all_teams.extend(current_teams)
                if past_teams:
                    all_teams.extend(past_teams)
                
                if not all_teams:
                    if attempt < max_retries - 1:
                        print(f"   ⚠️  No teams found, retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    return None
                
                # Calculate statistics using the same logic
                ranks = []
                seasons = set()
                
                for team in all_teams:
                    # Extract skill level (should be 1-9) from the skill_level field
                    skill_level = team.get('skill_level')
                    if skill_level is not None and skill_level != 'N/A' and skill_level != '-':
                        try:
                            skill_val = int(skill_level)
                            if 1 <= skill_val <= 9:  # Valid skill level range
                                ranks.append(skill_val)
                        except:
                            pass
                    
                    # Extract season information
                    season = team.get('season')
                    if season and season != 'N/A' and season.strip():
                        seasons.add(season.strip())
                
                # Calculate min_skill, max_skill, seasons_played
                result = {}
                
                if ranks:
                    result['min_skill'] = min(ranks)
                    result['max_skill'] = max(ranks)
                else:
                    result['min_skill'] = 'N/A'
                    result['max_skill'] = 'N/A'
                
                result['seasons_played'] = len(seasons) if seasons else 0
                
                return result
                
            except Exception as e:
                error_msg = str(e).lower()
                is_timeout = 'timeout' in error_msg or 'exceeded' in error_msg
                
                if is_timeout and attempt < max_retries - 1:
                    print(f"   ⚠️  Timeout error for userid {userid}: {e}")
                    print(f"   🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                    await asyncio.sleep(3)  # Wait longer before retry for timeouts
                    continue
                else:
                    print(f"⚠️ Error extracting player team history for userid {userid}: {e}")
                    if attempt < max_retries - 1:
                        print(f"   🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    return None
        
        # If we get here, all retries failed
        print(f"   ❌ Failed to extract team history for userid {userid} after {max_retries} attempts")
        return None

    async def _click_teams_tab(self, max_retries=3):
        """Click on the Teams tab to load team content"""
        for attempt in range(max_retries):
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
                                return True
                            
                            # Click the tab
                            await element.click()
                            
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
                                    await self.session_manager.page.wait_for_timeout(2000)
                                    await self.session_manager.page.wait_for_load_state('networkidle')
                                    return True
                        except:
                            continue
                except:
                    pass
                
                # If we get here, no Teams tab was found
                if attempt < max_retries - 1:
                    print(f"   ⚠️  Teams tab not found, retrying... (attempt {attempt + 2}/{max_retries})")
                    await asyncio.sleep(2)  # Wait before retry
                    continue
                
                return False
                
            except Exception as e:
                error_msg = str(e).lower()
                is_timeout = 'timeout' in error_msg or 'exceeded' in error_msg
                
                if is_timeout and attempt < max_retries - 1:
                    print(f"   ⚠️  Timeout error clicking Teams tab: {e}")
                    print(f"   🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                    await asyncio.sleep(3)  # Wait longer before retry for timeouts
                    continue
                else:
                    print(f"   ⚠️  Error clicking Teams tab: {e}")
                    if attempt < max_retries - 1:
                        print(f"   🔄 Retrying... (attempt {attempt + 2}/{max_retries})")
                        await asyncio.sleep(2)  # Wait before retry
                        continue
                    return False
        
        # If we get here, all retries failed
        print(f"   ❌ Failed to click Teams tab after {max_retries} attempts")
        return False

    async def _extract_current_teams(self):
        """Extract current teams information - using exact same logic as extract-player"""
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
            
            return current_teams
            
        except Exception as e:
            print(f"⚠️ Error extracting current teams: {e}")
            return []

    async def _extract_past_teams(self):
        """Extract past teams information with scrolling to load additional data - using exact same logic as extract-player"""
        try:
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
            
            return past_teams
            
        except Exception as e:
            print(f"⚠️ Error extracting past teams: {e}")
            return []

    async def _scroll_and_extract_past_teams(self):
        """Scroll to load additional past teams data using table-based extraction - stops when no new data loads"""
        try:
            all_teams = []
            previous_count = 0
            scroll_attempts = 0
            max_scroll_attempts = 20  # Safety limit
            
            print("   🔄 Starting scroll loop to load all teams...")
            
            while scroll_attempts < max_scroll_attempts:
                # Extract teams from current view using table-based approach
                current_teams = await self._extract_all_teams_from_table()
                print(f"   🔍 DEBUG: Found {len(current_teams)} teams in current view")
                
                # Add new teams to our collection
                new_teams_added = 0
                for team in current_teams:
                    # Check if this team is already in our collection
                    if not any(t.get('name') == team.get('name') and t.get('season') == team.get('season') for t in all_teams):
                        all_teams.append(team)
                        new_teams_added += 1
                        print(f"   ✅ Found new team: {team.get('name')} ({team.get('season')})")
                    else:
                        print(f"   🔍 DEBUG: Skipping duplicate team: {team.get('name')} ({team.get('season')})")
                
                print(f"   🔍 DEBUG: Total teams so far: {len(all_teams)}")
                
                # Check if we found new teams
                if new_teams_added == 0:
                    # No new teams found, try scrolling once more
                    print(f"   📜 No new teams found, attempting scroll...")
                    
                    # Scroll to bottom
                    await self.session_manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(3)  # Wait at least 2 seconds for content to load
                    
                    # Check for "Load More" or "Show More" buttons
                    load_more_selectors = [
                        'button:has-text("Load More")',
                        'button:has-text("Show More")',
                        'button:has-text("More")',
                        '.load-more',
                        '.show-more',
                        '[data-testid*="load"]',
                        '[data-testid*="more"]'
                    ]
                    
                    load_more_clicked = False
                    for selector in load_more_selectors:
                        try:
                            load_more_btn = await self.session_manager.page.query_selector(selector)
                            if load_more_btn:
                                await load_more_btn.click()
                                await asyncio.sleep(3)  # Wait for content to load
                                load_more_clicked = True
                                print(f"   ✅ Clicked load more button")
                                break
                        except:
                            continue
                    
                    if not load_more_clicked:
                        # No load more button, try scrolling up and down to trigger lazy loading
                        await self.session_manager.page.evaluate("window.scrollTo(0, 0)")
                        await asyncio.sleep(2)
                        await self.session_manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(3)
                    
                    # After scrolling, check if we got any new teams
                    current_teams_after_scroll = await self._extract_all_teams_from_table()
                    new_teams_after_scroll = 0
                    for team in current_teams_after_scroll:
                        if not any(t.get('name') == team.get('name') and t.get('season') == team.get('season') for t in all_teams):
                            all_teams.append(team)
                            new_teams_after_scroll += 1
                            print(f"   ✅ Found new team after scroll: {team.get('name')} ({team.get('season')})")
                    
                    if new_teams_after_scroll == 0:
                        # Still no new teams after scrolling, we're done
                        print(f"   ✅ No new teams found after scrolling, stopping")
                        break
                else:
                    # Found new teams, reset scroll attempts
                    scroll_attempts = 0
                    print(f"   ✅ Found {new_teams_added} new teams, resetting scroll attempts")
                
                scroll_attempts += 1
            
            print(f"   ✅ Scroll complete: Found {len(all_teams)} total teams")
            return all_teams
            
        except Exception as e:
            print(f"⚠️ Error scrolling and extracting past teams: {e}")
            return []

    async def _extract_all_teams_from_table(self):
        """Extract all teams from the current table view - using exact same logic as extract-player"""
        try:
            teams = []
            
            # Look for table rows that contain team data - try multiple selectors
            # We need to extract from BOTH "Current Teams" and "Past Teams" sections
            table_selectors = [
                'table tbody tr',  # Standard table rows
                'table tr',        # All table rows
                '.team-row',
                '.history-row',
                '[data-testid*="team"]',
                '[data-testid*="history"]'
            ]
            
            all_rows = []
            for selector in table_selectors:
                rows = await self.session_manager.page.query_selector_all(selector)
                if rows:
                    all_rows.extend(rows)
            
            # Also specifically look for both "Current Teams" and "Past Teams" sections
            current_teams_section = await self.session_manager.page.query_selector('div:has-text("Current Teams")')
            past_teams_section = await self.session_manager.page.query_selector('div:has-text("Past Teams")')
            
            if current_teams_section:
                current_rows = await current_teams_section.query_selector_all('table tbody tr')
                all_rows.extend(current_rows)
            
            if past_teams_section:
                past_rows = await past_teams_section.query_selector_all('table tbody tr')
                all_rows.extend(past_rows)
            
            # Remove duplicates
            unique_rows = []
            seen_rows = set()
            for row in all_rows:
                row_id = id(row)
                if row_id not in seen_rows:
                    unique_rows.append(row)
                    seen_rows.add(row_id)
            
            for i, row in enumerate(unique_rows):
                if i == 0:  # Skip header row
                    continue
                    
                # Extract data from each cell in the row
                cells = await row.query_selector_all('td')
                
                # Handle different table structures
                if len(cells) >= 2:  # At least 2 cells (team name and some data)
                    team_data = await self._extract_team_data_from_row_flexible(cells)
                    
                    if team_data and self._is_valid_team_data(team_data):
                        teams.append(team_data)
            return teams
            
        except Exception as e:
            print(f"⚠️ Error extracting teams from table: {e}")
            return []

    async def _extract_team_data_from_row(self, cells):
        """Extract team data from a table row (array of td elements) - using exact same logic as extract-player"""
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
                win_pct_match = re.search(r'(\d+\.?\d*)%', win_pct_cell)
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
                    team_data['win_percentage'] = (won / played) * 100
            
            return team_data
            
        except Exception as e:
            print(f"⚠️ Error extracting team data from row: {e}")
            return None

    async def _extract_team_data_from_row_flexible(self, cells):
        """Extract team data from a table row with flexible column handling"""
        try:
            team_data = {}
            
            # Get all cell text content
            cell_texts = []
            for cell in cells:
                text = await cell.text_content()
                cell_texts.append(text.strip() if text else '')
            
            
            # Handle different table structures
            if len(cells) >= 6:
                # Standard 6+ column format (Team, Skill, Played, Won, Win%, MVP)
                return await self._extract_team_data_from_row(cells)
            elif len(cells) == 2:
                # Simple 2-column format - check if first column is a year
                if cell_texts[0].isdigit() and len(cell_texts[0]) == 4:
                    # First column is year, second is team name
                    team_data['season'] = cell_texts[0]
                    team_data['name'] = cell_texts[1] if len(cell_texts) > 1 else 'N/A'
                else:
                    # First column is team name, second is season
                    team_data['name'] = cell_texts[0]
                    team_data['season'] = cell_texts[1] if len(cell_texts) > 1 else 'N/A'
                
                # For simple 2-column format, we don't have skill data
                team_data['skill_level'] = None
                team_data['matches_played'] = None
                team_data['matches_won'] = None
                team_data['win_percentage'] = None
                team_data['mvp_rank'] = None
            else:
                # Other formats - try to extract what we can
                team_data['name'] = cell_texts[0] if cell_texts else 'Unknown'
                team_data['season'] = cell_texts[1] if len(cell_texts) > 1 else 'N/A'
                # Set default values for missing data
                team_data['skill_level'] = None
                team_data['matches_played'] = None
                team_data['matches_won'] = None
                team_data['win_percentage'] = None
                team_data['mvp_rank'] = None
            
            return team_data if team_data.get('name') else None
            
        except Exception as e:
            print(f"⚠️ Error extracting team data from flexible row: {e}")
            return None

    def _is_valid_team_data(self, team_data):
        """Check if team data is valid - using exact same logic as extract-player"""
        try:
            # Must have at least a team name
            if not team_data.get('name'):
                return False
            
            # Must have some meaningful data
            has_skill = team_data.get('skill_level') is not None
            has_played = team_data.get('matches_played') is not None
            has_won = team_data.get('matches_won') is not None
            has_season = team_data.get('season') is not None
            
            # At least one of these should be present
            return has_skill or has_played or has_won or has_season
            
        except Exception as e:
            return False
