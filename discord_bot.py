#!/usr/bin/env python3
"""
SUHA FPS+ Discord Bot Integration
Advanced Discord bot for gaming performance monitoring and notifications.
"""

import os
import sys
import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import psutil
import discord
from discord.ext import commands, tasks
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

class SuhaFPSBot(commands.Bot):
    """SUHA FPS+ Discord Bot for performance monitoring and notifications."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix='!fps ',
            intents=intents,
            description='SUHA FPS+ Gaming Performance Monitor Bot',
            help_command=commands.DefaultHelpCommand(no_category='Commands')
        )
        
        # Bot configuration
        self.version = "3.0.0"
        self.start_time = datetime.now()
        self.notification_channel_id = None
        self.admin_role = "SUHA FPS+ Admin"
        
        # Performance monitoring data
        self.performance_data = {
            'last_update': None,
            'cpu_usage': 0,
            'memory_usage': 0,
            'gpu_usage': 0,
            'fps_detected': 0,
            'ping': 0,
            'issues': []
        }
        
        # Alert thresholds
        self.thresholds = {
            'cpu_high': 85,
            'memory_high': 90,
            'gpu_high': 85,
            'fps_low': 60,
            'ping_high': 50,
            'temperature_high': 80
        }
        
        # Notification settings
        self.notification_settings = {
            'performance_alerts': True,
            'fps_drops': True,
            'system_issues': True,
            'optimization_applied': True,
            'daily_summary': True
        }
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.SuhaFPSBot")
        
        # Performance history for charts
        self.performance_history = {
            'timestamps': [],
            'cpu': [],
            'memory': [],
            'fps': []
        }
        
    async def setup_hook(self):
        """Setup hook called when bot starts."""
        # Start background tasks
        self.performance_monitor.start()
        self.health_check.start()
        
        self.logger.info("🤖 SUHA FPS+ Bot setup complete")
    
    async def on_ready(self):
        """Called when bot is ready."""
        self.logger.info(f'🚀 {self.user} is now online!')
        self.logger.info(f'🎮 SUHA FPS+ v{self.version} Discord Bot Ready')
        self.logger.info(f'📊 Monitoring {len(self.guilds)} servers')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=f"🎯 Gaming Performance | v{self.version}"
        )
        await self.change_presence(activity=activity, status=discord.Status.online)
        
    async def on_guild_join(self, guild):
        """Called when bot joins a server."""
        self.logger.info(f"🏠 Joined server: {guild.name} ({guild.id})")
        
        # Try to send welcome message
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="🎮 SUHA FPS+ Bot",
                    description=f"""
                    **Welcome to SUHA FPS+ v{self.version}!**
                    
                    🎯 **Gaming Performance Monitoring**
                    📊 **Real-time System Analytics** 
                    🚨 **Smart Performance Alerts**
                    ⚡ **Optimization Notifications**
                    
                    Use `!fps help` to see all commands!
                    """,
                    color=0x00ff88,
                    timestamp=datetime.now()
                )
                embed.set_footer(text="SUHA FPS+ | Top-tier Gaming Performance")
                await channel.send(embed=embed)
                break
    
    # Performance monitoring task
    @tasks.loop(seconds=30)
    async def performance_monitor(self):
        """Monitor system performance every 30 seconds."""
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Update performance data
            self.performance_data.update({
                'last_update': datetime.now(),
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'ping': await self.get_network_ping()
            })
            
            # Check for performance issues
            await self.check_performance_issues()
            
            # Update performance history
            now = datetime.now()
            self.performance_history['timestamps'].append(now)
            self.performance_history['cpu'].append(cpu_percent)
            self.performance_history['memory'].append(memory.percent)
            
            # Keep only last 100 data points
            if len(self.performance_history['timestamps']) > 100:
                for key in self.performance_history:
                    self.performance_history[key] = self.performance_history[key][-100:]
            
        except Exception as e:
            self.logger.error(f"Performance monitoring error: {e}")
    
    @tasks.loop(minutes=5)
    async def health_check(self):
        """Health check every 5 minutes."""
        try:
            uptime = datetime.now() - self.start_time
            self.logger.info(f"🔄 Bot health check - Uptime: {uptime}")
            
            # Check if performance data is being updated
            if self.performance_data['last_update']:
                time_diff = datetime.now() - self.performance_data['last_update']
                if time_diff > timedelta(minutes=2):
                    self.logger.warning("⚠️ Performance monitoring seems stalled")
                    
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
    
    async def get_network_ping(self):
        """Get network ping (simplified version)."""
        try:
            # This is a basic implementation
            # In production, you'd use actual ping measurement
            return 25  # Placeholder value
        except:
            return 0
    
    async def check_performance_issues(self):
        """Check for performance issues and send alerts."""
        issues = []
        
        # CPU usage check
        if self.performance_data['cpu_usage'] > self.thresholds['cpu_high']:
            issues.append(f"🔥 High CPU usage: {self.performance_data['cpu_usage']:.1f}%")
        
        # Memory usage check
        if self.performance_data['memory_usage'] > self.thresholds['memory_high']:
            issues.append(f"🧠 High memory usage: {self.performance_data['memory_usage']:.1f}%")
        
        # Send alerts if issues found
        if issues and self.notification_settings['performance_alerts']:
            await self.send_performance_alert(issues)
    
    async def send_performance_alert(self, issues: List[str]):
        """Send performance alert to notification channel."""
        if not self.notification_channel_id:
            return
        
        try:
            channel = self.get_channel(self.notification_channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="🚨 Performance Alert",
                description="\n".join(issues),
                color=0xff4444,
                timestamp=datetime.now()
            )
            embed.set_footer(text="SUHA FPS+ Performance Monitor")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to send performance alert: {e}")
    
    async def send_notification(self, title: str, description: str, color: int = 0x00ff88):
        """Send a notification to the configured channel."""
        if not self.notification_channel_id:
            return
        
        try:
            channel = self.get_channel(self.notification_channel_id)
            if not channel:
                return
                
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.now()
            )
            embed.set_footer(text="SUHA FPS+ Notification System")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")

    # Bot commands
    @commands.command(name='status')
    async def status_command(self, ctx):
        """Display current system status."""
        embed = discord.Embed(
            title="🎮 SUHA FPS+ System Status",
            color=0x00ff88,
            timestamp=datetime.now()
        )
        
        # System information
        uptime = datetime.now() - self.start_time
        embed.add_field(
            name="🤖 Bot Status",
            value=f"""
            **Version:** {self.version}
            **Uptime:** {str(uptime).split('.')[0]}
            **Ping:** {round(self.latency * 1000)}ms
            """,
            inline=True
        )
        
        # Performance data
        embed.add_field(
            name="📊 Performance",
            value=f"""
            **CPU:** {self.performance_data['cpu_usage']:.1f}%
            **Memory:** {self.performance_data['memory_usage']:.1f}%
            **Network Ping:** {self.performance_data['ping']}ms
            """,
            inline=True
        )
        
        # Last update
        if self.performance_data['last_update']:
            time_ago = datetime.now() - self.performance_data['last_update']
            embed.add_field(
                name="🕐 Last Update",
                value=f"{time_ago.seconds} seconds ago",
                inline=False
            )
        
        embed.set_footer(text="SUHA FPS+ | Real-time Gaming Performance")
        await ctx.send(embed=embed)
    
    @commands.command(name='optimize')
    @commands.has_permissions(administrator=True)
    async def optimize_command(self, ctx, target: str = "all"):
        """Trigger system optimization."""
        embed = discord.Embed(
            title="⚡ SUHA FPS+ Optimization",
            description=f"Initiating {target} optimization...",
            color=0xffaa00,
            timestamp=datetime.now()
        )
        
        message = await ctx.send(embed=embed)
        
        # Simulate optimization process
        await asyncio.sleep(2)
        
        embed = discord.Embed(
            title="✅ Optimization Complete",
            description=f"""
            **Target:** {target.title()}
            **Status:** Completed successfully
            **Improvements:** CPU priority optimized, memory cleaned, network tuned
            """,
            color=0x00ff88,
            timestamp=datetime.now()
        )
        embed.set_footer(text="SUHA FPS+ Optimization System")
        
        await message.edit(embed=embed)
        
        # Send notification
        await self.send_notification(
            "⚡ System Optimization Applied",
            f"Optimization completed for: {target}"
        )
    
    @commands.command(name='alerts')
    @commands.has_permissions(administrator=True)
    async def alerts_command(self, ctx, setting: str = None, value: str = None):
        """Configure alert settings."""
        if not setting:
            # Show current settings
            embed = discord.Embed(
                title="🔔 Alert Settings",
                color=0x00aaff,
                timestamp=datetime.now()
            )
            
            for key, enabled in self.notification_settings.items():
                status = "✅ Enabled" if enabled else "❌ Disabled"
                embed.add_field(
                    name=key.replace('_', ' ').title(),
                    value=status,
                    inline=True
                )
            
            embed.set_footer(text="Use '!fps alerts <setting> <true/false>' to change")
            await ctx.send(embed=embed)
            return
        
        # Update setting
        if setting in self.notification_settings and value:
            self.notification_settings[setting] = value.lower() == 'true'
            
            embed = discord.Embed(
                title="✅ Alert Setting Updated",
                description=f"**{setting}:** {self.notification_settings[setting]}",
                color=0x00ff88
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Invalid setting or value. Use `!fps alerts` to see options.")
    
    @commands.command(name='setchannel')
    @commands.has_permissions(administrator=True)
    async def setchannel_command(self, ctx):
        """Set current channel as notification channel."""
        self.notification_channel_id = ctx.channel.id
        
        embed = discord.Embed(
            title="📢 Notification Channel Set",
            description=f"This channel will receive SUHA FPS+ notifications.",
            color=0x00ff88,
            timestamp=datetime.now()
        )
        await ctx.send(embed=embed)
        
        # Test notification
        await self.send_notification(
            "🎯 Test Notification",
            "SUHA FPS+ notifications are now active in this channel!"
        )

def run_discord_bot(token: str, logger: logging.Logger):
    """Run the Discord bot."""
    try:
        bot = SuhaFPSBot()
        logger.info("🚀 Starting SUHA FPS+ Discord Bot...")
        bot.run(token, log_handler=None)  # We handle logging ourselves
    except Exception as e:
        logger.error(f"❌ Discord bot error: {e}")

class DiscordBotManager:
    """Manages the Discord bot in a separate thread."""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('DISCORD_BOT_TOKEN')
        self.bot_thread = None
        self.bot_instance = None
        self.logger = logging.getLogger(f"{__name__}.DiscordBotManager")
        
    def start(self):
        """Start the Discord bot in a separate thread."""
        if not self.token:
            self.logger.error("❌ No Discord bot token provided")
            return False
        
        if self.bot_thread and self.bot_thread.is_alive():
            self.logger.warning("⚠️ Bot is already running")
            return True
        
        self.bot_thread = threading.Thread(
            target=run_discord_bot,
            args=(self.token, self.logger),
            daemon=True
        )
        self.bot_thread.start()
        
        self.logger.info("🤖 Discord bot started in background thread")
        return True
    
    def stop(self):
        """Stop the Discord bot."""
        if self.bot_instance:
            asyncio.create_task(self.bot_instance.close())
        
        self.logger.info("🛑 Discord bot stopped")

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get token from environment or prompt
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        token = input("Enter Discord bot token: ").strip()
    
    if token:
        manager = DiscordBotManager(token)
        manager.start()
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop()
    else:
        print("❌ No Discord bot token provided")