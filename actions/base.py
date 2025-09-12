"""
Base action class for APA Stat Scraper actions
"""

import asyncio
from abc import ABC, abstractmethod
from session_manager import APASessionManager
from logger import logger

class BaseAction(ABC):
    """Base class for all CLI actions"""
    
    def __init__(self):
        self.session_manager = APASessionManager()
    
    @abstractmethod
    def run(self, **kwargs):
        """Run the action. Must be implemented by subclasses."""
        pass
    
    async def _run_async(self, **kwargs):
        """Async implementation of the action. Must be implemented by subclasses."""
        pass
    
    def _run_with_session(self, **kwargs):
        """Helper method to run async action with session management"""
        try:
            logger.info(f"Starting action: {self.__class__.__name__}")
            return asyncio.run(self._run_async(**kwargs))
        except Exception as e:
            logger.error(f"Error in action {self.__class__.__name__}: {e}")
            print(f"❌ Error in action: {e}")
            return False
        finally:
            # Session cleanup is handled by the session manager
            logger.info(f"Completed action: {self.__class__.__name__}")
