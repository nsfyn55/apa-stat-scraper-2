#!/usr/bin/env python3
"""
Configuration management for APA Stat Scraper
Follows LSB standards for configuration and state management
"""

import os
import json
from pathlib import Path

class Config:
    """Configuration manager following LSB standards"""
    
    def __init__(self):
        # LSB-compliant paths
        self.project_name = "apa-stat-scraper-2"
        self.var_dir = Path("var") / self.project_name
        self.etc_dir = Path("etc") / self.project_name
        
        # Ensure directories exist
        self.var_dir.mkdir(parents=True, exist_ok=True)
        self.etc_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration file paths
        self.config_file = self.etc_dir / "config.json"
        self.session_file = self.var_dir / "session.json"
        self.browser_data_dir = self.var_dir / "browser_data"
        self.logs_dir = self.var_dir / "logs"
        self.cache_dir = self.var_dir / "cache"
        self.temp_dir = self.var_dir / "tmp"
        
        # Ensure all required directories exist
        for dir_path in [self.logs_dir, self.cache_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "browser": {
                "headless": False,
                "timeout": 30000,
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            "session": {
                "persist": True,
                "timeout": 3600
            },
            "scraping": {
                "delay_between_requests": 1.0,
                "max_retries": 3,
                "timeout": 30
            },
            "output": {
                "default_format": "csv",
                "include_timestamps": True,
                "backup_previous": True
            },
            "logging": {
                "level": "INFO",
                "file": "apa-stat-scraper.log",
                "max_size": "10MB",
                "backup_count": 5
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                return self._merge_config(default_config, config)
            except Exception as e:
                print(f"⚠️ Error loading config: {e}, using defaults")
                return default_config
        else:
            # Create default config file
            self._save_config(default_config)
            return default_config
    
    def _merge_config(self, default, user):
        """Merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving config: {e}")
    
    def get(self, key_path, default=None):
        """Get configuration value using dot notation (e.g., 'browser.headless')"""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path, value):
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
        
        # Save to file
        self._save_config(self.config)
    
    def get_browser_data_dir(self):
        """Get browser data directory path"""
        return str(self.browser_data_dir)
    
    def get_session_file(self):
        """Get session file path"""
        return str(self.session_file)
    
    def get_logs_dir(self):
        """Get logs directory path"""
        return str(self.logs_dir)
    
    def get_cache_dir(self):
        """Get cache directory path"""
        return str(self.cache_dir)
    
    def get_temp_dir(self):
        """Get temporary directory path"""
        return str(self.temp_dir)
    
    def get_var_dir(self):
        """Get var directory path"""
        return str(self.var_dir)
    
    def get_etc_dir(self):
        """Get etc directory path"""
        return str(self.etc_dir)

# Global config instance
config = Config()
