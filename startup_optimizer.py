#!/usr/bin/env python3
"""
System Startup Performance Optimizer
Automatically applies performance optimizations on system startup for gaming.

Features:
- Auto-detects games and applies appropriate profiles
- Monitors system performance in real-time
- Automatic FPS and latency optimization
- Background service management
- One-click gaming mode activation
"""

import os
import sys
import time
import subprocess
import threading
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import signal

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from ultimate_performance_optimizer import UltimatePerformanceOptimizer
    HAS_OPTIMIZER = True
except ImportError:
    HAS_OPTIMIZER = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

@dataclass
class GameProfile:
    """Gaming profile configuration."""
    name: str
    executable: str
    process_name: str
    optimization_profile: str
    launch_options: List[str]
    priority: str = "high"
    affinity_mask: Optional[int] = None

class GameDetector:
    """Detects running games and applies optimizations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.game_profiles = self._load_game_profiles()
        self.active_games = set()
        self.monitoring = False
        
    def _load_game_profiles(self) -> Dict[str, GameProfile]:
        """Load game-specific optimization profiles."""
        return {
            "cs2": GameProfile(
                name="Counter-Strike 2",
                executable="cs2.exe",
                process_name="cs2",
                optimization_profile="competitive",
                launch_options=["-novid", "-nojoy", "-high", "-threads 8", "+fps_max 0"]
            ),
            "valorant": GameProfile(
                name="Valorant",
                executable="VALORANT-Win64-Shipping.exe",
                process_name="VALORANT-Win64-Shipping",
                optimization_profile="competitive",
                launch_options=["-high", "-USEALLAVAILABLECORES"]
            ),
            "lol": GameProfile(
                name="League of Legends",
                executable="League of Legends.exe",
                process_name="League of Legends",
                optimization_profile="competitive",
                launch_options=[]
            ),
            "apex": GameProfile(
                name="Apex Legends",
                executable="r5apex.exe",
                process_name="r5apex",
                optimization_profile="competitive",
                launch_options=["-novid", "-high", "+fps_max unlimited"]
            ),
            "fortnite": GameProfile(
                name="Fortnite",
                executable="FortniteClient-Win64-Shipping.exe",
                process_name="FortniteClient-Win64-Shipping",
                optimization_profile="competitive",
                launch_options=["-USEALLAVAILABLECORES", "-high"]
            ),
            "overwatch": GameProfile(
                name="Overwatch 2",
                executable="Overwatch.exe",
                process_name="Overwatch",
                optimization_profile="competitive",
                launch_options=[]
            )
        }
    
    def detect_running_games(self) -> List[GameProfile]:
        """Detect currently running games."""
        if not HAS_PSUTIL:
            return []
        
        running_games = []
        
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    for game_id, profile in self.game_profiles.items():
                        if (profile.process_name.lower() in proc_name or 
                            profile.executable.lower() in proc_name):
                            if profile not in running_games:
                                running_games.append(profile)
                                self.logger.info(f"Detected game: {profile.name}")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Game detection error: {e}")
        
        return running_games
    
    def optimize_game_process(self, game: GameProfile) -> bool:
        """Apply optimizations to detected game process."""
        if not HAS_PSUTIL:
            return False
            
        try:
            for proc in psutil.process_iter(['name', 'exe', 'pid']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    if (game.process_name.lower() in proc_name or 
                        game.executable.lower() in proc_name):
                        
                        # Set process priority
                        if game.priority == "realtime":
                            proc.nice(psutil.REALTIME_PRIORITY_CLASS)
                        elif game.priority == "high":
                            proc.nice(psutil.HIGH_PRIORITY_CLASS)
                        
                        # Set CPU affinity if specified
                        if game.affinity_mask:
                            cpu_count = psutil.cpu_count()
                            affinity = [i for i in range(cpu_count) if game.affinity_mask & (1 << i)]
                            proc.cpu_affinity(affinity)
                        
                        self.logger.info(f"Optimized process: {proc.info['name']} (PID: {proc.info['pid']})")
                        return True
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Process optimization error: {e}")
        
        return False
    
    def start_monitoring(self):
        """Start monitoring for games."""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info("Game monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self.monitoring = False
        self.logger.info("Game monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring:
            try:
                current_games = set(game.name for game in self.detect_running_games())
                
                # Detect newly started games
                new_games = current_games - self.active_games
                for game_name in new_games:
                    game_profile = next((g for g in self.game_profiles.values() if g.name == game_name), None)
                    if game_profile:
                        self.logger.info(f"New game detected: {game_name}")
                        self.optimize_game_process(game_profile)
                
                # Detect stopped games
                stopped_games = self.active_games - current_games
                for game_name in stopped_games:
                    self.logger.info(f"Game stopped: {game_name}")
                
                self.active_games = current_games
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                time.sleep(10)

class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.monitoring = False
        self.performance_data = {
            "cpu_usage": [],
            "memory_usage": [],
            "fps": [],
            "latency": [],
            "timestamps": []
        }
        
    def start_monitoring(self, interval: int = 5):
        """Start performance monitoring."""
        self.monitoring = True
        self.interval = interval
        monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        monitor_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_performance(self):
        """Monitor system performance."""
        while self.monitoring:
            if not HAS_PSUTIL:
                time.sleep(self.interval)
                continue
                
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Store data
                self.performance_data["cpu_usage"].append(cpu_percent)
                self.performance_data["memory_usage"].append(memory_percent)
                self.performance_data["timestamps"].append(time.time())
                
                # Keep only last 100 measurements
                for key in self.performance_data:
                    if len(self.performance_data[key]) > 100:
                        self.performance_data[key] = self.performance_data[key][-100:]
                
                # Check for performance issues
                if cpu_percent > 80:
                    self.logger.warning(f"High CPU usage detected: {cpu_percent}%")
                
                if memory_percent > 85:
                    self.logger.warning(f"High memory usage detected: {memory_percent}%")
                
                time.sleep(self.interval)
                
            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                time.sleep(self.interval * 2)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.performance_data["cpu_usage"]:
            return {"error": "No data available"}
        
        return {
            "cpu_usage": self.performance_data["cpu_usage"][-1] if self.performance_data["cpu_usage"] else 0,
            "memory_usage": self.performance_data["memory_usage"][-1] if self.performance_data["memory_usage"] else 0,
            "avg_cpu": sum(self.performance_data["cpu_usage"][-10:]) / min(len(self.performance_data["cpu_usage"]), 10),
            "avg_memory": sum(self.performance_data["memory_usage"][-10:]) / min(len(self.performance_data["memory_usage"]), 10)
        }

class StartupOptimizer:
    """Main startup optimization system."""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        self.optimizer = UltimatePerformanceOptimizer() if HAS_OPTIMIZER else None
        self.game_detector = GameDetector()
        self.performance_monitor = PerformanceMonitor()
        
        self.running = False
        self.config_path = Path(__file__).parent / "startup_config.json"
        self.config = self._load_config()
        
    def setup_logging(self):
        """Setup logging system."""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "startup_optimizer.log"),
                logging.StreamHandler()
            ]
        )
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = {
            "auto_optimize": True,
            "startup_profile": "competitive",
            "monitor_games": True,
            "monitor_performance": True,
            "auto_priority": True,
            "disable_services": True,
            "registry_tweaks": True
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def apply_startup_optimizations(self):
        """Apply startup optimizations."""
        self.logger.info("Applying startup optimizations...")
        
        if not self.optimizer:
            self.logger.error("Ultimate Performance Optimizer not available")
            return False
        
        success = True
        
        try:
            # Apply the configured startup profile
            if self.config["auto_optimize"]:
                profile_name = self.config.get("startup_profile", "competitive")
                self.logger.info(f"Applying startup profile: {profile_name}")
                success &= self.optimizer.apply_profile(profile_name)
            
            # Individual optimizations based on config
            if self.config.get("registry_tweaks", True):
                self.logger.info("Applying registry optimizations...")
                success &= self.optimizer.apply_windows_registry_optimizations()
            
            if self.config.get("disable_services", True):
                self.logger.info("Optimizing background services...")
                success &= self.optimizer.disable_background_services("moderate")
            
            self.logger.info(f"Startup optimizations {'successful' if success else 'completed with issues'}")
            
        except Exception as e:
            self.logger.error(f"Startup optimization error: {e}")
            success = False
        
        return success
    
    def start_background_services(self):
        """Start background monitoring services."""
        if self.config.get("monitor_games", True):
            self.game_detector.start_monitoring()
        
        if self.config.get("monitor_performance", True):
            self.performance_monitor.start_monitoring()
        
        self.logger.info("Background services started")
    
    def stop_background_services(self):
        """Stop background monitoring services."""
        self.game_detector.stop_monitoring()
        self.performance_monitor.stop_monitoring()
        self.logger.info("Background services stopped")
    
    def create_desktop_shortcut(self):
        """Create a desktop shortcut for easy access."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Gaming Optimizer.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{Path(__file__).absolute()}"'
            shortcut.WorkingDirectory = str(Path(__file__).parent)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            
            self.logger.info(f"Desktop shortcut created: {shortcut_path}")
            
        except ImportError:
            self.logger.info("Desktop shortcut creation not supported on this platform")
        except Exception as e:
            self.logger.error(f"Failed to create desktop shortcut: {e}")
    
    def show_status_gui(self):
        """Show a simple status GUI."""
        try:
            import tkinter as tk
            from tkinter import ttk, messagebox
            
            def refresh_status():
                if self.performance_monitor:
                    metrics = self.performance_monitor.get_current_metrics()
                    if "error" not in metrics:
                        cpu_var.set(f"CPU: {metrics.get('cpu_usage', 0):.1f}%")
                        memory_var.set(f"Memory: {metrics.get('memory_usage', 0):.1f}%")
                
                games = self.game_detector.detect_running_games()
                games_var.set(f"Games: {len(games)} detected")
                
                root.after(5000, refresh_status)  # Update every 5 seconds
            
            def apply_optimizations():
                try:
                    profile = profile_var.get()
                    if self.optimizer:
                        success = self.optimizer.apply_profile(profile.lower())
                        messagebox.showinfo("Optimization", 
                            f"Profile '{profile}' {'applied successfully!' if success else 'applied with some issues.'}")
                except Exception as e:
                    messagebox.showerror("Error", f"Optimization failed: {e}")
            
            root = tk.Tk()
            root.title("Gaming Performance Monitor")
            root.geometry("400x300")
            
            # Status frame
            status_frame = ttk.LabelFrame(root, text="System Status", padding="10")
            status_frame.pack(fill="x", padx=10, pady=5)
            
            cpu_var = tk.StringVar(value="CPU: --")
            memory_var = tk.StringVar(value="Memory: --")
            games_var = tk.StringVar(value="Games: --")
            
            ttk.Label(status_frame, textvariable=cpu_var).pack(anchor="w")
            ttk.Label(status_frame, textvariable=memory_var).pack(anchor="w")
            ttk.Label(status_frame, textvariable=games_var).pack(anchor="w")
            
            # Profile selection
            profile_frame = ttk.LabelFrame(root, text="Quick Optimization", padding="10")
            profile_frame.pack(fill="x", padx=10, pady=5)
            
            profile_var = tk.StringVar(value="Competitive")
            profiles = ["Competitive", "Streaming", "Maximum", "Low_Latency"]
            
            for profile in profiles:
                ttk.Radiobutton(profile_frame, text=profile, variable=profile_var, value=profile).pack(anchor="w")
            
            ttk.Button(profile_frame, text="Apply Profile", command=apply_optimizations).pack(pady=5)
            
            # Control buttons
            control_frame = ttk.Frame(root)
            control_frame.pack(fill="x", padx=10, pady=10)
            
            ttk.Button(control_frame, text="Exit", command=root.destroy).pack(side="right", padx=5)
            
            # Start status updates
            refresh_status()
            
            root.mainloop()
            
        except ImportError:
            self.logger.info("GUI not available - tkinter not installed")
        except Exception as e:
            self.logger.error(f"GUI error: {e}")
    
    def run_interactive_mode(self):
        """Run in interactive mode."""
        print("\n" + "=" * 50)
        print("🚀 GAMING STARTUP OPTIMIZER")
        print("   Auto-optimization for peak gaming performance")
        print("=" * 50)
        
        while True:
            print("\n📋 OPTIONS:")
            print("  1. Apply Startup Optimizations")
            print("  2. Start Background Monitoring")
            print("  3. Show Current Status")
            print("  4. Configure Settings")
            print("  5. Create Desktop Shortcut")
            print("  6. Show GUI Status")
            print("  7. Exit")
            
            try:
                choice = int(input("\n➤ Select option: "))
                
                if choice == 1:
                    print("\n🚀 Applying startup optimizations...")
                    success = self.apply_startup_optimizations()
                    print(f"✅ Optimizations {'completed successfully!' if success else 'completed with issues.'}")
                
                elif choice == 2:
                    print("\n📊 Starting background monitoring...")
                    self.start_background_services()
                    self.running = True
                    print("✅ Background services started!")
                
                elif choice == 3:
                    print("\n📊 CURRENT STATUS:")
                    
                    # Performance metrics
                    if self.performance_monitor:
                        metrics = self.performance_monitor.get_current_metrics()
                        if "error" not in metrics:
                            print(f"  CPU Usage: {metrics.get('cpu_usage', 0):.1f}%")
                            print(f"  Memory Usage: {metrics.get('memory_usage', 0):.1f}%")
                            print(f"  Avg CPU (10s): {metrics.get('avg_cpu', 0):.1f}%")
                            print(f"  Avg Memory (10s): {metrics.get('avg_memory', 0):.1f}%")
                    
                    # Detected games
                    games = self.game_detector.detect_running_games()
                    print(f"  Detected Games: {len(games)}")
                    for game in games:
                        print(f"    - {game.name}")
                
                elif choice == 4:
                    print("\n⚙️ CONFIGURATION:")
                    print(f"  Auto Optimize: {self.config.get('auto_optimize', True)}")
                    print(f"  Startup Profile: {self.config.get('startup_profile', 'competitive')}")
                    print(f"  Monitor Games: {self.config.get('monitor_games', True)}")
                    print(f"  Monitor Performance: {self.config.get('monitor_performance', True)}")
                    
                    # Simple configuration
                    profile = input("Enter startup profile (competitive/streaming/maximum): ").strip()
                    if profile:
                        self.config["startup_profile"] = profile
                        self._save_config()
                        print("✅ Configuration saved!")
                
                elif choice == 5:
                    print("\n🔗 Creating desktop shortcut...")
                    self.create_desktop_shortcut()
                
                elif choice == 6:
                    print("\n🖥️ Opening GUI status window...")
                    self.show_status_gui()
                
                elif choice == 7:
                    if self.running:
                        print("\n🛑 Stopping background services...")
                        self.stop_background_services()
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice!")
                    
            except (ValueError, KeyboardInterrupt):
                if self.running:
                    print("\n🛑 Stopping background services...")
                    self.stop_background_services()
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run(self):
        """Main run method."""
        # Handle command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "auto":
                print("🚀 Running automatic optimization...")
                self.apply_startup_optimizations()
                self.start_background_services()
                
                # Keep running until interrupted
                try:
                    print("✅ Optimization complete. Background services running...")
                    print("Press Ctrl+C to stop")
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping background services...")
                    self.stop_background_services()
                    
            elif command == "gui":
                print("🖥️ Starting GUI mode...")
                self.apply_startup_optimizations()
                self.start_background_services()
                self.show_status_gui()
                self.stop_background_services()
                
            elif command == "optimize":
                print("🚀 Running optimization only...")
                self.apply_startup_optimizations()
                
            else:
                print("Usage: python startup_optimizer.py [auto|gui|optimize]")
                return
        else:
            # Interactive mode
            self.run_interactive_mode()

def signal_handler(signum, frame):
    """Handle system signals."""
    print("\n🛑 Received shutdown signal. Cleaning up...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    optimizer = StartupOptimizer()
    optimizer.run()

if __name__ == "__main__":
    main()