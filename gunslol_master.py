#!/usr/bin/env python3
"""
GUNSLOL Performance Master Launcher v5.0
The ultimate gaming performance optimization system.

This script launches and manages all optimization components:
- Ultimate Performance Optimizer
- CS2 Specific Optimizations  
- Registry Tweaks for Gaming
- Startup Optimization System
- Real-time Performance Monitoring

Features:
- One-click optimization profiles
- Automatic game detection and optimization
- Real-time FPS/latency monitoring
- Background performance management
- Comprehensive Windows tweaking
"""

import os
import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import signal

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import our optimization modules
try:
    from ultimate_performance_optimizer import UltimatePerformanceOptimizer
    HAS_ULTIMATE = True
except ImportError as e:
    print(f"⚠️ Ultimate Performance Optimizer not available: {e}")
    HAS_ULTIMATE = False

try:
    from cs2_optimizer import CS2Optimizer
    HAS_CS2 = True
except ImportError as e:
    print(f"⚠️ CS2 Optimizer not available: {e}")
    HAS_CS2 = False

try:
    from registry_optimizer import WindowsGamingRegistryOptimizer
    HAS_REGISTRY = True
except ImportError as e:
    print(f"⚠️ Registry Optimizer not available: {e}")
    HAS_REGISTRY = False

try:
    from startup_optimizer import StartupOptimizer
    HAS_STARTUP = True
except ImportError as e:
    print(f"⚠️ Startup Optimizer not available: {e}")
    HAS_STARTUP = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

@dataclass
class OptimizationProfile:
    """Master optimization profile."""
    name: str
    description: str
    components: List[str]
    settings: Dict[str, Any]
    risk_level: str
    recommended_for: List[str]

class GunslolPerformanceMaster:
    """Master performance optimization launcher."""
    
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize optimizers
        self.ultimate_optimizer = UltimatePerformanceOptimizer() if HAS_ULTIMATE else None
        self.cs2_optimizer = CS2Optimizer() if HAS_CS2 else None
        self.registry_optimizer = WindowsGamingRegistryOptimizer() if HAS_REGISTRY else None
        self.startup_optimizer = StartupOptimizer() if HAS_STARTUP else None
        
        # Performance tracking
        self.performance_data = {
            "sessions": [],
            "optimizations_applied": {},
            "system_info": self._get_system_info()
        }
        
        # Master profiles
        self.optimization_profiles = self._load_optimization_profiles()
        
        # Runtime state
        self.monitoring_active = False
        self.background_threads = []
    
    def setup_logging(self):
        """Setup logging system."""
        log_dir = current_dir / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "gunslol_master.log"),
                logging.StreamHandler()
            ]
        )
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "platform": sys.platform,
            "python_version": sys.version,
            "timestamp": time.time()
        }
        
        if HAS_PSUTIL:
            try:
                info.update({
                    "cpu_count": psutil.cpu_count(),
                    "cpu_count_logical": psutil.cpu_count(logical=True),
                    "memory_total": psutil.virtual_memory().total,
                    "boot_time": psutil.boot_time()
                })
            except:
                pass
        
        return info
    
    def _load_optimization_profiles(self) -> Dict[str, OptimizationProfile]:
        """Load master optimization profiles."""
        return {
            "competitive_fps": OptimizationProfile(
                name="Competitive FPS Gaming",
                description="Maximum FPS and minimum latency for competitive gaming (CS2, Valorant, etc.)",
                components=["ultimate", "cs2", "registry_safe", "startup"],
                settings={
                    "ultimate_profile": "competitive",
                    "registry_risk": "low",
                    "cs2_specific": True,
                    "background_monitoring": True
                },
                risk_level="low",
                recommended_for=["CS2", "Valorant", "Apex Legends", "Overwatch 2"]
            ),
            
            "streaming_gaming": OptimizationProfile(
                name="Gaming + Streaming",
                description="Balanced performance for gaming while streaming/recording",
                components=["ultimate", "registry_safe"],
                settings={
                    "ultimate_profile": "streaming",
                    "registry_risk": "low",
                    "cs2_specific": False,
                    "background_monitoring": True
                },
                risk_level="low",
                recommended_for=["Streaming", "Content Creation", "Multi-tasking"]
            ),
            
            "maximum_performance": OptimizationProfile(
                name="Maximum Performance",
                description="Extreme optimization - disable everything for maximum FPS",
                components=["ultimate", "registry_medium", "startup"],
                settings={
                    "ultimate_profile": "maximum",
                    "registry_risk": "medium",
                    "cs2_specific": False,
                    "background_monitoring": True
                },
                risk_level="medium",
                recommended_for=["High-end systems", "Benchmarking", "Single game focus"]
            ),
            
            "low_latency": OptimizationProfile(
                name="Ultra Low Latency",
                description="Minimize input lag and network latency to absolute minimum",
                components=["ultimate", "cs2", "registry_medium"],
                settings={
                    "ultimate_profile": "low_latency",
                    "registry_risk": "medium",
                    "cs2_specific": True,
                    "background_monitoring": False  # Reduce overhead
                },
                risk_level="medium",
                recommended_for=["Professional esports", "Ultra-competitive gaming"]
            ),
            
            "safe_optimization": OptimizationProfile(
                name="Safe Optimization",
                description="Conservative optimizations with minimal system impact",
                components=["ultimate", "registry_safe"],
                settings={
                    "ultimate_profile": "competitive",
                    "registry_risk": "low",
                    "cs2_specific": False,
                    "background_monitoring": True
                },
                risk_level="low",
                recommended_for=["First-time users", "Work computers", "Stability-critical systems"]
            ),
            
            "cs2_pro": OptimizationProfile(
                name="CS2 Professional",
                description="Specialized optimizations specifically for Counter-Strike 2",
                components=["ultimate", "cs2", "registry_medium"],
                settings={
                    "ultimate_profile": "competitive",
                    "registry_risk": "medium",
                    "cs2_specific": True,
                    "background_monitoring": True
                },
                risk_level="medium",
                recommended_for=["CS2", "Professional CS players", "CS2 tournaments"]
            )
        }
    
    def apply_optimization_profile(self, profile_name: str) -> Dict[str, bool]:
        """Apply a complete optimization profile."""
        if profile_name not in self.optimization_profiles:
            self.logger.error(f"Profile '{profile_name}' not found")
            return {}
        
        profile = self.optimization_profiles[profile_name]
        results = {}
        
        self.logger.info(f"Applying optimization profile: {profile.name}")
        print(f"\n🚀 APPLYING PROFILE: {profile.name.upper()}")
        print(f"📋 Description: {profile.description}")
        print(f"⚠️  Risk Level: {profile.risk_level.upper()}")
        print(f"🎯 Recommended for: {', '.join(profile.recommended_for)}")
        print("=" * 60)
        
        # Apply Ultimate Performance Optimizer
        if "ultimate" in profile.components and self.ultimate_optimizer:
            print("\n🔧 APPLYING ULTIMATE PERFORMANCE OPTIMIZATIONS...")
            ultimate_profile = profile.settings.get("ultimate_profile", "competitive")
            try:
                success = self.ultimate_optimizer.apply_profile(ultimate_profile)
                results["ultimate_optimizer"] = success
                print(f"✅ Ultimate optimizer: {'Success' if success else 'Partial success'}")
            except Exception as e:
                self.logger.error(f"Ultimate optimizer error: {e}")
                results["ultimate_optimizer"] = False
                print(f"❌ Ultimate optimizer: Failed ({e})")
        
        # Apply CS2 Optimizations
        if "cs2" in profile.components and profile.settings.get("cs2_specific", False) and self.cs2_optimizer:
            print("\n🎯 APPLYING CS2 SPECIFIC OPTIMIZATIONS...")
            try:
                cs2_results = self.cs2_optimizer.apply_all_optimizations()
                success = sum(cs2_results.values()) > len(cs2_results) * 0.5
                results["cs2_optimizer"] = success
                print(f"✅ CS2 optimizer: {'Success' if success else 'Partial success'}")
            except Exception as e:
                self.logger.error(f"CS2 optimizer error: {e}")
                results["cs2_optimizer"] = False
                print(f"❌ CS2 optimizer: Failed ({e})")
        
        # Apply Registry Optimizations
        if any(comp.startswith("registry") for comp in profile.components) and self.registry_optimizer:
            print("\n🏛️ APPLYING WINDOWS REGISTRY OPTIMIZATIONS...")
            risk_level = "low"
            if "registry_medium" in profile.components:
                risk_level = "medium"
            elif "registry_high" in profile.components:
                risk_level = "high"
            
            try:
                # Create restore point first
                self.registry_optimizer.create_restore_point()
                registry_results = self.registry_optimizer.apply_all_tweaks(risk_level)
                success = sum(registry_results.values()) > 0
                results["registry_optimizer"] = success
                print(f"✅ Registry optimizer: {'Success' if success else 'Partial success'}")
            except Exception as e:
                self.logger.error(f"Registry optimizer error: {e}")
                results["registry_optimizer"] = False
                print(f"❌ Registry optimizer: Failed ({e})")
        
        # Apply Startup Optimizations
        if "startup" in profile.components and self.startup_optimizer:
            print("\n🚀 APPLYING STARTUP OPTIMIZATIONS...")
            try:
                success = self.startup_optimizer.apply_startup_optimizations()
                results["startup_optimizer"] = success
                print(f"✅ Startup optimizer: {'Success' if success else 'Partial success'}")
            except Exception as e:
                self.logger.error(f"Startup optimizer error: {e}")
                results["startup_optimizer"] = False
                print(f"❌ Startup optimizer: Failed ({e})")
        
        # Start background monitoring if enabled
        if profile.settings.get("background_monitoring", True):
            print("\n📊 STARTING BACKGROUND MONITORING...")
            try:
                self.start_background_monitoring()
                results["background_monitoring"] = True
                print("✅ Background monitoring: Started")
            except Exception as e:
                self.logger.error(f"Background monitoring error: {e}")
                results["background_monitoring"] = False
                print(f"❌ Background monitoring: Failed ({e})")
        
        # Save optimization session
        self.performance_data["optimizations_applied"][profile_name] = {
            "timestamp": time.time(),
            "results": results,
            "profile": profile_name
        }
        
        # Show results summary
        successful = sum(results.values())
        total = len(results)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"🎯 PROFILE APPLICATION COMPLETE: {profile.name}")
        print(f"📊 Success Rate: {successful}/{total} components ({success_rate:.1f}%)")
        print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return results
    
    def start_background_monitoring(self):
        """Start background performance monitoring."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        
        # Start game detection monitoring
        if self.startup_optimizer:
            monitor_thread = threading.Thread(
                target=self._background_monitor_loop,
                daemon=True
            )
            monitor_thread.start()
            self.background_threads.append(monitor_thread)
            self.logger.info("Background monitoring started")
    
    def stop_background_monitoring(self):
        """Stop background performance monitoring."""
        self.monitoring_active = False
        if self.startup_optimizer and hasattr(self.startup_optimizer, 'stop_background_services'):
            self.startup_optimizer.stop_background_services()
        self.logger.info("Background monitoring stopped")
    
    def _background_monitor_loop(self):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Use startup optimizer's monitoring capabilities
                if self.startup_optimizer:
                    self.startup_optimizer.start_background_services()
                
                # Monitor for 60 seconds then check again
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Background monitoring error: {e}")
                time.sleep(30)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        status = {
            "timestamp": time.time(),
            "monitoring_active": self.monitoring_active,
            "available_optimizers": {
                "ultimate": HAS_ULTIMATE,
                "cs2": HAS_CS2,
                "registry": HAS_REGISTRY,
                "startup": HAS_STARTUP,
                "psutil": HAS_PSUTIL
            }
        }
        
        if HAS_PSUTIL:
            try:
                status["system_metrics"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                    "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
                }
            except Exception as e:
                status["system_metrics_error"] = str(e)
        
        return status
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance report."""
        report = [
            "=" * 80,
            "GUNSLOL PERFORMANCE MASTER - SYSTEM REPORT",
            "=" * 80,
            "",
            f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"System: {self.performance_data['system_info'].get('platform', 'Unknown')}",
            "",
            "AVAILABLE OPTIMIZERS:",
            f"  ✅ Ultimate Performance Optimizer: {'Available' if HAS_ULTIMATE else 'Not Available'}",
            f"  ✅ CS2 Optimizer: {'Available' if HAS_CS2 else 'Not Available'}",  
            f"  ✅ Registry Optimizer: {'Available' if HAS_REGISTRY else 'Not Available'}",
            f"  ✅ Startup Optimizer: {'Available' if HAS_STARTUP else 'Not Available'}",
            f"  ✅ System Monitoring: {'Available' if HAS_PSUTIL else 'Not Available'}",
            "",
        ]
        
        # Add optimization history
        if self.performance_data["optimizations_applied"]:
            report.append("OPTIMIZATION HISTORY:")
            for profile_name, session in self.performance_data["optimizations_applied"].items():
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session["timestamp"]))
                results = session["results"]
                successful = sum(results.values())
                total = len(results)
                report.append(f"  📅 {timestamp} - {profile_name}")
                report.append(f"     Success: {successful}/{total} components")
                for component, success in results.items():
                    status = "✅" if success else "❌"
                    report.append(f"     {status} {component.replace('_', ' ').title()}")
                report.append("")
        
        # Add current system status
        status = self.get_system_status()
        report.append("CURRENT SYSTEM STATUS:")
        report.append(f"  Monitoring Active: {'Yes' if status['monitoring_active'] else 'No'}")
        
        if "system_metrics" in status:
            metrics = status["system_metrics"]
            report.append(f"  CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            report.append(f"  Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
        
        report.append("")
        report.append("AVAILABLE OPTIMIZATION PROFILES:")
        for name, profile in self.optimization_profiles.items():
            report.append(f"  🎯 {profile.name}")
            report.append(f"     Description: {profile.description}")
            report.append(f"     Risk Level: {profile.risk_level.upper()}")
            report.append(f"     Components: {', '.join(profile.components)}")
            report.append("")
        
        return "\n".join(report)
    
    def run_interactive_mode(self):
        """Run in interactive mode with full menu system."""
        self.show_banner()
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\n➤ Select option: ").strip()
                
                if choice == "1":
                    self.show_profile_menu()
                elif choice == "2":
                    self.show_component_menu()
                elif choice == "3":
                    self.show_monitoring_menu()
                elif choice == "4":
                    self.show_system_info()
                elif choice == "5":
                    self.show_help()
                elif choice == "6":
                    print("\n📊 PERFORMANCE REPORT:")
                    print(self.generate_performance_report())
                elif choice == "7" or choice.lower() == 'q':
                    self.cleanup_and_exit()
                    break
                else:
                    print("❌ Invalid choice! Please try again.")
                    
            except (KeyboardInterrupt, EOFError):
                self.cleanup_and_exit()
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_banner(self):
        """Show the application banner."""
        print("\n" + "=" * 80)
        print("🎮 GUNSLOL PERFORMANCE MASTER v5.0")
        print("   Ultimate Gaming Performance Optimization System")
        print("   Maximum FPS • Minimum Latency • Peak Performance")
        print("=" * 80)
        
        # Show system compatibility
        print(f"\n🖥️  System: {sys.platform}")
        print(f"🐍 Python: {sys.version.split()[0]}")
        
        # Show available components
        components = []
        if HAS_ULTIMATE: components.append("Ultimate Optimizer")
        if HAS_CS2: components.append("CS2 Optimizer")  
        if HAS_REGISTRY: components.append("Registry Optimizer")
        if HAS_STARTUP: components.append("Startup Optimizer")
        if HAS_PSUTIL: components.append("System Monitoring")
        
        print(f"🔧 Available: {', '.join(components) if components else 'Limited functionality'}")
        
        if not HAS_ULTIMATE and not HAS_CS2 and not HAS_REGISTRY:
            print("\n⚠️  WARNING: Core optimization components not available!")
            print("   Some features may not work properly.")
    
    def show_main_menu(self):
        """Show the main menu."""
        print("\n" + "=" * 50)
        print("📋 MAIN MENU")
        print("=" * 50)
        print("  1. 🎯 Optimization Profiles (Recommended)")
        print("  2. 🔧 Individual Components")
        print("  3. 📊 Performance Monitoring")
        print("  4. 🖥️  System Information")
        print("  5. ❓ Help & Recommendations")
        print("  6. 📋 Generate Performance Report")
        print("  7. 🚪 Exit")
    
    def show_profile_menu(self):
        """Show optimization profile menu."""
        print("\n" + "=" * 60)
        print("🎯 OPTIMIZATION PROFILES")
        print("=" * 60)
        
        for i, (key, profile) in enumerate(self.optimization_profiles.items(), 1):
            risk_icon = "🔸" if profile.risk_level == "low" else "🔶" if profile.risk_level == "medium" else "🔴"
            print(f"  {i}. {risk_icon} {profile.name}")
            print(f"     📋 {profile.description}")
            print(f"     🎯 For: {', '.join(profile.recommended_for[:2])}")
            print(f"     ⚠️  Risk: {profile.risk_level.upper()}")
            print()
        
        print(f"  {len(self.optimization_profiles) + 1}. 🔙 Back to Main Menu")
        
        try:
            choice = int(input("\n➤ Select profile: "))
            
            profile_keys = list(self.optimization_profiles.keys())
            if 1 <= choice <= len(profile_keys):
                profile_key = profile_keys[choice - 1]
                profile = self.optimization_profiles[profile_key]
                
                print(f"\n🎯 Selected: {profile.name}")
                print(f"📋 {profile.description}")
                print(f"⚠️  Risk Level: {profile.risk_level.upper()}")
                
                confirm = input("\nApply this profile? (y/N): ").lower()
                if confirm in ['y', 'yes']:
                    self.apply_optimization_profile(profile_key)
                else:
                    print("❌ Profile application cancelled")
                    
        except ValueError:
            print("❌ Invalid choice!")
    
    def show_component_menu(self):
        """Show individual component menu."""
        print("\n" + "=" * 60)
        print("🔧 INDIVIDUAL COMPONENTS")
        print("=" * 60)
        
        options = []
        if HAS_ULTIMATE:
            options.append(("Ultimate Performance Optimizer", "ultimate"))
        if HAS_CS2:
            options.append(("CS2 Specific Optimizer", "cs2"))
        if HAS_REGISTRY:
            options.append(("Windows Registry Optimizer", "registry"))
        if HAS_STARTUP:
            options.append(("Startup Optimizer", "startup"))
        
        for i, (name, key) in enumerate(options, 1):
            print(f"  {i}. {name}")
        
        print(f"  {len(options) + 1}. 🔙 Back to Main Menu")
        
        try:
            choice = int(input("\n➤ Select component: "))
            
            if 1 <= choice <= len(options):
                _, component_key = options[choice - 1]
                self.run_individual_component(component_key)
                
        except ValueError:
            print("❌ Invalid choice!")
    
    def show_monitoring_menu(self):
        """Show monitoring menu."""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE MONITORING")
        print("=" * 60)
        
        status = self.get_system_status()
        print(f"🔍 Monitoring Status: {'Active' if status['monitoring_active'] else 'Inactive'}")
        
        if "system_metrics" in status:
            metrics = status["system_metrics"]
            print(f"💾 CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"🧠 Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
        
        print("\n📋 MONITORING OPTIONS:")
        print("  1. Start Background Monitoring")
        print("  2. Stop Background Monitoring") 
        print("  3. Show Current System Status")
        print("  4. 🔙 Back to Main Menu")
        
        try:
            choice = int(input("\n➤ Select option: "))
            
            if choice == 1:
                self.start_background_monitoring()
                print("✅ Background monitoring started")
            elif choice == 2:
                self.stop_background_monitoring()
                print("🛑 Background monitoring stopped")
            elif choice == 3:
                self.show_detailed_system_status()
                
        except ValueError:
            print("❌ Invalid choice!")
    
    def show_system_info(self):
        """Show detailed system information."""
        print("\n" + "=" * 60)
        print("🖥️ SYSTEM INFORMATION")
        print("=" * 60)
        
        info = self.performance_data["system_info"]
        print(f"Platform: {info.get('platform', 'Unknown')}")
        print(f"Python Version: {info.get('python_version', 'Unknown')}")
        
        if HAS_PSUTIL:
            try:
                print(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
                memory = psutil.virtual_memory()
                print(f"Total Memory: {memory.total / (1024**3):.1f} GB")
                print(f"Available Memory: {memory.available / (1024**3):.1f} GB ({memory.percent:.1f}% used)")
                
                # Boot time
                boot_time = psutil.boot_time()
                print(f"System Uptime: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))}")
                
            except Exception as e:
                print(f"System info error: {e}")
    
    def show_detailed_system_status(self):
        """Show detailed current system status."""
        status = self.get_system_status()
        
        print(f"\n🔍 DETAILED SYSTEM STATUS - {time.strftime('%H:%M:%S')}")
        print("=" * 50)
        
        if "system_metrics" in status:
            metrics = status["system_metrics"]
            print(f"💾 CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
            print(f"🧠 Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
            
            if "disk_io" in metrics and metrics["disk_io"]:
                disk = metrics["disk_io"]
                print(f"💽 Disk Read: {disk.get('read_bytes', 0) / (1024**2):.1f} MB")
                print(f"💽 Disk Write: {disk.get('write_bytes', 0) / (1024**2):.1f} MB")
            
            if "network_io" in metrics and metrics["network_io"]:
                net = metrics["network_io"]
                print(f"🌐 Network Sent: {net.get('bytes_sent', 0) / (1024**2):.1f} MB")
                print(f"🌐 Network Received: {net.get('bytes_recv', 0) / (1024**2):.1f} MB")
        else:
            print("⚠️ System metrics not available")
    
    def show_help(self):
        """Show help and recommendations."""
        print("\n" + "=" * 60)
        print("❓ HELP & RECOMMENDATIONS")
        print("=" * 60)
        
        print("\n🎯 GETTING STARTED:")
        print("  1. Start with 'Safe Optimization' profile for first-time users")
        print("  2. Use 'Competitive FPS Gaming' for maximum gaming performance")
        print("  3. Try 'CS2 Professional' for Counter-Strike 2 specifically")
        print("  4. Enable background monitoring for automatic optimizations")
        
        print("\n⚠️ IMPORTANT NOTES:")
        print("  • Always run as administrator for full functionality")
        print("  • Create a system restore point before major changes")
        print("  • Restart system after applying optimizations")
        print("  • Monitor system temperatures after optimization")
        
        print("\n🔧 TROUBLESHOOTING:")
        print("  • If system becomes unstable, use System Restore")
        print("  • Check logs in the 'logs' directory for errors")
        print("  • Disable optimizations if experiencing issues")
        print("  • Update GPU drivers after optimization")
        
        print("\n📞 SUPPORT:")
        print("  • Check log files for detailed error information")
        print("  • Create system restore points before changes")
        print("  • Test optimizations incrementally")
    
    def run_individual_component(self, component_key: str):
        """Run an individual optimization component."""
        if component_key == "ultimate" and self.ultimate_optimizer:
            print("\n🚀 Launching Ultimate Performance Optimizer...")
            self.ultimate_optimizer.run_interactive_mode()
        elif component_key == "cs2" and self.cs2_optimizer:
            print("\n🎯 Launching CS2 Optimizer...")
            # CS2 optimizer main function
            subprocess.run([sys.executable, str(current_dir / "cs2_optimizer.py")])
        elif component_key == "registry" and self.registry_optimizer:
            print("\n🏛️ Launching Registry Optimizer...")
            self.registry_optimizer.run_interactive_mode()
        elif component_key == "startup" and self.startup_optimizer:
            print("\n🚀 Launching Startup Optimizer...")
            self.startup_optimizer.run_interactive_mode()
        else:
            print(f"❌ Component '{component_key}' not available")
    
    def cleanup_and_exit(self):
        """Cleanup and exit gracefully."""
        print("\n🛑 Shutting down...")
        self.stop_background_monitoring()
        
        # Save performance data
        try:
            data_file = current_dir / "performance_data.json"
            with open(data_file, 'w') as f:
                json.dump(self.performance_data, f, indent=4, default=str)
            self.logger.info(f"Performance data saved to {data_file}")
        except Exception as e:
            self.logger.error(f"Failed to save performance data: {e}")
        
        print("👋 Goodbye! Thanks for using GUNSLOL Performance Master!")

def main():
    """Main entry point."""
    master = GunslolPerformanceMaster()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in master.optimization_profiles:
            print(f"🚀 Applying profile: {command}")
            master.apply_optimization_profile(command)
        elif command == "status":
            print(master.generate_performance_report())
        elif command == "monitor":
            print("📊 Starting monitoring mode...")
            master.start_background_monitoring()
            try:
                while True:
                    time.sleep(30)
                    status = master.get_system_status()
                    if "system_metrics" in status:
                        metrics = status["system_metrics"]
                        print(f"CPU: {metrics.get('cpu_percent', 0):.1f}% | Memory: {metrics.get('memory_percent', 0):.1f}%")
            except KeyboardInterrupt:
                master.stop_background_monitoring()
        elif command == "help":
            print("GUNSLOL Performance Master v5.0")
            print("\nUsage: python gunslol_master.py [profile|command]")
            print("\nAvailable profiles:")
            for name, profile in master.optimization_profiles.items():
                print(f"  {name} - {profile.description}")
            print("\nAvailable commands:")
            print("  status  - Show system status report")
            print("  monitor - Start monitoring mode")
            print("  help    - Show this help message")
        else:
            print(f"❌ Unknown command: {command}")
            print("Use 'python gunslol_master.py help' for usage information")
    else:
        # Interactive mode
        master.run_interactive_mode()

if __name__ == "__main__":
    main()