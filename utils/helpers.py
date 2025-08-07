"""
Helper utilities for the gaming performance monitor.
Contains common utility functions and system checks.
"""

import os
import sys
import ctypes
import platform
import subprocess
import psutil
import time
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
import logging
from functools import wraps

def is_admin() -> bool:
    """Check if the script is running with administrator privileges."""
    try:
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except AttributeError:
        return False

def request_admin_privileges() -> bool:
    """Request administrator privileges (Windows only)."""
    try:
        if platform.system() != 'Windows':
            print("Administrator privileges not supported on this platform")
            return False
        
        if is_admin():
            return True
        
        # Re-run the script with admin privileges
        script_path = sys.argv[0]
        params = ' '.join(sys.argv[1:])
        
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{script_path}" {params}', None, 1
        )
        
        # If successful, the current process should exit
        if result > 32:
            print("Restarting with administrator privileges...")
            return True
        else:
            print("Failed to obtain administrator privileges")
            return False
            
    except Exception as e:
        print(f"Error requesting admin privileges: {e}")
        return False

def load_yaml_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config if config else {}
        
    except Exception as e:
        logging.error(f"Failed to load configuration from {config_path}: {e}")
        return {}

def save_yaml_config(config: Dict[str, Any], config_path: Union[str, Path]) -> bool:
    """Save configuration to YAML file."""
    try:
        config_path = Path(config_path)
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save configuration to {config_path}: {e}")
        return False

def load_json_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from JSON file."""
    try:
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return config if config else {}
        
    except Exception as e:
        logging.error(f"Failed to load JSON configuration from {config_path}: {e}")
        return {}

def save_json_config(config: Dict[str, Any], config_path: Union[str, Path]) -> bool:
    """Save configuration to JSON file."""
    try:
        config_path = Path(config_path)
        
        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to save JSON configuration to {config_path}: {e}")
        return False

def get_system_info() -> Dict[str, Any]:
    """Get comprehensive system information."""
    try:
        info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'python_version': platform.python_version()
            },
            'cpu': {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {},
            'network': {
                'interfaces': list(psutil.net_if_addrs().keys())
            }
        }
        
        # Disk information
        for partition in psutil.disk_partitions():
            try:
                disk_usage = psutil.disk_usage(partition.mountpoint)
                info['disk'][partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'filesystem': partition.fstype,
                    'total': disk_usage.total,
                    'used': disk_usage.used,
                    'free': disk_usage.free,
                    'percent': (disk_usage.used / disk_usage.total) * 100
                }
            except PermissionError:
                continue
        
        return info
        
    except Exception as e:
        logging.error(f"Failed to get system info: {e}")
        return {}

def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are available."""
    dependencies = {
        'psutil': False,
        'yaml': False,
        'tkinter': False,
        'matplotlib': False,
        'numpy': False,
        'GPUtil': False,
        'py3nvml': False,
        'wmi': False,
        'win32api': False,
        'ping3': False,
        'speedtest': False,
        'plyer': False,
        'win10toast': False
    }
    
    # Check each dependency
    for dep in dependencies:
        try:
            if dep == 'tkinter':
                import tkinter
                dependencies[dep] = True
            elif dep == 'win32api':
                import win32api
                dependencies[dep] = True
            else:
                __import__(dep)
                dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    try:
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    except:
        return "0 B"

def format_frequency(hz: float) -> str:
    """Format frequency in Hz to human readable format."""
    try:
        if hz >= 1_000_000_000:
            return f"{hz / 1_000_000_000:.2f} GHz"
        elif hz >= 1_000_000:
            return f"{hz / 1_000_000:.0f} MHz"
        elif hz >= 1_000:
            return f"{hz / 1_000:.0f} KHz"
        else:
            return f"{hz:.0f} Hz"
    except:
        return "0 Hz"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format."""
    try:
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"
    except:
        return "0s"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default

def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a value between min and max values."""
    return max(min_value, min(value, max_value))

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, exceptions: Tuple = (Exception,)):
    """Decorator to retry function on exception."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                    else:
                        break
            
            # If all retries failed, raise the last exception
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

def run_command(command: List[str], timeout: int = 30, capture_output: bool = True) -> Tuple[int, str, str]:
    """
    Run a command and return exit code, stdout, and stderr.
    
    Args:
        command: Command and arguments as list
        timeout: Timeout in seconds
        capture_output: Whether to capture output
    
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            timeout=timeout,
            capture_output=capture_output,
            text=True,
            check=False
        )
        
        return result.returncode, result.stdout or "", result.stderr or ""
        
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return -1, "", str(e)

def find_process_by_name(process_name: str) -> List[psutil.Process]:
    """Find processes by name."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
        
    except Exception as e:
        logging.error(f"Error finding process {process_name}: {e}")
        return []

def kill_process_by_name(process_name: str) -> int:
    """Kill processes by name. Returns number of processes killed."""
    try:
        processes = find_process_by_name(process_name)
        killed_count = 0
        
        for proc in processes:
            try:
                proc.terminate()
                killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Wait for processes to terminate gracefully
        time.sleep(2)
        
        # Force kill any remaining processes
        for proc in processes:
            try:
                if proc.is_running():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return killed_count
        
    except Exception as e:
        logging.error(f"Error killing process {process_name}: {e}")
        return 0

def get_gpu_info() -> Dict[str, Any]:
    """Get GPU information using multiple methods."""
    gpu_info = {'gpus': [], 'method': 'none'}
    
    try:
        # Try GPUtil first
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            
            for gpu in gpus:
                gpu_info['gpus'].append({
                    'name': gpu.name,
                    'driver_version': gpu.driver,
                    'memory_total': gpu.memoryTotal,
                    'memory_used': gpu.memoryUsed,
                    'memory_free': gpu.memoryFree,
                    'temperature': gpu.temperature,
                    'load': gpu.load * 100
                })
            
            gpu_info['method'] = 'GPUtil'
            return gpu_info
            
        except ImportError:
            pass
        
        # Try NVML for NVIDIA GPUs
        try:
            import py3nvml.py3nvml as nvml
            nvml.nvmlInit()
            
            device_count = nvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = nvml.nvmlDeviceGetHandleByIndex(i)
                
                name = nvml.nvmlDeviceGetName(handle).decode('utf-8')
                memory_info = nvml.nvmlDeviceGetMemoryInfo(handle)
                
                try:
                    temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = 0
                
                try:
                    util = nvml.nvmlDeviceGetUtilizationRates(handle)
                    gpu_util = util.gpu
                    memory_util = util.memory
                except:
                    gpu_util = 0
                    memory_util = 0
                
                gpu_info['gpus'].append({
                    'name': name,
                    'memory_total': memory_info.total // (1024**2),  # MB
                    'memory_used': memory_info.used // (1024**2),   # MB
                    'memory_free': memory_info.free // (1024**2),   # MB
                    'temperature': temp,
                    'load': gpu_util,
                    'memory_load': memory_util
                })
            
            gpu_info['method'] = 'NVML'
            return gpu_info
            
        except ImportError:
            pass
        
        # Try WMI for Windows
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                
                for gpu in c.Win32_VideoController():
                    if gpu.Name and 'Microsoft' not in gpu.Name:
                        gpu_info['gpus'].append({
                            'name': gpu.Name,
                            'driver_version': gpu.DriverVersion or 'Unknown',
                            'memory_total': int(gpu.AdapterRAM or 0) // (1024**2) if gpu.AdapterRAM else 0,
                            'video_processor': gpu.VideoProcessor or 'Unknown'
                        })
                
                gpu_info['method'] = 'WMI'
                return gpu_info
                
            except ImportError:
                pass
        
    except Exception as e:
        logging.error(f"Error getting GPU info: {e}")
    
    return gpu_info

def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """Check if internet connection is available."""
    try:
        import socket
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

def get_network_interfaces() -> Dict[str, Dict[str, Any]]:
    """Get detailed network interface information."""
    try:
        interfaces = {}
        
        # Get interface addresses
        addrs = psutil.net_if_addrs()
        
        # Get interface statistics
        stats = psutil.net_if_stats()
        
        for interface_name in addrs:
            interface_info = {
                'addresses': [],
                'is_up': False,
                'speed': 0,
                'mtu': 0
            }
            
            # Get addresses
            for addr in addrs[interface_name]:
                addr_info = {
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask,
                    'broadcast': addr.broadcast
                }
                interface_info['addresses'].append(addr_info)
            
            # Get statistics
            if interface_name in stats:
                stat = stats[interface_name]
                interface_info.update({
                    'is_up': stat.isup,
                    'speed': stat.speed,
                    'mtu': stat.mtu,
                    'duplex': stat.duplex
                })
            
            interfaces[interface_name] = interface_info
        
        return interfaces
        
    except Exception as e:
        logging.error(f"Error getting network interfaces: {e}")
        return {}

def create_backup_config(config: Dict[str, Any], backup_dir: str = "backups") -> str:
    """Create a timestamped backup of configuration."""
    try:
        backup_path = Path(backup_dir)
        backup_path.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"config_backup_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Configuration backup created: {backup_file}")
        return str(backup_file)
        
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")
        return ""

def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate configuration against schema. Returns list of errors."""
    errors = []
    
    try:
        def validate_recursive(data, schema_part, path=""):
            if isinstance(schema_part, dict):
                if 'type' in schema_part:
                    # Validate type
                    expected_type = schema_part['type']
                    if expected_type == 'dict' and not isinstance(data, dict):
                        errors.append(f"{path}: Expected dict, got {type(data).__name__}")
                        return
                    elif expected_type == 'list' and not isinstance(data, list):
                        errors.append(f"{path}: Expected list, got {type(data).__name__}")
                        return
                    elif expected_type == 'int' and not isinstance(data, int):
                        errors.append(f"{path}: Expected int, got {type(data).__name__}")
                        return
                    elif expected_type == 'float' and not isinstance(data, (int, float)):
                        errors.append(f"{path}: Expected float, got {type(data).__name__}")
                        return
                    elif expected_type == 'string' and not isinstance(data, str):
                        errors.append(f"{path}: Expected string, got {type(data).__name__}")
                        return
                    
                    # Validate range
                    if 'min' in schema_part and isinstance(data, (int, float)):
                        if data < schema_part['min']:
                            errors.append(f"{path}: Value {data} below minimum {schema_part['min']}")
                    
                    if 'max' in schema_part and isinstance(data, (int, float)):
                        if data > schema_part['max']:
                            errors.append(f"{path}: Value {data} above maximum {schema_part['max']}")
                    
                    # Validate choices
                    if 'choices' in schema_part:
                        if data not in schema_part['choices']:
                            errors.append(f"{path}: Value '{data}' not in allowed choices {schema_part['choices']}")
                
                # Check required fields
                if 'required' in schema_part:
                    for required_field in schema_part['required']:
                        if required_field not in data:
                            errors.append(f"{path}: Missing required field '{required_field}'")
                
                # Validate nested fields
                if 'properties' in schema_part and isinstance(data, dict):
                    for key, value in data.items():
                        if key in schema_part['properties']:
                            new_path = f"{path}.{key}" if path else key
                            validate_recursive(value, schema_part['properties'][key], new_path)
            
            elif isinstance(schema_part, dict) and isinstance(data, dict):
                # Direct schema validation
                for key, sub_schema in schema_part.items():
                    if key in data:
                        new_path = f"{path}.{key}" if path else key
                        validate_recursive(data[key], sub_schema, new_path)
        
        validate_recursive(config, schema)
        
    except Exception as e:
        errors.append(f"Schema validation error: {e}")
    
    return errors

def get_available_ports(start_port: int = 8000, count: int = 10) -> List[int]:
    """Get a list of available network ports."""
    import socket
    
    available_ports = []
    
    for port in range(start_port, start_port + count * 10):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # Port is available
                available_ports.append(port)
                
                if len(available_ports) >= count:
                    break
                    
        except Exception:
            continue
    
    return available_ports

def measure_execution_time(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logging.debug(f"{func.__name__} executed in {execution_time:.3f} seconds")
        
        return result
    return wrapper

def create_directory_structure(base_path: str, structure: Dict[str, Any]) -> bool:
    """Create directory structure from dictionary definition."""
    try:
        base = Path(base_path)
        base.mkdir(exist_ok=True)
        
        for name, content in structure.items():
            item_path = base / name
            
            if isinstance(content, dict):
                # It's a directory
                item_path.mkdir(exist_ok=True)
                create_directory_structure(str(item_path), content)
            else:
                # It's a file
                if not item_path.exists():
                    if content is None:
                        # Create empty file
                        item_path.touch()
                    else:
                        # Create file with content
                        with open(item_path, 'w', encoding='utf-8') as f:
                            f.write(str(content))
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to create directory structure: {e}")
        return False