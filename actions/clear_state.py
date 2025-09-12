"""
Clear state action for APA Stat Scraper
Clears browser data, logs, and cache
"""

import os
import shutil
from pathlib import Path
from .base import BaseAction
from config import config

class ClearStateAction(BaseAction):
    """Action to clear browser state and application data"""
    
    def run(self, confirm=False):
        """Run the clear state action"""
        print("🚀 APA Stat Scraper - Clear State")
        print("=" * 40)
        
        if not confirm:
            print("⚠️  This will clear all browser data, logs, and cache.")
            print("   You will need to login again after clearing state.")
            response = input("Are you sure you want to continue? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                print("❌ Operation cancelled")
                return False
        
        return self._run_with_session()
    
    async def _run_async(self):
        """Async implementation of clear state"""
        try:
            var_dir = Path(config.get_var_dir())
            
            if not var_dir.exists():
                print("ℹ️  No state data found to clear")
                return True
            
            print("��️  Clearing browser data...")
            browser_data_dir = var_dir / "browser_data"
            if browser_data_dir.exists():
                shutil.rmtree(browser_data_dir)
                print("   ✅ Browser data cleared")
            else:
                print("   ℹ️  No browser data found")
            
            print("🗑️  Clearing logs...")
            logs_dir = var_dir / "logs"
            if logs_dir.exists():
                shutil.rmtree(logs_dir)
                print("   ✅ Logs cleared")
            else:
                print("   ℹ️  No logs found")
            
            print("🗑️  Clearing cache...")
            cache_dir = var_dir / "cache"
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
                print("   ✅ Cache cleared")
            else:
                print("   ℹ️  No cache found")
            
            print("🗑️  Clearing temporary files...")
            temp_dir = var_dir / "tmp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                print("   ✅ Temporary files cleared")
            else:
                print("   ℹ️  No temporary files found")
            
            # Recreate necessary directories
            print("📁 Recreating directory structure...")
            for dir_path in [logs_dir, cache_dir, temp_dir]:
                dir_path.mkdir(parents=True, exist_ok=True)
            
            print("✅ State cleared successfully!")
            print("💡 You will need to run 'python app.py login' to re-authenticate")
            
            return True
            
        except Exception as e:
            print(f"❌ Error clearing state: {e}")
            return False
