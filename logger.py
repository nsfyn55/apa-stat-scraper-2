#!/usr/bin/env python3
"""
Logging system for APA Stat Scraper
Follows LSB standards for logging
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from config import config

class APALogger:
    """Logging manager following LSB standards"""
    
    def __init__(self, name="apa-stat-scraper"):
        self.name = name
        self.logs_dir = config.get_logs_dir()
        self.log_file = Path(self.logs_dir) / config.get('logging.file', 'apa-stat-scraper.log')
        self.max_size = self._parse_size(config.get('logging.max_size', '10MB'))
        self.backup_count = config.get('logging.backup_count', 5)
        self.level = getattr(logging, config.get('logging.level', 'INFO').upper())
        
        # Ensure logs directory exists
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
    
    def _parse_size(self, size_str):
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def _setup_logger(self):
        """Setup logger with file and console handlers"""
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_size,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self):
        """Get the logger instance"""
        return self.logger
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)

# Global logger instance
logger = APALogger()
