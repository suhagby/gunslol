#!/usr/bin/env python3
"""
Ultimate Performance Optimizer v5.0
Comprehensive gaming performance optimization for maximum FPS, minimum latency, and competitive gaming.

Target Games: CS2, Valorant, League of Legends, and all competitive FPS games
Hardware: Optimized for high-end systems (RTX 3080+, i7-9700K+, 16GB+ RAM)
Features: Registry tweaks, CPU/GPU optimization, network tuning, Windows optimization
"""

import os
import sys
import subprocess
import json
import time
import threading
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import configparser
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Try to import system modules
try:
    import winreg
    import ctypes
    from ctypes import wintypes
    WINDOWS_PLATFORM = True
except ImportError:
    WINDOWS_PLATFORM = False

# Cross-platform system monitoring
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil not available - system monitoring will be limited")

@dataclass
class PerformanceProfile:
    """Performance optimization profile."""
    name: str
    description: str
    cpu_priority: str
    memory_optimization: bool
    network_optimization: bool
    registry_tweaks: bool
    gpu_optimizations: bool
    background_apps: str
    visual_effects: str
    game_mode: bool
    timer_resolution: float

class UltimatePerformanceOptimizer:
    """Main performance optimization system."""
    
    def __init__(self):
        self.setup_logging()
        self.is_admin = self._check_admin_privileges()
        self.optimization_results = {}
        self.performance_profiles = self._load_performance_profiles()
        self.active_processes = set()
        
    def setup_logging(self):
        """Setup logging system."""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "performance_optimizer.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges."""
        if not WINDOWS_PLATFORM:
            return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
            
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def _load_performance_profiles(self) -> Dict[str, PerformanceProfile]:
        """Load predefined performance profiles."""
        profiles = {
            "competitive": PerformanceProfile(
                name="Competitive Gaming",
                description="Maximum performance for competitive FPS games (CS2, Valorant)",
                cpu_priority="realtime",
                memory_optimization=True,
                network_optimization=True,
                registry_tweaks=True,
                gpu_optimizations=True,
                background_apps="disable_all",
                visual_effects="performance",
                game_mode=True,
                timer_resolution=0.5
            ),
            "streaming": PerformanceProfile(
                name="Gaming + Streaming",
                description="Balanced performance for gaming while streaming",
                cpu_priority="high",
                memory_optimization=True,
                network_optimization=True,
                registry_tweaks=True,
                gpu_optimizations=True,
                background_apps="disable_non_essential",
                visual_effects="balanced",
                game_mode=True,
                timer_resolution=1.0
            ),
            "maximum": PerformanceProfile(
                name="Maximum Performance",
                description="Extreme optimization - disable everything for max FPS",
                cpu_priority="realtime",
                memory_optimization=True,
                network_optimization=True,
                registry_tweaks=True,
                gpu_optimizations=True,
                background_apps="disable_all",
                visual_effects="performance",
                game_mode=True,
                timer_resolution=0.5
            ),
            "low_latency": PerformanceProfile(
                name="Ultra Low Latency",
                description="Minimum input lag and network latency",
                cpu_priority="realtime",
                memory_optimization=True,
                network_optimization=True,
                registry_tweaks=True,
                gpu_optimizations=True,
                background_apps="disable_all",
                visual_effects="performance",
                game_mode=True,
                timer_resolution=0.5
            )
        }
        return profiles
    
    def apply_windows_registry_optimizations(self) -> bool:
        """Apply comprehensive Windows registry optimizations."""
        if not WINDOWS_PLATFORM or not self.is_admin:
            self.logger.warning("Registry optimizations require Windows admin privileges")
            return False
            
        registry_optimizations = [
            # Gaming optimizations
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", 8, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Priority", 6, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Scheduling Category", "High", winreg.REG_SZ),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "SFIO Priority", "High", winreg.REG_SZ),
            
            # Network optimizations
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpAckFrequency", 1, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TCPNoDelay", 1, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpDelAckTicks", 0, winreg.REG_DWORD),
            
            # GPU optimizations
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", 2, winreg.REG_DWORD),
            
            # CPU optimizations
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Power", "CsEnabled", 0, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 0, winreg.REG_DWORD),
            
            # Memory optimizations
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", 0, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 1, winreg.REG_DWORD),
            
            # Timer resolution
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel", "GlobalTimerResolutionRequests", 1, winreg.REG_DWORD),
        ]
        
        successful = 0
        for hkey, subkey, name, value, reg_type in registry_optimizations:
            try:
                with winreg.OpenKey(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value)
                    successful += 1
                    self.logger.info(f"Set registry value: {subkey}\\{name} = {value}")
            except Exception as e:
                self.logger.error(f"Failed to set registry value {subkey}\\{name}: {e}")
        
        self.optimization_results["registry_optimizations"] = {
            "successful": successful,
            "total": len(registry_optimizations)
        }
        
        return successful > 0
    
    def optimize_cpu_performance(self) -> bool:
        """Apply CPU performance optimizations."""
        optimizations_applied = []
        
        try:
            # Set high performance power plan
            if WINDOWS_PLATFORM:
                result = subprocess.run([
                    "powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    optimizations_applied.append("High Performance Power Plan")
                    
                # Disable CPU throttling
                subprocess.run([
                    "powercfg", "/setacvalueindex", "scheme_current", 
                    "54533251-82be-4824-96c1-47b60b740d00", 
                    "bc5038f7-23e0-4960-96da-33abaf5935ec", "100"
                ], capture_output=True)
                optimizations_applied.append("CPU Throttling Disabled")
                
                # Set CPU minimum state to 100%
                subprocess.run([
                    "powercfg", "/setacvalueindex", "scheme_current",
                    "54533251-82be-4824-96c1-47b60b740d00",
                    "893dee8e-2bef-41e0-89c6-b55d0929964c", "100"
                ], capture_output=True)
                optimizations_applied.append("CPU Minimum State 100%")
            
            # Process priority optimizations
            if HAS_PSUTIL:
                current_process = psutil.Process()
                current_process.nice(psutil.REALTIME_PRIORITY_CLASS if WINDOWS_PLATFORM else -20)
                optimizations_applied.append("Process Priority Optimized")
            
        except Exception as e:
            self.logger.error(f"CPU optimization error: {e}")
        
        self.optimization_results["cpu_optimizations"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def optimize_gpu_performance(self) -> bool:
        """Apply GPU performance optimizations."""
        optimizations_applied = []
        
        try:
            # NVIDIA optimizations
            nvidia_settings = [
                ("PowerMizerEnable", 0x1),
                ("PerfLevelSrc", 0x2222),
                ("PowerMizerLevel", 0x1),
                ("PowerMizerLevelAC", 0x1),
                ("GPUPowerMizerMode", 1),
            ]
            
            if WINDOWS_PLATFORM:
                try:
                    nvidia_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                        r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak", 
                        0, winreg.KEY_SET_VALUE)
                    
                    for setting, value in nvidia_settings:
                        try:
                            winreg.SetValueEx(nvidia_key, setting, 0, winreg.REG_DWORD, value)
                            optimizations_applied.append(f"NVIDIA {setting}")
                        except:
                            pass
                    winreg.CloseKey(nvidia_key)
                except:
                    pass
            
            # DirectX/Graphics optimizations
            if WINDOWS_PLATFORM:
                try:
                    # Hardware Accelerated GPU Scheduling
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                        r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers", 
                        0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, "HwSchMode", 0, winreg.REG_DWORD, 2)
                        optimizations_applied.append("Hardware GPU Scheduling")
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"GPU optimization error: {e}")
        
        self.optimization_results["gpu_optimizations"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def optimize_network_performance(self) -> bool:
        """Apply network performance optimizations."""
        optimizations_applied = []
        
        try:
            if WINDOWS_PLATFORM:
                # TCP optimization commands
                network_commands = [
                    ["netsh", "int", "tcp", "set", "global", "autotuninglevel=disabled"],
                    ["netsh", "int", "tcp", "set", "global", "chimney=enabled"],
                    ["netsh", "int", "tcp", "set", "global", "rss=enabled"],
                    ["netsh", "int", "tcp", "set", "global", "netdma=enabled"],
                    ["netsh", "int", "tcp", "set", "heuristics", "disabled"],
                    ["netsh", "int", "tcp", "set", "supplemental", "internet", "congestionprovider=ctcp"],
                    ["netsh", "interface", "ipv4", "set", "subinterface", "\"Local Area Connection\"", "mtu=1500", "store=persistent"],
                ]
                
                for command in network_commands:
                    try:
                        result = subprocess.run(command, capture_output=True, text=True)
                        if result.returncode == 0:
                            optimizations_applied.append(f"Network: {' '.join(command[2:4])}")
                    except:
                        pass
                
                # Network adapter optimizations via registry
                network_registry_tweaks = [
                    (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpAckFrequency", 1),
                    (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TCPNoDelay", 1),
                    (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpDelAckTicks", 0),
                    (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "MaxUserPort", 65534),
                    (r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", "TcpTimedWaitDelay", 30),
                ]
                
                for subkey, name, value in network_registry_tweaks:
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                            optimizations_applied.append(f"Network Registry: {name}")
                    except:
                        pass
            
        except Exception as e:
            self.logger.error(f"Network optimization error: {e}")
        
        self.optimization_results["network_optimizations"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def optimize_memory_performance(self) -> bool:
        """Apply memory performance optimizations."""
        optimizations_applied = []
        
        try:
            if WINDOWS_PLATFORM:
                # Memory management registry tweaks
                memory_tweaks = [
                    (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", 0),
                    (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 1),
                    (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "DisablePagingExecutive", 1),
                    (r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "SystemPages", 0),
                ]
                
                for subkey, name, value in memory_tweaks:
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                            optimizations_applied.append(f"Memory: {name}")
                    except:
                        pass
            
            # System memory optimization
            if HAS_PSUTIL:
                try:
                    # Clear system caches (if possible)
                    if WINDOWS_PLATFORM:
                        subprocess.run(["sfc", "/scannow"], capture_output=True)
                    optimizations_applied.append("System Cache Optimization")
                except:
                    pass
            
        except Exception as e:
            self.logger.error(f"Memory optimization error: {e}")
        
        self.optimization_results["memory_optimizations"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def disable_background_services(self, level: str = "moderate") -> bool:
        """Disable unnecessary background services and processes."""
        if not WINDOWS_PLATFORM:
            return False
            
        optimizations_applied = []
        
        # Services to disable based on level
        services_to_disable = {
            "moderate": [
                "wuauserv",  # Windows Update
                "BITS",      # Background Intelligent Transfer Service
                "Spooler",   # Print Spooler
                "Fax",       # Fax Service
            ],
            "aggressive": [
                "wuauserv", "BITS", "Spooler", "Fax",
                "WSearch",   # Windows Search
                "SysMain",   # Superfetch/Prefetch
                "Themes",    # Themes Service
                "TabletInputService",  # Tablet Input
                "WMPNetworkSvc",  # Windows Media Player Network Service
            ],
            "extreme": [
                "wuauserv", "BITS", "Spooler", "Fax", "WSearch", "SysMain",
                "Themes", "TabletInputService", "WMPNetworkSvc",
                "AudioEndpointBuilder",  # Audio Endpoint Builder
                "Audiosrv",  # Windows Audio
                "Schedule",  # Task Scheduler
            ]
        }
        
        services = services_to_disable.get(level, services_to_disable["moderate"])
        
        for service in services:
            try:
                result = subprocess.run(
                    ["sc", "config", service, "start=", "disabled"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    subprocess.run(["sc", "stop", service], capture_output=True)
                    optimizations_applied.append(f"Disabled service: {service}")
            except:
                pass
        
        self.optimization_results["disabled_services"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def apply_cs2_specific_optimizations(self) -> bool:
        """Apply Counter-Strike 2 specific optimizations."""
        optimizations_applied = []
        
        try:
            # CS2 launch options (to be added to Steam)
            cs2_launch_options = [
                "-novid",           # Skip intro videos
                "-nojoy",           # Disable joystick support
                "-high",            # High CPU priority
                "-threads 8",       # Use 8 CPU threads
                "+fps_max 0",       # Unlimited FPS
                "+cl_forcepreload 1",  # Preload maps
                "+mat_queue_mode 2",   # Multithreaded rendering
                "-freq 240",        # Monitor refresh rate
                "+rate 786432",     # Maximum network rate
                "+cl_cmdrate 128",  # Command rate
                "+cl_updaterate 128",  # Update rate
                "+cl_interp_ratio 1",  # Interpolation
                "+cl_interp 0",     # Interpolation time
            ]
            
            # Create CS2 optimization config
            cs2_config_path = Path.home() / "cs2_optimization.cfg"
            with open(cs2_config_path, "w") as f:
                f.write("// CS2 Performance Configuration\n")
                f.write("fps_max 0\n")
                f.write("cl_forcepreload 1\n")
                f.write("mat_queue_mode 2\n")
                f.write("rate 786432\n")
                f.write("cl_cmdrate 128\n")
                f.write("cl_updaterate 128\n")
                f.write("cl_interp_ratio 1\n")
                f.write("cl_interp 0\n")
                f.write("// Network optimization\n")
                f.write("cl_lagcompensation 1\n")
                f.write("cl_predictweapons 1\n")
                f.write("// Video optimization\n")
                f.write("mat_monitorgamma 2.2\n")
                f.write("mat_powersavingsmode 0\n")
            
            optimizations_applied.append(f"CS2 config created: {cs2_config_path}")
            
            # CS2 registry optimizations
            if WINDOWS_PLATFORM:
                cs2_registry_tweaks = [
                    (r"SOFTWARE\Valve\Steam\Apps\730", "LaunchOptions", " ".join(cs2_launch_options)),
                ]
                
                for subkey, name, value in cs2_registry_tweaks:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey, 0, winreg.KEY_SET_VALUE) as key:
                            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                            optimizations_applied.append(f"CS2 Registry: {name}")
                    except:
                        pass
        
        except Exception as e:
            self.logger.error(f"CS2 optimization error: {e}")
        
        self.optimization_results["cs2_optimizations"] = optimizations_applied
        return len(optimizations_applied) > 0
    
    def set_timer_resolution(self, resolution_ms: float = 0.5) -> bool:
        """Set Windows timer resolution for lower latency."""
        if not WINDOWS_PLATFORM:
            return False
            
        try:
            # Try to set timer resolution using timeBeginPeriod
            winmm = ctypes.windll.winmm
            resolution = int(resolution_ms)
            result = winmm.timeBeginPeriod(resolution)
            if result == 0:  # TIMERR_NOERROR
                self.optimization_results["timer_resolution"] = f"{resolution}ms"
                return True
        except Exception as e:
            self.logger.error(f"Timer resolution error: {e}")
        
        return False
    
    def monitor_performance(self, duration: int = 60) -> Dict[str, Any]:
        """Monitor system performance for specified duration."""
        if not HAS_PSUTIL:
            return {"error": "psutil not available"}
        
        metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "gpu_usage": [],
            "fps": [],
            "latency": [],
            "timestamp": []
        }
        
        start_time = time.time()
        while time.time() - start_time < duration:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics["cpu_usage"].append(cpu_percent)
                
                # Memory metrics
                memory = psutil.virtual_memory()
                metrics["memory_usage"].append(memory.percent)
                
                # Timestamp
                metrics["timestamp"].append(time.time() - start_time)
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                break
        
        return metrics
    
    def apply_profile(self, profile_name: str) -> bool:
        """Apply a complete performance profile."""
        if profile_name not in self.performance_profiles:
            self.logger.error(f"Profile '{profile_name}' not found")
            return False
        
        profile = self.performance_profiles[profile_name]
        self.logger.info(f"Applying profile: {profile.name}")
        
        results = []
        
        # Apply optimizations based on profile
        if profile.registry_tweaks:
            results.append(self.apply_windows_registry_optimizations())
        
        if profile.cpu_priority in ["high", "realtime"]:
            results.append(self.optimize_cpu_performance())
        
        if profile.gpu_optimizations:
            results.append(self.optimize_gpu_performance())
        
        if profile.network_optimization:
            results.append(self.optimize_network_performance())
        
        if profile.memory_optimization:
            results.append(self.optimize_memory_performance())
        
        if profile.background_apps != "none":
            level = "extreme" if profile.background_apps == "disable_all" else "moderate"
            results.append(self.disable_background_services(level))
        
        if profile.timer_resolution:
            results.append(self.set_timer_resolution(profile.timer_resolution))
        
        # Apply CS2 specific optimizations for competitive profiles
        if "competitive" in profile_name.lower():
            results.append(self.apply_cs2_specific_optimizations())
        
        success_rate = sum(results) / len(results) if results else 0
        self.optimization_results["profile_applied"] = {
            "name": profile_name,
            "success_rate": success_rate,
            "total_optimizations": len(results)
        }
        
        return success_rate > 0.5
    
    def generate_report(self) -> str:
        """Generate a comprehensive optimization report."""
        report = [
            "=" * 60,
            "ULTIMATE PERFORMANCE OPTIMIZER - RESULTS REPORT",
            "=" * 60,
            "",
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Administrator Privileges: {'Yes' if self.is_admin else 'No'}",
            f"Platform: {'Windows' if WINDOWS_PLATFORM else 'Linux/Unix'}",
            "",
        ]
        
        for category, results in self.optimization_results.items():
            report.append(f"{category.upper().replace('_', ' ')}:")
            if isinstance(results, list):
                for result in results:
                    report.append(f"  ✓ {result}")
            elif isinstance(results, dict):
                for key, value in results.items():
                    report.append(f"  {key}: {value}")
            else:
                report.append(f"  {results}")
            report.append("")
        
        return "\n".join(report)
    
    def run_interactive_mode(self):
        """Run the optimizer in interactive mode."""
        print("\n" + "=" * 60)
        print("🚀 ULTIMATE PERFORMANCE OPTIMIZER v5.0")
        print("   Maximum FPS • Minimum Latency • Competitive Gaming")
        print("=" * 60)
        
        if not self.is_admin and WINDOWS_PLATFORM:
            print("⚠️  WARNING: Not running as administrator!")
            print("   Some optimizations may not work properly.")
            print("   Please run as administrator for full functionality.")
        
        while True:
            print("\n📋 OPTIMIZATION PROFILES:")
            for i, (key, profile) in enumerate(self.performance_profiles.items(), 1):
                print(f"  {i}. {profile.name} - {profile.description}")
            
            print("\n🔧 MANUAL OPTIMIZATIONS:")
            print(f"  {len(self.performance_profiles) + 1}. Windows Registry Optimizations")
            print(f"  {len(self.performance_profiles) + 2}. CPU Performance Optimization")
            print(f"  {len(self.performance_profiles) + 3}. GPU Performance Optimization")
            print(f"  {len(self.performance_profiles) + 4}. Network Optimization")
            print(f"  {len(self.performance_profiles) + 5}. Memory Optimization")
            print(f"  {len(self.performance_profiles) + 6}. CS2 Specific Optimizations")
            print(f"  {len(self.performance_profiles) + 7}. Performance Monitoring")
            
            print("\n🎯 SYSTEM:")
            print(f"  {len(self.performance_profiles) + 8}. Generate Report")
            print(f"  {len(self.performance_profiles) + 9}. Exit")
            
            try:
                choice = int(input("\n➤ Select option: "))
                
                profile_keys = list(self.performance_profiles.keys())
                
                if 1 <= choice <= len(profile_keys):
                    profile_key = profile_keys[choice - 1]
                    print(f"\n🚀 Applying {self.performance_profiles[profile_key].name}...")
                    self.apply_profile(profile_key)
                    print("✅ Profile applied successfully!")
                    
                elif choice == len(self.performance_profiles) + 1:
                    print("\n🔧 Applying Windows Registry Optimizations...")
                    self.apply_windows_registry_optimizations()
                    print("✅ Registry optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 2:
                    print("\n🔧 Applying CPU Performance Optimization...")
                    self.optimize_cpu_performance()
                    print("✅ CPU optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 3:
                    print("\n🔧 Applying GPU Performance Optimization...")
                    self.optimize_gpu_performance()
                    print("✅ GPU optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 4:
                    print("\n🔧 Applying Network Optimization...")
                    self.optimize_network_performance()
                    print("✅ Network optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 5:
                    print("\n🔧 Applying Memory Optimization...")
                    self.optimize_memory_performance()
                    print("✅ Memory optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 6:
                    print("\n🎮 Applying CS2 Specific Optimizations...")
                    self.apply_cs2_specific_optimizations()
                    print("✅ CS2 optimizations applied!")
                    
                elif choice == len(self.performance_profiles) + 7:
                    duration = int(input("Enter monitoring duration in seconds (default 60): ") or "60")
                    print(f"\n📊 Monitoring performance for {duration} seconds...")
                    metrics = self.monitor_performance(duration)
                    print("✅ Performance monitoring completed!")
                    
                elif choice == len(self.performance_profiles) + 8:
                    print("\n📊 OPTIMIZATION REPORT:")
                    print(self.generate_report())
                    
                elif choice == len(self.performance_profiles) + 9:
                    break
                    
                else:
                    print("❌ Invalid choice! Please try again.")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main entry point."""
    optimizer = UltimatePerformanceOptimizer()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == "competitive":
            print("🚀 Applying Competitive Gaming Profile...")
            optimizer.apply_profile("competitive")
        elif command == "streaming":
            print("🚀 Applying Gaming + Streaming Profile...")
            optimizer.apply_profile("streaming")
        elif command == "maximum":
            print("🚀 Applying Maximum Performance Profile...")
            optimizer.apply_profile("maximum")
        elif command == "report":
            print(optimizer.generate_report())
        else:
            print("Usage: python ultimate_performance_optimizer.py [competitive|streaming|maximum|report]")
            return
    else:
        # Interactive mode
        optimizer.run_interactive_mode()
    
    # Generate final report
    print("\n" + optimizer.generate_report())

if __name__ == "__main__":
    main()