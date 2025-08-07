"""
Windows system optimization module.
Applies Windows-specific optimizations for gaming performance.
"""

import os
import sys
import logging
import subprocess
import winreg
import ctypes
from typing import Dict, Any, List, Optional
import psutil
import threading
import time

try:
    import win32service
    import win32serviceutil
    import win32con
    import win32api
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class WindowsOptimizer:
    """Handles Windows-specific gaming optimizations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimization_history = []
        self.services_disabled = []
        self.registry_backups = {}
        
        # Services that can be safely disabled during gaming
        self.gaming_disable_services = [
            'Themes',                    # Windows Themes (slight performance gain)
            'TabletInputService',        # Tablet PC Input Service
            'WSearch',                   # Windows Search
            'SysMain',                   # Superfetch/Sysmain
            'DiagTrack',                # Connected User Experiences and Telemetry
            'dmwappushservice',         # Device Management WAP Push
            'WerSvc',                   # Windows Error Reporting
            'Spooler',                  # Print Spooler (if no printer needed)
            'Fax',                      # Fax Service
            'WMPNetworkSvc',            # Windows Media Player Network Sharing
            'Browser',                  # Computer Browser
            'TrkWks',                   # Distributed Link Tracking Client
            'MSDTC',                    # Distributed Transaction Coordinator
        ]
        
        # Registry optimizations
        self.registry_optimizations = {
            # Disable Windows Game Mode interference
            r'HKEY_CURRENT_USER\SOFTWARE\Microsoft\GameBar': {
                'AutoGameModeEnabled': (winreg.REG_DWORD, 0),
                'AllowAutoGameMode': (winreg.REG_DWORD, 0),
                'UseNexusForGameBarEnabled': (winreg.REG_DWORD, 0)
            },
            
            # Network optimizations
            r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters': {
                'TcpAckFrequency': (winreg.REG_DWORD, 1),
                'TCPNoDelay': (winreg.REG_DWORD, 1),
                'TcpDelAckTicks': (winreg.REG_DWORD, 0)
            },
            
            # Disable fullscreen optimizations
            r'HKEY_CURRENT_USER\System\GameConfigStore': {
                'GameDVR_Enabled': (winreg.REG_DWORD, 0),
                'GameDVR_FSEBehaviorMode': (winreg.REG_DWORD, 2),
                'GameDVR_FSEBehavior': (winreg.REG_DWORD, 2),
                'GameDVR_DXGIHonorFSEWindowsCompatible': (winreg.REG_DWORD, 1)
            },
            
            # Visual effects optimizations
            r'HKEY_CURRENT_USER\Control Panel\Desktop': {
                'UserPreferencesMask': (winreg.REG_BINARY, b'\x90\x12\x03\x80\x10\x00\x00\x00'),
                'MenuShowDelay': (winreg.REG_SZ, '0')
            },
            
            # Mouse optimizations
            r'HKEY_CURRENT_USER\Control Panel\Mouse': {
                'MouseSpeed': (winreg.REG_SZ, '0'),
                'MouseThreshold1': (winreg.REG_SZ, '0'),
                'MouseThreshold2': (winreg.REG_SZ, '0'),
                'SmoothMouseXCurve': (winreg.REG_BINARY, b''),
                'SmoothMouseYCurve': (winreg.REG_BINARY, b'')
            }
        }
        
        self.logger.info("WindowsOptimizer initialized")
    
    def optimize_for_gaming(self) -> Dict[str, bool]:
        """Apply comprehensive Windows optimizations for gaming."""
        results = {}
        
        try:
            self.logger.info("Starting Windows gaming optimizations...")
            
            # Enable Windows Game Mode properly
            results['game_mode'] = self._enable_game_mode()
            
            # Set high performance power plan
            results['power_plan'] = self._set_high_performance_power_plan()
            
            # Disable Windows Defender real-time protection temporarily
            results['defender'] = self._disable_defender_realtime()
            
            # Optimize visual effects
            results['visual_effects'] = self._optimize_visual_effects()
            
            # Disable unnecessary services
            results['services'] = self._disable_gaming_services()
            
            # Apply registry optimizations
            results['registry'] = self._apply_registry_optimizations()
            
            # Optimize virtual memory
            results['virtual_memory'] = self._optimize_virtual_memory()
            
            # Set process priority optimization
            results['process_priority'] = self._optimize_process_priorities()
            
            # Network stack optimizations
            results['network_stack'] = self._optimize_network_stack()
            
            self.logger.info(f"Windows optimizations completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during Windows optimization: {e}")
            return {'error': str(e)}
    
    def _enable_game_mode(self) -> bool:
        """Enable Windows Game Mode with proper configuration."""
        try:
            # Enable Game Mode via registry
            key_path = r'SOFTWARE\Microsoft\GameBar'
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'AutoGameModeEnabled', 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, 'AllowAutoGameMode', 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            except FileNotFoundError:
                # Create the key if it doesn't exist
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
                winreg.SetValueEx(key, 'AutoGameModeEnabled', 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, 'AllowAutoGameMode', 0, winreg.REG_DWORD, 1)
                winreg.CloseKey(key)
            
            # Also enable through Settings registry
            gaming_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR'
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, gaming_key, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'GameDVR_Enabled', 0, winreg.REG_DWORD, 0)  # Disable GameDVR
                winreg.CloseKey(key)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, gaming_key)
                winreg.SetValueEx(key, 'GameDVR_Enabled', 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
            
            self.logger.info("Windows Game Mode enabled")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable Game Mode: {e}")
            return False
    
    def _set_high_performance_power_plan(self) -> bool:
        """Set Windows to High Performance power plan."""
        try:
            # Get current power scheme
            result = subprocess.run(['powercfg', '/getactivescheme'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                current_scheme = result.stdout.strip()
                self.logger.info(f"Current power scheme: {current_scheme}")
            
            # Set to High Performance
            # High Performance GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
            result = subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Set power plan to High Performance")
                
                # Additional power optimizations
                power_optimizations = [
                    # Disable USB selective suspend
                    ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT', 
                     '2a737441-1930-4402-8d77-b2bebba308a3', '48e6b7a6-50f5-4782-a5d4-53bb8f07e226', '0'],
                    
                    # Set PCI Express Link State Power Management to Off
                    ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                     '501a4d13-42af-4429-9fd1-a8218c268e20', 'ee12f906-d277-404b-b6da-e5fa1a576df5', '0'],
                     
                    # Set processor power management to 100%
                    ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                     '54533251-82be-4824-96c1-47b60b740d00', 'bc5038f7-23e0-4960-96da-33abaf5935ec', '100'],
                ]
                
                for cmd in power_optimizations:
                    subprocess.run(cmd, capture_output=True)
                
                # Apply settings
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True)
                
                return True
            else:
                self.logger.warning(f"Failed to set power plan: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error setting power plan: {e}")
            return False
    
    def _disable_defender_realtime(self) -> bool:
        """Temporarily disable Windows Defender real-time protection."""
        try:
            # This is a temporary disable - requires admin privileges
            if not self._is_admin():
                self.logger.warning("Admin privileges required to disable Defender")
                return False
            
            # Disable real-time monitoring via PowerShell
            powershell_cmd = [
                'powershell', '-Command',
                'Set-MpPreference -DisableRealtimeMonitoring $true'
            ]
            
            result = subprocess.run(powershell_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Windows Defender real-time protection disabled")
                
                # Schedule re-enabling after gaming session
                threading.Timer(3600, self._reenable_defender).start()  # Re-enable after 1 hour
                
                return True
            else:
                self.logger.warning(f"Could not disable Defender: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error disabling Defender: {e}")
            return False
    
    def _reenable_defender(self):
        """Re-enable Windows Defender real-time protection."""
        try:
            powershell_cmd = [
                'powershell', '-Command',
                'Set-MpPreference -DisableRealtimeMonitoring $false'
            ]
            
            result = subprocess.run(powershell_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Windows Defender real-time protection re-enabled")
            else:
                self.logger.warning("Could not re-enable Defender automatically")
                
        except Exception as e:
            self.logger.error(f"Error re-enabling Defender: {e}")
    
    def _optimize_visual_effects(self) -> bool:
        """Optimize Windows visual effects for performance."""
        try:
            # Set visual effects to "Adjust for best performance"
            visual_fx_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects'
            
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, visual_fx_key, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, 'VisualFXSetting', 0, winreg.REG_DWORD, 2)  # Adjust for best performance
                winreg.CloseKey(key)
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, visual_fx_key)
                winreg.SetValueEx(key, 'VisualFXSetting', 0, winreg.REG_DWORD, 2)
                winreg.CloseKey(key)
            
            # Disable specific visual effects
            desktop_key = r'Control Panel\Desktop'
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, desktop_key, 0, winreg.KEY_SET_VALUE)
            
            # Disable animations
            winreg.SetValueEx(key, 'UserPreferencesMask', 0, winreg.REG_BINARY, 
                             b'\x90\x12\x03\x80\x10\x00\x00\x00')
            winreg.SetValueEx(key, 'MenuShowDelay', 0, winreg.REG_SZ, '0')
            
            winreg.CloseKey(key)
            
            self.logger.info("Visual effects optimized for performance")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing visual effects: {e}")
            return False
    
    def _disable_gaming_services(self) -> bool:
        """Disable unnecessary services during gaming."""
        if not HAS_WIN32:
            self.logger.warning("Win32 libraries not available for service management")
            return False
        
        try:
            disabled_count = 0
            
            for service_name in self.gaming_disable_services:
                try:
                    # Check if service exists and is running
                    service_status = win32serviceutil.QueryServiceStatus(service_name)
                    
                    if service_status[1] == win32service.SERVICE_RUNNING:
                        # Stop the service
                        win32serviceutil.StopService(service_name)
                        self.services_disabled.append(service_name)
                        disabled_count += 1
                        self.logger.debug(f"Stopped service: {service_name}")
                        
                except Exception as e:
                    self.logger.debug(f"Could not stop service {service_name}: {e}")
                    continue
            
            if disabled_count > 0:
                self.logger.info(f"Disabled {disabled_count} services for gaming")
                
                # Schedule re-enabling services after gaming
                threading.Timer(7200, self._reenable_services).start()  # 2 hours
                
            return disabled_count > 0
            
        except Exception as e:
            self.logger.error(f"Error disabling services: {e}")
            return False
    
    def _reenable_services(self):
        """Re-enable previously disabled services."""
        if not HAS_WIN32:
            return
        
        try:
            for service_name in self.services_disabled:
                try:
                    win32serviceutil.StartService(service_name)
                    self.logger.debug(f"Re-enabled service: {service_name}")
                except Exception as e:
                    self.logger.debug(f"Could not restart service {service_name}: {e}")
            
            self.services_disabled.clear()
            self.logger.info("Re-enabled previously disabled services")
            
        except Exception as e:
            self.logger.error(f"Error re-enabling services: {e}")
    
    def _apply_registry_optimizations(self) -> bool:
        """Apply gaming-focused registry optimizations."""
        try:
            applied_count = 0
            
            for reg_path, values in self.registry_optimizations.items():
                try:
                    # Determine the root key
                    if reg_path.startswith('HKEY_CURRENT_USER'):
                        root_key = winreg.HKEY_CURRENT_USER
                        sub_path = reg_path[len('HKEY_CURRENT_USER\\'):]
                    elif reg_path.startswith('HKEY_LOCAL_MACHINE'):
                        root_key = winreg.HKEY_LOCAL_MACHINE
                        sub_path = reg_path[len('HKEY_LOCAL_MACHINE\\'):]
                    else:
                        continue
                    
                    # Open or create the key
                    try:
                        key = winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_SET_VALUE)
                    except FileNotFoundError:
                        key = winreg.CreateKey(root_key, sub_path)
                    
                    # Apply each value
                    for value_name, (value_type, value_data) in values.items():
                        # Backup original value if exists
                        try:
                            original_value = winreg.QueryValueEx(key, value_name)
                            self.registry_backups[f"{reg_path}\\{value_name}"] = original_value
                        except FileNotFoundError:
                            pass
                        
                        # Set new value
                        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                        applied_count += 1
                    
                    winreg.CloseKey(key)
                    
                except Exception as e:
                    self.logger.debug(f"Could not apply registry optimization to {reg_path}: {e}")
                    continue
            
            if applied_count > 0:
                self.logger.info(f"Applied {applied_count} registry optimizations")
            
            return applied_count > 0
            
        except Exception as e:
            self.logger.error(f"Error applying registry optimizations: {e}")
            return False
    
    def _optimize_virtual_memory(self) -> bool:
        """Optimize virtual memory settings."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            
            # Calculate optimal page file size
            # For gaming: 1.5x RAM for initial size, 2x RAM for maximum
            initial_size_mb = int(total_memory_gb * 1.5 * 1024)
            max_size_mb = int(total_memory_gb * 2 * 1024)
            
            # Set page file size via WMI (requires admin)
            if self._is_admin():
                try:
                    import wmi
                    c = wmi.WMI()
                    
                    # Get page file settings
                    page_files = c.Win32_PageFileSetting()
                    
                    for pf in page_files:
                        pf.InitialSize = initial_size_mb
                        pf.MaximumSize = max_size_mb
                        pf.Put_()
                    
                    self.logger.info(f"Virtual memory optimized: {initial_size_mb}MB - {max_size_mb}MB")
                    return True
                    
                except Exception as e:
                    self.logger.debug(f"WMI page file optimization failed: {e}")
            
            # Fallback: registry method
            vm_key = r'SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, vm_key, 0, winreg.KEY_SET_VALUE)
            
            # Clear page file at shutdown (privacy + performance)
            winreg.SetValueEx(key, 'ClearPageFileAtShutdown', 0, winreg.REG_DWORD, 1)
            
            winreg.CloseKey(key)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing virtual memory: {e}")
            return False
    
    def _optimize_process_priorities(self) -> bool:
        """Optimize process priorities for gaming."""
        try:
            if not HAS_WIN32:
                return False
            
            # Get current process (our monitoring app)
            current_process = win32api.GetCurrentProcess()
            
            # Set high priority class for our monitoring process
            win32process.SetPriorityClass(current_process, win32process.HIGH_PRIORITY_CLASS)
            
            self.logger.info("Process priorities optimized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing process priorities: {e}")
            return False
    
    def _optimize_network_stack(self) -> bool:
        """Optimize Windows network stack for gaming."""
        try:
            # Network adapter optimizations via netsh commands
            network_commands = [
                # Disable TCP/IP task offloading (can cause issues)
                ['netsh', 'int', 'tcp', 'set', 'global', 'taskoffload=disabled'],
                
                # Optimize TCP window scaling
                ['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'],
                
                # Enable receive side scaling
                ['netsh', 'int', 'tcp', 'set', 'global', 'rss=enabled'],
                
                # Set TCP chimney offload
                ['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'],
            ]
            
            success_count = 0
            for cmd in network_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        self.logger.debug(f"Network command failed: {' '.join(cmd)} - {result.stderr}")
                except Exception as e:
                    self.logger.debug(f"Network optimization command error: {e}")
            
            if success_count > 0:
                self.logger.info(f"Applied {success_count} network optimizations")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Error optimizing network stack: {e}")
            return False
    
    def free_memory(self) -> Dict[str, Any]:
        """Free up system memory for gaming."""
        freed_memory = {}
        
        try:
            # Get initial memory status
            initial_memory = psutil.virtual_memory()
            
            # Clear system caches
            if self._is_admin():
                try:
                    # Clear working sets
                    kernel32 = ctypes.windll.kernel32
                    kernel32.SetProcessWorkingSetSize(-1, -1, -1)
                    
                    # Clear file system cache
                    subprocess.run(['powershell', '-Command', 
                                  '[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()'],
                                 capture_output=True)
                    
                    freed_memory['cache_cleared'] = True
                    
                except Exception as e:
                    self.logger.debug(f"Cache clearing failed: {e}")
                    freed_memory['cache_cleared'] = False
            
            # Force garbage collection in Python
            import gc
            gc.collect()
            
            # Get final memory status
            final_memory = psutil.virtual_memory()
            freed_mb = (final_memory.available - initial_memory.available) / (1024 * 1024)
            
            freed_memory['freed_mb'] = round(freed_mb, 2)
            freed_memory['available_memory_gb'] = round(final_memory.available / (1024**3), 2)
            
            self.logger.info(f"Memory optimization completed: {freed_memory}")
            return freed_memory
            
        except Exception as e:
            self.logger.error(f"Error freeing memory: {e}")
            return {'error': str(e)}
    
    def _is_admin(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def rollback_optimizations(self) -> bool:
        """Rollback applied optimizations."""
        try:
            rollback_count = 0
            
            # Restore registry values
            for reg_path, original_value in self.registry_backups.items():
                try:
                    # Parse registry path
                    path_parts = reg_path.split('\\')
                    if path_parts[0] == 'HKEY_CURRENT_USER':
                        root_key = winreg.HKEY_CURRENT_USER
                        sub_path = '\\'.join(path_parts[1:-1])
                        value_name = path_parts[-1]
                    elif path_parts[0] == 'HKEY_LOCAL_MACHINE':
                        root_key = winreg.HKEY_LOCAL_MACHINE
                        sub_path = '\\'.join(path_parts[1:-1])
                        value_name = path_parts[-1]
                    else:
                        continue
                    
                    key = winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, value_name, 0, original_value[1], original_value[0])
                    winreg.CloseKey(key)
                    
                    rollback_count += 1
                    
                except Exception as e:
                    self.logger.debug(f"Could not restore {reg_path}: {e}")
            
            # Re-enable services
            self._reenable_services()
            
            # Re-enable Defender
            self._reenable_defender()
            
            self.logger.info(f"Rolled back {rollback_count} optimizations")
            return rollback_count > 0
            
        except Exception as e:
            self.logger.error(f"Error during rollback: {e}")
            return False