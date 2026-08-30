"""
MeshNet Ultra - Production Entry Point
With logging, monitoring, and reliability features
"""

import sys
import os
import json
import time
import signal
import logging
import threading
from datetime import datetime
from typing import Optional
import socket

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/meshnet.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("MeshNet")

# Import MeshNet
try:
    from meshnet_ultra import MeshNetUltra
except ImportError as e:
    logger.error(f"Failed to import MeshNet: {e}")
    sys.exit(1)

class MeshNetProduction:
    """Production wrapper for MeshNet Ultra"""
    
    def __init__(self):
        self.node_id = os.getenv('NODE_ID', None)
        self.role = os.getenv('NODE_ROLE', 'auto')
        self.ultra: Optional[MeshNetUltra] = None
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("=" * 60)
        logger.info("🚀 MeshNet Ultra - Production Mode")
        logger.info(f"📡 Node Role: {self.role}")
        logger.info(f"🆔 Node ID: {self.node_id or 'Auto-generated'}")
        logger.info("=" * 60)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.ultra:
            self.ultra.running = False
        sys.exit(0)
    
    def start(self):
        """Start the production node"""
        try:
            # Initialize MeshNet
            self.ultra = MeshNetUltra()
            
            # Set custom node ID if provided
            if self.node_id:
                self.ultra.node_id = self.node_id
            
            # Start based on role
            if self.role == 'gateway':
                logger.info("🌍 Starting as Gateway...")
                self.ultra.become_gateway()
            elif self.role == 'client':
                logger.info("🔗 Starting as Client...")
                # Auto-connect to first available gateway
                self.ultra.start_auto_discovery()
            else:
                logger.info("🔄 Starting in Auto Mode...")
                self.ultra.start_auto_discovery()
            
            # Main loop with health monitoring
            self._health_monitor()
            
        except Exception as e:
            logger.error(f"Startup error: {e}")
            sys.exit(1)
    
    def _health_monitor(self):
        """Monitor system health"""
        while self.running:
            try:
                # Check if still running
                if not self.ultra.running:
                    logger.warning("MeshNet stopped, restarting...")
                    self._restart()
                
                # Check internet connectivity
                if not self._check_internet():
                    logger.warning("Internet connectivity lost")
                
                # Log status
                if self.ultra.aggregator.gateways:
                    logger.info(
                        f"📡 Active: {len(self.ultra.aggregator.gateways)} gateways, "
                        f"Speed: {self.ultra.aggregator.get_speed_boost():.2f}x"
                    )
                else:
                    logger.info("📡 Waiting for connections...")
                
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(60)
    
    def _check_internet(self) -> bool:
        """Check if we have internet connectivity"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            return True
        except:
            return False
    
    def _restart(self):
        """Restart the system"""
        logger.info("Restarting MeshNet...")
        self.ultra = MeshNetUltra()
        self.ultra.start_auto_discovery()

def main():
    """Main entry point"""
    try:
        production = MeshNetProduction()
        production.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
