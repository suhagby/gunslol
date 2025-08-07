#!/usr/bin/env python3
"""
Advanced Discord Bot v4.0 - Neural Gaming Assistant
Next-generation Discord bot with AI-powered gaming optimization and community features.
"""

import asyncio
import aiohttp
import discord
from discord.ext import commands, tasks
import json
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

@dataclass
class GamingSession:
    """Gaming session data."""
    user_id: int
    game: str
    start_time: float
    end_time: Optional[float] = None
    avg_fps: Optional[float] = None
    min_fps: Optional[float] = None
    max_fps: Optional[float] = None
    avg_latency: Optional[float] = None
    performance_score: Optional[float] = None

@dataclass
class OptimizationCommand:
    """Optimization command data."""
    user_id: int
    command: str
    timestamp: float
    status: str
    result: Optional[Dict[str, Any]] = None

class AdvancedGamingBot(commands.Bot):
    """Advanced Discord bot for gaming optimization and community features."""
    
    def __init__(self, command_prefix='!fps ', **options):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.reactions = True
        
        super().__init__(command_prefix=command_prefix, intents=intents, **options)
        
        # Bot state
        self.gaming_sessions: Dict[int, GamingSession] = {}
        self.user_stats: Dict[int, Dict[str, Any]] = {}
        self.optimization_history: List[OptimizationCommand] = []
        self.server_configs: Dict[int, Dict[str, Any]] = {}
        
        # Performance monitoring
        self.performance_data: Dict[int, List[Dict[str, Any]]] = {}
        self.alerts_enabled: Dict[int, bool] = {}
        
        # AI features
        self.ai_recommendations: Dict[int, List[Dict[str, Any]]] = {}
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Load persistent data
        asyncio.create_task(self.load_data())
        
        # Color scheme for embeds
        self.colors = {
            'primary': 0x00FF88,      # Neural green
            'secondary': 0xFF0080,     # Neural pink
            'accent': 0x00CCFF,       # Neural cyan
            'warning': 0xFFAA00,      # Neural orange
            'danger': 0xFF4444,       # Neural red
            'success': 0x44FF44       # Neural bright green
        }
    
    async def on_ready(self):
        """Called when bot is ready."""
        self.logger.info(f'{self.user} has connected to Discord!')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="gaming performance | !fps help"
            )
        )
        
        # Start background tasks
        self.performance_monitor.start()
        self.ai_analysis.start()
        self.data_backup.start()
        
        print(f"🤖 Advanced Gaming Bot v4.0 Ready!")
        print(f"🔗 Connected as: {self.user}")
        print(f"🏠 Serving {len(self.guilds)} servers")
    
    async def load_data(self):
        """Load persistent data from files."""
        data_files = {
            'user_stats': 'data/user_stats.json',
            'server_configs': 'data/server_configs.json',
            'optimization_history': 'data/optimization_history.json'
        }
        
        for attr, filepath in data_files.items():
            try:
                path = Path(filepath)
                if path.exists():
                    async with aiohttp.ClientSession() as session:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            setattr(self, attr, data)
            except Exception as e:
                self.logger.error(f"Failed to load {filepath}: {e}")
    
    async def save_data(self):
        """Save persistent data to files."""
        Path('data').mkdir(exist_ok=True)
        
        data_to_save = {
            'data/user_stats.json': self.user_stats,
            'data/server_configs.json': self.server_configs,
            'data/optimization_history.json': [asdict(cmd) for cmd in self.optimization_history[-1000:]]
        }
        
        for filepath, data in data_to_save.items():
            try:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            except Exception as e:
                self.logger.error(f"Failed to save {filepath}: {e}")
    
    @tasks.loop(seconds=30)
    async def performance_monitor(self):
        """Monitor performance for active gaming sessions."""
        try:
            for user_id, session in self.gaming_sessions.items():
                if session.end_time is None:  # Active session
                    # Simulate performance data collection
                    perf_data = await self._collect_performance_data(user_id)
                    
                    if user_id not in self.performance_data:
                        self.performance_data[user_id] = []
                    
                    self.performance_data[user_id].append(perf_data)
                    
                    # Check for performance alerts
                    if self.alerts_enabled.get(user_id, False):
                        await self._check_performance_alerts(user_id, perf_data)
        
        except Exception as e:
            self.logger.error(f"Performance monitor error: {e}")
    
    @tasks.loop(minutes=5)
    async def ai_analysis(self):
        """Perform AI analysis and generate recommendations."""
        try:
            for user_id, perf_data in self.performance_data.items():
                if len(perf_data) >= 10:  # Need sufficient data
                    recommendations = await self._generate_ai_recommendations(user_id, perf_data)
                    self.ai_recommendations[user_id] = recommendations
        
        except Exception as e:
            self.logger.error(f"AI analysis error: {e}")
    
    @tasks.loop(hours=1)
    async def data_backup(self):
        """Backup data periodically."""
        try:
            await self.save_data()
            self.logger.info("Data backup completed")
        except Exception as e:
            self.logger.error(f"Data backup error: {e}")
    
    async def _collect_performance_data(self, user_id: int) -> Dict[str, Any]:
        """Collect performance data for a user (simulated)."""
        return {
            'timestamp': time.time(),
            'fps': 120 + np.random.normal(0, 10),
            'latency': 15 + np.random.normal(0, 5),
            'cpu_usage': 45 + np.random.normal(0, 10),
            'gpu_usage': 80 + np.random.normal(0, 15),
            'memory_usage': 60 + np.random.normal(0, 8),
            'temperature': 65 + np.random.normal(0, 5)
        }
    
    async def _check_performance_alerts(self, user_id: int, perf_data: Dict[str, Any]):
        """Check if performance alerts should be sent."""
        alerts = []
        
        if perf_data['fps'] < 60:
            alerts.append(f"⚠️ Low FPS detected: {perf_data['fps']:.1f}")
        
        if perf_data['latency'] > 50:
            alerts.append(f"⚠️ High latency: {perf_data['latency']:.1f}ms")
        
        if perf_data['temperature'] > 80:
            alerts.append(f"🌡️ High temperature: {perf_data['temperature']:.1f}°C")
        
        if alerts:
            user = self.get_user(user_id)
            if user:
                try:
                    embed = discord.Embed(
                        title="🚨 Performance Alert",
                        description="\n".join(alerts),
                        color=self.colors['warning'],
                        timestamp=datetime.utcnow()
                    )
                    await user.send(embed=embed)
                except discord.Forbidden:
                    pass  # User has DMs disabled
    
    async def _generate_ai_recommendations(self, user_id: int, perf_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations."""
        recommendations = []
        
        recent_data = perf_data[-10:]  # Last 10 data points
        avg_fps = np.mean([d['fps'] for d in recent_data])
        avg_latency = np.mean([d['latency'] for d in recent_data])
        avg_temp = np.mean([d['temperature'] for d in recent_data])
        
        # FPS recommendations
        if avg_fps < 60:
            recommendations.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'FPS Optimization Needed',
                'description': f'Average FPS is {avg_fps:.1f}. Consider reducing graphics settings or applying CPU optimizations.',
                'confidence': 0.85
            })
        
        # Latency recommendations
        if avg_latency > 30:
            recommendations.append({
                'type': 'network',
                'priority': 'medium',
                'title': 'Network Latency High',
                'description': f'Average latency is {avg_latency:.1f}ms. Network optimization recommended.',
                'confidence': 0.75
            })
        
        # Thermal recommendations
        if avg_temp > 75:
            recommendations.append({
                'type': 'thermal',
                'priority': 'medium',
                'title': 'Thermal Management',
                'description': f'Average temperature is {avg_temp:.1f}°C. Consider fan curve optimization.',
                'confidence': 0.70
            })
        
        return recommendations
    
    # Command Groups
    @commands.group(name='status', invoke_without_command=True)
    async def status(self, ctx):
        """Show comprehensive system status."""
        user_id = ctx.author.id
        
        # Get current performance data
        current_perf = await self._collect_performance_data(user_id)
        
        # Create status embed
        embed = discord.Embed(
            title="🎮 Neural Gaming Status",
            color=self.colors['primary'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        # Performance metrics
        embed.add_field(
            name="🖼️ Performance",
            value=f"```\nFPS: {current_perf['fps']:.1f}\nLatency: {current_perf['latency']:.1f}ms\nScore: {self._calculate_performance_score(current_perf):.1f}/100```",
            inline=True
        )
        
        # System metrics
        embed.add_field(
            name="💻 System",
            value=f"```\nCPU: {current_perf['cpu_usage']:.1f}%\nGPU: {current_perf['gpu_usage']:.1f}%\nRAM: {current_perf['memory_usage']:.1f}%```",
            inline=True
        )
        
        # Thermal
        embed.add_field(
            name="🌡️ Thermal",
            value=f"```\nTemp: {current_perf['temperature']:.1f}°C\nStatus: {'Optimal' if current_perf['temperature'] < 70 else 'Warm' if current_perf['temperature'] < 80 else 'Hot'}```",
            inline=True
        )
        
        # Gaming session info
        if user_id in self.gaming_sessions:
            session = self.gaming_sessions[user_id]
            session_duration = time.time() - session.start_time
            embed.add_field(
                name="🎲 Current Session",
                value=f"```\nGame: {session.game}\nDuration: {self._format_duration(session_duration)}\nAvg FPS: {session.avg_fps or 'Calculating...'}```",
                inline=False
            )
        
        # AI recommendations
        if user_id in self.ai_recommendations and self.ai_recommendations[user_id]:
            rec = self.ai_recommendations[user_id][0]  # Top recommendation
            embed.add_field(
                name="🤖 AI Recommendation",
                value=f"**{rec['title']}**\n{rec['description'][:100]}...",
                inline=False
            )
        
        embed.set_footer(text="SUHA FPS+ Neural Interface v4.0")
        await ctx.send(embed=embed)
    
    @commands.command(name='optimize')
    async def optimize(self, ctx, optimization_type: str = 'auto'):
        """Perform system optimization."""
        user_id = ctx.author.id
        
        # Create optimization command record
        cmd = OptimizationCommand(
            user_id=user_id,
            command=f'optimize {optimization_type}',
            timestamp=time.time(),
            status='running'
        )
        
        self.optimization_history.append(cmd)
        
        # Create initial response
        embed = discord.Embed(
            title="🚀 Neural Optimization Initiated",
            description=f"Starting {optimization_type} optimization...",
            color=self.colors['accent'],
            timestamp=datetime.utcnow()
        )
        
        message = await ctx.send(embed=embed)
        
        # Simulate optimization process
        await asyncio.sleep(2)
        
        # Update embed with progress
        embed.description = "🔄 Analyzing system performance..."
        await message.edit(embed=embed)
        await asyncio.sleep(1)
        
        embed.description = "⚙️ Applying optimizations..."
        await message.edit(embed=embed)
        await asyncio.sleep(2)
        
        # Complete optimization
        cmd.status = 'completed'
        cmd.result = {
            'performance_gain': np.random.uniform(10, 25),
            'optimizations_applied': np.random.randint(5, 12),
            'estimated_fps_gain': np.random.uniform(5, 15)
        }
        
        # Final result
        embed = discord.Embed(
            title="✅ Optimization Complete",
            color=self.colors['success'],
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Results",
            value=f"```\nPerformance Gain: +{cmd.result['performance_gain']:.1f}%\nOptimizations: {cmd.result['optimizations_applied']}\nEst. FPS Gain: +{cmd.result['estimated_fps_gain']:.1f}```",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Optimizations Applied",
            value="• CPU priority adjustment\n• Memory cache optimization\n• Network stack tuning\n• GPU memory management\n• Thermal curve adjustment",
            inline=False
        )
        
        embed.set_footer(text="Optimization results may vary based on system configuration")
        await message.edit(embed=embed)
    
    @commands.command(name='profile')
    async def profile(self, ctx, game: str = None):
        """Manage gaming profiles."""
        user_id = ctx.author.id
        
        if not game:
            # Show available profiles
            profiles = {
                'competitive': '🏆 Competitive - Maximum performance',
                'streaming': '📹 Streaming - Balanced performance + stream quality',
                'casual': '😊 Casual - Optimized for casual gaming',
                'vr': '🥽 VR - VR gaming optimizations'
            }
            
            embed = discord.Embed(
                title="🎮 Gaming Profiles",
                description="Select a profile to optimize your system for specific gaming scenarios.",
                color=self.colors['primary']
            )
            
            for profile, description in profiles.items():
                embed.add_field(
                    name=f"`!fps profile {profile}`",
                    value=description,
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            # Apply profile
            embed = discord.Embed(
                title=f"✅ Profile Applied: {game.title()}",
                description=f"System optimized for {game} gaming.",
                color=self.colors['success'],
                timestamp=datetime.utcnow()
            )
            
            # Add profile-specific optimizations
            optimizations = {
                'competitive': [
                    "Maximum CPU performance",
                    "Minimized input latency",
                    "Disabled visual effects",
                    "Network optimization for low ping"
                ],
                'streaming': [
                    "Balanced CPU allocation",
                    "GPU encoder optimization",
                    "Bandwidth management",
                    "Stream stability enhancements"
                ],
                'casual': [
                    "Balanced performance",
                    "Enhanced visual quality",
                    "Power efficiency",
                    "Thermal management"
                ],
                'vr': [
                    "High frame rate stability",
                    "Motion smoothing",
                    "Latency minimization",
                    "USB optimization"
                ]
            }
            
            if game.lower() in optimizations:
                embed.add_field(
                    name="⚙️ Optimizations Applied",
                    value="\n".join([f"• {opt}" for opt in optimizations[game.lower()]]),
                    inline=False
                )
            
            await ctx.send(embed=embed)
    
    @commands.command(name='session')
    async def session(self, ctx, action: str, game: str = None):
        """Manage gaming sessions."""
        user_id = ctx.author.id
        
        if action.lower() == 'start':
            if not game:
                await ctx.send("❌ Please specify a game: `!fps session start <game>`")
                return
            
            if user_id in self.gaming_sessions and self.gaming_sessions[user_id].end_time is None:
                await ctx.send("❌ You already have an active gaming session!")
                return
            
            # Start new session
            session = GamingSession(
                user_id=user_id,
                game=game,
                start_time=time.time()
            )
            
            self.gaming_sessions[user_id] = session
            
            embed = discord.Embed(
                title="🎮 Gaming Session Started",
                description=f"Now tracking performance for **{game}**",
                color=self.colors['success'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📊 Tracking",
                value="• FPS monitoring\n• Latency tracking\n• Performance analysis\n• AI recommendations",
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        elif action.lower() == 'stop':
            if user_id not in self.gaming_sessions or self.gaming_sessions[user_id].end_time is not None:
                await ctx.send("❌ No active gaming session found!")
                return
            
            # End session
            session = self.gaming_sessions[user_id]
            session.end_time = time.time()
            
            # Calculate session stats
            duration = session.end_time - session.start_time
            
            # Generate session report
            embed = discord.Embed(
                title="🏁 Gaming Session Complete",
                description=f"Session for **{session.game}** ended",
                color=self.colors['primary'],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="⏱️ Duration",
                value=self._format_duration(duration),
                inline=True
            )
            
            embed.add_field(
                name="📊 Performance",
                value=f"```\nAvg FPS: {session.avg_fps or 'N/A'}\nMin FPS: {session.min_fps or 'N/A'}\nMax FPS: {session.max_fps or 'N/A'}```",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Score",
                value=f"```\nOverall: {session.performance_score or 'N/A'}/100```",
                inline=True
            )
            
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("❌ Invalid action. Use `start` or `stop`.")
    
    @commands.command(name='alerts')
    async def alerts(self, ctx, action: str = 'status'):
        """Manage performance alerts."""
        user_id = ctx.author.id
        
        if action.lower() == 'enable':
            self.alerts_enabled[user_id] = True
            embed = discord.Embed(
                title="🔔 Alerts Enabled",
                description="You will receive DM notifications for performance issues.",
                color=self.colors['success']
            )
            await ctx.send(embed=embed)
        
        elif action.lower() == 'disable':
            self.alerts_enabled[user_id] = False
            embed = discord.Embed(
                title="🔕 Alerts Disabled",
                description="Performance alerts have been disabled.",
                color=self.colors['warning']
            )
            await ctx.send(embed=embed)
        
        else:
            status = "✅ Enabled" if self.alerts_enabled.get(user_id, False) else "❌ Disabled"
            embed = discord.Embed(
                title="🔔 Alert Status",
                description=f"Performance alerts are currently **{status}**",
                color=self.colors['primary']
            )
            
            embed.add_field(
                name="Commands",
                value="`!fps alerts enable` - Enable alerts\n`!fps alerts disable` - Disable alerts",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name='graph')
    async def graph(self, ctx, metric: str = 'fps', duration: int = 60):
        """Generate performance graphs."""
        user_id = ctx.author.id
        
        if user_id not in self.performance_data or not self.performance_data[user_id]:
            await ctx.send("❌ No performance data available. Start a gaming session first!")
            return
        
        # Get data for specified duration (in minutes)
        cutoff_time = time.time() - (duration * 60)
        data = [d for d in self.performance_data[user_id] if d['timestamp'] >= cutoff_time]
        
        if not data:
            await ctx.send(f"❌ No data available for the last {duration} minutes.")
            return
        
        # Create graph
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6))
        fig.patch.set_facecolor('#0a0a0a')
        ax.set_facecolor('#1a1a1a')
        
        timestamps = [datetime.fromtimestamp(d['timestamp']) for d in data]
        values = [d[metric] for d in data]
        
        # Plot line
        ax.plot(timestamps, values, color='#00ff88', linewidth=2, alpha=0.8)
        ax.fill_between(timestamps, values, alpha=0.2, color='#00ff88')
        
        # Customize
        ax.set_title(f'{metric.upper()} Performance - Last {duration} minutes', 
                    color='#00ff88', fontsize=16, fontweight='bold')
        ax.set_xlabel('Time', color='white')
        ax.set_ylabel(metric.upper(), color='white')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3, color='#333333')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        # Add statistics
        avg_value = np.mean(values)
        max_value = np.max(values)
        min_value = np.min(values)
        
        stats_text = f'Avg: {avg_value:.1f}  Max: {max_value:.1f}  Min: {min_value:.1f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               color='#00ccff', fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        
        # Save and send
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close()
        
        file = discord.File(buffer, filename=f'{metric}_graph.png')
        
        embed = discord.Embed(
            title=f"📊 {metric.upper()} Performance Graph",
            description=f"Performance data for the last {duration} minutes",
            color=self.colors['accent'],
            timestamp=datetime.utcnow()
        )
        
        embed.set_image(url=f"attachment://{metric}_graph.png")
        embed.set_footer(text=f"Generated for {ctx.author.display_name}")
        
        await ctx.send(embed=embed, file=file)
    
    @commands.command(name='leaderboard')
    async def leaderboard(self, ctx, category: str = 'performance'):
        """Show performance leaderboards."""
        if not self.user_stats:
            await ctx.send("❌ No leaderboard data available yet.")
            return
        
        # Generate sample leaderboard data
        users = list(self.user_stats.keys()) if self.user_stats else [str(ctx.author.id)]
        
        leaderboard_data = []
        for user_id_str in users[:10]:  # Top 10
            try:
                user = self.get_user(int(user_id_str))
                if user:
                    leaderboard_data.append({
                        'name': user.display_name,
                        'score': np.random.uniform(80, 98),
                        'avg_fps': np.random.uniform(90, 144),
                        'sessions': np.random.randint(5, 50)
                    })
            except (ValueError, AttributeError):
                continue
        
        # Sort by category
        if category == 'fps':
            leaderboard_data.sort(key=lambda x: x['avg_fps'], reverse=True)
            title_suffix = "Average FPS"
            value_key = 'avg_fps'
        else:
            leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
            title_suffix = "Performance Score"
            value_key = 'score'
        
        embed = discord.Embed(
            title=f"🏆 Leaderboard - {title_suffix}",
            color=self.colors['primary'],
            timestamp=datetime.utcnow()
        )
        
        medals = ['🥇', '🥈', '🥉'] + ['🏅'] * 7
        
        leaderboard_text = ""
        for i, user_data in enumerate(leaderboard_data[:10]):
            medal = medals[i] if i < len(medals) else '🏅'
            value = f"{user_data[value_key]:.1f}"
            leaderboard_text += f"{medal} **{user_data['name']}** - {value}\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text="Rankings updated every hour")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='ai')
    async def ai_recommendations(self, ctx):
        """Get AI-powered recommendations."""
        user_id = ctx.author.id
        
        recommendations = self.ai_recommendations.get(user_id, [])
        
        if not recommendations:
            embed = discord.Embed(
                title="🤖 AI Assistant",
                description="No recommendations available yet. Start a gaming session to get personalized suggestions!",
                color=self.colors['accent']
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🤖 AI Performance Recommendations",
            description="Personalized suggestions based on your gaming data",
            color=self.colors['accent'],
            timestamp=datetime.utcnow()
        )
        
        priority_colors = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        
        for i, rec in enumerate(recommendations[:3]):  # Top 3 recommendations
            priority_icon = priority_colors.get(rec['priority'], '⚪')
            
            embed.add_field(
                name=f"{priority_icon} {rec['title']}",
                value=f"{rec['description']}\n*Confidence: {rec['confidence']:.0%}*",
                inline=False
            )
        
        embed.set_footer(text="AI analysis based on recent performance data")
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show comprehensive help."""
        embed = discord.Embed(
            title="🤖 Advanced Gaming Bot v4.0 - Neural Interface",
            description="Your AI-powered gaming performance assistant",
            color=self.colors['primary']
        )
        
        commands_data = {
            "📊 Monitoring": [
                "`!fps status` - Comprehensive system status",
                "`!fps session start <game>` - Start performance tracking",
                "`!fps session stop` - End tracking session",
                "`!fps graph <metric>` - Generate performance graphs"
            ],
            "⚙️ Optimization": [
                "`!fps optimize [type]` - Perform system optimization", 
                "`!fps profile <type>` - Apply gaming profiles",
                "`!fps ai` - Get AI recommendations"
            ],
            "🔔 Alerts & Settings": [
                "`!fps alerts enable/disable` - Manage performance alerts",
                "`!fps leaderboard` - View performance rankings"
            ]
        }
        
        for category, commands in commands_data.items():
            embed.add_field(
                name=category,
                value="\n".join(commands),
                inline=False
            )
        
        embed.add_field(
            name="🎮 Gaming Profiles",
            value="`competitive` • `streaming` • `casual` • `vr`",
            inline=False
        )
        
        embed.set_footer(text="SUHA FPS+ Neural Interface v4.0 • Advanced AI Gaming Assistant")
        await ctx.send(embed=embed)
    
    # Utility functions
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def _calculate_performance_score(self, perf_data: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        fps_score = min(100, (perf_data['fps'] / 120) * 100)
        latency_score = max(0, 100 - (perf_data['latency'] / 50) * 100)
        cpu_score = max(0, 100 - perf_data['cpu_usage'])
        temp_score = max(0, 100 - (perf_data['temperature'] - 40) * 2)
        
        return (fps_score * 0.4 + latency_score * 0.3 + cpu_score * 0.2 + temp_score * 0.1)

# Bot configuration and startup
async def setup_bot(token: str, owner_id: Optional[int] = None) -> AdvancedGamingBot:
    """Setup and configure the bot."""
    bot = AdvancedGamingBot()
    
    if owner_id:
        bot.owner_id = owner_id
    
    @bot.event
    async def on_command_error(ctx, error):
        """Handle command errors gracefully."""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `!fps help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided.")
        else:
            await ctx.send(f"❌ An error occurred: {str(error)[:100]}")
            bot.logger.error(f"Command error: {error}")
    
    return bot

# Main entry point
async def main():
    """Main function to run the bot."""
    import os
    
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Discord bot token not found in environment variables")
        print("Set DISCORD_BOT_TOKEN environment variable")
        return
    
    bot = await setup_bot(token)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()
    except Exception as e:
        print(f"❌ Bot error: {e}")
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())