"""
Notification system for the gaming performance monitor.
Handles desktop notifications, alerts, and user feedback for performance issues.
"""

import logging
import time
import threading
from typing import Dict, Any, List, Optional
from collections import deque
import json

try:
    import plyer
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

try:
    import win10toast
    HAS_WIN10TOAST = True
except ImportError:
    HAS_WIN10TOAST = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

class NotificationManager:
    """Manages notifications and alerts for the gaming performance monitor."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.notifications_enabled = True
        self.sound_enabled = False
        self.email_enabled = False
        
        # Notification history
        self.notification_history = deque(maxlen=100)
        
        # Rate limiting to prevent spam
        self.last_notification_times = {}
        self.min_notification_interval = 30  # seconds
        
        # Severity levels and their properties
        self.severity_config = {
            'critical': {
                'color': '#ff0000',
                'sound': 'SystemExclamation',
                'priority': 3,
                'min_interval': 10,  # Critical alerts more frequent
                'title_prefix': '🔴 CRITICAL:'
            },
            'warning': {
                'color': '#ffaa00',
                'sound': 'SystemAsterisk',
                'priority': 2,
                'min_interval': 30,
                'title_prefix': '🟠 WARNING:'
            },
            'info': {
                'color': '#0099ff',
                'sound': None,
                'priority': 1,
                'min_interval': 60,
                'title_prefix': '🔵 INFO:'
            }
        }
        
        # Performance issue descriptions
        self.issue_descriptions = {
            # System issues
            'high_cpu_temp': 'CPU temperature is critically high',
            'high_gpu_temp': 'GPU temperature is critically high',
            'high_memory': 'Memory usage is critically high',
            'low_fps': 'FPS has dropped below target threshold',
            'very_low_fps': 'FPS is critically low',
            'frame_stuttering': 'Significant frame time variance detected',
            'frequent_stuttering': 'Frequent frame stuttering detected',
            'high_input_latency': 'Input latency is higher than optimal',
            'game_cpu_bottleneck': 'Game process is CPU bottlenecked',
            
            # Network issues
            'high_ping': 'Network latency is too high for optimal gaming',
            'moderate_ping': 'Network latency is above optimal range',
            'high_jitter': 'Network jitter is causing instability',
            'packet_loss': 'Network packet loss detected',
            'network_errors': 'Network adapter errors detected',
            'low_bandwidth': 'Available bandwidth is below recommended',
            'unstable_connection': 'Network connection is unstable',
            
            # Hardware issues
            'cpu_stress': 'CPU is under high stress',
            'memory_stress': 'System memory is under stress',
            'gpu_stress': 'GPU is under high stress',
            'cpu_temp_stress': 'CPU temperature stress detected',
            'gpu_temp_stress': 'GPU temperature stress detected',
            'overall_stress': 'System is under overall performance stress'
        }
        
        # Notification methods available
        self.notification_methods = []
        self._detect_notification_methods()
        
        self.logger.info(f"NotificationManager initialized with methods: {self.notification_methods}")
    
    def _detect_notification_methods(self):
        """Detect available notification methods."""
        try:
            # Windows 10 Toast notifications
            if HAS_WIN10TOAST:
                self.notification_methods.append('win10toast')
                self.logger.info("Windows 10 Toast notifications available")
            
            # Cross-platform notifications
            if HAS_PLYER:
                self.notification_methods.append('plyer')
                self.logger.info("Plyer notifications available")
            
            # Sound notifications
            if HAS_WINSOUND:
                self.notification_methods.append('sound')
                self.logger.info("Windows sound notifications available")
            
            # Fallback to system notification
            if not self.notification_methods:
                self.notification_methods.append('console')
                self.logger.warning("No GUI notification methods available, using console")
                
        except Exception as e:
            self.logger.error(f"Error detecting notification methods: {e}")
    
    def notify_issues(self, issues: List[str], severity: str = 'warning'):
        """Send notifications for detected performance issues."""
        try:
            if not self.notifications_enabled or not issues:
                return
            
            # Filter issues by rate limiting
            filtered_issues = self._filter_rate_limited_issues(issues, severity)
            if not filtered_issues:
                return
            
            # Create notification content
            title, message = self._create_issue_notification_content(filtered_issues, severity)
            
            # Send notification
            self._send_notification(title, message, severity)
            
            # Log the notification
            self._log_notification(title, message, severity, filtered_issues)
            
        except Exception as e:
            self.logger.error(f"Error sending issue notifications: {e}")
    
    def notify_optimization_applied(self, optimization_type: str, results: Dict[str, Any]):
        """Notify when optimizations are applied."""
        try:
            if not self.notifications_enabled:
                return
            
            success_count = sum(1 for v in results.values() if v is True)
            total_count = len(results)
            
            title = f"🔧 Optimization Applied: {optimization_type.title()}"
            message = f"Applied {success_count}/{total_count} optimizations successfully"
            
            if success_count == total_count:
                severity = 'info'
            elif success_count > 0:
                severity = 'warning'
                message += f"\n{total_count - success_count} optimizations failed"
            else:
                severity = 'warning'
                message = f"All {total_count} optimizations failed"
            
            self._send_notification(title, message, severity)
            self._log_notification(title, message, severity, [optimization_type])
            
        except Exception as e:
            self.logger.error(f"Error sending optimization notification: {e}")
    
    def notify_system_status(self, status: str, details: str = ""):
        """Notify about system status changes."""
        try:
            if not self.notifications_enabled:
                return
            
            status_messages = {
                'startup': ('🚀 Gaming Monitor Started', 'Performance monitoring active'),
                'shutdown': ('🛑 Gaming Monitor Stopped', 'Performance monitoring stopped'),
                'game_detected': ('🎮 Game Detected', f'Started monitoring: {details}'),
                'game_ended': ('🏁 Game Ended', f'Stopped monitoring: {details}'),
                'optimization_needed': ('⚠️ Optimization Recommended', details),
                'system_stable': ('✅ System Stable', 'All metrics within normal ranges'),
                'admin_required': ('🔒 Admin Rights Required', 'Some optimizations require administrator privileges')
            }
            
            if status in status_messages:
                title, message = status_messages[status]
                if details and message != details:
                    message = f"{message}\n{details}"
                
                severity = 'info'
                if status in ['optimization_needed', 'admin_required']:
                    severity = 'warning'
                
                self._send_notification(title, message, severity)
                self._log_notification(title, message, severity, [status])
            
        except Exception as e:
            self.logger.error(f"Error sending system status notification: {e}")
    
    def notify_performance_milestone(self, milestone_type: str, value: float, target: float):
        """Notify when performance milestones are reached."""
        try:
            if not self.notifications_enabled:
                return
            
            milestone_messages = {
                'fps_target_reached': ('🎯 FPS Target Reached', f'Achieved {value:.1f} FPS (target: {target:.1f})'),
                'fps_record': ('🏆 FPS Record', f'New FPS record: {value:.1f} FPS'),
                'low_latency_achieved': ('⚡ Low Latency Achieved', f'Input latency: {value:.1f}ms (target: <{target:.1f}ms)'),
                'temperature_normalized': ('🌡️ Temperature Normalized', f'Temperature back to {value:.1f}°C'),
                'network_optimized': ('🌐 Network Optimized', f'Ping reduced to {value:.1f}ms')
            }
            
            if milestone_type in milestone_messages:
                title, message = milestone_messages[milestone_type]
                self._send_notification(title, message, 'info')
                self._log_notification(title, message, 'info', [milestone_type])
            
        except Exception as e:
            self.logger.error(f"Error sending performance milestone notification: {e}")
    
    def _filter_rate_limited_issues(self, issues: List[str], severity: str) -> List[str]:
        """Filter issues based on rate limiting."""
        try:
            current_time = time.time()
            severity_config = self.severity_config.get(severity, self.severity_config['info'])
            min_interval = severity_config['min_interval']
            
            filtered_issues = []
            
            for issue in issues:
                last_time = self.last_notification_times.get(issue, 0)
                
                if current_time - last_time >= min_interval:
                    filtered_issues.append(issue)
                    self.last_notification_times[issue] = current_time
            
            return filtered_issues
            
        except Exception as e:
            self.logger.error(f"Error filtering rate limited issues: {e}")
            return issues
    
    def _create_issue_notification_content(self, issues: List[str], severity: str) -> tuple:
        """Create notification title and message for issues."""
        try:
            severity_config = self.severity_config.get(severity, self.severity_config['warning'])
            
            if len(issues) == 1:
                issue = issues[0]
                title = f"{severity_config['title_prefix']} Performance Issue"
                message = self.issue_descriptions.get(issue, f"Issue detected: {issue}")
            else:
                title = f"{severity_config['title_prefix']} Multiple Issues Detected"
                issue_list = []
                for issue in issues[:3]:  # Show max 3 issues
                    description = self.issue_descriptions.get(issue, issue)
                    issue_list.append(f"• {description}")
                
                message = "\n".join(issue_list)
                if len(issues) > 3:
                    message += f"\n• And {len(issues) - 3} more issues..."
            
            return title, message
            
        except Exception as e:
            self.logger.error(f"Error creating notification content: {e}")
            return "Performance Issue", "Issues detected in gaming performance"
    
    def _send_notification(self, title: str, message: str, severity: str):
        """Send notification using available methods."""
        try:
            severity_config = self.severity_config.get(severity, self.severity_config['info'])
            
            # Try Windows 10 Toast first
            if 'win10toast' in self.notification_methods:
                self._send_win10_toast(title, message, severity_config)
            
            # Try cross-platform notification
            elif 'plyer' in self.notification_methods:
                self._send_plyer_notification(title, message, severity_config)
            
            # Fallback to console
            else:
                self._send_console_notification(title, message, severity)
            
            # Play sound if enabled and available
            if self.sound_enabled and 'sound' in self.notification_methods:
                self._play_notification_sound(severity_config)
                
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
    
    def _send_win10_toast(self, title: str, message: str, severity_config: Dict):
        """Send Windows 10 toast notification."""
        try:
            import win10toast
            toaster = win10toast.ToastNotifier()
            
            # Truncate message if too long
            if len(message) > 200:
                message = message[:197] + "..."
            
            duration = 10 if severity_config['priority'] >= 2 else 5
            
            toaster.show_toast(
                title=title,
                msg=message,
                duration=duration,
                icon_path=None,  # Use default icon
                threaded=True
            )
            
            self.logger.debug(f"Sent Windows 10 toast: {title}")
            
        except Exception as e:
            self.logger.error(f"Windows 10 toast notification failed: {e}")
    
    def _send_plyer_notification(self, title: str, message: str, severity_config: Dict):
        """Send cross-platform notification using plyer."""
        try:
            from plyer import notification
            
            # Truncate message if too long
            if len(message) > 200:
                message = message[:197] + "..."
            
            timeout = 10 if severity_config['priority'] >= 2 else 5
            
            notification.notify(
                title=title,
                message=message,
                app_name="Gaming Performance Monitor",
                timeout=timeout,
                toast=True
            )
            
            self.logger.debug(f"Sent plyer notification: {title}")
            
        except Exception as e:
            self.logger.error(f"Plyer notification failed: {e}")
    
    def _send_console_notification(self, title: str, message: str, severity: str):
        """Send console notification as fallback."""
        try:
            separator = "=" * 50
            print(f"\n{separator}")
            print(f"NOTIFICATION [{severity.upper()}]: {title}")
            print(f"{separator}")
            print(message)
            print(f"{separator}\n")
            
            self.logger.info(f"Console notification: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"Console notification failed: {e}")
    
    def _play_notification_sound(self, severity_config: Dict):
        """Play notification sound."""
        try:
            if not HAS_WINSOUND or not severity_config.get('sound'):
                return
            
            sound_name = severity_config['sound']
            
            # Play system sound
            if hasattr(winsound, f'MB_{sound_name.upper()}'):
                sound_flag = getattr(winsound, f'MB_{sound_name.upper()}')
                winsound.MessageBeep(sound_flag)
            else:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                
        except Exception as e:
            self.logger.debug(f"Sound notification failed: {e}")
    
    def _log_notification(self, title: str, message: str, severity: str, context: List[str]):
        """Log notification to history."""
        try:
            notification_entry = {
                'timestamp': time.time(),
                'title': title,
                'message': message,
                'severity': severity,
                'context': context
            }
            
            self.notification_history.append(notification_entry)
            
            # Log to logger based on severity
            if severity == 'critical':
                self.logger.error(f"CRITICAL NOTIFICATION: {title} - {message}")
            elif severity == 'warning':
                self.logger.warning(f"WARNING NOTIFICATION: {title} - {message}")
            else:
                self.logger.info(f"INFO NOTIFICATION: {title} - {message}")
                
        except Exception as e:
            self.logger.error(f"Error logging notification: {e}")
    
    def get_notification_history(self, limit: int = 20) -> List[Dict]:
        """Get recent notification history."""
        try:
            recent_notifications = list(self.notification_history)[-limit:]
            
            # Convert timestamps to readable format
            for notification in recent_notifications:
                notification['time_str'] = time.strftime(
                    '%Y-%m-%d %H:%M:%S', 
                    time.localtime(notification['timestamp'])
                )
            
            return recent_notifications
            
        except Exception as e:
            self.logger.error(f"Error getting notification history: {e}")
            return []
    
    def clear_notification_history(self):
        """Clear notification history."""
        try:
            self.notification_history.clear()
            self.last_notification_times.clear()
            self.logger.info("Notification history cleared")
            
        except Exception as e:
            self.logger.error(f"Error clearing notification history: {e}")
    
    def configure_notifications(self, config: Dict[str, Any]):
        """Configure notification settings."""
        try:
            if 'enabled' in config:
                self.notifications_enabled = config['enabled']
            
            if 'sound_enabled' in config:
                self.sound_enabled = config['sound_enabled']
            
            if 'email_enabled' in config:
                self.email_enabled = config['email_enabled']
            
            if 'min_interval' in config:
                self.min_notification_interval = config['min_interval']
            
            if 'severity_config' in config:
                self.severity_config.update(config['severity_config'])
            
            self.logger.info(f"Notification configuration updated: {config}")
            
        except Exception as e:
            self.logger.error(f"Error configuring notifications: {e}")
    
    def test_notifications(self):
        """Test all notification methods."""
        try:
            test_notifications = [
                ("Test Info", "This is an info notification test", "info"),
                ("Test Warning", "This is a warning notification test", "warning"),
                ("Test Critical", "This is a critical notification test", "critical")
            ]
            
            for title, message, severity in test_notifications:
                self._send_notification(title, message, severity)
                time.sleep(2)  # Brief delay between tests
            
            self.logger.info("Notification test completed")
            
        except Exception as e:
            self.logger.error(f"Notification test failed: {e}")
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        try:
            if not self.notification_history:
                return {
                    'total_notifications': 0,
                    'by_severity': {},
                    'recent_count': 0,
                    'rate_limited_count': 0
                }
            
            # Count by severity
            severity_counts = {}
            recent_count = 0
            current_time = time.time()
            
            for notification in self.notification_history:
                severity = notification['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                # Count recent notifications (last hour)
                if current_time - notification['timestamp'] <= 3600:
                    recent_count += 1
            
            return {
                'total_notifications': len(self.notification_history),
                'by_severity': severity_counts,
                'recent_count': recent_count,
                'rate_limited_count': len(self.last_notification_times),
                'methods_available': self.notification_methods,
                'settings': {
                    'enabled': self.notifications_enabled,
                    'sound_enabled': self.sound_enabled,
                    'email_enabled': self.email_enabled
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting notification stats: {e}")
            return {}
    
    def shutdown(self):
        """Shutdown notification system."""
        try:
            # Send shutdown notification if enabled
            if self.notifications_enabled:
                self.notify_system_status('shutdown')
                
                # Brief delay to allow notification to be sent
                time.sleep(1)
            
            # Clear rate limiting
            self.last_notification_times.clear()
            
            self.logger.info("Notification system shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during notification system shutdown: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.shutdown()
        except:
            pass