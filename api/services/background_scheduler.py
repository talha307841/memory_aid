"""
Background scheduler service for MemoryAid application
Handles automatic memory capture simulation at configurable intervals
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
import signal
import sys

from services.config import get_settings
from services.memory_service import MemoryService

logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """Background scheduler for automatic memory capture"""
    
    def __init__(self):
        self.settings = get_settings()
        self.memory_service = MemoryService()
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.interval_seconds = self.settings.capture_interval_seconds
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down scheduler...")
        asyncio.create_task(self.stop())
    
    async def start(self):
        """Start the background scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        logger.info(f"Starting background scheduler with {self.interval_seconds}s interval")
        
        # Start the main loop
        self.task = asyncio.create_task(self._run_scheduler())
        
        # Start initial capture after a short delay
        asyncio.create_task(self._delayed_initial_capture())
    
    async def _delayed_initial_capture(self):
        """Start initial capture after a short delay"""
        await asyncio.sleep(5)  # Wait 5 seconds before first capture
        if self.running:
            await self._capture_memory()
    
    async def _run_scheduler(self):
        """Main scheduler loop"""
        try:
            while self.running:
                # Wait for the next interval
                await asyncio.sleep(self.interval_seconds)
                
                if self.running:
                    # Capture memory
                    await self._capture_memory()
                    
        except asyncio.CancelledError:
            logger.info("Scheduler task cancelled")
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")
            self.running = False
    
    async def _capture_memory(self):
        """Capture a single memory"""
        try:
            logger.info("Starting scheduled memory capture...")
            
            # Simulate capture
            memory_id = await self.memory_service.simulate_capture()
            
            logger.info(f"Scheduled capture completed: {memory_id}")
            
        except Exception as e:
            logger.error(f"Error in scheduled capture: {e}")
    
    async def stop(self):
        """Stop the background scheduler"""
        if not self.running:
            return
        
        logger.info("Stopping background scheduler...")
        self.running = False
        
        # Cancel the main task
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.running
    
    def get_status(self) -> dict:
        """Get scheduler status information"""
        return {
            "running": self.running,
            "interval_seconds": self.interval_seconds,
            "next_capture_in": self.interval_seconds if self.running else None,
            "last_capture": datetime.now().isoformat() if self.running else None
        }
    
    async def trigger_capture(self):
        """Manually trigger a memory capture"""
        if not self.running:
            logger.warning("Cannot trigger capture: scheduler not running")
            return None
        
        try:
            logger.info("Manual capture triggered")
            memory_id = await self._capture_memory()
            return memory_id
        except Exception as e:
            logger.error(f"Error in manual capture: {e}")
            return None
    
    def update_interval(self, new_interval_seconds: int):
        """Update the capture interval"""
        if new_interval_seconds < 10:  # Minimum 10 seconds
            logger.warning(f"Interval too short: {new_interval_seconds}s, using minimum 10s")
            new_interval_seconds = 10
        
        self.interval_seconds = new_interval_seconds
        logger.info(f"Capture interval updated to {new_interval_seconds} seconds")
    
    async def run_forever(self):
        """Run the scheduler indefinitely (for standalone usage)"""
        try:
            await self.start()
            
            # Keep running until interrupted
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            await self.stop()

# Standalone runner for testing
async def main():
    """Standalone runner for testing the scheduler"""
    scheduler = BackgroundScheduler()
    
    try:
        await scheduler.run_forever()
    except Exception as e:
        logger.error(f"Error running scheduler: {e}")
        await scheduler.stop()

if __name__ == "__main__":
    # Configure logging for standalone usage
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the scheduler
    asyncio.run(main())
