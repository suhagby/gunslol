#!/usr/bin/env python3
"""
PC Gaming Performance Monitoring and Optimization System
Entry point for the gaming performance monitor with real-time optimization.

Target Hardware:
- CPU: Intel i7-9700K
- GPU: NVIDIA RTX 3080
- RAM: 16GB
- Storage: M.2 SSD 1TB 7000MB/s
- OS: Windows 11/10
"""

import sys
import os
import threading
import time
import signal
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from config.hardware_profiles import HardwareProfiles
from monitors.system_monitor import SystemMonitor
from monitors.game_monitor import GameMonitor
from monitors.network_monitor import NetworkMonitor
from optimizers.windows_optimizer import WindowsOptimizer
from optimizers.hardware_optimizer import HardwareOptimizer
from optimizers.network_optimizer import NetworkOptimizer
from ui.dashboard import Dashboard
from ui.notifications import NotificationManager
from utils.logger import setup_logger
from utils.database import DatabaseManager
from utils.helpers import is_admin, request_admin_privileges

class GamingPerformanceMonitor:
    """Main class for the gaming performance monitoring system."""
    
    def __init__(self):
        self.logger = setup_logger('GamingPerformanceMonitor')
        self.running = False
        self.monitors = {}
        self.optimizers = {}
        self.dashboard = None
        self.notification_manager = None
        self.db_manager = None
        
        # Hardware profile for target system
        self.hardware_profile = HardwareProfiles.get_i7_9700k_rtx3080_profile()
        
    def initialize(self):
        """Initialize all system components."""
        try:
            # Check for admin privileges
            if not is_admin():
                self.logger.warning("Running without administrator privileges. Some optimizations may not work.")
                if request_admin_privileges():
                    self.logger.info("Restart with administrator privileges requested.")
                    return False
            
            # Initialize database
            self.db_manager = DatabaseManager()
            
            # Initialize monitors
            self.monitors['system'] = SystemMonitor(self.hardware_profile)
            self.monitors['game'] = GameMonitor()
            self.monitors['network'] = NetworkMonitor()
            
            # Initialize optimizers
            self.optimizers['windows'] = WindowsOptimizer()
            self.optimizers['hardware'] = HardwareOptimizer(self.hardware_profile)
            self.optimizers['network'] = NetworkOptimizer()
            
            # Initialize UI components
            self.notification_manager = NotificationManager()
            self.dashboard = Dashboard(self.monitors, self.optimizers)
            
            self.logger.info("Gaming Performance Monitor initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
    
    def start_monitoring(self):
        """Start all monitoring threads."""
        try:
            for name, monitor in self.monitors.items():
                thread = threading.Thread(target=monitor.start, daemon=True)
                thread.start()
                self.logger.info(f"Started {name} monitor")
            
            # Start optimization thread
            optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
            optimization_thread.start()
            
            self.running = True
            self.logger.info("All monitors started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            raise
    
    def _optimization_loop(self):
        """Main optimization loop that runs continuously."""
        while self.running:
            try:
                # Get current system state
                system_metrics = self.monitors['system'].get_current_metrics()
                game_metrics = self.monitors['game'].get_current_metrics()
                network_metrics = self.monitors['network'].get_current_metrics()
                
                # Check for performance issues and apply optimizations
                self._check_and_optimize(system_metrics, game_metrics, network_metrics)
                
                # Wait before next check (5 seconds)
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in optimization loop: {e}")
                time.sleep(10)  # Longer wait on error
    
    def _check_and_optimize(self, system_metrics, game_metrics, network_metrics):
        """Check for performance issues and apply optimizations."""
        issues_found = []
        
        # Check FPS drops
        if game_metrics.get('fps', 0) < self.hardware_profile['thresholds']['min_fps']:
            issues_found.append('low_fps')
            self.optimizers['windows'].optimize_for_gaming()
            self.optimizers['hardware'].boost_performance()
        
        # Check high temperatures
        cpu_temp = system_metrics.get('cpu_temperature', 0)
        gpu_temp = system_metrics.get('gpu_temperature', 0)
        
        if cpu_temp > self.hardware_profile['thresholds']['max_cpu_temp']:
            issues_found.append('high_cpu_temp')
            self.optimizers['hardware'].manage_cpu_cooling()
        
        if gpu_temp > self.hardware_profile['thresholds']['max_gpu_temp']:
            issues_found.append('high_gpu_temp')
            self.optimizers['hardware'].manage_gpu_cooling()
        
        # Check memory usage
        memory_usage = system_metrics.get('memory_percent', 0)
        if memory_usage > self.hardware_profile['thresholds']['max_memory_usage']:
            issues_found.append('high_memory')
            self.optimizers['windows'].free_memory()
        
        # Check network issues
        ping = network_metrics.get('ping', 0)
        if ping > self.hardware_profile['thresholds']['max_ping']:
            issues_found.append('high_ping')
            self.optimizers['network'].optimize_connection()
        
        # Log and notify about issues
        if issues_found:
            self.logger.warning(f"Performance issues detected: {', '.join(issues_found)}")
            self.notification_manager.notify_issues(issues_found)
            
            # Store in database
            self.db_manager.log_optimization_event(issues_found, time.time())
    
    def stop(self):
        """Stop the monitoring system."""
        self.logger.info("Stopping Gaming Performance Monitor...")
        self.running = False
        
        # Stop all monitors
        for name, monitor in self.monitors.items():
            monitor.stop()
            self.logger.info(f"Stopped {name} monitor")
        
        # Close database connection
        if self.db_manager:
            self.db_manager.close()
        
        self.logger.info("Gaming Performance Monitor stopped")
    
    def run(self):
        """Main run method."""
        if not self.initialize():
            return False
        
        try:
            # Start monitoring in background
            self.start_monitoring()
            
            # Run dashboard (this blocks until UI is closed)
            self.dashboard.run()
            
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.stop()
        
        return True

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown."""
    print("\nReceived shutdown signal. Stopping...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run the monitor
    monitor = GamingPerformanceMonitor()
    success = monitor.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())