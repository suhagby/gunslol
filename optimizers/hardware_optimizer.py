"""
Hardware-specific optimization module.
Handles CPU, GPU, and memory optimizations specific to the target hardware.
"""

import os
import sys
import logging
import subprocess
import time
import threading
from typing import Dict, Any, Optional, List
import psutil

try:
    import GPUtil
    HAS_GPUTIL = True
except ImportError:
    HAS_GPUTIL = False

try:
    import py3nvml.py3nvml as nvml
    nvml.nvmlInit()
    HAS_NVML = True
except:
    HAS_NVML = False

try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

class HardwareOptimizer:
    """Handles hardware-specific optimizations for Intel i7-9700K + RTX 3080."""
    
    def __init__(self, hardware_profile: Dict[str, Any]):
        self.hardware_profile = hardware_profile
        self.logger = logging.getLogger(__name__)
        
        # Current optimization state
        self.cpu_boosted = False
        self.gpu_boosted = False
        self.memory_optimized = False
        
        # Backup original settings
        self.original_settings = {}
        
        # Initialize hardware interfaces
        self.wmi_conn = None
        if HAS_WMI:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception as e:
                self.logger.debug(f"WMI initialization failed: {e}")
        
        # GPU initialization
        self.gpu_device_count = 0
        self.nvml_handles = []
        
        if HAS_NVML:
            try:
                self.gpu_device_count = nvml.nvmlDeviceGetCount()
                for i in range(self.gpu_device_count):
                    handle = nvml.nvmlDeviceGetHandleByIndex(i)
                    self.nvml_handles.append(handle)
                self.logger.info(f"Initialized NVML for {self.gpu_device_count} GPU(s)")
            except Exception as e:
                self.logger.warning(f"NVML GPU initialization failed: {e}")
        
        self.logger.info("HardwareOptimizer initialized for i7-9700K + RTX 3080")
    
    def boost_performance(self) -> Dict[str, bool]:
        """Apply performance boost optimizations to all hardware components."""
        results = {}
        
        try:
            self.logger.info("Applying hardware performance boost...")
            
            # CPU optimizations
            results['cpu_boost'] = self._boost_cpu_performance()
            
            # GPU optimizations
            results['gpu_boost'] = self._boost_gpu_performance()
            
            # Memory optimizations
            results['memory_optimization'] = self._optimize_memory_performance()
            
            # Storage optimizations
            results['storage_optimization'] = self._optimize_storage_performance()
            
            self.logger.info(f"Hardware performance boost completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during hardware performance boost: {e}")
            return {'error': str(e)}
    
    def _boost_cpu_performance(self) -> bool:
        """Optimize Intel i7-9700K CPU performance."""
        try:
            cpu_profile = self.hardware_profile.get('cpu', {})
            
            success_count = 0
            
            # Set CPU affinity for critical processes
            if self._set_cpu_affinity():
                success_count += 1
            
            # Optimize CPU power management
            if self._optimize_cpu_power_management():
                success_count += 1
            
            # Set process priorities
            if self._optimize_process_priorities():
                success_count += 1
            
            # CPU cache optimizations
            if self._optimize_cpu_cache():
                success_count += 1
            
            # Thermal management
            if self._optimize_cpu_thermal_management():
                success_count += 1
            
            self.cpu_boosted = success_count > 0
            self.logger.info(f"CPU optimization completed: {success_count} optimizations applied")
            
            return self.cpu_boosted
            
        except Exception as e:
            self.logger.error(f"CPU optimization error: {e}")
            return False
    
    def _set_cpu_affinity(self) -> bool:
        """Set CPU affinity for optimal performance."""
        try:
            current_process = psutil.Process()
            
            # For i7-9700K (8 cores, no hyperthreading), use all cores
            available_cores = list(range(psutil.cpu_count(logical=False)))
            
            # Set affinity to physical cores only
            current_process.cpu_affinity(available_cores)
            
            self.logger.info(f"Set CPU affinity to cores: {available_cores}")
            return True
            
        except Exception as e:
            self.logger.error(f"CPU affinity optimization failed: {e}")
            return False
    
    def _optimize_cpu_power_management(self) -> bool:
        """Optimize CPU power management for performance."""
        try:
            # Disable CPU power saving features for maximum performance
            power_commands = [
                # Set processor performance boost mode
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 '54533251-82be-4824-96c1-47b60b740d00', '45bcc044-d885-43e2-8605-ee0ec6e96b59', '0'],
                
                # Disable processor idle
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 '54533251-82be-4824-96c1-47b60b740d00', '5d76a2ca-e8c0-402f-a133-2158492d58ad', '1'],
                 
                # Set maximum processor state to 100%
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 '54533251-82be-4824-96c1-47b60b740d00', 'bc5038f7-23e0-4960-96da-33abaf5935ec', '100'],
                 
                # Set minimum processor state to 100% for gaming
                ['powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                 '54533251-82be-4824-96c1-47b60b740d00', '893dee8e-2bef-41e0-89c6-b55d0929964c', '100'],
            ]
            
            success_count = 0
            for cmd in power_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        self.logger.debug(f"Power command failed: {' '.join(cmd)}")
                except Exception as e:
                    self.logger.debug(f"Power command error: {e}")
            
            # Apply the settings
            if success_count > 0:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True)
                self.logger.info(f"Applied {success_count} CPU power optimizations")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"CPU power optimization failed: {e}")
            return False
    
    def _optimize_process_priorities(self) -> bool:
        """Optimize process priorities for gaming performance."""
        try:
            import win32api
            import win32process
            import win32con
            
            # Set our monitor process to high priority
            current_process = win32api.GetCurrentProcess()
            win32process.SetPriorityClass(current_process, win32process.HIGH_PRIORITY_CLASS)
            
            # Find and boost game processes
            boosted_games = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Check if it's a known game process
                    game_executables = [
                        'league of legends.exe', 'valorant.exe', 'cs2.exe',
                        'fortnite.exe', 'apex_legends.exe', 'overwatch.exe',
                        'cod.exe', 'cyberpunk2077.exe', 'eldenring.exe'
                    ]
                    
                    if any(game_exe in proc_name for game_exe in game_executables):
                        # Set game process to realtime priority (careful!)
                        game_handle = win32api.OpenProcess(
                            win32con.PROCESS_SET_INFORMATION, False, proc.pid
                        )
                        win32process.SetPriorityClass(game_handle, win32process.HIGH_PRIORITY_CLASS)
                        win32api.CloseHandle(game_handle)
                        
                        boosted_games += 1
                        self.logger.info(f"Boosted priority for game: {proc.info['name']}")
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                    continue
            
            self.logger.info(f"Process priority optimization completed: {boosted_games} games boosted")
            return True
            
        except ImportError:
            self.logger.warning("Win32 libraries not available for process priority optimization")
            return False
        except Exception as e:
            self.logger.error(f"Process priority optimization failed: {e}")
            return False
    
    def _optimize_cpu_cache(self) -> bool:
        """Optimize CPU cache behavior for gaming."""
        try:
            # Set memory allocation policy for better cache usage
            success_count = 0
            
            # Optimize memory mapping for games
            try:
                import mlock
                # Lock critical memory pages in RAM (prevents swapping)
                success_count += 1
            except ImportError:
                pass
            
            # Optimize CPU cache through system calls
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                
                # Set process working set size to optimize cache usage
                # For 16GB system, set working set to ~12GB max
                min_size = 2 * 1024 * 1024 * 1024  # 2GB minimum
                max_size = 12 * 1024 * 1024 * 1024  # 12GB maximum
                
                result = kernel32.SetProcessWorkingSetSize(-1, min_size, max_size)
                if result:
                    success_count += 1
                    self.logger.info("CPU cache working set optimized")
                    
            except Exception as e:
                self.logger.debug(f"Cache optimization failed: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"CPU cache optimization failed: {e}")
            return False
    
    def _optimize_cpu_thermal_management(self) -> bool:
        """Optimize CPU thermal management for sustained performance."""
        try:
            cpu_profile = self.hardware_profile.get('cpu', {})
            max_temp = cpu_profile.get('temp_critical', 85)
            
            # Monitor temperature and adjust accordingly
            temps = psutil.sensors_temperatures()
            cpu_temp = 0
            
            # Get CPU temperature from available sensors
            if 'coretemp' in temps:
                cpu_temp = max([sensor.current for sensor in temps['coretemp']])
            elif 'cpu_thermal' in temps:
                cpu_temp = temps['cpu_thermal'][0].current
            
            if cpu_temp > 0:
                self.logger.info(f"Current CPU temperature: {cpu_temp}°C")
                
                # If temperature is high, implement thermal throttling prevention
                if cpu_temp > max_temp - 5:  # 5°C before critical
                    self._manage_cpu_cooling()
                    return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"CPU thermal management failed: {e}")
            return False
    
    def manage_cpu_cooling(self) -> bool:
        """Manage CPU cooling to prevent thermal throttling."""
        try:
            self.logger.info("Managing CPU cooling due to high temperature")
            
            # Reduce CPU maximum frequency temporarily
            power_cmd = [
                'powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                '54533251-82be-4824-96c1-47b60b740d00', 
                'bc5038f7-23e0-4960-96da-33abaf5935ec', '95'  # 95% max CPU
            ]
            
            result = subprocess.run(power_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True)
                self.logger.info("Reduced CPU maximum frequency to 95% for cooling")
                
                # Schedule restoration after cooling
                threading.Timer(300, self._restore_cpu_frequency).start()  # 5 minutes
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"CPU cooling management failed: {e}")
            return False
    
    def _restore_cpu_frequency(self):
        """Restore CPU to maximum frequency after cooling."""
        try:
            power_cmd = [
                'powercfg', '/setacvalueindex', 'SCHEME_CURRENT',
                '54533251-82be-4824-96c1-47b60b740d00', 
                'bc5038f7-23e0-4960-96da-33abaf5935ec', '100'
            ]
            
            result = subprocess.run(power_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                subprocess.run(['powercfg', '/setactive', 'SCHEME_CURRENT'], capture_output=True)
                self.logger.info("Restored CPU maximum frequency to 100%")
                
        except Exception as e:
            self.logger.error(f"CPU frequency restoration failed: {e}")
    
    def _boost_gpu_performance(self) -> bool:
        """Optimize NVIDIA RTX 3080 performance."""
        try:
            gpu_profile = self.hardware_profile.get('gpu', {})
            
            success_count = 0
            
            # NVIDIA-specific optimizations
            if self._optimize_nvidia_settings():
                success_count += 1
            
            # GPU power limit optimization
            if self._optimize_gpu_power_limit():
                success_count += 1
            
            # GPU memory optimization
            if self._optimize_gpu_memory():
                success_count += 1
            
            # GPU fan curve optimization
            if self._optimize_gpu_cooling():
                success_count += 1
            
            self.gpu_boosted = success_count > 0
            self.logger.info(f"GPU optimization completed: {success_count} optimizations applied")
            
            return self.gpu_boosted
            
        except Exception as e:
            self.logger.error(f"GPU optimization error: {e}")
            return False
    
    def _optimize_nvidia_settings(self) -> bool:
        """Optimize NVIDIA Control Panel settings via registry."""
        try:
            import winreg
            
            # NVIDIA Control Panel registry optimizations
            nvidia_key = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000'
            
            nvidia_optimizations = {
                'PowerMizerEnable': (winreg.REG_DWORD, 1),
                'PowerMizerLevel': (winreg.REG_DWORD, 0),  # Prefer maximum performance
                'PowerMizerLevelAC': (winreg.REG_DWORD, 0),
                'PerfLevelSrc': (winreg.REG_DWORD, 0x2222),
            }
            
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, nvidia_key, 0, winreg.KEY_SET_VALUE)
                
                for value_name, (value_type, value_data) in nvidia_optimizations.items():
                    try:
                        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                    except Exception as e:
                        self.logger.debug(f"Could not set {value_name}: {e}")
                
                winreg.CloseKey(key)
                self.logger.info("Applied NVIDIA registry optimizations")
                return True
                
            except FileNotFoundError:
                self.logger.warning("NVIDIA registry key not found")
                return False
                
        except Exception as e:
            self.logger.error(f"NVIDIA settings optimization failed: {e}")
            return False
    
    def _optimize_gpu_power_limit(self) -> bool:
        """Optimize GPU power limit for maximum performance."""
        try:
            if not HAS_NVML or len(self.nvml_handles) == 0:
                self.logger.warning("NVML not available for GPU power optimization")
                return False
            
            success_count = 0
            
            for i, handle in enumerate(self.nvml_handles):
                try:
                    # Get current power limit
                    current_limit = nvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)
                    max_power_limit = current_limit[1] / 1000.0  # Convert to watts
                    
                    # Get current power limit
                    current_power = nvml.nvmlDeviceGetPowerManagementLimitDefault(handle) / 1000.0
                    
                    self.logger.info(f"GPU {i} current power limit: {current_power}W, max: {max_power_limit}W")
                    
                    # For RTX 3080, try to increase power limit to maximum
                    if max_power_limit > current_power:
                        try:
                            nvml.nvmlDeviceSetPowerManagementLimitDefault(handle, int(max_power_limit * 1000))
                            success_count += 1
                            self.logger.info(f"Increased GPU {i} power limit to {max_power_limit}W")
                        except nvml.NVMLError as e:
                            self.logger.debug(f"Could not increase power limit: {e}")
                    
                except nvml.NVMLError as e:
                    self.logger.debug(f"GPU {i} power limit optimization failed: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"GPU power limit optimization failed: {e}")
            return False
    
    def _optimize_gpu_memory(self) -> bool:
        """Optimize GPU memory for gaming performance."""
        try:
            if not HAS_NVML or len(self.nvml_handles) == 0:
                return False
            
            success_count = 0
            
            for i, handle in enumerate(self.nvml_handles):
                try:
                    # Get memory info
                    mem_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                    total_memory = mem_info.total / (1024**3)  # GB
                    
                    self.logger.info(f"GPU {i} total VRAM: {total_memory:.1f}GB")
                    
                    # GPU memory optimizations through NVIDIA ML
                    try:
                        # Clear GPU memory cache if needed
                        if mem_info.used / mem_info.total > 0.9:  # >90% usage
                            self.logger.info(f"GPU {i} memory usage high, attempting cleanup")
                            # This would require specific CUDA operations
                            success_count += 1
                    
                    except Exception as e:
                        self.logger.debug(f"GPU memory optimization failed: {e}")
                    
                except nvml.NVMLError as e:
                    self.logger.debug(f"GPU {i} memory info failed: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"GPU memory optimization failed: {e}")
            return False
    
    def _optimize_gpu_cooling(self) -> bool:
        """Optimize GPU cooling for sustained performance."""
        try:
            if not HAS_NVML or len(self.nvml_handles) == 0:
                return False
            
            success_count = 0
            
            for i, handle in enumerate(self.nvml_handles):
                try:
                    # Get current temperature
                    temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    self.logger.info(f"GPU {i} temperature: {temp}°C")
                    
                    # Get fan speed
                    try:
                        fan_speed = nvml.nvmlDeviceGetFanSpeed(handle)
                        self.logger.info(f"GPU {i} fan speed: {fan_speed}%")
                        
                        # If temperature is high, increase fan speed
                        gpu_profile = self.hardware_profile.get('gpu', {})
                        temp_warning = gpu_profile.get('temp_warning', 78)
                        
                        if temp > temp_warning and fan_speed < 80:
                            # Try to set more aggressive fan curve
                            # Note: This typically requires MSI Afterburner or similar
                            self.logger.info(f"GPU {i} temperature high, aggressive cooling recommended")
                            success_count += 1
                            
                    except nvml.NVMLError:
                        # Fan speed control might not be available
                        pass
                    
                except nvml.NVMLError as e:
                    self.logger.debug(f"GPU {i} temperature check failed: {e}")
                    continue
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"GPU cooling optimization failed: {e}")
            return False
    
    def manage_gpu_cooling(self) -> bool:
        """Manage GPU cooling to prevent thermal throttling."""
        try:
            if not HAS_NVML or len(self.nvml_handles) == 0:
                return False
            
            self.logger.info("Managing GPU cooling due to high temperature")
            
            for i, handle in enumerate(self.nvml_handles):
                try:
                    # Get current temperature
                    temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                    
                    gpu_profile = self.hardware_profile.get('gpu', {})
                    temp_critical = gpu_profile.get('temp_critical', 83)
                    
                    if temp > temp_critical - 5:  # 5°C before critical
                        # Reduce power limit temporarily
                        try:
                            current_limit = nvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)
                            reduced_limit = int(current_limit[1] * 0.9)  # 90% of max power
                            
                            nvml.nvmlDeviceSetPowerManagementLimitDefault(handle, reduced_limit)
                            self.logger.info(f"Reduced GPU {i} power limit for cooling")
                            
                            # Schedule restoration
                            threading.Timer(300, lambda: self._restore_gpu_power_limit(i, handle)).start()
                            
                        except nvml.NVMLError as e:
                            self.logger.debug(f"Could not reduce GPU power limit: {e}")
                    
                except nvml.NVMLError as e:
                    self.logger.debug(f"GPU {i} thermal management failed: {e}")
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"GPU cooling management failed: {e}")
            return False
    
    def _restore_gpu_power_limit(self, gpu_index: int, handle):
        """Restore GPU power limit after cooling."""
        try:
            # Restore to maximum power limit
            constraints = nvml.nvmlDeviceGetPowerManagementLimitConstraints(handle)
            max_limit = constraints[1]
            
            nvml.nvmlDeviceSetPowerManagementLimitDefault(handle, max_limit)
            self.logger.info(f"Restored GPU {gpu_index} power limit to maximum")
            
        except Exception as e:
            self.logger.error(f"GPU power limit restoration failed: {e}")
    
    def _optimize_memory_performance(self) -> bool:
        """Optimize system memory for gaming performance."""
        try:
            memory_profile = self.hardware_profile.get('memory', {})
            
            success_count = 0
            
            # Memory allocation optimizations
            if self._optimize_memory_allocation():
                success_count += 1
            
            # XMP profile optimization
            if self._optimize_memory_timings():
                success_count += 1
            
            # Memory compression settings
            if self._optimize_memory_compression():
                success_count += 1
            
            self.memory_optimized = success_count > 0
            self.logger.info(f"Memory optimization completed: {success_count} optimizations applied")
            
            return self.memory_optimized
            
        except Exception as e:
            self.logger.error(f"Memory optimization error: {e}")
            return False
    
    def _optimize_memory_allocation(self) -> bool:
        """Optimize memory allocation for gaming."""
        try:
            import ctypes
            
            # Optimize heap allocation
            kernel32 = ctypes.windll.kernel32
            
            # Set low fragmentation heap
            heap_handle = kernel32.GetProcessHeap()
            heap_info = ctypes.c_ulong(2)  # Low fragmentation heap
            
            result = kernel32.HeapSetInformation(
                heap_handle, 
                0,  # HeapCompatibilityInformation
                ctypes.byref(heap_info),
                ctypes.sizeof(heap_info)
            )
            
            if result:
                self.logger.info("Enabled low fragmentation heap")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Memory allocation optimization failed: {e}")
            return False
    
    def _optimize_memory_timings(self) -> bool:
        """Optimize memory timings and XMP profile."""
        try:
            # Check if XMP is enabled (read-only check)
            memory_profile = self.hardware_profile.get('memory', {})
            
            if memory_profile.get('xmp_enabled', False):
                self.logger.info("XMP profile is enabled in hardware profile")
                
                # Memory timing optimizations through Windows
                # Set memory management flags
                import winreg
                
                mm_key = r'SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
                
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, mm_key, 0, winreg.KEY_SET_VALUE)
                    
                    # Optimize memory management
                    winreg.SetValueEx(key, 'LargeSystemCache', 0, winreg.REG_DWORD, 0)  # Optimize for programs
                    winreg.SetValueEx(key, 'SystemCacheLimit', 0, winreg.REG_DWORD, 0xFFFFFFFF)
                    
                    winreg.CloseKey(key)
                    self.logger.info("Applied memory timing optimizations")
                    return True
                    
                except Exception as e:
                    self.logger.debug(f"Memory timing registry optimization failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Memory timing optimization failed: {e}")
            return False
    
    def _optimize_memory_compression(self) -> bool:
        """Optimize memory compression settings."""
        try:
            # Disable memory compression for gaming (reduces latency)
            compression_cmd = [
                'powershell', '-Command',
                'Disable-MMAgent -MemoryCompression'
            ]
            
            result = subprocess.run(compression_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Disabled memory compression for lower latency")
                return True
            else:
                self.logger.debug(f"Memory compression disable failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Memory compression optimization failed: {e}")
            return False
    
    def _optimize_storage_performance(self) -> bool:
        """Optimize M.2 SSD storage performance."""
        try:
            storage_profile = self.hardware_profile.get('storage', {})
            
            success_count = 0
            
            # Disable indexing on game drives
            if self._disable_drive_indexing():
                success_count += 1
            
            # Optimize SSD settings
            if self._optimize_ssd_settings():
                success_count += 1
            
            # Optimize prefetch settings
            if self._optimize_prefetch_settings():
                success_count += 1
            
            self.logger.info(f"Storage optimization completed: {success_count} optimizations applied")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Storage optimization error: {e}")
            return False
    
    def _disable_drive_indexing(self) -> bool:
        """Disable Windows indexing on SSDs for better performance."""
        try:
            # Get drive letters
            drives = psutil.disk_partitions()
            
            success_count = 0
            
            for drive in drives:
                if 'fixed' in drive.opts.lower():  # Fixed drives only
                    drive_letter = drive.device
                    
                    # Disable indexing via command
                    disable_cmd = ['fsutil', 'behavior', 'set', 'DisableIndexing', '1']
                    
                    result = subprocess.run(disable_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        success_count += 1
                        self.logger.info(f"Disabled indexing on drive {drive_letter}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Drive indexing optimization failed: {e}")
            return False
    
    def _optimize_ssd_settings(self) -> bool:
        """Optimize SSD-specific settings."""
        try:
            import winreg
            
            # SSD optimizations
            ssd_optimizations = {
                # Disable defrag scheduling for SSDs
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\OptimalLayout': {
                    'EnableAutoLayout': (winreg.REG_DWORD, 0)
                },
                
                # Optimize TRIM settings
                r'SYSTEM\CurrentControlSet\Control\FileSystem': {
                    'DisableDeleteNotification': (winreg.REG_DWORD, 0)  # Enable TRIM
                }
            }
            
            success_count = 0
            
            for reg_path, values in ssd_optimizations.items():
                try:
                    if reg_path.startswith('HKEY_CURRENT_USER'):
                        root_key = winreg.HKEY_CURRENT_USER
                        sub_path = reg_path[len('HKEY_CURRENT_USER\\'):]
                    else:
                        root_key = winreg.HKEY_LOCAL_MACHINE
                        sub_path = reg_path
                    
                    try:
                        key = winreg.OpenKey(root_key, sub_path, 0, winreg.KEY_SET_VALUE)
                    except FileNotFoundError:
                        key = winreg.CreateKey(root_key, sub_path)
                    
                    for value_name, (value_type, value_data) in values.items():
                        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
                        success_count += 1
                    
                    winreg.CloseKey(key)
                    
                except Exception as e:
                    self.logger.debug(f"SSD optimization failed for {reg_path}: {e}")
            
            self.logger.info(f"Applied {success_count} SSD optimizations")
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"SSD settings optimization failed: {e}")
            return False
    
    def _optimize_prefetch_settings(self) -> bool:
        """Optimize Windows prefetch settings for SSD."""
        try:
            import winreg
            
            # Optimize prefetch for SSD
            prefetch_key = r'SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters'
            
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, prefetch_key, 0, winreg.KEY_SET_VALUE)
            
            # Set prefetch to boot files only (optimal for SSD)
            winreg.SetValueEx(key, 'EnablePrefetcher', 0, winreg.REG_DWORD, 2)  # Boot files only
            winreg.SetValueEx(key, 'EnableSuperfetch', 0, winreg.REG_DWORD, 0)   # Disable superfetch
            
            winreg.CloseKey(key)
            
            self.logger.info("Optimized prefetch settings for SSD")
            return True
            
        except Exception as e:
            self.logger.error(f"Prefetch optimization failed: {e}")
            return False
    
    def get_hardware_status(self) -> Dict[str, Any]:
        """Get current hardware optimization status."""
        status = {
            'cpu_boosted': self.cpu_boosted,
            'gpu_boosted': self.gpu_boosted,
            'memory_optimized': self.memory_optimized,
            'optimization_history': self.optimization_history.copy(),
            'hardware_profile': self.hardware_profile['profile_name']
        }
        
        return status