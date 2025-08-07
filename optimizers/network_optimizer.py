"""
Network optimization module.
Handles network stack optimizations for reduced latency and improved gaming performance.
"""

import os
import sys
import logging
import subprocess
import socket
import time
from typing import Dict, Any, List, Optional
import psutil

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

class NetworkOptimizer:
    """Handles network optimizations for gaming performance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.optimizations_applied = []
        self.original_settings = {}
        
        # DNS servers for gaming optimization
        self.gaming_dns_servers = {
            'cloudflare': {
                'primary': '1.1.1.1',
                'secondary': '1.0.0.1',
                'name': 'Cloudflare'
            },
            'google': {
                'primary': '8.8.8.8', 
                'secondary': '8.8.4.4',
                'name': 'Google'
            },
            'quad9': {
                'primary': '9.9.9.9',
                'secondary': '149.112.112.112', 
                'name': 'Quad9'
            },
            'opendns': {
                'primary': '208.67.222.222',
                'secondary': '208.67.220.220',
                'name': 'OpenDNS'
            }
        }
        
        # Network adapter optimizations
        self.adapter_optimizations = {
            # TCP/IP optimizations
            'tcp_optimizations': {
                'TcpAckFrequency': 1,         # Disable TCP delayed ACK
                'TCPNoDelay': 1,              # Disable Nagle algorithm
                'TcpDelAckTicks': 0,          # Immediate ACK
                'TcpWindowSize': 65535,       # Optimize TCP window size
                'DefaultTTL': 64,             # Optimize TTL
                'EnablePMTUDiscovery': 1,     # Enable path MTU discovery
                'GlobalMaxTcpWindowSize': 65535  # Global TCP window size
            },
            
            # Network adapter settings
            'adapter_settings': {
                'InterruptModeration': 0,     # Disable interrupt moderation
                'FlowControl': 0,             # Disable flow control
                'RSS': 1,                     # Enable Receive Side Scaling
                'LsoV2IPv4': 0,               # Disable Large Send Offload
                'LsoV2IPv6': 0,               # Disable LSO for IPv6
                'TCPChecksumOffloadIPv4': 0,  # Disable TCP checksum offload
                'TCPChecksumOffloadIPv6': 0,  # Disable TCP checksum offload IPv6
                'UDPChecksumOffloadIPv4': 0,  # Disable UDP checksum offload
                'UDPChecksumOffloadIPv6': 0,  # Disable UDP checksum offload IPv6
            }
        }
        
        self.logger.info("NetworkOptimizer initialized")
    
    def optimize_connection(self) -> Dict[str, bool]:
        """Apply comprehensive network optimizations for gaming."""
        results = {}
        
        try:
            self.logger.info("Starting network optimizations...")
            
            # DNS optimization
            results['dns_optimization'] = self._optimize_dns_settings()
            
            # TCP/IP stack optimization  
            results['tcp_ip_optimization'] = self._optimize_tcp_ip_stack()
            
            # Network adapter optimization
            results['adapter_optimization'] = self._optimize_network_adapters()
            
            # QoS optimization
            results['qos_optimization'] = self._optimize_qos_settings()
            
            # Windows network stack optimization
            results['network_stack'] = self._optimize_windows_network_stack()
            
            # Gaming-specific network optimization
            results['gaming_network'] = self._optimize_gaming_network_settings()
            
            # Firewall optimization
            results['firewall_optimization'] = self._optimize_firewall_settings()
            
            self.logger.info(f"Network optimizations completed: {results}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error during network optimization: {e}")
            return {'error': str(e)}
    
    def _optimize_dns_settings(self) -> bool:
        """Optimize DNS settings for faster resolution."""
        try:
            # Choose best DNS servers (Cloudflare for gaming)
            dns_config = self.gaming_dns_servers['cloudflare']
            primary_dns = dns_config['primary']
            secondary_dns = dns_config['secondary']
            
            success_count = 0
            
            # Get network interfaces
            interfaces = psutil.net_if_stats()
            active_interfaces = [name for name, stats in interfaces.items() 
                               if stats.isup and not name.startswith('Loopback')]
            
            for interface in active_interfaces[:1]:  # Optimize primary interface
                try:
                    # Set DNS servers using netsh
                    primary_cmd = ['netsh', 'interface', 'ip', 'set', 'dns', f'name={interface}', 
                                 'source=static', f'addr={primary_dns}']
                    
                    result = subprocess.run(primary_cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Add secondary DNS
                        secondary_cmd = ['netsh', 'interface', 'ip', 'add', 'dns', f'name={interface}', 
                                       f'addr={secondary_dns}', 'index=2']
                        
                        subprocess.run(secondary_cmd, capture_output=True, text=True)
                        success_count += 1
                        self.logger.info(f"Set DNS servers for {interface}: {primary_dns}, {secondary_dns}")
                    
                except Exception as e:
                    self.logger.debug(f"DNS optimization failed for {interface}: {e}")
                    continue
            
            # Flush DNS cache
            try:
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True)
                self.logger.info("DNS cache flushed")
                success_count += 1
            except Exception as e:
                self.logger.debug(f"DNS cache flush failed: {e}")
            
            # Registry DNS optimizations
            if HAS_WINREG:
                try:
                    dns_key = r'SYSTEM\CurrentControlSet\Services\Dnscache\Parameters'
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, dns_key, 0, winreg.KEY_SET_VALUE)
                    
                    # Optimize DNS cache
                    winreg.SetValueEx(key, 'CacheHashTableBucketSize', 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(key, 'CacheHashTableSize', 0, winreg.REG_DWORD, 384)
                    winreg.SetValueEx(key, 'MaxCacheEntryTtlLimit', 0, winreg.REG_DWORD, 86400)  # 24 hours
                    winreg.SetValueEx(key, 'MaxSOACacheEntryTtlLimit', 0, winreg.REG_DWORD, 300)  # 5 minutes
                    
                    winreg.CloseKey(key)
                    self.logger.info("Applied DNS registry optimizations")
                    success_count += 1
                    
                except Exception as e:
                    self.logger.debug(f"DNS registry optimization failed: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"DNS optimization failed: {e}")
            return False
    
    def _optimize_tcp_ip_stack(self) -> bool:
        """Optimize TCP/IP stack for gaming performance."""
        try:
            if not HAS_WINREG:
                return False
            
            success_count = 0
            tcp_optimizations = self.adapter_optimizations['tcp_optimizations']
            
            # TCP/IP Parameters registry key
            tcpip_key = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
            
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, tcpip_key, 0, winreg.KEY_SET_VALUE)
                
                for param_name, param_value in tcp_optimizations.items():
                    try:
                        # Backup original value
                        try:
                            original = winreg.QueryValueEx(key, param_name)
                            self.original_settings[f'tcp_{param_name}'] = original
                        except FileNotFoundError:
                            pass
                        
                        # Set optimized value
                        winreg.SetValueEx(key, param_name, 0, winreg.REG_DWORD, param_value)
                        success_count += 1
                        
                    except Exception as e:
                        self.logger.debug(f"TCP parameter {param_name} optimization failed: {e}")
                
                winreg.CloseKey(key)
                
            except Exception as e:
                self.logger.error(f"TCP/IP registry access failed: {e}")
            
            # Additional TCP optimizations via netsh
            netsh_commands = [
                # TCP global settings
                ['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'chimney=enabled'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'rss=enabled'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'netdma=enabled'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'dca=enabled'],
                
                # TCP optimizer settings
                ['netsh', 'int', 'tcp', 'set', 'global', 'ecncapability=enabled'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'timestamps=enabled'],
            ]
            
            for cmd in netsh_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        success_count += 1
                    else:
                        self.logger.debug(f"Netsh command failed: {' '.join(cmd)}")
                except Exception as e:
                    self.logger.debug(f"Netsh command error: {e}")
            
            if success_count > 0:
                self.logger.info(f"Applied {success_count} TCP/IP optimizations")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"TCP/IP stack optimization failed: {e}")
            return False
    
    def _optimize_network_adapters(self) -> bool:
        """Optimize network adapter settings for gaming."""
        try:
            if not HAS_WINREG:
                return False
            
            success_count = 0
            
            # Find network adapter registry keys
            adapter_base = r'SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}'
            
            try:
                base_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_base)
                
                # Enumerate network adapters
                adapter_count = winreg.QueryInfoKey(base_key)[0]
                
                for i in range(adapter_count):
                    try:
                        adapter_name = winreg.EnumKey(base_key, i)
                        
                        # Skip non-numeric keys
                        if not adapter_name.isdigit():
                            continue
                        
                        adapter_path = f"{adapter_base}\\{adapter_name}"
                        
                        try:
                            adapter_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, adapter_path, 0, 
                                                       winreg.KEY_READ | winreg.KEY_SET_VALUE)
                            
                            # Check if this is a real network adapter
                            try:
                                driver_desc = winreg.QueryValueEx(adapter_key, 'DriverDesc')[0]
                                if any(skip in driver_desc.lower() for skip in 
                                     ['loopback', 'virtual', 'bluetooth', 'vpn', 'tap', 'tunnel']):
                                    winreg.CloseKey(adapter_key)
                                    continue
                            except:
                                winreg.CloseKey(adapter_key)
                                continue
                            
                            # Apply adapter optimizations
                            adapter_settings = self.adapter_optimizations['adapter_settings']
                            
                            for setting_name, setting_value in adapter_settings.items():
                                try:
                                    winreg.SetValueEx(adapter_key, setting_name, 0, 
                                                    winreg.REG_DWORD, setting_value)
                                    success_count += 1
                                except Exception as e:
                                    self.logger.debug(f"Adapter setting {setting_name} failed: {e}")
                            
                            winreg.CloseKey(adapter_key)
                            self.logger.info(f"Optimized network adapter: {driver_desc}")
                            
                        except Exception as e:
                            self.logger.debug(f"Adapter optimization failed for {adapter_name}: {e}")
                    
                    except Exception as e:
                        self.logger.debug(f"Adapter enumeration error at index {i}: {e}")
                        continue
                
                winreg.CloseKey(base_key)
                
            except Exception as e:
                self.logger.error(f"Network adapter registry access failed: {e}")
            
            if success_count > 0:
                self.logger.info(f"Applied {success_count} network adapter optimizations")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Network adapter optimization failed: {e}")
            return False
    
    def _optimize_qos_settings(self) -> bool:
        """Optimize Quality of Service settings for gaming."""
        try:
            success_count = 0
            
            # Enable QoS Packet Scheduler
            qos_commands = [
                # Enable QoS
                ['netsh', 'int', 'ip', 'set', 'global', 'taskoffload=enabled'],
                
                # Set QoS reserved bandwidth to 0 (allow full bandwidth usage)
                ['netsh', 'int', 'tcp', 'set', 'global', 'nonsackrttresiliency=disabled'],
                
                # Optimize interface priorities
                ['netsh', 'int', 'ip', 'set', 'global', 'sourceroutingbehavior=dontforward'],
            ]
            
            for cmd in qos_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        success_count += 1
                except Exception as e:
                    self.logger.debug(f"QoS command failed: {e}")
            
            # Registry QoS optimizations
            if HAS_WINREG:
                try:
                    # Disable QoS limit
                    qos_key = r'SOFTWARE\Policies\Microsoft\Windows\Psched'
                    
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, qos_key, 0, winreg.KEY_SET_VALUE)
                    except FileNotFoundError:
                        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, qos_key)
                    
                    # Set NonBestEffortLimit to 0 (no bandwidth reservation)
                    winreg.SetValueEx(key, 'NonBestEffortLimit', 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    
                    success_count += 1
                    self.logger.info("Disabled QoS bandwidth reservation")
                    
                except Exception as e:
                    self.logger.debug(f"QoS registry optimization failed: {e}")
            
            # Gaming traffic prioritization via registry
            if HAS_WINREG:
                try:
                    # Set network throttling index to disable throttling
                    throttle_key = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
                    
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, throttle_key, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, 'NetworkThrottlingIndex', 0, winreg.REG_DWORD, 0xFFFFFFFF)
                    winreg.SetValueEx(key, 'SystemResponsiveness', 0, winreg.REG_DWORD, 0)
                    winreg.CloseKey(key)
                    
                    success_count += 1
                    self.logger.info("Disabled network throttling")
                    
                except Exception as e:
                    self.logger.debug(f"Network throttling optimization failed: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"QoS optimization failed: {e}")
            return False
    
    def _optimize_windows_network_stack(self) -> bool:
        """Optimize Windows network stack for gaming."""
        try:
            success_count = 0
            
            # Windows network stack optimizations
            network_commands = [
                # Reset network stack
                ['netsh', 'winsock', 'reset'],
                
                # Reset TCP/IP stack  
                ['netsh', 'int', 'ip', 'reset'],
                
                # Optimize network buffer sizes
                ['netsh', 'int', 'tcp', 'set', 'global', 'maxsynretransmissions=2'],
                ['netsh', 'int', 'tcp', 'set', 'global', 'initialrto=3000'],
                
                # Enable TCP window scaling
                ['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal'],
                
                # Optimize for gaming
                ['netsh', 'int', 'tcp', 'set', 'supplemental', 'template=internet', 'icw=10'],
            ]
            
            for cmd in network_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if result.returncode == 0:
                        success_count += 1
                        self.logger.debug(f"Applied network command: {' '.join(cmd)}")
                    else:
                        self.logger.debug(f"Network command failed: {' '.join(cmd)}")
                except Exception as e:
                    self.logger.debug(f"Network stack command error: {e}")
            
            # Additional stack optimizations via registry
            if HAS_WINREG:
                try:
                    # IPv4 optimizations
                    ipv4_key = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, ipv4_key, 0, winreg.KEY_SET_VALUE)
                    
                    stack_optimizations = {
                        'SynAttackProtect': 0,        # Disable SYN attack protection (gaming)
                        'EnableConnectionRateLimiting': 0,  # Disable connection rate limiting
                        'EnableDCA': 1,               # Enable Direct Cache Access
                        'EnableRSS': 1,               # Enable Receive Side Scaling
                        'EnableTCPA': 1,              # Enable TCP Chimney
                        'EnableDeadGWDetect': 0,      # Disable dead gateway detection
                    }
                    
                    for param_name, param_value in stack_optimizations.items():
                        try:
                            winreg.SetValueEx(key, param_name, 0, winreg.REG_DWORD, param_value)
                            success_count += 1
                        except Exception as e:
                            self.logger.debug(f"Stack parameter {param_name} failed: {e}")
                    
                    winreg.CloseKey(key)
                    
                except Exception as e:
                    self.logger.debug(f"Network stack registry optimization failed: {e}")
            
            if success_count > 0:
                self.logger.info(f"Applied {success_count} network stack optimizations")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Windows network stack optimization failed: {e}")
            return False
    
    def _optimize_gaming_network_settings(self) -> bool:
        """Apply gaming-specific network optimizations."""
        try:
            success_count = 0
            
            # Gaming-specific optimizations via registry
            if HAS_WINREG:
                try:
                    # Games and multimedia network profile
                    games_key = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games'
                    
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, games_key, 0, winreg.KEY_SET_VALUE)
                    except FileNotFoundError:
                        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, games_key)
                    
                    # Set gaming priority
                    gaming_settings = {
                        'Affinity': 0,
                        'Background Only': 'False',
                        'BackgroundPriority': 0,
                        'Clock Rate': 10000,
                        'GPU Priority': 8,
                        'Priority': 6,
                        'Scheduling Category': 'High',
                        'SFIO Priority': 'High'
                    }
                    
                    for setting_name, setting_value in gaming_settings.items():
                        try:
                            if isinstance(setting_value, str):
                                winreg.SetValueEx(key, setting_name, 0, winreg.REG_SZ, setting_value)
                            else:
                                winreg.SetValueEx(key, setting_name, 0, winreg.REG_DWORD, setting_value)
                            success_count += 1
                        except Exception as e:
                            self.logger.debug(f"Gaming setting {setting_name} failed: {e}")
                    
                    winreg.CloseKey(key)
                    self.logger.info("Applied gaming network profile")
                    
                except Exception as e:
                    self.logger.debug(f"Gaming network profile optimization failed: {e}")
                
                # Network latency optimization
                try:
                    latency_key = r'SYSTEM\CurrentControlSet\Control\Session Manager\kernel'
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, latency_key, 0, winreg.KEY_SET_VALUE)
                    
                    # Optimize kernel for gaming
                    winreg.SetValueEx(key, 'GlobalTimerResolutionRequests', 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(key)
                    
                    success_count += 1
                    self.logger.info("Applied network latency optimizations")
                    
                except Exception as e:
                    self.logger.debug(f"Network latency optimization failed: {e}")
            
            # Socket buffer optimizations
            try:
                # These would typically require application-specific implementation
                # For system-wide optimization, we use the registry settings above
                pass
            except Exception as e:
                self.logger.debug(f"Socket buffer optimization failed: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Gaming network optimization failed: {e}")
            return False
    
    def _optimize_firewall_settings(self) -> bool:
        """Optimize Windows Firewall settings for gaming."""
        try:
            success_count = 0
            
            # Gaming ports that should be optimized
            gaming_ports = [
                # Common gaming ports
                {'port': 80, 'protocol': 'TCP', 'name': 'HTTP'},
                {'port': 443, 'protocol': 'TCP', 'name': 'HTTPS'},
                {'port': 53, 'protocol': 'UDP', 'name': 'DNS'},
                
                # Steam
                {'port': 27015, 'protocol': 'TCP', 'name': 'Steam'},
                {'port': 27015, 'protocol': 'UDP', 'name': 'Steam'},
                
                # Discord
                {'port': 50000, 'protocol': 'UDP', 'name': 'Discord Voice'},
                
                # Common game ranges
                {'port': '1024-65535', 'protocol': 'TCP', 'name': 'Gaming TCP Range'},
                {'port': '1024-65535', 'protocol': 'UDP', 'name': 'Gaming UDP Range'},
            ]
            
            # Optimize firewall for gaming (non-destructive)
            try:
                # Check firewall status without disabling it
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.logger.info("Firewall status checked for gaming optimization")
                    
                    # Set firewall to allow gaming applications (safer than disabling)
                    firewall_cmd = [
                        'netsh', 'advfirewall', 'set', 'allprofiles', 
                        'settings', 'inboundusernotification', 'disable'
                    ]
                    
                    result = subprocess.run(firewall_cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        success_count += 1
                        self.logger.info("Optimized firewall notifications for gaming")
                
            except Exception as e:
                self.logger.debug(f"Firewall optimization failed: {e}")
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Firewall optimization failed: {e}")
            return False
    
    def test_network_performance(self) -> Dict[str, Any]:
        """Test network performance after optimizations."""
        results = {}
        
        try:
            # DNS resolution test
            dns_results = self._test_dns_performance()
            if dns_results:
                results['dns_performance'] = dns_results
            
            # Ping test to gaming servers
            ping_results = self._test_gaming_ping()
            if ping_results:
                results['gaming_ping'] = ping_results
            
            # Network adapter status
            adapter_status = self._check_adapter_status()
            if adapter_status:
                results['adapter_status'] = adapter_status
            
        except Exception as e:
            self.logger.error(f"Network performance test failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def _test_dns_performance(self) -> Dict[str, float]:
        """Test DNS resolution performance."""
        test_domains = ['google.com', 'github.com', 'discord.com', 'steampowered.com']
        dns_times = []
        
        try:
            for domain in test_domains:
                start_time = time.time()
                try:
                    socket.gethostbyname(domain)
                    resolve_time = (time.time() - start_time) * 1000  # Convert to ms
                    dns_times.append(resolve_time)
                except:
                    continue
            
            if dns_times:
                return {
                    'average_dns_time': round(sum(dns_times) / len(dns_times), 2),
                    'min_dns_time': round(min(dns_times), 2),
                    'max_dns_time': round(max(dns_times), 2),
                    'domains_tested': len(dns_times)
                }
        
        except Exception as e:
            self.logger.error(f"DNS performance test failed: {e}")
        
        return {}
    
    def _test_gaming_ping(self) -> Dict[str, float]:
        """Test ping to gaming servers."""
        gaming_servers = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        ping_results = {}
        
        try:
            for server in gaming_servers:
                try:
                    # Simple ping test
                    result = subprocess.run(['ping', '-n', '4', server], 
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        output = result.stdout
                        # Parse ping results (Windows format)
                        import re
                        ping_times = re.findall(r'time[<=](\d+)ms', output)
                        
                        if ping_times:
                            ping_values = [float(t) for t in ping_times]
                            ping_results[server] = {
                                'average': round(sum(ping_values) / len(ping_values), 2),
                                'min': round(min(ping_values), 2),
                                'max': round(max(ping_values), 2)
                            }
                
                except Exception as e:
                    self.logger.debug(f"Ping test to {server} failed: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Gaming ping test failed: {e}")
        
        return ping_results
    
    def _check_adapter_status(self) -> Dict[str, Any]:
        """Check network adapter optimization status."""
        status = {}
        
        try:
            # Get network interface statistics
            interfaces = psutil.net_if_stats()
            
            for name, stats in interfaces.items():
                if stats.isup and not name.startswith('Loopback'):
                    status[name] = {
                        'speed': stats.speed,
                        'mtu': stats.mtu,
                        'is_up': stats.isup,
                        'duplex': stats.duplex
                    }
            
            # Get network I/O counters
            net_io = psutil.net_io_counters()
            if net_io:
                status['total_io'] = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errors_in': net_io.errin,
                    'errors_out': net_io.errout,
                    'drops_in': net_io.dropin,
                    'drops_out': net_io.dropout
                }
        
        except Exception as e:
            self.logger.error(f"Adapter status check failed: {e}")
        
        return status
    
    def rollback_optimizations(self) -> bool:
        """Rollback network optimizations."""
        try:
            rollback_count = 0
            
            # Restore original registry settings
            if HAS_WINREG and self.original_settings:
                for setting_key, (original_value, value_type) in self.original_settings.items():
                    try:
                        # Parse the key path
                        if setting_key.startswith('tcp_'):
                            reg_key = r'SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'
                            value_name = setting_key[4:]  # Remove 'tcp_' prefix
                            
                            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key, 0, winreg.KEY_SET_VALUE)
                            winreg.SetValueEx(key, value_name, 0, value_type, original_value)
                            winreg.CloseKey(key)
                            
                            rollback_count += 1
                    
                    except Exception as e:
                        self.logger.debug(f"Could not restore {setting_key}: {e}")
            
            # Reset network stack to defaults
            reset_commands = [
                ['netsh', 'int', 'tcp', 'reset'],
                ['netsh', 'winsock', 'reset'],
            ]
            
            for cmd in reset_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    if result.returncode == 0:
                        rollback_count += 1
                except Exception as e:
                    self.logger.debug(f"Reset command failed: {e}")
            
            if rollback_count > 0:
                self.logger.info(f"Rolled back {rollback_count} network optimizations")
                self.logger.warning("Network changes may require system restart to take full effect")
            
            return rollback_count > 0
            
        except Exception as e:
            self.logger.error(f"Network optimization rollback failed: {e}")
            return False
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current network optimization status."""
        return {
            'optimizations_applied': len(self.optimizations_applied),
            'applied_optimizations': self.optimizations_applied.copy(),
            'backup_settings_count': len(self.original_settings),
            'dns_servers': self.gaming_dns_servers,
        }