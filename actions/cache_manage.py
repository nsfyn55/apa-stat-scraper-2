#!/usr/bin/env python3
"""
Cache Management Action

This action provides cache management functionality including:
- Viewing cache statistics
- Clearing specific cache entries
- Clearing all cache entries
- Cleaning up expired cache files
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

from cache_manager import CacheManager
from logger import logger


class CacheManageAction:
    """Action for managing the application cache."""
    
    def __init__(self):
        self.cache_manager = CacheManager()
    
    def run(self, args: argparse.Namespace) -> int:
        """
        Run the cache management action.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # The subcommand is stored in args.cache_action when called from cache-manage
            subcommand = getattr(args, 'cache_action', None)
            if subcommand == 'stats':
                return self._show_stats()
            elif subcommand == 'clear':
                return self._clear_cache(args)
            elif subcommand == 'cleanup':
                return self._cleanup_expired()
            else:
                logger.error(f"Unknown cache management action: {subcommand}")
                return 1
                
        except Exception as e:
            logger.error(f"Cache management error: {e}")
            return 1
    
    def _show_stats(self) -> int:
        """Show cache statistics."""
        try:
            stats = self.cache_manager.get_cache_stats()
            
            print("📊 Cache Statistics")
            print("=" * 50)
            print(f"Total cache files: {stats['total_files']}")
            print(f"Valid files: {stats['valid_files']}")
            print(f"Expired files: {stats['expired_files']}")
            print(f"Expanded files: {stats['expanded_files']}")
            print(f"Unexpanded files: {stats['unexpanded_files']}")
            
            if stats['total_files'] > 0:
                print(f"\nCache directory: {self.cache_manager.cache_dir}")
                print(f"Cache size: {self._format_size(stats.get('total_size', 0))}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return 1
    
    def _clear_cache(self, args: argparse.Namespace) -> int:
        """Clear cache entries."""
        try:
            if args.all:
                # Clear all cache files
                cleared = self._clear_all_cache()
                print(f"✅ Cleared {cleared} cache files")
                return 0
            
            # Clear specific cache entry
            if not args.action_type or not args.identifier:
                logger.error("Action type and identifier are required for specific cache clearing")
                return 1
            
            cleared = self.cache_manager.clear_cache(
                action_type=args.action_type,
                identifier=args.identifier,
                league=args.league,
                expand=args.expand
            )
            
            if cleared > 0:
                print(f"✅ Cleared {cleared} cache file(s) for {args.action_type}:{args.identifier}")
            else:
                print(f"ℹ️  No cache files found for {args.action_type}:{args.identifier}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return 1
    
    def _clear_all_cache(self) -> int:
        """Clear all cache files."""
        try:
            cache_dir = self.cache_manager.cache_dir
            if not cache_dir.exists():
                return 0
            
            cache_files = list(cache_dir.glob("*.json"))
            cleared_count = 0
            
            for cache_file in cache_files:
                try:
                    cache_file.unlink()
                    cleared_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete {cache_file}: {e}")
            
            return cleared_count
            
        except Exception as e:
            logger.error(f"Failed to clear all cache: {e}")
            return 0
    
    def _cleanup_expired(self) -> int:
        """Clean up expired cache files."""
        try:
            cleaned = self.cache_manager.cleanup_expired()
            print(f"🧹 Cleaned up {cleaned} expired cache files")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {e}")
            return 1
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"


def create_parser(subparsers) -> argparse.ArgumentParser:
    """Create the cache-manage argument parser."""
    parser = subparsers.add_parser(
        'cache-manage',
        help='Manage application cache (view stats, clear cache, cleanup expired)'
    )
    
    # Action subcommand
    action_subparsers = parser.add_subparsers(
        dest='cache_action',
        help='Cache management action',
        required=True
    )
    
    # Stats action
    stats_parser = action_subparsers.add_parser(
        'stats',
        help='Show cache statistics'
    )
    
    # Clear action
    clear_parser = action_subparsers.add_parser(
        'clear',
        help='Clear cache entries'
    )
    clear_group = clear_parser.add_mutually_exclusive_group(required=True)
    clear_group.add_argument(
        '--all',
        action='store_true',
        help='Clear all cache files'
    )
    clear_group.add_argument(
        '--specific',
        action='store_true',
        help='Clear specific cache entry (requires --action-type and --identifier)'
    )
    
    # Specific clear options
    clear_parser.add_argument(
        '--action-type',
        choices=['player', 'team'],
        help='Type of action to clear cache for'
    )
    clear_parser.add_argument(
        '--identifier',
        help='Identifier to clear cache for (player ID or team ID)'
    )
    clear_parser.add_argument(
        '--league',
        help='League to clear cache for (optional)'
    )
    clear_parser.add_argument(
        '--expand',
        action='store_true',
        help='Clear expanded cache entries only'
    )
    
    # Cleanup action
    cleanup_parser = action_subparsers.add_parser(
        'cleanup',
        help='Clean up expired cache files'
    )
    
    return parser
