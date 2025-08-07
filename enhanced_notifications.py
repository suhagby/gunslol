#!/usr/bin/env python3
"""
SUHA FPS+ Enhanced Notification System
Advanced notification system with Discord integration and smart alerts.
"""

import os
import sys
import time
import json
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from collections import deque

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

@dataclass
class Notification:
    """Notification data structure."""
    id: str
    title: str
    message: str
    severity: str  # 'info', 'warning', 'error', 'critical'
    category: str  # 'performance', 'system', 'game', 'ai'
    timestamp: datetime
    data: Dict[str, Any] = None
    acknowledged: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity,
            'category': self.category,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data or {},
            'acknowledged': self.acknowledged
        }

class NotificationChannel:
    """Base class for notification channels."""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification through this channel."""
        raise NotImplementedError
    
    def is_enabled(self) -> bool:
        """Check if channel is enabled."""
        return self.enabled
    
    def enable(self):
        """Enable the channel."""
        self.enabled = True
    
    def disable(self):
        """Disable the channel."""
        self.enabled = False

class ConsoleNotificationChannel(NotificationChannel):
    """Console/terminal notification channel."""
    
    def __init__(self):
        super().__init__("Console")
        
        # Color codes for different severities
        self.colors = {
            'info': '\033[94m',      # Blue
            'warning': '\033[93m',   # Yellow
            'error': '\033[91m',     # Red
            'critical': '\033[95m',  # Magenta
            'reset': '\033[0m'       # Reset
        }
        
        # Icons for different categories
        self.icons = {
            'performance': '⚡',
            'system': '🖥️',
            'game': '🎮',
            'ai': '🤖',
            'discord': '🎯',
            'network': '🌐',
            'default': '📢'
        }
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification to console."""
        try:
            color = self.colors.get(notification.severity, '')
            icon = self.icons.get(notification.category, self.icons['default'])
            reset = self.colors['reset']
            
            timestamp = notification.timestamp.strftime('%H:%M:%S')
            
            print(f"{color}[{timestamp}] {icon} {notification.title}{reset}")
            print(f"{color}{notification.message}{reset}")
            
            if notification.data:
                print(f"{color}Data: {json.dumps(notification.data, indent=2)}{reset}")
            
            print()  # Empty line for readability
            
            return True
            
        except Exception as e:
            self.logger.error(f"Console notification error: {e}")
            return False

class FileNotificationChannel(NotificationChannel):
    """File-based notification channel."""
    
    def __init__(self, log_file: Path = None):
        super().__init__("File")
        self.log_file = log_file or Path("logs") / f"notifications_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(exist_ok=True)
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification to file."""
        try:
            log_entry = {
                'timestamp': notification.timestamp.isoformat(),
                'severity': notification.severity,
                'category': notification.category,
                'title': notification.title,
                'message': notification.message,
                'data': notification.data or {}
            }
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            return True
            
        except Exception as e:
            self.logger.error(f"File notification error: {e}")
            return False

class DiscordNotificationChannel(NotificationChannel):
    """Discord notification channel."""
    
    def __init__(self, discord_bot_manager=None):
        super().__init__("Discord")
        self.bot_manager = discord_bot_manager
        
        # Emoji mapping for different severities
        self.severity_emojis = {
            'info': '💡',
            'warning': '⚠️',
            'error': '❌',
            'critical': '🔥'
        }
        
        # Color mapping for Discord embeds
        self.severity_colors = {
            'info': 0x00aaff,      # Blue
            'warning': 0xffaa00,   # Orange
            'error': 0xff4444,     # Red
            'critical': 0xff0000   # Bright Red
        }
    
    async def send_notification(self, notification: Notification) -> bool:
        """Send notification to Discord."""
        try:
            if not self.bot_manager or not hasattr(self.bot_manager, 'bot_instance'):
                return False
            
            bot = self.bot_manager.bot_instance
            if not bot:
                return False
            
            # Format notification for Discord
            emoji = self.severity_emojis.get(notification.severity, '📢')
            color = self.severity_colors.get(notification.severity, 0x00aaff)
            
            title = f"{emoji} {notification.title}"
            description = notification.message
            
            # Add data if present
            if notification.data:
                description += f"\n\n**Details:**\n```json\n{json.dumps(notification.data, indent=2)}\n```"
            
            # Send via Discord bot
            await bot.send_notification(title, description, color)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Discord notification error: {e}")
            return False

class EnhancedNotificationManager:
    """Enhanced notification manager for SUHA FPS+."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.EnhancedNotificationManager")
        
        # Notification storage
        self.notifications = deque(maxlen=1000)  # Keep last 1000 notifications
        self.notification_history = {}  # Categorized history
        
        # Notification channels
        self.channels: Dict[str, NotificationChannel] = {}
        self.default_channels = ['Console', 'File']
        
        # Configuration
        self.config = self._load_config()
        
        # Rate limiting
        self.rate_limits = {}  # Track notification frequency
        self.rate_limit_window = 300  # 5 minutes
        self.max_notifications_per_window = 10
        
        # Smart filtering
        self.smart_filters = {
            'duplicate_suppression': True,
            'importance_threshold': 0.5,
            'quiet_hours': None  # Can be set to (start_hour, end_hour)
        }
        
        # Initialize default channels
        self._initialize_channels()
        
        # Statistics
        self.stats = {
            'total_sent': 0,
            'sent_by_severity': {'info': 0, 'warning': 0, 'error': 0, 'critical': 0},
            'sent_by_category': {},
            'rate_limited': 0,
            'filtered': 0
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load notification configuration."""
        config_file = Path("notification_config.json")
        
        default_config = {
            'enabled_channels': ['Console', 'File'],
            'severity_filters': {
                'Console': ['info', 'warning', 'error', 'critical'],
                'File': ['warning', 'error', 'critical'],
                'Discord': ['warning', 'error', 'critical']
            },
            'category_filters': {
                'performance': True,
                'system': True,
                'game': True,
                'ai': True,
                'discord': True,
                'network': True
            },
            'rate_limiting': {
                'enabled': True,
                'window_seconds': 300,
                'max_per_window': 10
            },
            'smart_features': {
                'duplicate_suppression': True,
                'importance_scoring': True,
                'quiet_hours': None
            }
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                return {**default_config, **loaded_config}
            except Exception as e:
                self.logger.error(f"Failed to load notification config: {e}")
        
        return default_config
    
    def _initialize_channels(self):
        """Initialize notification channels."""
        # Always initialize console and file channels
        self.channels['Console'] = ConsoleNotificationChannel()
        self.channels['File'] = FileNotificationChannel()
        
        # Discord channel will be added when bot is available
        self.logger.info("Notification channels initialized")
    
    def add_discord_channel(self, discord_bot_manager):
        """Add Discord notification channel."""
        try:
            self.channels['Discord'] = DiscordNotificationChannel(discord_bot_manager)
            self.logger.info("Discord notification channel added")
        except Exception as e:
            self.logger.error(f"Failed to add Discord channel: {e}")
    
    def remove_channel(self, channel_name: str):
        """Remove a notification channel."""
        if channel_name in self.channels:
            del self.channels[channel_name]
            self.logger.info(f"Removed notification channel: {channel_name}")
    
    async def send_notification(
        self, 
        title: str, 
        message: str, 
        severity: str = 'info',
        category: str = 'system',
        data: Dict[str, Any] = None
    ) -> bool:
        """Send a notification through all enabled channels."""
        try:
            # Create notification object
            notification = Notification(
                id=f"{int(time.time())}_{len(self.notifications)}",
                title=title,
                message=message,
                severity=severity,
                category=category,
                timestamp=datetime.now(),
                data=data
            )
            
            # Apply smart filtering
            if not self._should_send_notification(notification):
                self.stats['filtered'] += 1
                return False
            
            # Check rate limiting
            if not self._check_rate_limit(notification):
                self.stats['rate_limited'] += 1
                self.logger.warning(f"Rate limited notification: {title}")
                return False
            
            # Store notification
            self.notifications.append(notification)
            self._update_history(notification)
            
            # Send through enabled channels
            success_count = 0
            enabled_channels = self.config.get('enabled_channels', self.default_channels)
            
            for channel_name in enabled_channels:
                channel = self.channels.get(channel_name)
                if channel and channel.is_enabled():
                    # Check severity filter for this channel
                    severity_filters = self.config.get('severity_filters', {})
                    allowed_severities = severity_filters.get(channel_name, ['info', 'warning', 'error', 'critical'])
                    
                    if notification.severity in allowed_severities:
                        try:
                            success = await channel.send_notification(notification)
                            if success:
                                success_count += 1
                        except Exception as e:
                            self.logger.error(f"Failed to send notification via {channel_name}: {e}")
            
            # Update statistics
            self.stats['total_sent'] += 1
            self.stats['sent_by_severity'][severity] = self.stats['sent_by_severity'].get(severity, 0) + 1
            self.stats['sent_by_category'][category] = self.stats['sent_by_category'].get(category, 0) + 1
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"Notification sending error: {e}")
            return False
    
    def _should_send_notification(self, notification: Notification) -> bool:
        """Apply smart filtering to determine if notification should be sent."""
        
        # Category filter
        category_filters = self.config.get('category_filters', {})
        if not category_filters.get(notification.category, True):
            return False
        
        # Duplicate suppression
        if self.smart_filters.get('duplicate_suppression', True):
            # Check for similar notifications in the last 5 minutes
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            recent_notifications = [n for n in self.notifications 
                                 if n.timestamp > five_minutes_ago and n.title == notification.title]
            
            if len(recent_notifications) >= 3:  # Too many similar notifications
                return False
        
        # Quiet hours
        quiet_hours = self.smart_filters.get('quiet_hours')
        if quiet_hours:
            current_hour = datetime.now().hour
            start_hour, end_hour = quiet_hours
            
            if start_hour <= current_hour <= end_hour:
                # Only allow critical notifications during quiet hours
                return notification.severity == 'critical'
        
        return True
    
    def _check_rate_limit(self, notification: Notification) -> bool:
        """Check if notification passes rate limiting."""
        if not self.config.get('rate_limiting', {}).get('enabled', True):
            return True
        
        current_time = time.time()
        category = notification.category
        
        # Initialize rate limit tracking for category
        if category not in self.rate_limits:
            self.rate_limits[category] = []
        
        # Clean old timestamps
        window_seconds = self.config.get('rate_limiting', {}).get('window_seconds', 300)
        cutoff_time = current_time - window_seconds
        self.rate_limits[category] = [t for t in self.rate_limits[category] if t > cutoff_time]
        
        # Check limit
        max_per_window = self.config.get('rate_limiting', {}).get('max_per_window', 10)
        if len(self.rate_limits[category]) >= max_per_window:
            return False
        
        # Add current timestamp
        self.rate_limits[category].append(current_time)
        return True
    
    def _update_history(self, notification: Notification):
        """Update notification history."""
        category = notification.category
        
        if category not in self.notification_history:
            self.notification_history[category] = deque(maxlen=100)
        
        self.notification_history[category].append(notification.to_dict())
    
    # Convenience methods for different severity levels
    async def info(self, title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
        """Send info notification."""
        return await self.send_notification(title, message, 'info', category, data)
    
    async def warning(self, title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
        """Send warning notification."""
        return await self.send_notification(title, message, 'warning', category, data)
    
    async def error(self, title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
        """Send error notification."""
        return await self.send_notification(title, message, 'error', category, data)
    
    async def critical(self, title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
        """Send critical notification."""
        return await self.send_notification(title, message, 'critical', category, data)
    
    # Performance-specific notifications
    async def performance_alert(self, metric: str, value: float, threshold: float, severity: str = 'warning'):
        """Send performance-related alert."""
        title = f"Performance Alert: {metric.upper()}"
        message = f"{metric} is at {value:.1f}{'%' if metric in ['cpu', 'memory'] else ''} (threshold: {threshold:.1f})"
        
        data = {
            'metric': metric,
            'current_value': value,
            'threshold': threshold,
            'percentage_over': ((value - threshold) / threshold) * 100
        }
        
        return await self.send_notification(title, message, severity, 'performance', data)
    
    async def fps_drop_alert(self, current_fps: int, target_fps: int, game_name: str = None):
        """Send FPS drop alert."""
        title = "🎮 FPS Drop Detected"
        message = f"FPS dropped to {current_fps} (target: {target_fps})"
        
        if game_name:
            message += f" in {game_name}"
        
        data = {
            'current_fps': current_fps,
            'target_fps': target_fps,
            'game': game_name,
            'fps_drop_percentage': ((target_fps - current_fps) / target_fps) * 100
        }
        
        severity = 'critical' if current_fps < target_fps * 0.5 else 'warning'
        return await self.send_notification(title, message, severity, 'game', data)
    
    async def ai_recommendation(self, recommendation: str, confidence: float, impact: str):
        """Send AI recommendation notification."""
        title = "🤖 AI Optimization Recommendation"
        message = f"{recommendation} (Confidence: {confidence:.1%}, Expected Impact: {impact})"
        
        data = {
            'recommendation': recommendation,
            'confidence': confidence,
            'expected_impact': impact
        }
        
        return await self.send_notification(title, message, 'info', 'ai', data)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics."""
        return {
            'total_notifications': len(self.notifications),
            'statistics': self.stats.copy(),
            'active_channels': list(self.channels.keys()),
            'recent_notifications': len([n for n in self.notifications 
                                      if (datetime.now() - n.timestamp).seconds < 3600])  # Last hour
        }
    
    def get_recent_notifications(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notifications."""
        recent = list(self.notifications)[-limit:]
        return [n.to_dict() for n in reversed(recent)]
    
    def clear_notifications(self):
        """Clear all notifications."""
        self.notifications.clear()
        self.notification_history.clear()
        self.logger.info("All notifications cleared")

# Global notification manager instance
notification_manager = None

def get_notification_manager() -> EnhancedNotificationManager:
    """Get global notification manager instance."""
    global notification_manager
    if notification_manager is None:
        notification_manager = EnhancedNotificationManager()
    return notification_manager

# Convenience functions for easy use
async def notify_info(title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
    """Send info notification."""
    manager = get_notification_manager()
    return await manager.info(title, message, category, data)

async def notify_warning(title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
    """Send warning notification."""
    manager = get_notification_manager()
    return await manager.warning(title, message, category, data)

async def notify_error(title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
    """Send error notification."""
    manager = get_notification_manager()
    return await manager.error(title, message, category, data)

async def notify_critical(title: str, message: str, category: str = 'system', data: Dict[str, Any] = None):
    """Send critical notification."""
    manager = get_notification_manager()
    return await manager.critical(title, message, category, data)

# Test function
async def test_notifications():
    """Test the notification system."""
    manager = get_notification_manager()
    
    # Test different types of notifications
    await manager.info("System Started", "SUHA FPS+ has been initialized successfully")
    await manager.performance_alert("cpu", 85.5, 80.0, "warning")
    await manager.fps_drop_alert(45, 60, "Cyberpunk 2077")
    await manager.ai_recommendation("Reduce background processes", 0.85, "15-20% performance improvement")
    
    print("Test notifications sent!")
    print("Statistics:", manager.get_statistics())

if __name__ == "__main__":
    # Test the notification system
    asyncio.run(test_notifications())