"""
Cache Manager for APA Stat Scraper
Handles caching of extracted data with configurable timeout
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional, Dict


class CacheManager:
    """Manages caching of extracted data with timeout functionality"""
    
    def __init__(self, cache_dir: str = "var/apa-stat-scraper-2/cache", timeout_hours: int = 12):
        """
        Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            timeout_hours: Number of hours before cache expires (default: 12)
        """
        self.cache_dir = Path(cache_dir)
        self.timeout_hours = timeout_hours
        self.timeout_seconds = timeout_hours * 3600
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_cache_key(self, action_type: str, identifier: str, league: str = None, expand: bool = False) -> str:
        """
        Generate a unique cache key for the given parameters
        
        Args:
            action_type: Type of action ('team' or 'player')
            identifier: Team ID or User ID
            league: League name (optional)
            expand: Whether data was expanded (for team extraction)
            
        Returns:
            MD5 hash string to use as cache key
        """
        # Create a string that uniquely identifies this request
        key_string = f"{action_type}:{identifier}"
        if league:
            key_string += f":{league}"
        if expand:
            key_string += ":expanded"
        
        # Generate MD5 hash
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the full path to a cache file"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """
        Check if a cache file is still valid (not expired)
        
        Args:
            cache_file: Path to the cache file
            
        Returns:
            True if cache is valid, False if expired or doesn't exist
        """
        if not cache_file.exists():
            return False
        
        try:
            # Get file modification time
            file_mtime = cache_file.stat().st_mtime
            current_time = datetime.now().timestamp()
            
            # Check if file is older than timeout
            age_seconds = current_time - file_mtime
            return age_seconds < self.timeout_seconds
            
        except (OSError, ValueError):
            return False
    
    def get_cached_data(self, action_type: str, identifier: str, league: str = None, expand: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data if it exists and is still valid
        
        Args:
            action_type: Type of action ('team' or 'player')
            identifier: Team ID or User ID
            league: League name (optional)
            expand: Whether data was expanded (for team extraction)
            
        Returns:
            Cached data dictionary if valid, None if not found or expired
        """
        cache_key = self._generate_cache_key(action_type, identifier, league, expand)
        cache_file = self._get_cache_file_path(cache_key)
        
        if not self._is_cache_valid(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add cache metadata
            data['_cache_info'] = {
                'cached_at': datetime.fromtimestamp(cache_file.stat().st_mtime).isoformat(),
                'cache_key': cache_key,
                'action_type': action_type,
                'identifier': identifier,
                'league': league,
                'expanded': expand
            }
            
            return data
            
        except (json.JSONDecodeError, OSError, ValueError) as e:
            print(f"⚠️ Error reading cache file {cache_file}: {e}")
            return None
    
    def cache_data(self, action_type: str, identifier: str, data: Dict[str, Any], league: str = None, expand: bool = False) -> bool:
        """
        Cache extracted data
        
        Args:
            action_type: Type of action ('team' or 'player')
            identifier: Team ID or User ID
            data: Data to cache
            league: League name (optional)
            expand: Whether data was expanded (for team extraction)
            
        Returns:
            True if successfully cached, False otherwise
        """
        cache_key = self._generate_cache_key(action_type, identifier, league, expand)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            # Add cache metadata to the data
            data['_cache_info'] = {
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key,
                'action_type': action_type,
                'identifier': identifier,
                'league': league,
                'expanded': expand,
                'timeout_hours': self.timeout_hours
            }
            
            # Write to cache file
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (OSError, ValueError) as e:
            print(f"⚠️ Error writing cache file {cache_file}: {e}")
            return False
    
    def clear_cache(self, action_type: str = None, identifier: str = None) -> int:
        """
        Clear cache files
        
        Args:
            action_type: Type of action to clear ('team' or 'player'), None for all
            identifier: Specific identifier to clear, None for all
            
        Returns:
            Number of files cleared
        """
        cleared_count = 0
        
        try:
            if action_type and identifier:
                # Clear specific cache entry (both expanded and unexpanded)
                cache_key_expanded = self._generate_cache_key(action_type, identifier, expand=True)
                cache_key_unexpanded = self._generate_cache_key(action_type, identifier, expand=False)
                
                for cache_key in [cache_key_expanded, cache_key_unexpanded]:
                    cache_file = self._get_cache_file_path(cache_key)
                    if cache_file.exists():
                        cache_file.unlink()
                        cleared_count += 1
            else:
                # Clear all cache files or files matching action_type
                for cache_file in self.cache_dir.glob("*.json"):
                    if action_type is None:
                        # Clear all files
                        cache_file.unlink()
                        cleared_count += 1
                    else:
                        # Check if this file matches the action type
                        try:
                            with open(cache_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('_cache_info', {}).get('action_type') == action_type:
                                cache_file.unlink()
                                cleared_count += 1
                        except (json.JSONDecodeError, OSError):
                            # If we can't read the file, delete it anyway
                            cache_file.unlink()
                            cleared_count += 1
                            
        except OSError as e:
            print(f"⚠️ Error clearing cache: {e}")
        
        return cleared_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'total_files': 0,
            'valid_files': 0,
            'expired_files': 0,
            'total_size_bytes': 0,
            'action_types': {},
            'expanded_files': 0,
            'unexpanded_files': 0,
            'oldest_file': None,
            'newest_file': None
        }
        
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            stats['total_files'] = len(cache_files)
            
            if not cache_files:
                return stats
            
            file_times = []
            
            for cache_file in cache_files:
                try:
                    # Get file size
                    file_size = cache_file.stat().st_size
                    stats['total_size_bytes'] += file_size
                    
                    # Check if valid
                    if self._is_cache_valid(cache_file):
                        stats['valid_files'] += 1
                    else:
                        stats['expired_files'] += 1
                    
                    # Get file modification time
                    file_mtime = cache_file.stat().st_mtime
                    file_times.append(file_mtime)
                    
                    # Try to get action type and expand status from file content
                    try:
                        with open(cache_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        action_type = data.get('_cache_info', {}).get('action_type', 'unknown')
                        expanded = data.get('_cache_info', {}).get('expanded', False)
                        
                        stats['action_types'][action_type] = stats['action_types'].get(action_type, 0) + 1
                        
                        if expanded:
                            stats['expanded_files'] += 1
                        else:
                            stats['unexpanded_files'] += 1
                            
                    except (json.JSONDecodeError, OSError):
                        stats['action_types']['unknown'] = stats['action_types'].get('unknown', 0) + 1
                        
                except OSError:
                    # If we can't process this file, continue with the next one
                    continue
            
            if file_times:
                stats['oldest_file'] = datetime.fromtimestamp(min(file_times)).isoformat()
                stats['newest_file'] = datetime.fromtimestamp(max(file_times)).isoformat()
            
        except OSError as e:
            print(f"⚠️ Error getting cache stats: {e}")
        
        return stats
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache files
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                if not self._is_cache_valid(cache_file):
                    cache_file.unlink()
                    removed_count += 1
                    
        except OSError as e:
            print(f"⚠️ Error cleaning up expired cache: {e}")
        
        return removed_count