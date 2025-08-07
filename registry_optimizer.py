#!/usr/bin/env python3
"""
Windows Gaming Registry Optimizer
Comprehensive registry tweaks for maximum gaming performance, FPS, and minimum latency.

⚠️  WARNING: This script modifies Windows registry settings.
Always create a system restore point before running!

Features:
- Game Mode optimizations
- Network latency reduction
- CPU performance tweaks
- GPU optimization
- Memory management
- Timer resolution optimization
- Input lag reduction
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

try:
    import winreg
    WINDOWS_PLATFORM = True
except ImportError:
    WINDOWS_PLATFORM = False
    if __name__ == "__main__":
        print("❌ This script is designed for Windows systems only!")
        sys.exit(1)

@dataclass
class RegistryTweak:
    """Registry tweak configuration."""
    hkey: int
    subkey: str
    name: str
    value: Any
    reg_type: int
    description: str
    category: str
    risk_level: str = "low"  # low, medium, high
    requires_restart: bool = False

class WindowsGamingRegistryOptimizer:
    """Windows registry optimizer for gaming performance."""
    
    def __init__(self):
        if not WINDOWS_PLATFORM:
            print("⚠️ Registry optimizer only works on Windows systems")
            self.registry_tweaks = {}
            return
            
        self.tweaks_applied = []
        self.tweaks_failed = []
        self.backup_file = Path(__file__).parent / "registry_backup.json"
        
        # Registry tweaks organized by category
        self.registry_tweaks = self._load_registry_tweaks()
    
    def _load_registry_tweaks(self) -> Dict[str, List[RegistryTweak]]:
        """Load all registry tweaks organized by category."""
        if not WINDOWS_PLATFORM:
            return {}
            
        tweaks = {
            "game_mode": self._get_game_mode_tweaks(),
            "network": self._get_network_tweaks(),
            "cpu": self._get_cpu_tweaks(),
            "gpu": self._get_gpu_tweaks(),
            "memory": self._get_memory_tweaks(),
            "timer": self._get_timer_tweaks(),
            "input": self._get_input_tweaks(),
            "visual": self._get_visual_tweaks(),
            "services": self._get_services_tweaks()
        }
        return tweaks
    
    def _get_game_mode_tweaks(self) -> List[RegistryTweak]:
        """Game Mode and gaming-specific tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                name="GPU Priority",
                value=8,
                reg_type=winreg.REG_DWORD,
                description="Set GPU priority for games to highest level",
                category="game_mode",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                name="Priority",
                value=6,
                reg_type=winreg.REG_DWORD,
                description="Set overall priority for games to high",
                category="game_mode",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                name="Scheduling Category",
                value="High",
                reg_type=winreg.REG_SZ,
                description="Set scheduling category to high for games",
                category="game_mode",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                name="SFIO Priority",
                value="High",
                reg_type=winreg.REG_SZ,
                description="Set Storage and File I/O priority to high for games",
                category="game_mode",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"SOFTWARE\Microsoft\GameBar",
                name="UseNexusForGameBarEnabled",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable Xbox Game Bar for better performance",
                category="game_mode",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"SOFTWARE\Microsoft\GameBar",
                name="AllowAutoGameMode",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Allow automatic Game Mode activation",
                category="game_mode",
                risk_level="low"
            )
        ]
    
    def _get_network_tweaks(self) -> List[RegistryTweak]:
        """Network performance and latency reduction tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="TcpAckFrequency",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Reduce TCP ACK frequency for lower latency",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="TCPNoDelay",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Disable Nagle's algorithm for reduced latency",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="TcpDelAckTicks",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Minimize delayed ACK timeout",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="MaxUserPort",
                value=65534,
                reg_type=winreg.REG_DWORD,
                description="Increase maximum user port range",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="TcpTimedWaitDelay",
                value=30,
                reg_type=winreg.REG_DWORD,
                description="Reduce TCP TIME_WAIT delay",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="DefaultTTL",
                value=64,
                reg_type=winreg.REG_DWORD,
                description="Optimize default TTL for gaming",
                category="network",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                name="TcpMaxDupAcks",
                value=2,
                reg_type=winreg.REG_DWORD,
                description="Optimize TCP duplicate ACK handling",
                category="network",
                risk_level="low"
            )
        ]
    
    def _get_cpu_tweaks(self) -> List[RegistryTweak]:
        """CPU performance optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Power",
                name="CsEnabled",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable Connected Standby for better performance",
                category="cpu",
                risk_level="medium",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Power",
                name="HiberbootEnabled",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable Fast Startup (Hiberboot)",
                category="cpu",
                risk_level="low",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Processor",
                name="Capabilities",
                value=0x0007e066,
                reg_type=winreg.REG_DWORD,
                description="Optimize processor capabilities",
                category="cpu",
                risk_level="medium"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Processor\Performance",
                name="TimeCheck",
                value=200,
                reg_type=winreg.REG_DWORD,
                description="Reduce CPU performance monitoring interval",
                category="cpu",
                risk_level="low"
            )
        ]
    
    def _get_gpu_tweaks(self) -> List[RegistryTweak]:
        """GPU performance optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                name="HwSchMode",
                value=2,
                reg_type=winreg.REG_DWORD,
                description="Enable Hardware Accelerated GPU Scheduling",
                category="gpu",
                risk_level="low",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                name="PlatformSupportMiracast",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable Miracast for better GPU performance",
                category="gpu",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                name="NetworkThrottlingIndex",
                value=4294967295,
                reg_type=winreg.REG_DWORD,
                description="Disable network throttling for multimedia",
                category="gpu",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                name="SystemResponsiveness",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Optimize system responsiveness for gaming",
                category="gpu",
                risk_level="low"
            )
        ]
    
    def _get_memory_tweaks(self) -> List[RegistryTweak]:
        """Memory management optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                name="ClearPageFileAtShutdown",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Don't clear pagefile at shutdown for faster boot",
                category="memory",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                name="LargeSystemCache",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Optimize system cache for better performance",
                category="memory",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                name="DisablePagingExecutive",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Keep system drivers in physical memory",
                category="memory",
                risk_level="medium",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                name="SystemPages",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Optimize system page allocation",
                category="memory",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
                name="EnablePrefetcher",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable prefetcher for SSD optimization",
                category="memory",
                risk_level="medium"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
                name="EnableSuperfetch",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Disable superfetch for SSD optimization",
                category="memory",
                risk_level="medium"
            )
        ]
    
    def _get_timer_tweaks(self) -> List[RegistryTweak]:
        """System timer resolution optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
                name="GlobalTimerResolutionRequests",
                value=1,
                reg_type=winreg.REG_DWORD,
                description="Allow applications to set high timer resolution",
                category="timer",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
                name="DpcWatchdogProfileOffset",
                value=0,
                reg_type=winreg.REG_DWORD,
                description="Optimize DPC watchdog for timing accuracy",
                category="timer",
                risk_level="medium"
            )
        ]
    
    def _get_input_tweaks(self) -> List[RegistryTweak]:
        """Input lag reduction and mouse optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Mouse",
                name="MouseHoverTime",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Reduce mouse hover time for faster response",
                category="input",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Mouse",
                name="MouseSpeed",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Disable mouse acceleration for gaming",
                category="input",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Mouse",
                name="MouseThreshold1",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Disable mouse acceleration threshold 1",
                category="input",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Mouse",
                name="MouseThreshold2",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Disable mouse acceleration threshold 2",
                category="input",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\mouclass\Parameters",
                name="MouseDataQueueSize",
                value=20,
                reg_type=winreg.REG_DWORD,
                description="Increase mouse data queue size",
                category="input",
                risk_level="low"
            )
        ]
    
    def _get_visual_tweaks(self) -> List[RegistryTweak]:
        """Visual effects and desktop composition tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                name="VisualFXSetting",
                value=2,  # Custom performance settings
                reg_type=winreg.REG_DWORD,
                description="Set visual effects to custom/performance",
                category="visual",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Desktop",
                name="MenuShowDelay",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Remove menu show delay",
                category="visual",
                risk_level="low"
            ),
            RegistryTweak(
                hkey=winreg.HKEY_CURRENT_USER,
                subkey=r"Control Panel\Desktop\WindowMetrics",
                name="MinAnimate",
                value="0",
                reg_type=winreg.REG_SZ,
                description="Disable window minimize/maximize animations",
                category="visual",
                risk_level="low"
            )
        ]
    
    def _get_services_tweaks(self) -> List[RegistryTweak]:
        """Windows services optimization tweaks."""
        return [
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\SysMain",
                name="Start",
                value=4,  # Disabled
                reg_type=winreg.REG_DWORD,
                description="Disable Superfetch/SysMain service",
                category="services",
                risk_level="medium",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\WSearch",
                name="Start",
                value=4,  # Disabled
                reg_type=winreg.REG_DWORD,
                description="Disable Windows Search service for gaming",
                category="services",
                risk_level="medium",
                requires_restart=True
            ),
            RegistryTweak(
                hkey=winreg.HKEY_LOCAL_MACHINE,
                subkey=r"SYSTEM\CurrentControlSet\Services\Spooler",
                name="Start",
                value=4,  # Disabled
                reg_type=winreg.REG_DWORD,
                description="Disable Print Spooler if not needed",
                category="services",
                risk_level="low",
                requires_restart=True
            )
        ]
    
    def check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def create_restore_point(self) -> bool:
        """Create a system restore point before applying tweaks."""
        if not WINDOWS_PLATFORM:
            print("⚠️ System restore points only available on Windows")
            return False
            
        try:
            result = subprocess.run([
                "powershell", "-Command",
                "Checkpoint-Computer -Description 'Gaming Registry Optimizer Backup' -RestorePointType 'MODIFY_SETTINGS'"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ System restore point created successfully")
                return True
            else:
                print(f"⚠️ Failed to create restore point: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️ Failed to create restore point: {e}")
            return False
    
    def backup_registry_values(self, tweaks: List[RegistryTweak]) -> bool:
        """Backup current registry values before modification."""
        backup_data = {
            "timestamp": time.time(),
            "values": []
        }
        
        for tweak in tweaks:
            try:
                with winreg.OpenKey(tweak.hkey, tweak.subkey, 0, winreg.KEY_READ) as key:
                    try:
                        current_value, current_type = winreg.QueryValueEx(key, tweak.name)
                        backup_data["values"].append({
                            "hkey": tweak.hkey,
                            "subkey": tweak.subkey,
                            "name": tweak.name,
                            "original_value": current_value,
                            "original_type": current_type
                        })
                    except FileNotFoundError:
                        # Value doesn't exist, note this
                        backup_data["values"].append({
                            "hkey": tweak.hkey,
                            "subkey": tweak.subkey,
                            "name": tweak.name,
                            "original_value": None,
                            "original_type": None
                        })
            except Exception as e:
                print(f"⚠️ Could not backup {tweak.subkey}\\{tweak.name}: {e}")
        
        try:
            with open(self.backup_file, 'w') as f:
                # Convert registry constants to strings for JSON serialization
                serializable_data = {
                    "timestamp": backup_data["timestamp"],
                    "values": []
                }
                for item in backup_data["values"]:
                    serializable_item = item.copy()
                    serializable_item["hkey"] = str(serializable_item["hkey"])
                    serializable_data["values"].append(serializable_item)
                
                json.dump(serializable_data, f, indent=4)
            
            print(f"✅ Registry backup created: {self.backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create backup file: {e}")
            return False
    
    def apply_tweak(self, tweak: RegistryTweak) -> bool:
        """Apply a single registry tweak."""
        try:
            # Try to create the key if it doesn't exist
            with winreg.CreateKeyEx(tweak.hkey, tweak.subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, tweak.name, 0, tweak.reg_type, tweak.value)
                
            self.tweaks_applied.append(tweak)
            return True
            
        except Exception as e:
            print(f"❌ Failed to apply {tweak.subkey}\\{tweak.name}: {e}")
            self.tweaks_failed.append((tweak, str(e)))
            return False
    
    def apply_category_tweaks(self, category: str) -> int:
        """Apply all tweaks in a specific category."""
        if category not in self.registry_tweaks:
            print(f"❌ Unknown category: {category}")
            return 0
        
        tweaks = self.registry_tweaks[category]
        print(f"\n🔧 Applying {category.upper()} tweaks ({len(tweaks)} total)...")
        
        # Backup values first
        self.backup_registry_values(tweaks)
        
        successful = 0
        for tweak in tweaks:
            print(f"  {'🔸' if tweak.risk_level == 'low' else '🔶' if tweak.risk_level == 'medium' else '🔴'} {tweak.description}")
            if self.apply_tweak(tweak):
                print(f"    ✅ Applied: {tweak.subkey}\\{tweak.name}")
                successful += 1
            else:
                print(f"    ❌ Failed: {tweak.subkey}\\{tweak.name}")
        
        print(f"✅ Applied {successful}/{len(tweaks)} {category} tweaks")
        return successful
    
    def apply_all_tweaks(self, risk_level: str = "low") -> Dict[str, int]:
        """Apply all registry tweaks up to specified risk level."""
        if not WINDOWS_PLATFORM:
            print("⚠️ Registry tweaks only available on Windows systems")
            return {}
            
        risk_levels = ["low", "medium", "high"]
        max_risk_index = risk_levels.index(risk_level)
        
        results = {}
        total_successful = 0
        total_tweaks = 0
        
        print(f"\n🚀 Applying all registry tweaks (risk level: {risk_level})...")
        print("=" * 60)
        
        for category, tweaks in self.registry_tweaks.items():
            # Filter tweaks by risk level
            filtered_tweaks = [t for t in tweaks if risk_levels.index(t.risk_level) <= max_risk_index]
            
            if not filtered_tweaks:
                continue
            
            print(f"\n📁 {category.upper().replace('_', ' ')} OPTIMIZATIONS:")
            
            # Backup and apply tweaks
            self.backup_registry_values(filtered_tweaks)
            
            successful = 0
            for tweak in filtered_tweaks:
                risk_icon = "🔸" if tweak.risk_level == "low" else "🔶" if tweak.risk_level == "medium" else "🔴"
                restart_icon = " 🔄" if tweak.requires_restart else ""
                
                print(f"  {risk_icon} {tweak.description}{restart_icon}")
                
                if self.apply_tweak(tweak):
                    successful += 1
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed")
            
            results[category] = successful
            total_successful += successful
            total_tweaks += len(filtered_tweaks)
            
            print(f"  📊 Category result: {successful}/{len(filtered_tweaks)} successful")
        
        print("\n" + "=" * 60)
        print(f"🎯 OVERALL RESULTS: {total_successful}/{total_tweaks} tweaks applied successfully")
        
        return results
    
    def show_recommendations(self):
        """Show post-optimization recommendations."""
        restart_required = any(tweak.requires_restart for tweak in self.tweaks_applied)
        
        print("\n" + "=" * 60)
        print("📋 POST-OPTIMIZATION RECOMMENDATIONS")
        print("=" * 60)
        
        if restart_required:
            print("\n🔄 RESTART REQUIRED:")
            print("  Some tweaks require a system restart to take effect.")
            print("  Please restart your computer when convenient.")
        
        print("\n🎮 GAMING SETTINGS:")
        print("  • Set Windows to High Performance power plan")
        print("  • Close unnecessary background programs")
        print("  • Update GPU drivers to latest version")
        print("  • Enable Game Mode in Windows Settings")
        print("  • Set games to Fullscreen Exclusive mode")
        
        print("\n🖥️ DISPLAY SETTINGS:")
        print("  • Set monitor to highest refresh rate")
        print("  • Disable Windows fullscreen optimizations")
        print("  • Turn off Windows Game DVR")
        print("  • Disable Hardware-accelerated GPU scheduling if issues occur")
        
        print("\n🔧 ADDITIONAL TWEAKS:")
        print("  • Disable Windows Defender real-time protection (if using other AV)")
        print("  • Set virtual memory to system managed")
        print("  • Run disk cleanup and defragmentation")
        print("  • Update all drivers to latest versions")
        
        print("\n⚠️ TROUBLESHOOTING:")
        print("  • If system becomes unstable, restore from backup")
        print("  • Use System Restore to revert changes if needed")
        print("  • Monitor system temperatures after changes")
        
        print(f"\n💾 BACKUP LOCATION: {self.backup_file}")
        print("    Use this file to restore original values if needed")
    
    def run_interactive_mode(self):
        """Run the optimizer in interactive mode."""
        if not WINDOWS_PLATFORM:
            print("\n❌ Registry Optimizer is only available on Windows systems")
            print("   This module requires Windows registry access")
            return
            
        print("\n" + "=" * 60)
        print("🎯 WINDOWS GAMING REGISTRY OPTIMIZER")
        print("   Maximum FPS • Minimum Latency • Peak Performance")
        print("=" * 60)
        
        if not self.check_admin_privileges():
            print("\n❌ ADMINISTRATOR PRIVILEGES REQUIRED!")
            print("   Please run this script as administrator.")
            print("   Right-click and select 'Run as administrator'")
            return
        
        print("\n✅ Running with administrator privileges")
        
        # Create restore point
        print("\n🛡️ Creating system restore point...")
        self.create_restore_point()
        
        while True:
            print("\n📋 REGISTRY OPTIMIZATION OPTIONS:")
            print("  1. Apply ALL Optimizations (Low Risk Only)")
            print("  2. Apply ALL Optimizations (Medium Risk)")
            print("  3. Apply ALL Optimizations (High Risk - Advanced)")
            print()
            print("  🎯 CATEGORY-SPECIFIC OPTIMIZATIONS:")
            print("  4. Game Mode Optimizations")
            print("  5. Network Latency Reduction")
            print("  6. CPU Performance Tweaks")
            print("  7. GPU Optimizations")
            print("  8. Memory Management")
            print("  9. Timer Resolution")
            print("  10. Input Lag Reduction")
            print("  11. Visual Effects")
            print("  12. Services Optimization")
            print()
            print("  📊 UTILITIES:")
            print("  13. Create System Restore Point")
            print("  14. Show Recommendations")
            print("  15. Exit")
            
            try:
                choice = int(input("\n➤ Select option: "))
                
                if choice == 1:
                    self.apply_all_tweaks("low")
                elif choice == 2:
                    self.apply_all_tweaks("medium")
                elif choice == 3:
                    print("\n⚠️ WARNING: High-risk tweaks may cause system instability!")
                    confirm = input("Are you sure? (type 'yes' to confirm): ")
                    if confirm.lower() == 'yes':
                        self.apply_all_tweaks("high")
                elif choice == 4:
                    self.apply_category_tweaks("game_mode")
                elif choice == 5:
                    self.apply_category_tweaks("network")
                elif choice == 6:
                    self.apply_category_tweaks("cpu")
                elif choice == 7:
                    self.apply_category_tweaks("gpu")
                elif choice == 8:
                    self.apply_category_tweaks("memory")
                elif choice == 9:
                    self.apply_category_tweaks("timer")
                elif choice == 10:
                    self.apply_category_tweaks("input")
                elif choice == 11:
                    self.apply_category_tweaks("visual")
                elif choice == 12:
                    self.apply_category_tweaks("services")
                elif choice == 13:
                    self.create_restore_point()
                elif choice == 14:
                    self.show_recommendations()
                elif choice == 15:
                    break
                else:
                    print("❌ Invalid choice!")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Show final recommendations
        if self.tweaks_applied:
            self.show_recommendations()

def main():
    """Main entry point."""
    if not WINDOWS_PLATFORM:
        print("❌ This script is designed for Windows systems only!")
        return
    
    optimizer = WindowsGamingRegistryOptimizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if not optimizer.check_admin_privileges():
            print("❌ Administrator privileges required!")
            return
        
        if command == "low":
            optimizer.create_restore_point()
            optimizer.apply_all_tweaks("low")
        elif command == "medium":
            optimizer.create_restore_point()
            optimizer.apply_all_tweaks("medium")
        elif command == "high":
            optimizer.create_restore_point()
            optimizer.apply_all_tweaks("high")
        elif command == "safe":
            optimizer.create_restore_point()
            optimizer.apply_category_tweaks("game_mode")
            optimizer.apply_category_tweaks("network")
        else:
            print("Usage: python registry_optimizer.py [low|medium|high|safe]")
            return
        
        optimizer.show_recommendations()
    else:
        optimizer.run_interactive_mode()

if __name__ == "__main__":
    main()