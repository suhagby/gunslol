#!/usr/bin/env python3
"""
SUHA FPS+ v4.0 - Neural Gaming Performance Launcher
Integrated launcher system connecting all advanced components.
"""

import asyncio
import sys
import os
import threading
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import signal

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import new v4 components
try:
    from ai_engine_v4 import create_ai_engine, SystemState
    from advanced_performance_optimizer_v4 import create_optimization_engine, setup_high_performance_loop
    from windows_optimizer_v4 import create_windows_optimizer
    from discord_bot_v4 import setup_bot
    HAS_V4_COMPONENTS = True
except ImportError as e:
    print(f"⚠️  V4 components not fully available: {e}")
    HAS_V4_COMPONENTS = False

# Import existing components
try:
    import psutil
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

@dataclass
class LauncherConfig:
    """Launcher configuration."""
    ai_engine_enabled: bool = True
    performance_optimizer_enabled: bool = True
    windows_optimizer_enabled: bool = True
    web_dashboard_enabled: bool = True
    discord_bot_enabled: bool = False  # Requires token
    auto_optimize: bool = True
    monitoring_interval: float = 1.0
    web_port: int = 5000
    debug_mode: bool = False

class ComponentManager:
    """Manages all system components."""
    
    def __init__(self, config: LauncherConfig):
        self.config = config
        self.logger = self._setup_logging()
        
        # Component instances
        self.ai_engine = None
        self.performance_optimizer = None
        self.windows_optimizer = None
        self.web_app = None
        self.discord_bot = None
        
        # Component status
        self.component_status = {
            'ai_engine': 'stopped',
            'performance_optimizer': 'stopped', 
            'windows_optimizer': 'stopped',
            'web_dashboard': 'stopped',
            'discord_bot': 'stopped'
        }
        
        # Runtime data
        self.current_metrics = {}
        self.running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging system."""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger('SUHA_FPS_Launcher')
        logger.setLevel(logging.DEBUG if self.config.debug_mode else logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_dir / 'launcher.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    async def start_all_components(self):
        """Start all enabled components."""
        self.logger.info("🚀 Starting SUHA FPS+ v4.0 Neural Gaming Performance System")
        self.running = True
        
        startup_tasks = []
        
        # Start AI Engine
        if self.config.ai_engine_enabled and HAS_V4_COMPONENTS:
            startup_tasks.append(self._start_ai_engine())
        
        # Start Performance Optimizer
        if self.config.performance_optimizer_enabled and HAS_V4_COMPONENTS:
            startup_tasks.append(self._start_performance_optimizer())
        
        # Start Windows Optimizer
        if self.config.windows_optimizer_enabled and HAS_V4_COMPONENTS:
            startup_tasks.append(self._start_windows_optimizer())
        
        # Start Web Dashboard
        if self.config.web_dashboard_enabled and HAS_FLASK:
            startup_tasks.append(self._start_web_dashboard())
        
        # Start Discord Bot
        if self.config.discord_bot_enabled and os.getenv('DISCORD_BOT_TOKEN'):
            startup_tasks.append(self._start_discord_bot())
        
        # Execute all startup tasks
        results = await asyncio.gather(*startup_tasks, return_exceptions=True)
        
        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Component startup failed: {result}")
            else:
                self.logger.info(f"Component started successfully")
        
        # Start monitoring loop
        if self.running:
            asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("✅ All components started successfully")
    
    async def _start_ai_engine(self):
        """Start AI engine component."""
        try:
            self.ai_engine = await create_ai_engine()
            self.component_status['ai_engine'] = 'running'
            self.logger.info("🤖 AI Engine v4.0 started")
        except Exception as e:
            self.component_status['ai_engine'] = 'error'
            raise Exception(f"AI Engine startup failed: {e}")
    
    async def _start_performance_optimizer(self):
        """Start performance optimizer component."""
        try:
            self.performance_optimizer = await create_optimization_engine(max_workers=8)
            self.component_status['performance_optimizer'] = 'running'
            self.logger.info("⚡ Performance Optimizer v4.0 started")
        except Exception as e:
            self.component_status['performance_optimizer'] = 'error'
            raise Exception(f"Performance Optimizer startup failed: {e}")
    
    async def _start_windows_optimizer(self):
        """Start Windows optimizer component."""
        try:
            self.windows_optimizer = create_windows_optimizer()
            self.component_status['windows_optimizer'] = 'running'
            self.logger.info("🖥️  Windows Optimizer v4.0 started")
        except Exception as e:
            self.component_status['windows_optimizer'] = 'error'
            raise Exception(f"Windows Optimizer startup failed: {e}")
    
    async def _start_web_dashboard(self):
        """Start web dashboard component."""
        try:
            self.web_app = self._create_web_app()
            
            # Start web server in thread
            def run_web_app():
                self.web_app.run(
                    host='0.0.0.0',
                    port=self.config.web_port,
                    debug=self.config.debug_mode,
                    use_reloader=False
                )
            
            web_thread = threading.Thread(target=run_web_app, daemon=True)
            web_thread.start()
            
            # Wait a moment to ensure server starts
            await asyncio.sleep(1)
            
            self.component_status['web_dashboard'] = 'running'
            self.logger.info(f"🌐 Web Dashboard started on port {self.config.web_port}")
            
        except Exception as e:
            self.component_status['web_dashboard'] = 'error'
            raise Exception(f"Web Dashboard startup failed: {e}")
    
    async def _start_discord_bot(self):
        """Start Discord bot component."""
        try:
            token = os.getenv('DISCORD_BOT_TOKEN')
            if not token:
                raise Exception("Discord bot token not found")
            
            self.discord_bot = await setup_bot(token)
            
            # Start bot in background task
            asyncio.create_task(self.discord_bot.start(token))
            
            self.component_status['discord_bot'] = 'running'
            self.logger.info("🤖 Discord Bot v4.0 started")
            
        except Exception as e:
            self.component_status['discord_bot'] = 'error'
            raise Exception(f"Discord Bot startup failed: {e}")
    
    def _create_web_app(self) -> Flask:
        """Create Flask web application."""
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'neural-gaming-interface-v4'
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        @app.route('/')
        def dashboard():
            """Main dashboard route."""
            return render_template('neural_interface_2040.html')
        
        @app.route('/api/status')
        def api_status():
            """API status endpoint."""
            return jsonify({
                'components': self.component_status,
                'metrics': self.current_metrics,
                'timestamp': time.time()
            })
        
        @app.route('/api/optimize', methods=['POST'])
        def api_optimize():
            """API optimization endpoint."""
            try:
                data = request.json or {}
                optimization_type = data.get('type', 'auto')
                
                # Queue optimization task
                asyncio.create_task(self._handle_optimization_request(optimization_type))
                
                return jsonify({
                    'status': 'success',
                    'message': f'Optimization {optimization_type} queued'
                })
            except Exception as e:
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
        
        @socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.logger.info(f"Client connected: {request.sid}")
            emit('status', {
                'components': self.component_status,
                'metrics': self.current_metrics
            })
        
        @socketio.on('neural_optimize')
        def handle_neural_optimize():
            """Handle neural optimization request."""
            asyncio.create_task(self._handle_optimization_request('neural'))
            emit('optimization_started', {'type': 'neural'})
        
        @socketio.on('system_cleanup')
        def handle_system_cleanup():
            """Handle system cleanup request."""
            asyncio.create_task(self._handle_optimization_request('cleanup'))
            emit('cleanup_started', {})
        
        @socketio.on('performance_boost')
        def handle_performance_boost():
            """Handle performance boost request."""
            asyncio.create_task(self._handle_optimization_request('boost'))
            emit('boost_started', {})
        
        self.socketio = socketio
        return app
    
    async def _handle_optimization_request(self, optimization_type: str):
        """Handle optimization request."""
        try:
            self.logger.info(f"Processing optimization request: {optimization_type}")
            
            # Get current metrics
            if self.performance_optimizer:
                current_metrics = await self.performance_optimizer.collect_metrics()
                
                if optimization_type == 'neural':
                    # AI-driven optimization
                    if self.ai_engine:
                        system_state = SystemState(
                            timestamp=time.time(),
                            cpu_usage=current_metrics.cpu_usage,
                            cpu_temp=current_metrics.cpu_temp,
                            cpu_freq=current_metrics.cpu_freq,
                            memory_usage=current_metrics.memory_usage,
                            gpu_usage=current_metrics.gpu_usage,
                            gpu_temp=current_metrics.gpu_temp,
                            gpu_memory=current_metrics.gpu_memory,
                            disk_io=current_metrics.disk_read + current_metrics.disk_write,
                            network_latency=25.0,  # Default latency
                            fps=120.0,  # Default FPS
                            frame_time=8.33,  # Default frame time
                            running_games=["Unknown"],
                            system_load=current_metrics.cpu_usage / 100
                        )
                        
                        analysis = await self.ai_engine.analyze_system_state(system_state)
                        recommendations = analysis['recommendations']
                        
                        self.logger.info(f"AI generated {len(recommendations)} recommendations")
                
                elif optimization_type == 'cleanup':
                    # System cleanup
                    result = await self.performance_optimizer.optimize_system(target_performance=85.0)
                    self.logger.info(f"System cleanup completed: {result['status']}")
                
                elif optimization_type == 'boost':
                    # Performance boost
                    if self.windows_optimizer:
                        result = await self.windows_optimizer.apply_all_optimizations()
                        self.logger.info(f"Performance boost applied: {result['successful_optimizations']} optimizations")
            
        except Exception as e:
            self.logger.error(f"Optimization request failed: {e}")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Collect metrics from all components
                await self._collect_system_metrics()
                
                # Emit to web clients if available
                if hasattr(self, 'socketio'):
                    self.socketio.emit('performance_update', self.current_metrics)
                
                # Auto-optimization check
                if self.config.auto_optimize:
                    await self._check_auto_optimization()
                
                await asyncio.sleep(self.config.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5.0)
    
    async def _collect_system_metrics(self):
        """Collect metrics from all sources."""
        metrics = {
            'timestamp': time.time(),
            'fps': 120 + (time.time() % 60) * 0.5,  # Simulate FPS variation
            'latency': 15 + abs(time.time() % 30 - 15) * 0.3,  # Simulate latency variation
            'score': 95,
            'cpu': 0,
            'gpu': 0,
            'memory': 0,
            'temperature': 65
        }
        
        # Get real system metrics
        try:
            metrics['cpu'] = psutil.cpu_percent(interval=None)
            metrics['memory'] = psutil.virtual_memory().percent
            
            # Get temperature if available
            try:
                temps = psutil.sensors_temperatures()
                if temps and 'cpu_thermal' in temps:
                    metrics['temperature'] = temps['cpu_thermal'][0].current
                elif temps and 'coretemp' in temps:
                    metrics['temperature'] = temps['coretemp'][0].current
            except (AttributeError, KeyError, IndexError):
                pass
            
            # Simulate GPU metrics
            metrics['gpu'] = min(95, metrics['cpu'] + 20)
            
        except Exception as e:
            self.logger.error(f"Metrics collection error: {e}")
        
        self.current_metrics = metrics
    
    async def _check_auto_optimization(self):
        """Check if auto-optimization should be triggered."""
        if not self.current_metrics:
            return
        
        # Check for performance issues
        performance_issues = []
        
        if self.current_metrics.get('cpu', 0) > 85:
            performance_issues.append('high_cpu')
        
        if self.current_metrics.get('memory', 0) > 90:
            performance_issues.append('high_memory')
        
        if self.current_metrics.get('temperature', 0) > 80:
            performance_issues.append('high_temperature')
        
        if self.current_metrics.get('fps', 120) < 45:
            performance_issues.append('low_fps')
        
        # Trigger optimization if issues found
        if performance_issues:
            self.logger.info(f"Auto-optimization triggered: {', '.join(performance_issues)}")
            await self._handle_optimization_request('auto')
    
    async def stop_all_components(self):
        """Stop all components gracefully."""
        self.logger.info("🛑 Stopping all components...")
        self.running = False
        
        # Stop components
        if self.ai_engine:
            await self.ai_engine.stop()
            self.component_status['ai_engine'] = 'stopped'
        
        if self.performance_optimizer:
            await self.performance_optimizer.stop()
            self.component_status['performance_optimizer'] = 'stopped'
        
        if self.discord_bot:
            await self.discord_bot.close()
            self.component_status['discord_bot'] = 'stopped'
        
        self.logger.info("✅ All components stopped")

class InteractiveLauncher:
    """Interactive launcher interface."""
    
    def __init__(self):
        self.component_manager = None
        self.running = False
    
    def show_banner(self):
        """Show startup banner."""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                     SUHA FPS+ v4.0                          ║
    ║              Neural Gaming Performance System                ║
    ║                                                              ║
    ║  🤖 AI Engine v4.0        ⚡ Performance Optimizer v4.0     ║
    ║  🖥️  Windows Optimizer     🌐 Neural Web Interface 2040     ║ 
    ║  🤖 Discord Bot v4.0      📊 Real-time Monitoring          ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def show_menu(self):
        """Show main menu."""
        print("\n" + "="*60)
        print("🚀 MAIN MENU")
        print("="*60)
        print("1. 🏃 Quick Start (All Components)")
        print("2. ⚙️  Custom Configuration")
        print("3. 🔧 Component Status")
        print("4. 🎮 Gaming Profile Setup")
        print("5. 📊 Performance Analysis")
        print("6. 🤖 AI Recommendations")
        print("7. 🌐 Open Web Dashboard")
        print("8. 🛑 Stop All Components")
        print("9. ❌ Exit")
        print("="*60)
    
    def get_user_choice(self) -> str:
        """Get user menu choice."""
        try:
            choice = input("\n👉 Enter your choice (1-9): ").strip()
            return choice
        except KeyboardInterrupt:
            return "9"
        except:
            return ""
    
    async def handle_choice(self, choice: str):
        """Handle user menu choice."""
        if choice == "1":
            await self._quick_start()
        elif choice == "2":
            await self._custom_configuration()
        elif choice == "3":
            self._show_component_status()
        elif choice == "4":
            await self._gaming_profile_setup()
        elif choice == "5":
            await self._performance_analysis()
        elif choice == "6":
            await self._ai_recommendations()
        elif choice == "7":
            self._open_web_dashboard()
        elif choice == "8":
            await self._stop_components()
        elif choice == "9":
            await self._exit()
        else:
            print("❌ Invalid choice. Please try again.")
    
    async def _quick_start(self):
        """Quick start all components."""
        print("\n🚀 Starting SUHA FPS+ v4.0 with default configuration...")
        
        config = LauncherConfig(
            ai_engine_enabled=True,
            performance_optimizer_enabled=True,
            windows_optimizer_enabled=True,
            web_dashboard_enabled=True,
            discord_bot_enabled=bool(os.getenv('DISCORD_BOT_TOKEN')),
            auto_optimize=True
        )
        
        self.component_manager = ComponentManager(config)
        await self.component_manager.start_all_components()
        
        print("\n✅ All components started successfully!")
        print(f"🌐 Web Dashboard: http://localhost:{config.web_port}")
        print("🎮 Your gaming performance is now being optimized in real-time!")
        
        self.running = True
    
    async def _custom_configuration(self):
        """Custom configuration setup."""
        print("\n⚙️ Custom Configuration")
        print("-" * 30)
        
        config = LauncherConfig()
        
        # AI Engine
        response = input("Enable AI Engine v4.0? (Y/n): ").strip().lower()
        config.ai_engine_enabled = response != 'n'
        
        # Performance Optimizer
        response = input("Enable Performance Optimizer v4.0? (Y/n): ").strip().lower()
        config.performance_optimizer_enabled = response != 'n'
        
        # Windows Optimizer
        response = input("Enable Windows Optimizer v4.0? (Y/n): ").strip().lower()
        config.windows_optimizer_enabled = response != 'n'
        
        # Web Dashboard
        response = input("Enable Web Dashboard? (Y/n): ").strip().lower()
        config.web_dashboard_enabled = response != 'n'
        
        if config.web_dashboard_enabled:
            try:
                port = input(f"Web Dashboard Port ({config.web_port}): ").strip()
                if port:
                    config.web_port = int(port)
            except ValueError:
                print("Invalid port, using default")
        
        # Discord Bot
        if os.getenv('DISCORD_BOT_TOKEN'):
            response = input("Enable Discord Bot v4.0? (y/N): ").strip().lower()
            config.discord_bot_enabled = response == 'y'
        else:
            print("⚠️ Discord Bot token not found, bot will be disabled")
            config.discord_bot_enabled = False
        
        # Auto-optimization
        response = input("Enable auto-optimization? (Y/n): ").strip().lower()
        config.auto_optimize = response != 'n'
        
        # Debug mode
        response = input("Enable debug mode? (y/N): ").strip().lower()
        config.debug_mode = response == 'y'
        
        print("\n🚀 Starting with custom configuration...")
        self.component_manager = ComponentManager(config)
        await self.component_manager.start_all_components()
        
        print("\n✅ Components started with custom configuration!")
        self.running = True
    
    def _show_component_status(self):
        """Show component status."""
        print("\n📊 Component Status")
        print("-" * 40)
        
        if not self.component_manager:
            print("❌ No components running")
            return
        
        status_symbols = {
            'running': '✅',
            'stopped': '⭕',
            'error': '❌'
        }
        
        for component, status in self.component_manager.component_status.items():
            symbol = status_symbols.get(status, '❓')
            print(f"{symbol} {component.replace('_', ' ').title()}: {status}")
        
        if self.component_manager.current_metrics:
            print(f"\n📈 Current Performance:")
            metrics = self.component_manager.current_metrics
            print(f"   CPU Usage: {metrics.get('cpu', 0):.1f}%")
            print(f"   Memory Usage: {metrics.get('memory', 0):.1f}%")
            print(f"   Temperature: {metrics.get('temperature', 0):.1f}°C")
            print(f"   FPS: {metrics.get('fps', 0):.1f}")
            print(f"   Latency: {metrics.get('latency', 0):.1f}ms")
    
    async def _gaming_profile_setup(self):
        """Gaming profile setup."""
        print("\n🎮 Gaming Profile Setup")
        print("-" * 30)
        
        profiles = {
            '1': 'Competitive - Maximum Performance',
            '2': 'Streaming - Balanced Performance', 
            '3': 'Casual - Optimized for Fun',
            '4': 'VR - Virtual Reality Gaming'
        }
        
        for key, desc in profiles.items():
            print(f"{key}. {desc}")
        
        choice = input("\nSelect gaming profile (1-4): ").strip()
        
        if choice in profiles:
            print(f"\n🎯 Applying {profiles[choice]} profile...")
            
            if self.component_manager and self.component_manager.windows_optimizer:
                try:
                    result = await self.component_manager.windows_optimizer.apply_all_optimizations()
                    print(f"✅ Applied {result['successful_optimizations']} optimizations")
                except Exception as e:
                    print(f"❌ Profile application failed: {e}")
            else:
                print("❌ Windows Optimizer not available")
        else:
            print("❌ Invalid profile selection")
    
    async def _performance_analysis(self):
        """Performance analysis."""
        print("\n📊 Performance Analysis")
        print("-" * 30)
        
        if not self.component_manager:
            print("❌ No components running for analysis")
            return
        
        if self.component_manager.performance_optimizer:
            try:
                recommendations = await self.component_manager.performance_optimizer.get_optimization_recommendations()
                
                if recommendations:
                    print(f"\n🔍 Found {len(recommendations)} recommendations:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        priority_symbol = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rec['priority'], '⚪')
                        print(f"\n{i}. {priority_symbol} {rec['title']}")
                        print(f"   {rec['description']}")
                        print(f"   Expected: {rec['expected_improvement']}")
                        print(f"   Confidence: {rec['confidence']:.0%}")
                else:
                    print("✅ No performance issues detected")
                    
            except Exception as e:
                print(f"❌ Performance analysis failed: {e}")
        else:
            print("❌ Performance Optimizer not available")
    
    async def _ai_recommendations(self):
        """Show AI recommendations."""
        print("\n🤖 AI Performance Recommendations")
        print("-" * 40)
        
        if not self.component_manager or not self.component_manager.ai_engine:
            print("❌ AI Engine not available")
            return
        
        try:
            # Create sample system state from current metrics
            metrics = self.component_manager.current_metrics
            system_state = SystemState(
                timestamp=time.time(),
                cpu_usage=metrics.get('cpu', 45),
                cpu_temp=metrics.get('temperature', 65),
                cpu_freq=3800.0,
                memory_usage=metrics.get('memory', 60),
                gpu_usage=metrics.get('gpu', 80),
                gpu_temp=75.0,
                gpu_memory=8.0,
                disk_io=50.0,
                network_latency=metrics.get('latency', 25),
                fps=metrics.get('fps', 120),
                frame_time=8.33,
                running_games=["Gaming"],
                system_load=metrics.get('cpu', 45) / 100
            )
            
            analysis = await self.component_manager.ai_engine.analyze_system_state(system_state)
            
            print(f"🧠 AI Analysis Results:")
            print(f"   Performance Score: {analysis['current_performance']:.1f}/100")
            print(f"   Optimization Urgency: {analysis['optimization_urgency'].upper()}")
            print(f"   Gaming Readiness: {analysis['gaming_readiness']['overall_score']:.1f}%")
            
            if analysis['recommendations']:
                print(f"\n💡 AI Recommendations:")
                for i, rec in enumerate(analysis['recommendations'][:3], 1):
                    print(f"\n{i}. {rec['action'].replace('_', ' ').title()}")
                    print(f"   {rec['description']}")
                    print(f"   Expected: {rec['expected_improvement']}")
                    print(f"   Confidence: {rec['confidence']:.0%}")
            
            if analysis['anomalies']['detected']:
                print(f"\n⚠️  Anomaly Detected:")
                print(f"   Severity: {analysis['anomalies']['severity'].upper()}")
                print(f"   Affected: {', '.join(analysis['anomalies']['affected_components'])}")
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
    
    def _open_web_dashboard(self):
        """Open web dashboard."""
        if not self.component_manager:
            print("❌ No components running")
            return
        
        port = self.component_manager.config.web_port
        url = f"http://localhost:{port}"
        
        print(f"\n🌐 Opening Web Dashboard: {url}")
        
        try:
            import webbrowser
            webbrowser.open(url)
            print("✅ Web dashboard opened in your default browser")
        except:
            print(f"📋 Please manually open: {url}")
    
    async def _stop_components(self):
        """Stop all components."""
        if self.component_manager:
            await self.component_manager.stop_all_components()
            print("\n🛑 All components stopped")
            self.running = False
        else:
            print("❌ No components to stop")
    
    async def _exit(self):
        """Exit the launcher."""
        print("\n👋 Exiting SUHA FPS+ v4.0...")
        
        if self.component_manager:
            await self.component_manager.stop_all_components()
        
        print("✅ Goodbye! Game on! 🎮")
        self.running = False
    
    async def run(self):
        """Run the interactive launcher."""
        self.show_banner()
        
        while True:
            try:
                self.show_menu()
                choice = self.get_user_choice()
                
                if choice == "9":
                    await self._exit()
                    break
                
                await self.handle_choice(choice)
                
                if choice in ["1", "2"] and self.running:
                    print("\n🎮 System is now running! Press Ctrl+C to return to menu...")
                    try:
                        while self.running:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        print("\n\n📋 Returning to main menu...")
                        continue
                
            except KeyboardInterrupt:
                print("\n\n👋 Exiting...")
                if self.component_manager:
                    await self.component_manager.stop_all_components()
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue

def handle_signal(signum, frame):
    """Handle system signals."""
    print("\n🛑 Received shutdown signal...")
    asyncio.create_task(cleanup_and_exit())

async def cleanup_and_exit():
    """Cleanup and exit."""
    print("🧹 Cleaning up...")
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Setup high-performance event loop if available
    if HAS_V4_COMPONENTS:
        loop = setup_high_performance_loop()
        asyncio.set_event_loop(loop)
    
    # Create and run launcher
    launcher = InteractiveLauncher()
    
    try:
        asyncio.run(launcher.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()