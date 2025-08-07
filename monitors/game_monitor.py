"""
Game performance monitoring module.
Monitors FPS, frame times, input latency and game-specific metrics.
"""

import time
import threading
import logging
import ctypes
import ctypes.wintypes
from typing import Dict, Any, Optional, List
from collections import deque
import psutil

try:
    import win32gui
    import win32process
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

try:
    from ctypes import wintypes
    HAS_CTYPES_WINTYPES = True
except ImportError:
    HAS_CTYPES_WINTYPES = False

class GameMonitor:
    """Monitors game performance including FPS, frame times, and input latency."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.current_game = None
        self.game_metrics = {}
        self.metrics_history = deque(maxlen=2000)  # Store more for FPS analysis
        self.lock = threading.Lock()
        
        # FPS measurement
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.frame_times = deque(maxlen=120)  # Last 120 frames for analysis
        
        # Game detection
        self.known_games = {
            'League of Legends': ['League of Legends.exe', 'LeagueClient.exe'],
            'Counter-Strike 2': ['cs2.exe'],
            'Valorant': ['VALORANT.exe', 'VALORANT-Win64-Shipping.exe'],
            'Fortnite': ['FortniteClient-Win64-Shipping.exe'],
            'Call of Duty': ['cod.exe', 'ModernWarfare.exe', 'warzone.exe'],
            'Apex Legends': ['r5apex.exe'],
            'Overwatch 2': ['Overwatch.exe'],
            'Cyberpunk 2077': ['Cyberpunk2077.exe'],
            'Elden Ring': ['eldenring.exe'],
            'Minecraft': ['javaw.exe', 'Minecraft.exe'],
            'World of Warcraft': ['Wow.exe', 'WowClassic.exe'],
            'Dota 2': ['dota2.exe'],
            'Rainbow Six Siege': ['RainbowSix.exe'],
            'PUBG': ['TslGame.exe'],
            'Rocket League': ['RocketLeague.exe'],
            'GTA V': ['GTA5.exe'],
            'Red Dead Redemption 2': ['RDR2.exe'],
            'The Witcher 3': ['witcher3.exe'],
            'Battlefield': ['bf1.exe', 'bfv.exe', 'Battlefield2042.exe']
        }
        
        # Windows API setup for advanced monitoring
        self.setup_windows_api()
        
        self.logger.info("GameMonitor initialized")
    
    def setup_windows_api(self):
        """Setup Windows API functions for advanced game monitoring."""
        if not HAS_WIN32 or not HAS_CTYPES_WINTYPES:
            self.logger.warning("Windows API not available for advanced monitoring")
            return
        
        try:
            # Setup for DWM frame counting (Windows Vista+)
            self.dwmapi = ctypes.windll.dwmapi
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            
            # Define structures
            class DWM_TIMING_INFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', wintypes.UINT),
                    ('rateRefresh', ctypes.c_uint64),
                    ('qpcRefreshPeriod', ctypes.c_uint64),
                    ('rateCompose', ctypes.c_uint64),
                    ('qpcVBlank', ctypes.c_uint64),
                    ('cRefresh', ctypes.c_uint64),
                    ('cDXRefresh', ctypes.c_uint),
                    ('qpcCompose', ctypes.c_uint64),
                    ('cFrame', ctypes.c_uint64),
                    ('cDXPresent', ctypes.c_uint),
                    ('cRefreshFrame', ctypes.c_uint64),
                    ('cFrameSubmitted', ctypes.c_uint64),
                    ('cDXPresentSubmitted', ctypes.c_uint),
                    ('cFrameConfirmed', ctypes.c_uint64),
                    ('cDXPresentConfirmed', ctypes.c_uint),
                    ('cRefreshConfirmed', ctypes.c_uint64),
                    ('cDXRefreshConfirmed', ctypes.c_uint),
                    ('cFramesLate', ctypes.c_uint64),
                    ('cFramesOutstanding', ctypes.c_uint)
                ]
            
            self.DWM_TIMING_INFO = DWM_TIMING_INFO
            
            # Performance counter frequency
            freq = ctypes.c_uint64()
            self.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
            self.perf_freq = freq.value
            
        except Exception as e:
            self.logger.warning(f"Could not setup Windows API monitoring: {e}")
    
    def start(self):
        """Start the game monitoring loop."""
        self.running = True
        
        # Start main monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        # Start FPS counting thread
        fps_thread = threading.Thread(target=self._fps_monitoring_loop, daemon=True)
        fps_thread.start()
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent game metrics."""
        with self.lock:
            return self.game_metrics.copy()
    
    def get_current_game(self) -> Optional[str]:
        """Get the currently detected game."""
        return self.current_game
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Detect current game
                self._detect_current_game()
                
                # Collect game metrics
                metrics = self._collect_game_metrics()
                
                with self.lock:
                    self.game_metrics = metrics
                    self.metrics_history.append({
                        'timestamp': time.time(),
                        'game': self.current_game,
                        'metrics': metrics.copy()
                    })
                
                time.sleep(0.5)  # Update twice per second
                
            except Exception as e:
                self.logger.error(f"Error in game monitoring loop: {e}")
                time.sleep(2)
    
    def _fps_monitoring_loop(self):
        """FPS monitoring loop with high precision."""
        while self.running:
            try:
                if self.current_game:
                    fps_data = self._measure_fps()
                    if fps_data:
                        with self.lock:
                            self.game_metrics.update(fps_data)
                
                time.sleep(0.016)  # ~60 Hz monitoring
                
            except Exception as e:
                self.logger.error(f"Error in FPS monitoring: {e}")
                time.sleep(1)
    
    def _detect_current_game(self):
        """Detect currently running game."""
        current_game = None
        game_processes = []
        
        try:
            # Check all running processes
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name']
                    if proc_name:
                        # Check against known games
                        for game_name, executables in self.known_games.items():
                            if proc_name.lower() in [exe.lower() for exe in executables]:
                                game_processes.append({
                                    'name': game_name,
                                    'process': proc,
                                    'executable': proc_name
                                })
                                break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Determine the active game (prefer fullscreen or focused)
            if game_processes:
                active_game = self._find_active_game(game_processes)
                if active_game:
                    current_game = active_game['name']
            
        except Exception as e:
            self.logger.error(f"Error detecting game: {e}")
        
        if current_game != self.current_game:
            if current_game:
                self.logger.info(f"Detected game: {current_game}")
            else:
                self.logger.info("No game detected")
            self.current_game = current_game
    
    def _find_active_game(self, game_processes: List[Dict]) -> Optional[Dict]:
        """Find the active game from detected processes."""
        if not HAS_WIN32:
            return game_processes[0] if game_processes else None
        
        try:
            # Get foreground window
            foreground_hwnd = win32gui.GetForegroundWindow()
            if not foreground_hwnd:
                return game_processes[0] if game_processes else None
            
            # Get process ID of foreground window
            _, foreground_pid = win32process.GetWindowThreadProcessId(foreground_hwnd)
            
            # Check if any game process matches foreground
            for game_proc in game_processes:
                if game_proc['process'].pid == foreground_pid:
                    # Check if window is fullscreen
                    if self._is_fullscreen_window(foreground_hwnd):
                        game_proc['is_fullscreen'] = True
                    return game_proc
            
            # If no match with foreground, return first game
            return game_processes[0] if game_processes else None
            
        except Exception as e:
            self.logger.debug(f"Error finding active game: {e}")
            return game_processes[0] if game_processes else None
    
    def _is_fullscreen_window(self, hwnd) -> bool:
        """Check if a window is fullscreen."""
        if not HAS_WIN32:
            return False
        
        try:
            # Get window rect
            window_rect = win32gui.GetWindowRect(hwnd)
            
            # Get monitor info
            monitor = win32gui.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32gui.GetMonitorInfo(monitor)
            monitor_rect = monitor_info['Monitor']
            
            # Check if window covers entire monitor
            return (window_rect[0] <= monitor_rect[0] and
                    window_rect[1] <= monitor_rect[1] and
                    window_rect[2] >= monitor_rect[2] and
                    window_rect[3] >= monitor_rect[3])
            
        except Exception:
            return False
    
    def _collect_game_metrics(self) -> Dict[str, Any]:
        """Collect game performance metrics."""
        metrics = {}
        
        try:
            if not self.current_game:
                return metrics
            
            # Basic game info
            metrics['game_name'] = self.current_game
            metrics['game_detected'] = True
            
            # Get game process info
            game_process = self._get_game_process()
            if game_process:
                metrics.update(self._get_process_metrics(game_process))
            
            # Frame timing analysis
            metrics.update(self._analyze_frame_timing())
            
            # Input latency estimation
            metrics.update(self._estimate_input_latency())
            
        except Exception as e:
            self.logger.error(f"Error collecting game metrics: {e}")
        
        return metrics
    
    def _get_game_process(self):
        """Get the main game process."""
        if not self.current_game:
            return None
        
        try:
            executables = self.known_games.get(self.current_game, [])
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() in [exe.lower() for exe in executables]:
                    return proc
        except Exception:
            pass
        
        return None
    
    def _get_process_metrics(self, process) -> Dict[str, Any]:
        """Get metrics from game process."""
        metrics = {}
        
        try:
            # CPU usage of game process
            cpu_percent = process.cpu_percent()
            metrics['game_cpu_usage'] = cpu_percent
            
            # Memory usage of game process
            memory_info = process.memory_info()
            metrics['game_memory_rss'] = memory_info.rss
            metrics['game_memory_vms'] = memory_info.vms
            
            # Process priority
            metrics['game_priority'] = process.nice()
            
            # Number of threads
            metrics['game_threads'] = process.num_threads()
            
            # Process status
            metrics['game_status'] = process.status()
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.debug(f"Could not get process metrics: {e}")
        except Exception as e:
            self.logger.error(f"Error getting process metrics: {e}")
        
        return metrics
    
    def _measure_fps(self) -> Dict[str, Any]:
        """Measure FPS using various methods."""
        fps_data = {}
        
        try:
            # Method 1: Simple frame counting
            current_time = time.time()
            time_diff = current_time - self.last_fps_time
            
            if time_diff >= 1.0:  # Update every second
                fps = self.fps_counter / time_diff
                fps_data['fps'] = round(fps, 2)
                
                self.fps_counter = 0
                self.last_fps_time = current_time
            
            # Method 2: DWM timing (Windows)
            if HAS_WIN32 and hasattr(self, 'dwmapi'):
                dwm_fps = self._get_dwm_fps()
                if dwm_fps:
                    fps_data['fps_dwm'] = dwm_fps
            
            # Increment frame counter
            self.fps_counter += 1
            
            # Record frame time
            if len(self.frame_times) > 0:
                frame_time = current_time - self.frame_times[-1]
                fps_data['frame_time'] = round(frame_time * 1000, 2)  # Convert to ms
            
            self.frame_times.append(current_time)
            
        except Exception as e:
            self.logger.debug(f"Error measuring FPS: {e}")
        
        return fps_data
    
    def _get_dwm_fps(self) -> Optional[float]:
        """Get FPS using Desktop Window Manager timing info."""
        try:
            timing_info = self.DWM_TIMING_INFO()
            timing_info.cbSize = ctypes.sizeof(self.DWM_TIMING_INFO)
            
            result = self.dwmapi.DwmGetCompositionTimingInfo(None, ctypes.byref(timing_info))
            if result == 0:  # S_OK
                # Calculate refresh rate
                if timing_info.rateRefresh.value > 0:
                    refresh_rate = timing_info.rateRefresh.value / timing_info.qpcRefreshPeriod.value * self.perf_freq
                    return round(refresh_rate, 2)
        
        except Exception as e:
            self.logger.debug(f"DWM FPS measurement failed: {e}")
        
        return None
    
    def _analyze_frame_timing(self) -> Dict[str, Any]:
        """Analyze frame timing for consistency metrics."""
        analysis = {}
        
        try:
            if len(self.frame_times) < 10:
                return analysis
            
            # Calculate frame times in milliseconds
            recent_frame_times = list(self.frame_times)[-60:]  # Last 60 frames
            frame_deltas = []
            
            for i in range(1, len(recent_frame_times)):
                delta = (recent_frame_times[i] - recent_frame_times[i-1]) * 1000
                frame_deltas.append(delta)
            
            if frame_deltas:
                # Average frame time
                avg_frame_time = sum(frame_deltas) / len(frame_deltas)
                analysis['avg_frame_time'] = round(avg_frame_time, 2)
                analysis['avg_fps_calculated'] = round(1000 / avg_frame_time, 2) if avg_frame_time > 0 else 0
                
                # Frame time consistency
                max_frame_time = max(frame_deltas)
                min_frame_time = min(frame_deltas)
                analysis['max_frame_time'] = round(max_frame_time, 2)
                analysis['min_frame_time'] = round(min_frame_time, 2)
                analysis['frame_time_variance'] = round(max_frame_time - min_frame_time, 2)
                
                # Stuttering detection (frames taking >2x average)
                stutter_threshold = avg_frame_time * 2
                stutters = [ft for ft in frame_deltas if ft > stutter_threshold]
                analysis['stutter_count'] = len(stutters)
                analysis['stutter_percentage'] = round((len(stutters) / len(frame_deltas)) * 100, 2)
                
                # 1% and 0.1% low FPS (common gaming metrics)
                sorted_frame_times = sorted(frame_deltas, reverse=True)
                one_percent_index = max(0, int(len(sorted_frame_times) * 0.01) - 1)
                point_one_percent_index = max(0, int(len(sorted_frame_times) * 0.001) - 1)
                
                if one_percent_index < len(sorted_frame_times):
                    one_percent_low = sorted_frame_times[one_percent_index]
                    analysis['1_percent_low_fps'] = round(1000 / one_percent_low, 2) if one_percent_low > 0 else 0
                
                if point_one_percent_index < len(sorted_frame_times):
                    point_one_percent_low = sorted_frame_times[point_one_percent_index]
                    analysis['0_1_percent_low_fps'] = round(1000 / point_one_percent_low, 2) if point_one_percent_low > 0 else 0
        
        except Exception as e:
            self.logger.debug(f"Frame timing analysis error: {e}")
        
        return analysis
    
    def _estimate_input_latency(self) -> Dict[str, Any]:
        """Estimate input latency based on available metrics."""
        latency_data = {}
        
        try:
            # This is a simplified estimation
            # Real input latency measurement requires specialized hardware/software
            
            # Base system latency estimation
            base_latency = 1.0  # ms baseline
            
            # Add display latency (typical for gaming monitors)
            display_latency = 5.0  # ms
            
            # Add frame time contribution
            current_metrics = self.get_current_metrics()
            frame_time = current_metrics.get('frame_time', 16.67)  # Default to 60 FPS
            
            # Input lag increases with frame time
            frame_contribution = frame_time / 2  # Half frame time on average
            
            total_estimated_latency = base_latency + display_latency + frame_contribution
            latency_data['estimated_input_latency'] = round(total_estimated_latency, 2)
            
            # Categorize latency
            if total_estimated_latency < 20:
                latency_data['latency_category'] = 'excellent'
            elif total_estimated_latency < 40:
                latency_data['latency_category'] = 'good'
            elif total_estimated_latency < 60:
                latency_data['latency_category'] = 'acceptable'
            else:
                latency_data['latency_category'] = 'poor'
        
        except Exception as e:
            self.logger.debug(f"Input latency estimation error: {e}")
        
        return latency_data
    
    def get_performance_issues(self) -> List[str]:
        """Detect performance issues in current game session."""
        issues = []
        metrics = self.get_current_metrics()
        
        try:
            # Low FPS
            fps = metrics.get('fps', 0) or metrics.get('avg_fps_calculated', 0)
            if fps > 0 and fps < 30:
                issues.append('very_low_fps')
            elif fps > 0 and fps < 60:
                issues.append('low_fps')
            
            # High frame time variance (stuttering)
            frame_variance = metrics.get('frame_time_variance', 0)
            if frame_variance > 10:
                issues.append('frame_stuttering')
            
            # High stutter percentage
            stutter_pct = metrics.get('stutter_percentage', 0)
            if stutter_pct > 5:
                issues.append('frequent_stuttering')
            
            # High input latency
            input_latency = metrics.get('estimated_input_latency', 0)
            if input_latency > 50:
                issues.append('high_input_latency')
            
            # Game process issues
            game_cpu = metrics.get('game_cpu_usage', 0)
            if game_cpu > 95:
                issues.append('game_cpu_bottleneck')
        
        except Exception as e:
            self.logger.error(f"Error detecting performance issues: {e}")
        
        return issues