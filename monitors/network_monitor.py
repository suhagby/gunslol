"""
Network performance monitoring module.
Monitors ping, jitter, packet loss, bandwidth, and network latency.
"""

import time
import threading
import logging
import subprocess
import statistics
import socket
from typing import Dict, Any, List, Optional
from collections import deque
import psutil

try:
    import ping3
    HAS_PING3 = True
except ImportError:
    HAS_PING3 = False

try:
    import speedtest
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class NetworkMonitor:
    """Monitors network performance for gaming optimization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.network_metrics = {}
        self.metrics_history = deque(maxlen=1000)
        self.lock = threading.Lock()
        
        # Ping monitoring
        self.ping_history = deque(maxlen=100)
        self.gaming_servers = [
            # Popular game servers and CDNs
            '8.8.8.8',           # Google DNS
            '1.1.1.1',           # Cloudflare DNS
            '208.67.222.222',    # OpenDNS
            '149.154.167.99',    # Discord
            '104.16.249.249',    # Cloudflare gaming CDN
        ]
        
        # Gaming server endpoints for specific games
        self.game_servers = {
            'League of Legends': ['104.160.131.3', '104.160.131.1'],  # Riot Games
            'Counter-Strike 2': ['146.66.152.12', '155.133.248.37'],  # Valve/Steam
            'Valorant': ['104.160.131.3', '104.160.131.1'],           # Riot Games
            'Fortnite': ['18.211.135.69', '3.90.189.27'],            # Epic Games
            'Apex Legends': ['8.26.207.132', '8.26.207.133'],        # EA
            'Call of Duty': ['136.147.174.25', '38.102.136.180'],     # Activision
            'Overwatch 2': ['24.105.62.129', '137.221.105.152'],     # Blizzard
        }
        
        # Network adapter tracking
        self.last_net_io = None
        self.last_net_time = time.time()
        
        # Bandwidth testing
        self.last_speed_test = 0
        self.speed_test_interval = 1800  # 30 minutes
        
        self.logger.info("NetworkMonitor initialized")
    
    def start(self):
        """Start the network monitoring loop."""
        self.running = True
        
        # Start main monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        # Start ping monitoring thread
        ping_thread = threading.Thread(target=self._ping_monitoring_loop, daemon=True)
        ping_thread.start()
        
        # Start bandwidth monitoring thread
        bandwidth_thread = threading.Thread(target=self._bandwidth_monitoring_loop, daemon=True)
        bandwidth_thread.start()
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent network metrics."""
        with self.lock:
            return self.network_metrics.copy()
    
    def _monitoring_loop(self):
        """Main network monitoring loop."""
        while self.running:
            try:
                metrics = self._collect_network_metrics()
                
                with self.lock:
                    self.network_metrics.update(metrics)
                    self.metrics_history.append({
                        'timestamp': time.time(),
                        'metrics': metrics.copy()
                    })
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in network monitoring loop: {e}")
                time.sleep(10)
    
    def _ping_monitoring_loop(self):
        """Continuous ping monitoring loop."""
        while self.running:
            try:
                ping_results = self._measure_ping_to_servers()
                
                if ping_results:
                    with self.lock:
                        self.network_metrics.update(ping_results)
                        self.ping_history.extend([
                            result for result in ping_results.values() 
                            if isinstance(result, (int, float)) and result > 0
                        ])
                
                time.sleep(2)  # Ping every 2 seconds
                
            except Exception as e:
                self.logger.error(f"Error in ping monitoring: {e}")
                time.sleep(5)
    
    def _bandwidth_monitoring_loop(self):
        """Periodic bandwidth testing loop."""
        while self.running:
            try:
                current_time = time.time()
                
                # Run speed test periodically
                if current_time - self.last_speed_test > self.speed_test_interval:
                    self.logger.info("Running bandwidth speed test...")
                    speed_results = self._run_speed_test()
                    
                    if speed_results:
                        with self.lock:
                            self.network_metrics.update(speed_results)
                        self.last_speed_test = current_time
                        self.logger.info(f"Speed test completed: {speed_results}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in bandwidth monitoring: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _collect_network_metrics(self) -> Dict[str, Any]:
        """Collect basic network metrics."""
        metrics = {}
        
        try:
            # Network I/O statistics
            net_io = psutil.net_io_counters()
            current_time = time.time()
            
            if net_io and self.last_net_io:
                time_diff = current_time - self.last_net_time
                
                if time_diff > 0:
                    # Calculate rates
                    bytes_sent_rate = (net_io.bytes_sent - self.last_net_io.bytes_sent) / time_diff
                    bytes_recv_rate = (net_io.bytes_recv - self.last_net_io.bytes_recv) / time_diff
                    
                    metrics['network_upload_rate'] = bytes_sent_rate / 1024 / 1024  # MB/s
                    metrics['network_download_rate'] = bytes_recv_rate / 1024 / 1024  # MB/s
                    
                    # Packet rates
                    packets_sent_rate = (net_io.packets_sent - self.last_net_io.packets_sent) / time_diff
                    packets_recv_rate = (net_io.packets_recv - self.last_net_io.packets_recv) / time_diff
                    
                    metrics['network_packets_sent_rate'] = packets_sent_rate
                    metrics['network_packets_recv_rate'] = packets_recv_rate
                    
                    # Error rates
                    if net_io.errin > self.last_net_io.errin:
                        metrics['network_errors_in'] = net_io.errin - self.last_net_io.errin
                    if net_io.errout > self.last_net_io.errout:
                        metrics['network_errors_out'] = net_io.errout - self.last_net_io.errout
                    if net_io.dropin > self.last_net_io.dropin:
                        metrics['network_drops_in'] = net_io.dropin - self.last_net_io.dropin
                    if net_io.dropout > self.last_net_io.dropout:
                        metrics['network_drops_out'] = net_io.dropout - self.last_net_io.dropout
            
            # Update tracking variables
            self.last_net_io = net_io
            self.last_net_time = current_time
            
            # Network interface information
            interfaces = psutil.net_if_stats()
            active_interfaces = []
            
            for interface_name, interface_stats in interfaces.items():
                if interface_stats.isup and not interface_name.startswith('Loopback'):
                    interface_info = {
                        'name': interface_name,
                        'speed': interface_stats.speed,  # Mbps
                        'mtu': interface_stats.mtu,
                        'duplex': interface_stats.duplex
                    }
                    active_interfaces.append(interface_info)
            
            metrics['active_interfaces'] = active_interfaces
            
            # Connection count
            try:
                connections = psutil.net_connections()
                established_connections = [c for c in connections if c.status == 'ESTABLISHED']
                metrics['established_connections'] = len(established_connections)
                metrics['total_connections'] = len(connections)
            except psutil.AccessDenied:
                pass
            
        except Exception as e:
            self.logger.error(f"Error collecting network metrics: {e}")
        
        return metrics
    
    def _measure_ping_to_servers(self) -> Dict[str, Any]:
        """Measure ping to various servers."""
        ping_results = {}
        
        try:
            # Test primary gaming servers
            for server in self.gaming_servers[:3]:  # Test first 3 to avoid spam
                ping_time = self._ping_server(server)
                if ping_time is not None:
                    ping_results[f'ping_{server.replace(".", "_")}'] = ping_time
            
            # Calculate statistics from recent pings
            if self.ping_history:
                recent_pings = list(self.ping_history)[-30:]  # Last 30 pings
                ping_results['ping_avg'] = round(statistics.mean(recent_pings), 2)
                ping_results['ping_min'] = round(min(recent_pings), 2)
                ping_results['ping_max'] = round(max(recent_pings), 2)
                
                if len(recent_pings) > 1:
                    ping_results['ping_jitter'] = round(statistics.stdev(recent_pings), 2)
                    
                    # Calculate packet loss approximation
                    expected_pings = 30  # Expected number of successful pings
                    actual_pings = len([p for p in recent_pings if p > 0])
                    packet_loss = max(0, (expected_pings - actual_pings) / expected_pings * 100)
                    ping_results['packet_loss_estimated'] = round(packet_loss, 2)
        
        except Exception as e:
            self.logger.error(f"Error measuring ping: {e}")
        
        return ping_results
    
    def _ping_server(self, server: str, timeout: float = 3.0) -> Optional[float]:
        """Ping a specific server and return response time."""
        try:
            if HAS_PING3:
                # Use ping3 library (requires admin privileges on Windows)
                result = ping3.ping(server, timeout=timeout)
                if result is not None:
                    return round(result * 1000, 2)  # Convert to ms
            
            # Fallback to system ping command
            return self._system_ping(server, timeout)
            
        except Exception as e:
            self.logger.debug(f"Ping to {server} failed: {e}")
            return None
    
    def _system_ping(self, server: str, timeout: float = 3.0) -> Optional[float]:
        """Use system ping command as fallback."""
        try:
            import platform
            
            # Determine ping command based on OS
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', '1', '-w', str(int(timeout * 1000)), server]
            else:
                cmd = ['ping', '-c', '1', '-W', str(int(timeout)), server]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 1)
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse ping output to extract time
                if platform.system().lower() == 'windows':
                    # Windows: "time=1ms" or "time<1ms"
                    import re
                    match = re.search(r'time[<=](\d+(?:\.\d+)?)ms', output)
                    if match:
                        return float(match.group(1))
                else:
                    # Unix-like: "time=1.234 ms"
                    import re
                    match = re.search(r'time=(\d+(?:\.\d+)?)\s*ms', output)
                    if match:
                        return float(match.group(1))
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            self.logger.debug(f"System ping to {server} failed: {e}")
        
        return None
    
    def _run_speed_test(self) -> Dict[str, Any]:
        """Run internet speed test."""
        speed_results = {}
        
        try:
            if not HAS_SPEEDTEST:
                self.logger.warning("Speedtest library not available")
                return speed_results
            
            # Create speedtest client
            st = speedtest.Speedtest()
            
            # Get best server
            st.get_best_server()
            server_info = st.get_best_server()
            
            speed_results['speedtest_server'] = f"{server_info['sponsor']} - {server_info['name']}"
            speed_results['speedtest_server_distance'] = server_info['d']
            speed_results['speedtest_server_ping'] = server_info['latency']
            
            # Test download speed
            self.logger.info("Testing download speed...")
            download_speed = st.download() / 1024 / 1024  # Convert to Mbps
            speed_results['download_speed_mbps'] = round(download_speed, 2)
            
            # Test upload speed
            self.logger.info("Testing upload speed...")
            upload_speed = st.upload() / 1024 / 1024  # Convert to Mbps
            speed_results['upload_speed_mbps'] = round(upload_speed, 2)
            
            # Additional metrics
            speed_results['speedtest_timestamp'] = time.time()
            
        except Exception as e:
            self.logger.error(f"Speed test failed: {e}")
        
        return speed_results
    
    def get_game_server_ping(self, game_name: str) -> Optional[Dict[str, float]]:
        """Get ping to specific game servers."""
        if game_name not in self.game_servers:
            return None
        
        game_pings = {}
        servers = self.game_servers[game_name]
        
        for server in servers:
            ping_time = self._ping_server(server)
            if ping_time is not None:
                game_pings[server] = ping_time
        
        if game_pings:
            game_pings['average'] = sum(game_pings.values()) / len(game_pings)
            game_pings['best'] = min(game_pings.values())
            
        return game_pings if game_pings else None
    
    def test_dns_performance(self) -> Dict[str, Any]:
        """Test DNS resolution performance."""
        dns_results = {}
        
        dns_servers = [
            ('Cloudflare', '1.1.1.1'),
            ('Google', '8.8.8.8'),
            ('OpenDNS', '208.67.222.222'),
            ('Quad9', '9.9.9.9')
        ]
        
        test_domains = [
            'google.com',
            'github.com',
            'discord.com',
            'steampowered.com',
            'riotgames.com'
        ]
        
        try:
            for dns_name, dns_server in dns_servers:
                dns_times = []
                
                for domain in test_domains:
                    start_time = time.time()
                    try:
                        # Simple DNS resolution test
                        socket.gethostbyname(domain)
                        resolve_time = (time.time() - start_time) * 1000  # Convert to ms
                        dns_times.append(resolve_time)
                    except:
                        continue
                
                if dns_times:
                    dns_results[f'dns_{dns_name.lower()}_avg'] = round(statistics.mean(dns_times), 2)
                    dns_results[f'dns_{dns_name.lower()}_min'] = round(min(dns_times), 2)
                    dns_results[f'dns_{dns_name.lower()}_max'] = round(max(dns_times), 2)
        
        except Exception as e:
            self.logger.error(f"DNS performance test failed: {e}")
        
        return dns_results
    
    def check_network_stability(self) -> Dict[str, Any]:
        """Check network connection stability."""
        stability_metrics = {}
        
        try:
            recent_history = list(self.metrics_history)[-60:]  # Last 5 minutes
            
            if len(recent_history) < 10:
                return stability_metrics
            
            # Extract ping values
            ping_values = []
            for entry in recent_history:
                ping_avg = entry['metrics'].get('ping_avg')
                if ping_avg:
                    ping_values.append(ping_avg)
            
            if ping_values:
                # Ping stability
                ping_variance = statistics.variance(ping_values) if len(ping_values) > 1 else 0
                stability_metrics['ping_variance'] = round(ping_variance, 2)
                stability_metrics['ping_stability'] = 'stable' if ping_variance < 25 else 'unstable'
                
                # Connection drops detection
                connection_drops = 0
                for i in range(1, len(ping_values)):
                    if ping_values[i] > ping_values[i-1] * 2:  # Sudden ping spike
                        connection_drops += 1
                
                stability_metrics['connection_spikes'] = connection_drops
                stability_metrics['connection_stability_score'] = max(0, 100 - (ping_variance + connection_drops * 10))
            
            # Network interface stability
            error_count = 0
            drop_count = 0
            
            for entry in recent_history:
                metrics = entry['metrics']
                error_count += metrics.get('network_errors_in', 0) + metrics.get('network_errors_out', 0)
                drop_count += metrics.get('network_drops_in', 0) + metrics.get('network_drops_out', 0)
            
            stability_metrics['total_network_errors'] = error_count
            stability_metrics['total_packet_drops'] = drop_count
            
            # Overall network health score
            health_score = 100
            health_score -= min(50, ping_variance)  # Subtract up to 50 for ping variance
            health_score -= min(30, error_count * 5)  # Subtract for errors
            health_score -= min(20, drop_count * 10)  # Subtract for drops
            
            stability_metrics['network_health_score'] = max(0, round(health_score, 1))
            
        except Exception as e:
            self.logger.error(f"Network stability check failed: {e}")
        
        return stability_metrics
    
    def get_network_issues(self) -> List[str]:
        """Detect network issues affecting gaming performance."""
        issues = []
        metrics = self.get_current_metrics()
        
        try:
            # High ping
            ping_avg = metrics.get('ping_avg', 0)
            if ping_avg > 100:
                issues.append('high_ping')
            elif ping_avg > 50:
                issues.append('moderate_ping')
            
            # High jitter
            jitter = metrics.get('ping_jitter', 0)
            if jitter > 20:
                issues.append('high_jitter')
            
            # Packet loss
            packet_loss = metrics.get('packet_loss_estimated', 0)
            if packet_loss > 2:
                issues.append('packet_loss')
            
            # Network errors
            if metrics.get('network_errors_in', 0) > 0 or metrics.get('network_errors_out', 0) > 0:
                issues.append('network_errors')
            
            # Low bandwidth (if speed test available)
            download_speed = metrics.get('download_speed_mbps', 0)
            if download_speed > 0 and download_speed < 25:  # Less than 25 Mbps
                issues.append('low_bandwidth')
            
            # Connection instability
            stability_score = self.check_network_stability().get('network_health_score', 100)
            if stability_score < 70:
                issues.append('unstable_connection')
        
        except Exception as e:
            self.logger.error(f"Error detecting network issues: {e}")
        
        return issues