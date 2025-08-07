#!/usr/bin/env python3
"""
AI-Powered System Analyzer
Comprehensive PC analysis with intelligent problem detection and optimization recommendations.
"""

import os
import sys
import json
import time
import logging
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import pickle

import psutil

@dataclass
class SystemIssue:
    """Represents a detected system issue."""
    id: str
    category: str  # 'cpu', 'memory', 'gpu', 'network', 'storage', 'system', 'gaming'
    severity: str  # 'critical', 'warning', 'info'
    title: str
    description: str
    impact: str  # Description of performance impact
    recommendations: List[str]  # List of recommended fixes
    detection_time: float
    confidence: float  # 0.0 to 1.0
    auto_fixable: bool
    affects_gaming: bool
    safe_with_anticheat: bool

@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation."""
    id: str
    category: str
    title: str
    description: str
    expected_improvement: str
    risk_level: str  # 'low', 'medium', 'high'
    requires_restart: bool
    auto_applicable: bool
    safe_with_anticheat: bool
    priority: int  # 1-10, higher is more important

class AntiCheatSafety:
    """Manages anti-cheat compatibility for optimizations."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.AntiCheatSafety")
        
        # Known anti-cheat systems and their restrictions
        self.anticheat_systems = {
            'vanguard': {  # Valorant
                'forbidden_processes': ['cheat_engine', 'process_hacker'],
                'forbidden_registry': [
                    'HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management\\DisablePagingExecutive'
                ],
                'forbidden_services': ['debugging_services'],
                'safe_optimizations': ['network_tcp', 'windows_visual_effects', 'disk_cleanup']
            },
            'vac': {  # Steam/CS2
                'forbidden_processes': ['cheat_engine', 'artmoney'],
                'forbidden_dll_injection': True,
                'forbidden_memory_modification': True,
                'safe_optimizations': ['network_optimization', 'cpu_priority', 'visual_effects', 'disk_cleanup']
            },
            'battleye': {  # PUBG, Fortnite, etc
                'forbidden_processes': ['cheat_engine', 'process_hacker', 'wireshark'],
                'forbidden_memory_access': True,
                'safe_optimizations': ['network_tcp', 'cpu_governor', 'visual_effects']
            },
            'easyanticheat': {  # EAC
                'forbidden_processes': ['cheat_engine', 'artmoney'],
                'forbidden_kernel_drivers': ['debug_drivers'],
                'safe_optimizations': ['network_optimization', 'visual_effects', 'disk_optimization']
            }
        }
        
        # Safe optimization categories that work with all anti-cheats
        self.universally_safe_optimizations = [
            'windows_visual_effects',
            'disk_cleanup',
            'network_tcp_optimization',
            'power_plan_optimization',
            'startup_programs_cleanup',
            'windows_update_optimization',
            'registry_cleanup_safe',
            'temporary_files_cleanup'
        ]
    
    def is_optimization_safe(self, optimization_id: str, detected_anticheats: List[str] = None) -> bool:
        """Check if an optimization is safe with detected anti-cheat systems."""
        try:
            # Always allow universally safe optimizations
            if optimization_id in self.universally_safe_optimizations:
                return True
            
            # If no anti-cheats detected, allow most optimizations except dangerous ones
            if not detected_anticheats:
                dangerous_optimizations = [
                    'memory_injection',
                    'process_hollowing',
                    'dll_injection',
                    'kernel_driver_modification',
                    'debug_privilege_escalation'
                ]
                return optimization_id not in dangerous_optimizations
            
            # Check against each detected anti-cheat
            for anticheat in detected_anticheats:
                if anticheat in self.anticheat_systems:
                    anticheat_info = self.anticheat_systems[anticheat]
                    safe_opts = anticheat_info.get('safe_optimizations', [])
                    
                    # If explicitly listed as safe, allow it
                    if optimization_id in safe_opts:
                        continue
                    
                    # Otherwise, be conservative and deny
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking optimization safety: {e}")
            return False  # Be conservative on error
    
    def detect_running_anticheats(self) -> List[str]:
        """Detect currently running anti-cheat systems."""
        detected = []
        
        try:
            # Check for known anti-cheat processes
            anticheat_processes = {
                'vgtray.exe': 'vanguard',
                'vgc.exe': 'vanguard',
                'steam.exe': 'vac',  # When Steam is running with VAC games
                'BEService.exe': 'battleye',
                'BattlEye.exe': 'battleye',
                'EasyAntiCheat.exe': 'easyanticheat',
                'EACLauncher.exe': 'easyanticheat'
            }
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name']
                    if proc_name and proc_name.lower() in [p.lower() for p in anticheat_processes.keys()]:
                        anticheat_type = anticheat_processes.get(proc_name, 'unknown')
                        if anticheat_type not in detected:
                            detected.append(anticheat_type)
                            self.logger.info(f"Detected anti-cheat system: {anticheat_type}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        
        except Exception as e:
            self.logger.error(f"Error detecting anti-cheat systems: {e}")
        
        return detected

class AISystemAnalyzer:
    """AI-powered system analyzer for comprehensive PC optimization."""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(f"{__name__}.AISystemAnalyzer")
        self.config = config or {}
        
        # Initialize components
        self.anticheat_safety = AntiCheatSafety()
        
        # Analysis data
        self.detected_issues = {}  # issue_id -> SystemIssue
        self.recommendations = {}  # rec_id -> OptimizationRecommendation
        self.system_baseline = None
        self.learning_data = defaultdict(list)
        self.analysis_history = deque(maxlen=1000)
        
        # Analysis state
        self.last_analysis_time = 0
        self.analysis_interval = 30  # seconds
        self.learning_enabled = True
        self.auto_fix_enabled = False
        
        # Load learning data if available
        self.learning_file = Path("data/ai_learning_data.pkl")
        self.learning_file.parent.mkdir(exist_ok=True)
        self._load_learning_data()
        
        self.logger.info("AI System Analyzer initialized")
    
    def analyze_system(self, force: bool = False) -> Dict[str, Any]:
        """Perform comprehensive system analysis."""
        try:
            current_time = time.time()
            
            # Check if analysis is needed
            if not force and (current_time - self.last_analysis_time) < self.analysis_interval:
                return self._get_current_analysis_summary()
            
            self.logger.info("Starting comprehensive system analysis...")
            
            # Detect anti-cheat systems first
            detected_anticheats = self.anticheat_safety.detect_running_anticheats()
            
            # Clear previous issues for fresh analysis
            self.detected_issues.clear()
            self.recommendations.clear()
            
            # Gather system information
            system_info = self._gather_system_info()
            
            # Analyze different system components
            self._analyze_cpu_performance(system_info)
            self._analyze_memory_usage(system_info)
            self._analyze_storage_performance(system_info)
            self._analyze_network_performance(system_info)
            self._analyze_gpu_performance(system_info)
            self._analyze_system_configuration(system_info)
            self._analyze_gaming_performance(system_info)
            self._analyze_process_optimization(system_info)
            
            # Generate recommendations based on issues
            self._generate_optimization_recommendations(detected_anticheats)
            
            # Apply machine learning insights
            self._apply_learning_insights(system_info)
            
            # Update learning data
            if self.learning_enabled:
                self._update_learning_data(system_info)
            
            # Store analysis results
            analysis_result = {
                'timestamp': current_time,
                'system_info': system_info,
                'detected_anticheats': detected_anticheats,
                'issues': {k: asdict(v) for k, v in self.detected_issues.items()},
                'recommendations': {k: asdict(v) for k, v in self.recommendations.items()},
                'analysis_summary': self._create_analysis_summary()
            }
            
            self.analysis_history.append(analysis_result)
            self.last_analysis_time = current_time
            
            self.logger.info(f"System analysis completed. Found {len(self.detected_issues)} issues, {len(self.recommendations)} recommendations")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error during system analysis: {e}")
            return {}
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information."""
        try:
            # CPU Information
            cpu_info = {
                'usage_percent': psutil.cpu_percent(interval=1),
                'usage_per_cpu': psutil.cpu_percent(interval=1, percpu=True),
                'count_logical': psutil.cpu_count(logical=True),
                'count_physical': psutil.cpu_count(logical=False),
                'freq_current': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'freq_max': psutil.cpu_freq().max if psutil.cpu_freq() else 0,
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Memory Information
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
                'free': memory.free,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_percent': swap.percent
            }
            
            # Disk Information
            disk_info = {}
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    disk_info[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percent': partition_usage.percent
                    }
                except (PermissionError, FileNotFoundError):
                    continue
            
            # Network Information
            network_info = {
                'connections': len(psutil.net_connections()),
                'interfaces': {}
            }
            
            net_io = psutil.net_io_counters(pernic=True)
            for interface, stats in net_io.items():
                network_info['interfaces'][interface] = {
                    'bytes_sent': stats.bytes_sent,
                    'bytes_recv': stats.bytes_recv,
                    'packets_sent': stats.packets_sent,
                    'packets_recv': stats.packets_recv,
                    'errin': stats.errin,
                    'errout': stats.errout,
                    'dropin': stats.dropin,
                    'dropout': stats.dropout
                }
            
            # Process Information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Boot time and uptime
            boot_time = psutil.boot_time()
            uptime = time.time() - boot_time
            
            return {
                'timestamp': time.time(),
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'processes': processes,
                'boot_time': boot_time,
                'uptime_seconds': uptime
            }
            
        except Exception as e:
            self.logger.error(f"Error gathering system info: {e}")
            return {}
    
    def _analyze_cpu_performance(self, system_info: Dict[str, Any]):
        """Analyze CPU performance and detect issues."""
        try:
            cpu_info = system_info.get('cpu', {})
            
            # High CPU usage issue
            usage = cpu_info.get('usage_percent', 0)
            if usage > 85:
                issue_id = 'high_cpu_usage'
                self.detected_issues[issue_id] = SystemIssue(
                    id=issue_id,
                    category='cpu',
                    severity='warning' if usage < 95 else 'critical',
                    title='High CPU Usage Detected',
                    description=f'CPU usage is at {usage:.1f}%, which may impact gaming performance',
                    impact='May cause frame drops, stuttering, and increased input latency',
                    recommendations=[
                        'Close unnecessary background applications',
                        'Optimize Windows background services',
                        'Adjust process priorities',
                        'Enable CPU performance mode'
                    ],
                    detection_time=time.time(),
                    confidence=0.9,
                    auto_fixable=True,
                    affects_gaming=True,
                    safe_with_anticheat=True
                )
            
            # CPU frequency analysis
            freq_current = cpu_info.get('freq_current', 0)
            freq_max = cpu_info.get('freq_max', 0)
            
            if freq_max > 0 and freq_current < freq_max * 0.7:
                issue_id = 'cpu_not_boosting'
                self.detected_issues[issue_id] = SystemIssue(
                    id=issue_id,
                    category='cpu',
                    severity='warning',
                    title='CPU Not Running at Optimal Frequency',
                    description=f'CPU running at {freq_current:.0f}MHz instead of max {freq_max:.0f}MHz',
                    impact='Reduced gaming performance and slower system responsiveness',
                    recommendations=[
                        'Set power plan to High Performance',
                        'Disable CPU power saving features',
                        'Check thermal throttling',
                        'Update CPU drivers'
                    ],
                    detection_time=time.time(),
                    confidence=0.8,
                    auto_fixable=True,
                    affects_gaming=True,
                    safe_with_anticheat=True
                )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing CPU performance: {e}")
    
    def _analyze_memory_usage(self, system_info: Dict[str, Any]):
        """Analyze memory usage and detect issues."""
        try:
            memory_info = system_info.get('memory', {})
            
            # High memory usage
            memory_percent = memory_info.get('percent', 0)
            if memory_percent > 85:
                issue_id = 'high_memory_usage'
                self.detected_issues[issue_id] = SystemIssue(
                    id=issue_id,
                    category='memory',
                    severity='warning' if memory_percent < 95 else 'critical',
                    title='High Memory Usage Detected',
                    description=f'Memory usage is at {memory_percent:.1f}%',
                    impact='May cause system slowdowns, increased load times, and potential crashes',
                    recommendations=[
                        'Close memory-intensive applications',
                        'Clear system cache',
                        'Disable memory-hungry startup programs',
                        'Consider adding more RAM'
                    ],
                    detection_time=time.time(),
                    confidence=0.9,
                    auto_fixable=True,
                    affects_gaming=True,
                    safe_with_anticheat=True
                )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing memory usage: {e}")
    
    def _analyze_storage_performance(self, system_info: Dict[str, Any]):
        """Analyze storage performance and detect issues."""
        try:
            disk_info = system_info.get('disk', {})
            
            for device, info in disk_info.items():
                # High disk usage
                disk_percent = info.get('percent', 0)
                if disk_percent > 90:
                    issue_id = f'high_disk_usage_{device.replace(":", "").replace("\\", "_")}'
                    self.detected_issues[issue_id] = SystemIssue(
                        id=issue_id,
                        category='storage',
                        severity='critical' if disk_percent > 95 else 'warning',
                        title=f'High Disk Usage on {device}',
                        description=f'Disk {device} is {disk_percent:.1f}% full',
                        impact='May cause system instability, slow performance, and prevent game updates',
                        recommendations=[
                            'Clean up temporary files',
                            'Uninstall unused programs',
                            'Move files to external storage',
                            'Run disk cleanup utilities'
                        ],
                        detection_time=time.time(),
                        confidence=1.0,
                        auto_fixable=True,
                        affects_gaming=True,
                        safe_with_anticheat=True
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing storage performance: {e}")
    
    def _analyze_network_performance(self, system_info: Dict[str, Any]):
        """Analyze network performance and detect issues."""
        try:
            network_info = system_info.get('network', {})
            interfaces = network_info.get('interfaces', {})
            
            # Check for network errors
            for interface, stats in interfaces.items():
                error_rate = stats.get('errin', 0) + stats.get('errout', 0)
                drop_rate = stats.get('dropin', 0) + stats.get('dropout', 0)
                
                if error_rate > 100:
                    issue_id = f'network_errors_{interface.replace(" ", "_")}'
                    self.detected_issues[issue_id] = SystemIssue(
                        id=issue_id,
                        category='network',
                        severity='warning',
                        title=f'Network Errors on {interface}',
                        description=f'Interface {interface} has {error_rate} errors',
                        impact='May cause network instability, increased latency, and connection drops',
                        recommendations=[
                            'Update network drivers',
                            'Check network cable connections',
                            'Restart network adapter',
                            'Run network diagnostics'
                        ],
                        detection_time=time.time(),
                        confidence=0.8,
                        auto_fixable=True,
                        affects_gaming=True,
                        safe_with_anticheat=True
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing network performance: {e}")
    
    def _analyze_gpu_performance(self, system_info: Dict[str, Any]):
        """Analyze GPU performance (if available)."""
        try:
            # Try to get GPU information using different methods
            gpu_info = self._get_gpu_info()
            
            if gpu_info:
                # GPU temperature analysis
                gpu_temp = gpu_info.get('temperature', 0)
                if gpu_temp > 83:
                    issue_id = 'high_gpu_temperature'
                    self.detected_issues[issue_id] = SystemIssue(
                        id=issue_id,
                        category='gpu',
                        severity='critical' if gpu_temp > 90 else 'warning',
                        title='High GPU Temperature',
                        description=f'GPU temperature is {gpu_temp}°C',
                        impact='Risk of thermal throttling and reduced gaming performance',
                        recommendations=[
                            'Increase case ventilation',
                            'Clean GPU fans and heatsink',
                            'Reduce GPU overclock',
                            'Check thermal paste condition'
                        ],
                        detection_time=time.time(),
                        confidence=0.9,
                        auto_fixable=False,
                        affects_gaming=True,
                        safe_with_anticheat=True
                    )
                    
        except Exception as e:
            self.logger.debug(f"GPU analysis not available: {e}")
    
    def _get_gpu_info(self) -> Optional[Dict[str, Any]]:
        """Get GPU information using available methods."""
        try:
            # Try py3nvml for NVIDIA GPUs
            try:
                import py3nvml.py3nvml as nvml
                nvml.nvmlInit()
                handle = nvml.nvmlDeviceGetHandleByIndex(0)
                temp = nvml.nvmlDeviceGetTemperature(handle, nvml.NVML_TEMPERATURE_GPU)
                util = nvml.nvmlDeviceGetUtilizationRates(handle)
                
                return {
                    'temperature': temp,
                    'utilization': util.gpu,
                    'memory_utilization': util.memory
                }
            except:
                pass
            
            # Try GPUtil
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    return {
                        'temperature': gpu.temperature,
                        'utilization': gpu.load * 100,
                        'memory_utilization': gpu.memoryUtil * 100
                    }
            except:
                pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Could not get GPU info: {e}")
            return None
    
    def _analyze_system_configuration(self, system_info: Dict[str, Any]):
        """Analyze system configuration for optimization opportunities."""
        try:
            # Check power plan (Windows)
            if sys.platform == 'win32':
                try:
                    import subprocess
                    result = subprocess.run(['powercfg', '/getactivescheme'], 
                                          capture_output=True, text=True)
                    if 'High performance' not in result.stdout:
                        issue_id = 'power_plan_not_optimal'
                        self.detected_issues[issue_id] = SystemIssue(
                            id=issue_id,
                            category='system',
                            severity='info',
                            title='Power Plan Not Optimized for Gaming',
                            description='System is not using High Performance power plan',
                            impact='May reduce CPU and GPU performance during gaming',
                            recommendations=[
                                'Switch to High Performance power plan',
                                'Disable CPU power saving features',
                                'Set minimum processor state to 100%'
                            ],
                            detection_time=time.time(),
                            confidence=0.8,
                            auto_fixable=True,
                            affects_gaming=True,
                            safe_with_anticheat=True
                        )
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Error analyzing system configuration: {e}")
    
    def _analyze_gaming_performance(self, system_info: Dict[str, Any]):
        """Analyze gaming-specific performance aspects."""
        try:
            processes = system_info.get('processes', [])
            
            # Look for gaming-related processes
            gaming_processes = []
            for proc in processes:
                name = proc.get('name', '').lower()
                if any(game in name for game in ['steam', 'game', 'cs2', 'valorant', 'lol']):
                    gaming_processes.append(proc)
            
            # Check if any games are running with suboptimal settings
            for proc in gaming_processes:
                cpu_usage = proc.get('cpu_percent', 0)
                memory_usage = proc.get('memory_percent', 0)
                
                if cpu_usage > 90:
                    issue_id = f'game_high_cpu_{proc["pid"]}'
                    self.detected_issues[issue_id] = SystemIssue(
                        id=issue_id,
                        category='gaming',
                        severity='warning',
                        title=f'High CPU Usage in Game Process',
                        description=f'Game {proc["name"]} using {cpu_usage:.1f}% CPU',
                        impact='May cause frame drops and stuttering',
                        recommendations=[
                            'Reduce game graphics settings',
                            'Set game to high priority',
                            'Close background applications',
                            'Check for CPU bottlenecks'
                        ],
                        detection_time=time.time(),
                        confidence=0.8,
                        auto_fixable=True,
                        affects_gaming=True,
                        safe_with_anticheat=True
                    )
                    
        except Exception as e:
            self.logger.error(f"Error analyzing gaming performance: {e}")
    
    def _analyze_process_optimization(self, system_info: Dict[str, Any]):
        """Analyze processes for optimization opportunities."""
        try:
            processes = system_info.get('processes', [])
            
            # Check for unnecessary background processes
            unnecessary_processes = [
                'adobe', 'office', 'skype', 'discord', 'spotify', 'chrome',
                'firefox', 'teams', 'zoom', 'slack'
            ]
            
            running_unnecessary = []
            for proc in processes:
                name = proc.get('name', '').lower()
                if any(unnecessary in name for unnecessary in unnecessary_processes):
                    running_unnecessary.append(proc)
            
            if len(running_unnecessary) > 5:
                issue_id = 'too_many_background_processes'
                self.detected_issues[issue_id] = SystemIssue(
                    id=issue_id,
                    category='system',
                    severity='info',
                    title='Too Many Background Processes',
                    description=f'Found {len(running_unnecessary)} non-essential background processes',
                    impact='May consume system resources and reduce gaming performance',
                    recommendations=[
                        'Close unnecessary applications before gaming',
                        'Disable auto-start for non-essential programs',
                        'Use gaming mode or focus assistant',
                        'Consider game-specific process management'
                    ],
                    detection_time=time.time(),
                    confidence=0.6,
                    auto_fixable=True,
                    affects_gaming=True,
                    safe_with_anticheat=True
                )
                
        except Exception as e:
            self.logger.error(f"Error analyzing process optimization: {e}")
    
    def _generate_optimization_recommendations(self, detected_anticheats: List[str]):
        """Generate optimization recommendations based on detected issues."""
        try:
            # General system optimizations
            general_recommendations = [
                OptimizationRecommendation(
                    id='windows_visual_effects_optimization',
                    category='system',
                    title='Optimize Windows Visual Effects',
                    description='Disable unnecessary visual effects to improve performance',
                    expected_improvement='5-10% better system responsiveness',
                    risk_level='low',
                    requires_restart=False,
                    auto_applicable=True,
                    safe_with_anticheat=True,
                    priority=7
                ),
                OptimizationRecommendation(
                    id='power_plan_optimization',
                    category='system',
                    title='Optimize Power Plan Settings',
                    description='Configure power plan for maximum performance',
                    expected_improvement='10-15% better CPU performance',
                    risk_level='low',
                    requires_restart=False,
                    auto_applicable=True,
                    safe_with_anticheat=True,
                    priority=8
                ),
                OptimizationRecommendation(
                    id='network_tcp_optimization',
                    category='network',
                    title='Optimize Network TCP Settings',
                    description='Fine-tune TCP parameters for gaming',
                    expected_improvement='Reduced network latency and improved stability',
                    risk_level='low',
                    requires_restart=True,
                    auto_applicable=True,
                    safe_with_anticheat=True,
                    priority=6
                )
            ]
            
            # Add general recommendations
            for rec in general_recommendations:
                if self.anticheat_safety.is_optimization_safe(rec.id, detected_anticheats):
                    self.recommendations[rec.id] = rec
                    
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
    
    def _apply_learning_insights(self, system_info: Dict[str, Any]):
        """Apply machine learning insights from historical data."""
        try:
            if not self.learning_enabled or not self.learning_data:
                return
            
            # Analyze patterns in historical data
            cpu_usage_history = self.learning_data.get('cpu_usage', [])
            memory_usage_history = self.learning_data.get('memory_usage', [])
            
            # Predict potential issues based on trends
            if len(cpu_usage_history) > 10:
                recent_cpu_trend = cpu_usage_history[-5:]
                avg_recent = sum(recent_cpu_trend) / len(recent_cpu_trend)
                
                if avg_recent > 80:
                    issue_id = 'predicted_cpu_bottleneck'
                    self.detected_issues[issue_id] = SystemIssue(
                        id=issue_id,
                        category='cpu',
                        severity='info',
                        title='Predicted CPU Bottleneck',
                        description='AI predicts potential CPU bottleneck based on usage patterns',
                        impact='May experience performance degradation during peak usage',
                        recommendations=[
                            'Monitor CPU usage during gaming',
                            'Consider preemptive optimizations',
                            'Schedule maintenance tasks for low-usage periods'
                        ],
                        detection_time=time.time(),
                        confidence=0.6,
                        auto_fixable=True,
                        affects_gaming=True,
                        safe_with_anticheat=True
                    )
                    
        except Exception as e:
            self.logger.error(f"Error applying learning insights: {e}")
    
    def _update_learning_data(self, system_info: Dict[str, Any]):
        """Update learning data with current system information."""
        try:
            # Extract key metrics for learning
            cpu_usage = system_info.get('cpu', {}).get('usage_percent', 0)
            memory_usage = system_info.get('memory', {}).get('percent', 0)
            
            # Store data (keep last 1000 samples)
            self.learning_data['cpu_usage'].append(cpu_usage)
            self.learning_data['memory_usage'].append(memory_usage)
            
            # Trim old data
            for key in self.learning_data:
                if len(self.learning_data[key]) > 1000:
                    self.learning_data[key] = self.learning_data[key][-1000:]
            
            # Save learning data periodically
            if len(self.learning_data.get('cpu_usage', [])) % 50 == 0:
                self._save_learning_data()
                
        except Exception as e:
            self.logger.error(f"Error updating learning data: {e}")
    
    def _save_learning_data(self):
        """Save learning data to disk."""
        try:
            with open(self.learning_file, 'wb') as f:
                pickle.dump(dict(self.learning_data), f)
            self.logger.debug("Learning data saved")
        except Exception as e:
            self.logger.error(f"Error saving learning data: {e}")
    
    def _load_learning_data(self):
        """Load learning data from disk."""
        try:
            if self.learning_file.exists():
                with open(self.learning_file, 'rb') as f:
                    data = pickle.load(f)
                    self.learning_data.update(data)
                self.logger.info(f"Loaded learning data with {len(self.learning_data)} categories")
        except Exception as e:
            self.logger.debug(f"Could not load learning data: {e}")
    
    def _create_analysis_summary(self) -> Dict[str, Any]:
        """Create a summary of the analysis results."""
        try:
            critical_issues = sum(1 for issue in self.detected_issues.values() if issue.severity == 'critical')
            warning_issues = sum(1 for issue in self.detected_issues.values() if issue.severity == 'warning')
            info_issues = sum(1 for issue in self.detected_issues.values() if issue.severity == 'info')
            
            gaming_affecting = sum(1 for issue in self.detected_issues.values() if issue.affects_gaming)
            auto_fixable = sum(1 for issue in self.detected_issues.values() if issue.auto_fixable)
            
            high_priority_recs = sum(1 for rec in self.recommendations.values() if rec.priority >= 8)
            auto_applicable_recs = sum(1 for rec in self.recommendations.values() if rec.auto_applicable)
            
            return {
                'total_issues': len(self.detected_issues),
                'critical_issues': critical_issues,
                'warning_issues': warning_issues,
                'info_issues': info_issues,
                'gaming_affecting_issues': gaming_affecting,
                'auto_fixable_issues': auto_fixable,
                'total_recommendations': len(self.recommendations),
                'high_priority_recommendations': high_priority_recs,
                'auto_applicable_recommendations': auto_applicable_recs,
                'overall_health_score': self._calculate_health_score(),
                'performance_impact_level': self._assess_performance_impact()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating analysis summary: {e}")
            return {}
    
    def _calculate_health_score(self) -> int:
        """Calculate overall system health score (0-100)."""
        try:
            base_score = 100
            
            # Deduct points for issues
            for issue in self.detected_issues.values():
                if issue.severity == 'critical':
                    base_score -= 15
                elif issue.severity == 'warning':
                    base_score -= 8
                elif issue.severity == 'info':
                    base_score -= 3
            
            return max(0, base_score)
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 50
    
    def _assess_performance_impact(self) -> str:
        """Assess overall performance impact level."""
        try:
            critical_count = sum(1 for issue in self.detected_issues.values() if issue.severity == 'critical')
            warning_count = sum(1 for issue in self.detected_issues.values() if issue.severity == 'warning')
            gaming_affecting = sum(1 for issue in self.detected_issues.values() if issue.affects_gaming)
            
            if critical_count > 0 or gaming_affecting > 3:
                return 'high'
            elif warning_count > 2 or gaming_affecting > 1:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            self.logger.error(f"Error assessing performance impact: {e}")
            return 'unknown'
    
    def _get_current_analysis_summary(self) -> Dict[str, Any]:
        """Get current analysis summary without running new analysis."""
        if self.analysis_history:
            return self.analysis_history[-1]
        return {}
    
    def get_issues_for_notification(self) -> List[Dict[str, Any]]:
        """Get issues that should trigger notifications."""
        try:
            notification_worthy = []
            
            for issue in self.detected_issues.values():
                # Only notify for critical and warning issues that affect gaming
                if issue.severity in ['critical', 'warning'] and issue.affects_gaming:
                    notification_worthy.append({
                        'id': issue.id,
                        'title': issue.title,
                        'description': issue.description,
                        'severity': issue.severity,
                        'impact': issue.impact,
                        'auto_fixable': issue.auto_fixable
                    })
            
            return notification_worthy
            
        except Exception as e:
            self.logger.error(f"Error getting issues for notification: {e}")
            return []