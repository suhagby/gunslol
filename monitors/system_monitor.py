"""
System performance monitoring module.
Monitors CPU, GPU, memory, temperature, and disk I/O performance.
"""

import psutil
import time
import threading
import logging
from typing import Dict, Any, Optional
from collections import deque

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

class SystemMonitor:
    """Monitors system performance metrics including CPU, GPU, memory, and temperatures."""
    
    def __init__(self, hardware_profile: Dict[str, Any]):
        self.hardware_profile = hardware_profile
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.metrics_history = deque(maxlen=1000)  # Store last 1000 readings
        self.current_metrics = {}
        self.lock = threading.Lock()
        
        # Initialize WMI for Windows temperature monitoring
        self.wmi_conn = None
        if HAS_WMI:
            try:
                self.wmi_conn = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            except:
                try:
                    self.wmi_conn = wmi.WMI(namespace="root\\WMI")
                except:
                    self.logger.warning("Could not initialize WMI for temperature monitoring")
        
        # GPU initialization
        self.gpu_initialized = False
        self.nvml_device_count = 0
        
        if HAS_NVML:
            try:
                self.nvml_device_count = nvml.nvmlDeviceGetCount()
                self.gpu_initialized = True
                self.logger.info(f"NVML initialized with {self.nvml_device_count} GPU(s)")
            except:
                self.logger.warning("Could not initialize NVML for GPU monitoring")
        
        self.logger.info("SystemMonitor initialized")
    
    def start(self):
        """Start the system monitoring loop."""
        self.running = True
        interval = self.hardware_profile.get('monitoring', {}).get('cpu_interval', 1.0)
        
        while self.running:
            try:
                metrics = self._collect_metrics()
                
                with self.lock:
                    self.current_metrics = metrics
                    self.metrics_history.append({
                        'timestamp': time.time(),
                        'metrics': metrics.copy()
                    })
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent system metrics."""
        with self.lock:
            return self.current_metrics.copy()
    
    def get_metrics_history(self, seconds: int = 60) -> list:
        """Get metrics history for the specified number of seconds."""
        cutoff_time = time.time() - seconds
        
        with self.lock:
            return [
                entry for entry in self.metrics_history
                if entry['timestamp'] >= cutoff_time
            ]
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect all system performance metrics."""
        metrics = {}
        
        try:
            # CPU Metrics
            metrics.update(self._get_cpu_metrics())
            
            # Memory Metrics
            metrics.update(self._get_memory_metrics())
            
            # GPU Metrics
            metrics.update(self._get_gpu_metrics())
            
            # Temperature Metrics
            metrics.update(self._get_temperature_metrics())
            
            # Disk I/O Metrics
            metrics.update(self._get_disk_metrics())
            
            # System Load Metrics
            metrics.update(self._get_system_load_metrics())
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU performance metrics."""
        metrics = {}
        
        try:
            # CPU usage per core and overall
            cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
            metrics['cpu_usage_per_core'] = cpu_percent
            metrics['cpu_usage_total'] = sum(cpu_percent) / len(cpu_percent)
            
            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                metrics['cpu_frequency_current'] = freq.current
                metrics['cpu_frequency_max'] = freq.max
                metrics['cpu_frequency_min'] = freq.min
            
            # CPU count
            metrics['cpu_cores_physical'] = psutil.cpu_count(logical=False)
            metrics['cpu_cores_logical'] = psutil.cpu_count(logical=True)
            
            # Load average (Linux/Unix) or equivalent
            try:
                load_avg = psutil.getloadavg()
                metrics['load_average_1m'] = load_avg[0]
                metrics['load_average_5m'] = load_avg[1]
                metrics['load_average_15m'] = load_avg[2]
            except:
                # Windows doesn't have load average
                pass
            
            # CPU times
            cpu_times = psutil.cpu_times()
            metrics['cpu_time_user'] = cpu_times.user
            metrics['cpu_time_system'] = cpu_times.system
            metrics['cpu_time_idle'] = cpu_times.idle
            
        except Exception as e:
            self.logger.error(f"Error getting CPU metrics: {e}")
        
        return metrics
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory usage metrics."""
        metrics = {}
        
        try:
            # RAM metrics
            memory = psutil.virtual_memory()
            metrics['memory_total'] = memory.total
            metrics['memory_available'] = memory.available
            metrics['memory_percent'] = memory.percent
            metrics['memory_used'] = memory.used
            metrics['memory_free'] = memory.free
            
            # Swap metrics
            swap = psutil.swap_memory()
            metrics['swap_total'] = swap.total
            metrics['swap_used'] = swap.used
            metrics['swap_free'] = swap.free
            metrics['swap_percent'] = swap.percent
            
            # Calculate memory pressure
            memory_pressure = (memory.percent + swap.percent * 0.5) / 100
            metrics['memory_pressure'] = min(memory_pressure, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error getting memory metrics: {e}")
        
        return metrics
    
    def _get_gpu_metrics(self) -> Dict[str, Any]:
        """Get GPU performance metrics."""
        metrics = {}
        
        try:
            if HAS_GPUTIL:
                gpus = GPUtil.getGPUs()
                for i, gpu in enumerate(gpus):
                    prefix = f'gpu_{i}_' if len(gpus) > 1 else 'gpu_'
                    
                    metrics[f'{prefix}usage'] = gpu.load * 100
                    metrics[f'{prefix}memory_used'] = gpu.memoryUsed
                    metrics[f'{prefix}memory_total'] = gpu.memoryTotal
                    metrics[f'{prefix}memory_percent'] = (gpu.memoryUsed / gpu.memoryTotal) * 100
                    metrics[f'{prefix}temperature'] = gpu.temperature
                    metrics[f'{prefix}name'] = gpu.name
            
            # NVIDIA specific metrics using NVML
            if HAS_NVML and self.gpu_initialized:
                for i in range(self.nvml_device_count):
                    try:
                        handle = nvml.nvmlDeviceGetHandleByIndex(i)
                        prefix = f'gpu_{i}_' if self.nvml_device_count > 1 else 'gpu_'
                        
                        # Power usage
                        try:
                            power = nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                            metrics[f'{prefix}power_usage'] = power
                        except:
                            pass
                        
                        # Clock speeds
                        try:
                            gpu_clock = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_GRAPHICS)
                            memory_clock = nvml.nvmlDeviceGetClockInfo(handle, nvml.NVML_CLOCK_MEM)
                            metrics[f'{prefix}clock_graphics'] = gpu_clock
                            metrics[f'{prefix}clock_memory'] = memory_clock
                        except:
                            pass
                        
                        # Fan speed
                        try:
                            fan_speed = nvml.nvmlDeviceGetFanSpeed(handle)
                            metrics[f'{prefix}fan_speed'] = fan_speed
                        except:
                            pass
                        
                        # Performance state
                        try:
                            perf_state = nvml.nvmlDeviceGetPerformanceState(handle)
                            metrics[f'{prefix}performance_state'] = perf_state
                        except:
                            pass
                            
                    except Exception as e:
                        self.logger.debug(f"Error getting NVML metrics for GPU {i}: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error getting GPU metrics: {e}")
        
        return metrics
    
    def _get_temperature_metrics(self) -> Dict[str, Any]:
        """Get system temperature metrics."""
        metrics = {}
        
        try:
            # Try to get temperature from psutil (Linux)
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                
                for name, entries in temps.items():
                    for i, entry in enumerate(entries):
                        sensor_name = f"{name}_{i}" if len(entries) > 1 else name
                        metrics[f'temp_{sensor_name}'] = entry.current
                        if entry.high:
                            metrics[f'temp_{sensor_name}_high'] = entry.high
                        if entry.critical:
                            metrics[f'temp_{sensor_name}_critical'] = entry.critical
            
            # Windows temperature monitoring via WMI
            if self.wmi_conn:
                try:
                    sensors = self.wmi_conn.Sensor()
                    for sensor in sensors:
                        if sensor.SensorType == 'Temperature':
                            sensor_name = sensor.Name.replace(' ', '_').lower()
                            metrics[f'temp_{sensor_name}'] = sensor.Value
                except Exception as e:
                    self.logger.debug(f"WMI temperature query failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Error getting temperature metrics: {e}")
        
        return metrics
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk I/O performance metrics."""
        metrics = {}
        
        try:
            # Disk usage
            disk_usage = psutil.disk_usage('/')
            metrics['disk_total'] = disk_usage.total
            metrics['disk_used'] = disk_usage.used
            metrics['disk_free'] = disk_usage.free
            metrics['disk_percent'] = (disk_usage.used / disk_usage.total) * 100
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics['disk_read_count'] = disk_io.read_count
                metrics['disk_write_count'] = disk_io.write_count
                metrics['disk_read_bytes'] = disk_io.read_bytes
                metrics['disk_write_bytes'] = disk_io.write_bytes
                metrics['disk_read_time'] = disk_io.read_time
                metrics['disk_write_time'] = disk_io.write_time
                
                # Calculate I/O rates (simple approximation)
                if hasattr(self, '_last_disk_io'):
                    time_diff = time.time() - self._last_disk_time
                    if time_diff > 0:
                        read_rate = (disk_io.read_bytes - self._last_disk_io.read_bytes) / time_diff
                        write_rate = (disk_io.write_bytes - self._last_disk_io.write_bytes) / time_diff
                        metrics['disk_read_rate'] = read_rate
                        metrics['disk_write_rate'] = write_rate
                
                self._last_disk_io = disk_io
                self._last_disk_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Error getting disk metrics: {e}")
        
        return metrics
    
    def _get_system_load_metrics(self) -> Dict[str, Any]:
        """Get system load and process metrics."""
        metrics = {}
        
        try:
            # Boot time
            metrics['boot_time'] = psutil.boot_time()
            metrics['uptime'] = time.time() - psutil.boot_time()
            
            # Process count
            metrics['process_count'] = len(psutil.pids())
            
            # Network connections
            try:
                connections = psutil.net_connections()
                metrics['network_connections'] = len(connections)
            except psutil.AccessDenied:
                pass
            
        except Exception as e:
            self.logger.error(f"Error getting system load metrics: {e}")
        
        return metrics
    
    def is_system_under_stress(self) -> Dict[str, bool]:
        """Check if system is under stress based on thresholds."""
        stress_indicators = {}
        metrics = self.get_current_metrics()
        thresholds = self.hardware_profile.get('thresholds', {})
        
        try:
            # CPU stress
            cpu_usage = metrics.get('cpu_usage_total', 0)
            stress_indicators['cpu_stress'] = cpu_usage > thresholds.get('max_cpu_usage', 90)
            
            # Memory stress
            memory_percent = metrics.get('memory_percent', 0)
            stress_indicators['memory_stress'] = memory_percent > thresholds.get('max_memory_usage', 90)
            
            # GPU stress
            gpu_usage = metrics.get('gpu_usage', 0)
            stress_indicators['gpu_stress'] = gpu_usage > thresholds.get('max_gpu_usage', 95)
            
            # Temperature stress
            cpu_temp = metrics.get('temp_cpu_package', 0) or metrics.get('cpu_temperature', 0)
            gpu_temp = metrics.get('gpu_temperature', 0)
            
            stress_indicators['cpu_temp_stress'] = cpu_temp > thresholds.get('max_cpu_temp', 85)
            stress_indicators['gpu_temp_stress'] = gpu_temp > thresholds.get('max_gpu_temp', 83)
            
            # Overall system stress
            stress_indicators['overall_stress'] = any(stress_indicators.values())
            
        except Exception as e:
            self.logger.error(f"Error checking system stress: {e}")
        
        return stress_indicators