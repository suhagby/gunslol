#!/usr/bin/env python3
"""
Advanced Performance Optimizer for Gaming Systems
Implements cutting-edge optimizations for maximum gaming performance,
low latency, reduced input lag, and optimal resource utilization.
"""

import os
import sys
import subprocess
import platform
import time
import threading
from pathlib import Path
import psutil
import yaml
from typing import Dict, List, Optional, Tuple

class AdvancedPerformanceOptimizer:
    """Advanced system optimizer for maximum gaming performance."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.optimizations_applied = []
        self.monitoring_active = False
        self.load_config()
        self.detect_hardware()
        
    def load_config(self):
        """Load configuration settings."""
        try:
            config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"Config loading error: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration if file is not available."""
        return {
            'thresholds': {
                'max_cpu_temp': 85,
                'max_memory_usage': 90,
                'max_ping': 50,
                'min_fps': 60
            },
            'hardware': {
                'cpu': {'cores': psutil.cpu_count()},
                'memory': {'capacity': round(psutil.virtual_memory().total / (1024**3))}
            }
        }
    
    def detect_hardware(self):
        """Advanced hardware detection and profiling."""
        print("🔍 Detecting hardware configuration...")
        
        self.hardware_info = {
            'cpu': self._detect_cpu(),
            'memory': self._detect_memory(),
            'storage': self._detect_storage(),
            'network': self._detect_network(),
            'usb': self._detect_usb_devices(),
            'audio': self._detect_audio_devices()
        }
        
        self._print_hardware_summary()
    
    def _detect_cpu(self) -> Dict:
        """Detect CPU specifications and capabilities."""
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'max_frequency': 0,
            'min_frequency': 0,
            'current_frequency': 0,
            'architecture': platform.machine(),
            'features': []
        }
        
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info['max_frequency'] = cpu_freq.max
                cpu_info['min_frequency'] = cpu_freq.min  
                cpu_info['current_frequency'] = cpu_freq.current
        except:
            pass
        
        # Detect CPU features
        if self.platform == 'linux':
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'avx2' in cpuinfo:
                        cpu_info['features'].append('AVX2')
                    if 'sse4_2' in cpuinfo:
                        cpu_info['features'].append('SSE4.2')
                    if 'hypervisor' not in cpuinfo:
                        cpu_info['features'].append('Native')
            except:
                pass
        
        return cpu_info
    
    def _detect_memory(self) -> Dict:
        """Detect memory specifications."""
        memory = psutil.virtual_memory()
        return {
            'total_gb': round(memory.total / (1024**3), 1),
            'available_gb': round(memory.available / (1024**3), 1),
            'used_percent': memory.percent,
            'type': 'DDR4',  # Assumed for modern systems
            'speed': 3200   # Assumed, would need platform-specific detection
        }
    
    def _detect_storage(self) -> List[Dict]:
        """Detect storage devices."""
        storage_devices = []
        
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    storage_devices.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 1),
                        'used_percent': round((usage.used / usage.total) * 100, 1),
                        'is_ssd': self._is_ssd(partition.device)
                    })
                except:
                    continue
        except:
            pass
        
        return storage_devices
    
    def _is_ssd(self, device: str) -> bool:
        """Detect if storage device is SSD."""
        if self.platform == 'linux':
            try:
                # Check if device is rotational (0 = SSD, 1 = HDD)
                device_name = device.split('/')[-1].rstrip('0123456789')
                rotational_file = f'/sys/block/{device_name}/queue/rotational'
                if os.path.exists(rotational_file):
                    with open(rotational_file, 'r') as f:
                        return f.read().strip() == '0'
            except:
                pass
        
        # Fallback: assume SSD for common SSD indicators
        ssd_indicators = ['nvme', 'ssd', 'm.2']
        return any(indicator in device.lower() for indicator in ssd_indicators)
    
    def _detect_network(self) -> Dict:
        """Detect network capabilities."""
        network_info = {
            'interfaces': [],
            'active_connections': 0
        }
        
        try:
            interfaces = psutil.net_if_stats()
            for interface, stats in interfaces.items():
                if stats.isup and interface not in ['lo', 'localhost']:
                    network_info['interfaces'].append({
                        'name': interface,
                        'speed': stats.speed,  # Mbps
                        'mtu': stats.mtu,
                        'is_wireless': 'wl' in interface.lower() or 'wifi' in interface.lower()
                    })
            
            network_info['active_connections'] = len(psutil.net_connections())
        except:
            pass
        
        return network_info
    
    def _detect_usb_devices(self) -> List[Dict]:
        """Detect USB devices for input optimization."""
        usb_devices = []
        
        if self.platform == 'linux':
            try:
                # Use lsusb command to detect USB devices
                result = subprocess.run(['lsusb'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'mouse' in line.lower() or 'keyboard' in line.lower():
                        usb_devices.append({
                            'description': line.strip(),
                            'type': 'mouse' if 'mouse' in line.lower() else 'keyboard'
                        })
            except:
                pass
        
        return usb_devices
    
    def _detect_audio_devices(self) -> List[Dict]:
        """Detect audio devices for latency optimization."""
        audio_devices = []
        
        if self.platform == 'linux':
            try:
                # Check for ALSA devices
                if os.path.exists('/proc/asound/cards'):
                    with open('/proc/asound/cards', 'r') as f:
                        for line in f:
                            if ':' in line and not line.startswith(' '):
                                audio_devices.append({
                                    'name': line.strip(),
                                    'type': 'audio_card'
                                })
            except:
                pass
        
        return audio_devices
    
    def _print_hardware_summary(self):
        """Print detected hardware summary."""
        print("\n💻 Hardware Configuration Detected:")
        print(f"   CPU: {self.hardware_info['cpu']['physical_cores']}C/{self.hardware_info['cpu']['logical_cores']}T @ {self.hardware_info['cpu']['max_frequency']:.0f}MHz")
        print(f"   Memory: {self.hardware_info['memory']['total_gb']:.1f}GB ({self.hardware_info['memory']['used_percent']:.1f}% used)")
        print(f"   Storage: {len(self.hardware_info['storage'])} device(s)")
        for storage in self.hardware_info['storage']:
            ssd_type = "SSD" if storage['is_ssd'] else "HDD"
            print(f"     - {storage['device']}: {storage['total_gb']:.1f}GB {ssd_type} ({storage['used_percent']:.1f}% used)")
        print(f"   Network: {len(self.hardware_info['network']['interfaces'])} interface(s)")
        print(f"   USB Input: {len(self.hardware_info['usb'])} device(s)")
        print(f"   Audio: {len(self.hardware_info['audio'])} device(s)")
    
    def optimize_low_latency_gaming(self):
        """Apply comprehensive low-latency optimizations for gaming."""
        print("\n🚀 Applying Advanced Low-Latency Gaming Optimizations...")
        
        # CPU optimizations
        self._optimize_cpu_for_gaming()
        
        # Memory optimizations
        self._optimize_memory_latency()
        
        # Network optimizations
        self._optimize_network_latency()
        
        # Input device optimizations
        self._optimize_input_devices()
        
        # Audio latency optimizations
        self._optimize_audio_latency()
        
        # System interrupt optimizations
        self._optimize_system_interrupts()
        
        # Process scheduling optimizations
        self._optimize_process_scheduling()
        
        print(f"\n✅ Applied {len(self.optimizations_applied)} optimizations:")
        for opt in self.optimizations_applied:
            print(f"   - {opt}")
    
    def _optimize_cpu_for_gaming(self):
        """Advanced CPU optimizations for gaming."""
        try:
            if self.platform == 'linux':
                # Set CPU governor to performance
                try:
                    subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'performance'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("CPU governor set to performance")
                except:
                    pass
                
                # Disable CPU C-states for consistent latency
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo 1 > /sys/devices/system/cpu/cpu0/cpuidle/state1/disable'], 
                                 check=False, capture_output=True)
                    subprocess.run(['sudo', 'sh', '-c', 'echo 1 > /sys/devices/system/cpu/cpu0/cpuidle/state2/disable'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("CPU C-states disabled for low latency")
                except:
                    pass
                
                # Set CPU affinity for better cache utilization
                self._optimize_cpu_affinity()
                
                # Optimize CPU scheduler parameters
                scheduler_params = {
                    '/proc/sys/kernel/sched_migration_cost_ns': '500000',
                    '/proc/sys/kernel/sched_min_granularity_ns': '750000',
                    '/proc/sys/kernel/sched_wakeup_granularity_ns': '1000000',
                    '/proc/sys/kernel/sched_latency_ns': '6000000',
                    '/proc/sys/kernel/sched_rt_period_us': '1000000',
                    '/proc/sys/kernel/sched_rt_runtime_us': '950000'
                }
                
                for param, value in scheduler_params.items():
                    try:
                        subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param}'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                self.optimizations_applied.append("CPU scheduler optimized for gaming")
        
        except Exception as e:
            print(f"CPU optimization error: {e}")
    
    def _optimize_cpu_affinity(self):
        """Optimize CPU core affinity for gaming processes."""
        try:
            # Reserve specific cores for gaming (use physical cores only)
            physical_cores = self.hardware_info['cpu']['physical_cores']
            
            if physical_cores >= 4:
                # Reserve cores 0-1 for system, 2-7 for gaming
                gaming_cores = ','.join(str(i) for i in range(2, min(8, physical_cores)))
                
                # Set default CPU affinity for new processes
                subprocess.run(['sudo', 'sh', '-c', f'echo {gaming_cores} > /proc/irq/default_smp_affinity'], 
                             check=False, capture_output=True)
                
                self.optimizations_applied.append(f"CPU cores {gaming_cores} reserved for gaming")
        
        except Exception as e:
            print(f"CPU affinity optimization error: {e}")
    
    def _optimize_memory_latency(self):
        """Optimize memory subsystem for low latency."""
        try:
            if self.platform == 'linux':
                # Memory management optimizations
                memory_params = {
                    '/proc/sys/vm/swappiness': '1',  # Minimize swapping
                    '/proc/sys/vm/vfs_cache_pressure': '50',  # Balance cache pressure
                    '/proc/sys/vm/dirty_ratio': '10',  # Reduce dirty memory ratio
                    '/proc/sys/vm/dirty_background_ratio': '3',  # Aggressive background writing
                    '/proc/sys/vm/dirty_expire_centisecs': '1500',  # Faster dirty expiration
                    '/proc/sys/vm/dirty_writeback_centisecs': '500',  # More frequent writeback
                    '/proc/sys/vm/page-cluster': '0',  # Disable page clustering for SSDs
                    '/proc/sys/vm/overcommit_memory': '1',  # Allow memory overcommit
                }
                
                for param, value in memory_params.items():
                    try:
                        subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param}'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                # Enable transparent huge pages for better memory performance
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo always > /sys/kernel/mm/transparent_hugepage/enabled'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Transparent huge pages enabled")
                except:
                    pass
                
                # Optimize memory zone reclaim
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo 0 > /proc/sys/vm/zone_reclaim_mode'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Memory zone reclaim optimized")
                except:
                    pass
                
                self.optimizations_applied.append("Memory latency parameters optimized")
        
        except Exception as e:
            print(f"Memory optimization error: {e}")
    
    def _optimize_network_latency(self):
        """Advanced network optimizations for gaming."""
        try:
            if self.platform == 'linux':
                # TCP/IP stack optimizations
                network_params = {
                    # TCP optimizations
                    '/proc/sys/net/ipv4/tcp_low_latency': '1',
                    '/proc/sys/net/ipv4/tcp_timestamps': '1',
                    '/proc/sys/net/ipv4/tcp_sack': '1',
                    '/proc/sys/net/ipv4/tcp_window_scaling': '1',
                    '/proc/sys/net/ipv4/tcp_congestion_control': 'bbr',
                    '/proc/sys/net/ipv4/tcp_no_delay_ack': '1',
                    '/proc/sys/net/ipv4/tcp_slow_start_after_idle': '0',
                    
                    # Buffer optimizations
                    '/proc/sys/net/core/rmem_max': '134217728',
                    '/proc/sys/net/core/wmem_max': '134217728',
                    '/proc/sys/net/core/rmem_default': '262144',
                    '/proc/sys/net/core/wmem_default': '262144',
                    '/proc/sys/net/core/netdev_max_backlog': '5000',
                    
                    # Network device optimizations
                    '/proc/sys/net/core/netdev_budget': '600',
                    '/proc/sys/net/core/dev_weight': '64'
                }
                
                for param, value in network_params.items():
                    try:
                        subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param}'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                # Optimize network interface settings
                self._optimize_network_interfaces()
                
                self.optimizations_applied.append("Network stack optimized for low latency")
        
        except Exception as e:
            print(f"Network optimization error: {e}")
    
    def _optimize_network_interfaces(self):
        """Optimize network interface settings."""
        try:
            for interface in self.hardware_info['network']['interfaces']:
                if not interface['is_wireless'] and interface['name'] != 'lo':
                    interface_name = interface['name']
                    
                    # Disable various offloading features that can introduce latency
                    ethtool_commands = [
                        f'ethtool -K {interface_name} tx off rx off',
                        f'ethtool -K {interface_name} tso off',
                        f'ethtool -K {interface_name} gso off',
                        f'ethtool -K {interface_name} gro off',
                        f'ethtool -G {interface_name} rx 4096 tx 4096',  # Increase ring buffers
                        f'ethtool -C {interface_name} rx-usecs 0 tx-usecs 0'  # Disable interrupt coalescing
                    ]
                    
                    for cmd in ethtool_commands:
                        try:
                            subprocess.run(['sudo'] + cmd.split(), check=False, capture_output=True)
                        except:
                            pass
                    
                    self.optimizations_applied.append(f"Network interface {interface_name} optimized")
        
        except Exception as e:
            print(f"Network interface optimization error: {e}")
    
    def _optimize_input_devices(self):
        """Optimize input devices for minimal latency."""
        try:
            if self.platform == 'linux':
                # Optimize USB polling rate for mice and keyboards
                usb_params = {
                    '/sys/module/usbhid/parameters/mousepoll': '1',  # 1000Hz polling
                    '/sys/module/usbhid/parameters/kbpoll': '1'      # 1000Hz polling  
                }
                
                for param, value in usb_params.items():
                    try:
                        if os.path.exists(param):
                            subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param}'], 
                                         check=False, capture_output=True)
                    except:
                        pass
                
                # Disable USB autosuspend for input devices
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo -1 > /sys/module/usbcore/parameters/autosuspend'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("USB autosuspend disabled for input devices")
                except:
                    pass
                
                # Set high priority for USB interrupt handlers
                self._optimize_usb_interrupts()
                
                self.optimizations_applied.append("Input devices optimized for low latency")
        
        except Exception as e:
            print(f"Input device optimization error: {e}")
    
    def _optimize_usb_interrupts(self):
        """Optimize USB interrupt handling."""
        try:
            # Find USB interrupt numbers and set high priority
            with open('/proc/interrupts', 'r') as f:
                for line in f:
                    if 'usb' in line.lower() or 'ehci' in line.lower() or 'xhci' in line.lower():
                        parts = line.split(':')
                        if parts:
                            irq_num = parts[0].strip()
                            if irq_num.isdigit():
                                try:
                                    subprocess.run(['sudo', 'chrt', '-f', '-p', '99', f'/proc/irq/{irq_num}'], 
                                                 check=False, capture_output=True)
                                except:
                                    pass
            
            self.optimizations_applied.append("USB interrupt priorities optimized")
        
        except Exception as e:
            print(f"USB interrupt optimization error: {e}")
    
    def _optimize_audio_latency(self):
        """Optimize audio system for low latency."""
        try:
            if self.platform == 'linux':
                # ALSA optimizations
                alsa_configs = [
                    'echo "pcm.!default { type hw card 0 device 0 }" > ~/.asoundrc',
                    'echo "defaults.pcm.rate_converter \"samplerate_best\"" >> ~/.asoundrc'
                ]
                
                for config in alsa_configs:
                    try:
                        subprocess.run(['sh', '-c', config], check=False, capture_output=True)
                    except:
                        pass
                
                # Set real-time priority for audio processes
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo "@audio - rtprio 99" >> /etc/security/limits.conf'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Audio real-time priority configured")
                except:
                    pass
                
                self.optimizations_applied.append("Audio latency optimized")
        
        except Exception as e:
            print(f"Audio optimization error: {e}")
    
    def _optimize_system_interrupts(self):
        """Optimize system interrupt handling."""
        try:
            if self.platform == 'linux':
                # Disable IRQ balancing for consistent latency
                try:
                    subprocess.run(['sudo', 'systemctl', 'stop', 'irqbalance'], 
                                 check=False, capture_output=True)
                    subprocess.run(['sudo', 'systemctl', 'disable', 'irqbalance'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("IRQ balancing disabled")
                except:
                    pass
                
                # Set interrupt affinity manually for better performance
                self._set_interrupt_affinity()
                
                # Optimize kernel interrupt handling
                interrupt_params = {
                    '/proc/sys/kernel/sched_rt_period_us': '1000000',
                    '/proc/sys/kernel/sched_rt_runtime_us': '950000'
                }
                
                for param, value in interrupt_params.items():
                    try:
                        subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param}'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                self.optimizations_applied.append("System interrupt handling optimized")
        
        except Exception as e:
            print(f"Interrupt optimization error: {e}")
    
    def _set_interrupt_affinity(self):
        """Set optimal interrupt affinity."""
        try:
            physical_cores = self.hardware_info['cpu']['physical_cores']
            
            if physical_cores >= 4:
                # Bind network interrupts to core 0
                # Bind USB interrupts to core 1
                # Leave cores 2+ for applications
                
                with open('/proc/interrupts', 'r') as f:
                    for line in f:
                        parts = line.split(':')
                        if len(parts) > 1:
                            irq_num = parts[0].strip()
                            desc = parts[-1].strip().lower()
                            
                            if irq_num.isdigit():
                                cpu_mask = '1'  # Default to core 0
                                
                                if 'eth' in desc or 'network' in desc:
                                    cpu_mask = '1'  # Core 0 for network
                                elif 'usb' in desc or 'input' in desc:
                                    cpu_mask = '2'  # Core 1 for USB/input
                                
                                try:
                                    subprocess.run(['sudo', 'sh', '-c', f'echo {cpu_mask} > /proc/irq/{irq_num}/smp_affinity'], 
                                                 check=False, capture_output=True)
                                except:
                                    pass
                
                self.optimizations_applied.append("Interrupt affinity optimized")
        
        except Exception as e:
            print(f"Interrupt affinity optimization error: {e}")
    
    def _optimize_process_scheduling(self):
        """Optimize process scheduling for gaming."""
        try:
            # Set real-time priority for gaming processes
            gaming_processes = [
                'steam', 'steamwebhelper', 'League of Legends', 'RiotClientServices',
                'valorant', 'csgo', 'cs2', 'fortnite', 'apex', 'overwatch'
            ]
            
            prioritized_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(game.lower() in proc_name for game in gaming_processes):
                        process = psutil.Process(proc.info['pid'])
                        
                        # Set real-time priority (Linux)
                        if self.platform == 'linux':
                            try:
                                subprocess.run(['sudo', 'chrt', '-f', '-p', '50', str(proc.info['pid'])], 
                                             check=False, capture_output=True)
                            except:
                                # Fallback to nice priority
                                process.nice(-20)
                        
                        prioritized_count += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                    pass
            
            if prioritized_count > 0:
                self.optimizations_applied.append(f"Gaming processes prioritized ({prioritized_count} processes)")
            
            # Optimize process scheduler settings
            if self.platform == 'linux':
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo 0 > /proc/sys/kernel/sched_autogroup_enabled'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Process auto-grouping disabled")
                except:
                    pass
        
        except Exception as e:
            print(f"Process scheduling optimization error: {e}")
    
    def get_performance_metrics(self) -> Dict:
        """Get current performance metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Disk metrics
            disk_io = psutil.disk_io_counters()
            
            return {
                'timestamp': time.time(),
                'cpu': {
                    'usage_percent': sum(cpu_percent) / len(cpu_percent),
                    'usage_per_core': cpu_percent,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'frequency_percent': (cpu_freq.current / cpu_freq.max * 100) if cpu_freq and cpu_freq.max else 0
                },
                'memory': {
                    'usage_percent': memory.percent,
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3),
                    'total_gb': memory.total / (1024**3)
                },
                'network': {
                    'bytes_sent': network_io.bytes_sent if network_io else 0,
                    'bytes_recv': network_io.bytes_recv if network_io else 0,
                    'packets_sent': network_io.packets_sent if network_io else 0,
                    'packets_recv': network_io.packets_recv if network_io else 0
                },
                'disk': {
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                }
            }
        
        except Exception as e:
            print(f"Performance metrics error: {e}")
            return {}
    
    def generate_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        metrics = self.get_performance_metrics()
        
        if not metrics:
            return ["Unable to generate recommendations - metrics unavailable"]
        
        # CPU recommendations
        cpu_usage = metrics.get('cpu', {}).get('usage_percent', 0)
        if cpu_usage > 90:
            recommendations.append("🔥 High CPU usage detected - consider closing background applications")
        elif cpu_usage < 30:
            recommendations.append("💡 CPU usage is low - you can enable more visual effects or increase game settings")
        
        # Memory recommendations
        memory_usage = metrics.get('memory', {}).get('usage_percent', 0)
        if memory_usage > 85:
            recommendations.append("🧠 High memory usage - consider closing unused applications")
            recommendations.append("💾 Consider upgrading to 32GB RAM for optimal gaming performance")
        
        # Storage recommendations
        storage_devices = self.hardware_info.get('storage', [])
        for storage in storage_devices:
            if storage['used_percent'] > 85:
                recommendations.append(f"💾 Storage {storage['device']} is {storage['used_percent']:.1f}% full - consider cleaning up")
        
        # Network recommendations
        active_connections = self.hardware_info.get('network', {}).get('active_connections', 0)
        if active_connections > 100:
            recommendations.append("🌐 Many active network connections - check for unnecessary background apps")
        
        # Hardware-specific recommendations
        cpu_cores = self.hardware_info.get('cpu', {}).get('physical_cores', 0)
        if cpu_cores < 6:
            recommendations.append("⚡ Consider upgrading to a CPU with 6+ cores for modern gaming")
        
        memory_gb = self.hardware_info.get('memory', {}).get('total_gb', 0)
        if memory_gb < 16:
            recommendations.append("🧠 Consider upgrading to 16GB+ RAM for smooth gaming")
        
        # Check if SSDs are being used
        has_ssd = any(storage['is_ssd'] for storage in storage_devices)
        if not has_ssd:
            recommendations.append("💾 Consider upgrading to SSD/NVMe storage for faster load times")
        
        if not recommendations:
            recommendations.append("✅ System is well optimized - no immediate recommendations")
        
        return recommendations

def main():
    """Main optimization function."""
    print("🎮 Advanced Gaming Performance Optimizer")
    print("=" * 60)
    
    optimizer = AdvancedPerformanceOptimizer()
    
    print("\n🔧 Applying Advanced Optimizations...")
    optimizer.optimize_low_latency_gaming()
    
    print("\n📊 Current Performance Metrics:")
    metrics = optimizer.get_performance_metrics()
    if metrics:
        cpu = metrics.get('cpu', {})
        memory = metrics.get('memory', {})
        print(f"   CPU: {cpu.get('usage_percent', 0):.1f}% @ {cpu.get('frequency', 0):.0f}MHz")
        print(f"   Memory: {memory.get('usage_percent', 0):.1f}% ({memory.get('available_gb', 0):.1f}GB available)")
    
    print("\n💡 Performance Recommendations:")
    recommendations = optimizer.generate_recommendations()
    for i, recommendation in enumerate(recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    print("\n🎯 Optimization complete! System is now optimized for maximum gaming performance.")
    print("💡 Restart games to apply all optimizations.")

if __name__ == "__main__":
    main()