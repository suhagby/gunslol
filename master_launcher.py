#!/usr/bin/env python3
"""
SUHA FPS+ v4.0 - Master Gaming Performance System Launcher
Comprehensive production-ready launcher for all system components
"""

import asyncio
import sys
import os
import subprocess
import json
import time
import threading
import signal
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import logging
from datetime import datetime

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/master_launcher.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure logs directory exists
Path('logs').mkdir(exist_ok=True)

@dataclass
class ComponentStatus:
    """Status of a system component."""
    name: str
    running: bool = False
    pid: Optional[int] = None
    port: Optional[int] = None
    health: str = "unknown"  # healthy, warning, error, unknown
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0

@dataclass
class SystemConfiguration:
    """Master system configuration."""
    # Component toggles
    ai_engine_enabled: bool = True
    performance_optimizer_enabled: bool = True
    windows_optimizer_enabled: bool = True
    web_dashboard_enabled: bool = True
    discord_bot_enabled: bool = False  # Disabled by default due to token requirement
    neural_launcher_enabled: bool = True
    
    # Network settings
    web_dashboard_port: int = 5000
    api_port: int = 5001
    websocket_port: int = 5002
    
    # AI settings
    ai_learning_enabled: bool = True
    ai_prediction_horizon: int = 60
    ai_model_path: str = "models/neural_performance_v4.pth"
    
    # Performance settings
    performance_monitoring_interval: float = 1.0
    auto_optimization_enabled: bool = True
    max_workers: int = 8
    
    # Discord settings
    discord_bot_token: Optional[str] = None
    
    # Security settings
    api_rate_limit: int = 60
    secure_mode: bool = False
    require_admin: bool = False

class DependencyManager:
    """Manages system dependencies and installations."""
    
    REQUIRED_PACKAGES = [
        'psutil>=5.9.0',
        'numpy>=1.21.0',
        'scipy>=1.9.0', 
        'flask>=2.3.0',
        'flask-socketio>=5.3.0',
        'pyyaml>=6.0',
        'requests>=2.28.0',
        'colorlog>=6.7.0',
        'aiofiles>=22.1.0',
        'aiohttp>=3.8.0'
    ]
    
    OPTIONAL_PACKAGES = [
        'torch>=1.13.0',
        'torchvision>=0.14.0', 
        'scikit-learn>=1.1.0',
        'pandas>=1.5.0',
        'discord.py>=2.3.0',
        'matplotlib>=3.6.0',
        'plotly>=5.15.0'
    ]
    
    @staticmethod
    def check_package_installed(package_name: str) -> bool:
        """Check if a package is installed."""
        try:
            package_name_only = package_name.split('>=')[0].split('[')[0]
            __import__(package_name_only.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    @staticmethod
    def install_package(package: str, optional: bool = False) -> bool:
        """Install a single package."""
        try:
            logger.info(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '--break-system-packages', '--no-cache-dir',
                '--timeout=30', package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully installed {package}")
                return True
            else:
                if optional:
                    logger.warning(f"⚠️ Optional package {package} failed to install: {result.stderr}")
                else:
                    logger.error(f"❌ Failed to install {package}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Exception installing {package}: {e}")
            return False
    
    def install_dependencies(self) -> Tuple[int, int]:
        """Install all required and optional dependencies."""
        logger.info("🔧 Installing system dependencies...")
        
        required_installed = 0
        optional_installed = 0
        
        # Install required packages
        for package in self.REQUIRED_PACKAGES:
            if not self.check_package_installed(package):
                if self.install_package(package):
                    required_installed += 1
            else:
                required_installed += 1
                logger.info(f"✅ {package} already installed")
        
        # Install optional packages
        for package in self.OPTIONAL_PACKAGES:
            if not self.check_package_installed(package):
                if self.install_package(package, optional=True):
                    optional_installed += 1
            else:
                optional_installed += 1
                logger.info(f"✅ {package} already installed")
        
        logger.info(f"📊 Dependencies: {required_installed}/{len(self.REQUIRED_PACKAGES)} required, {optional_installed}/{len(self.OPTIONAL_PACKAGES)} optional")
        return required_installed, optional_installed

class ComponentManager:
    """Manages individual system components."""
    
    def __init__(self, config: SystemConfiguration):
        self.config = config
        self.components: Dict[str, ComponentStatus] = {}
        self.processes: Dict[str, subprocess.Popen] = {}
        self.shutdown_requested = False
        
        # Initialize component statuses
        self._init_component_statuses()
    
    def _init_component_statuses(self):
        """Initialize component status tracking."""
        components = [
            "ai_engine", "performance_optimizer", "windows_optimizer",
            "web_dashboard", "discord_bot", "neural_launcher"
        ]
        
        for comp in components:
            self.components[comp] = ComponentStatus(name=comp)
    
    def start_component(self, component_name: str) -> bool:
        """Start a specific component."""
        try:
            if component_name in self.processes:
                logger.warning(f"⚠️ Component {component_name} already running")
                return True
            
            script_map = {
                "ai_engine": "ai_engine_v4.py",
                "performance_optimizer": "advanced_performance_optimizer_v4.py", 
                "windows_optimizer": "windows_optimizer_v4.py",
                "web_dashboard": "web_dashboard.py",
                "discord_bot": "discord_bot_v4.py",
                "neural_launcher": "neural_launcher_v4.py"
            }
            
            if component_name not in script_map:
                logger.error(f"❌ Unknown component: {component_name}")
                return False
            
            script_path = Path(script_map[component_name])
            if not script_path.exists():
                logger.error(f"❌ Script not found: {script_path}")
                return False
            
            # Start the process
            logger.info(f"🚀 Starting {component_name}...")
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes[component_name] = process
            self.components[component_name].running = True
            self.components[component_name].pid = process.pid
            self.components[component_name].last_check = datetime.now()
            
            logger.info(f"✅ Started {component_name} (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {component_name}: {e}")
            return False
    
    def stop_component(self, component_name: str) -> bool:
        """Stop a specific component."""
        try:
            if component_name not in self.processes:
                logger.warning(f"⚠️ Component {component_name} not running")
                return True
            
            process = self.processes[component_name]
            logger.info(f"🛑 Stopping {component_name}...")
            
            # Graceful shutdown
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Force killing {component_name}...")
                process.kill()
                process.wait()
            
            del self.processes[component_name]
            self.components[component_name].running = False
            self.components[component_name].pid = None
            self.components[component_name].last_check = datetime.now()
            
            logger.info(f"✅ Stopped {component_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop {component_name}: {e}")
            return False
    
    def check_component_health(self, component_name: str) -> bool:
        """Check if a component is healthy."""
        try:
            if component_name not in self.processes:
                return False
            
            process = self.processes[component_name]
            
            # Check if process is still running
            if process.poll() is not None:
                logger.warning(f"⚠️ Component {component_name} has stopped unexpectedly")
                self.components[component_name].running = False
                self.components[component_name].health = "error"
                return False
            
            # Update resource usage (if psutil available)
            try:
                import psutil
                proc = psutil.Process(process.pid)
                self.components[component_name].cpu_usage = proc.cpu_percent()
                self.components[component_name].memory_usage = proc.memory_percent()
            except ImportError:
                pass
            
            self.components[component_name].health = "healthy"
            self.components[component_name].last_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ Health check failed for {component_name}: {e}")
            self.components[component_name].health = "error"
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "components": {name: asdict(status) for name, status in self.components.items()},
            "total_processes": len(self.processes),
            "config": asdict(self.config)
        }

class WebDashboardManager:
    """Manages the enhanced web dashboard."""
    
    def __init__(self, config: SystemConfiguration, component_manager: ComponentManager):
        self.config = config
        self.component_manager = component_manager
        self.app = None
        
    def create_web_app(self):
        """Create enhanced Flask application."""
        try:
            from flask import Flask, render_template, jsonify, request
            from flask_socketio import SocketIO, emit
        except ImportError:
            logger.error("❌ Flask not available for web dashboard")
            return None
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'suha_fps_neural_2040'
        socketio = SocketIO(app, cors_allowed_origins="*")
        
        @app.route('/')
        def dashboard():
            """Main dashboard route."""
            return render_template('enhanced_neural_interface.html')
        
        @app.route('/api/status')
        def api_status():
            """API endpoint for system status."""
            return jsonify(self.component_manager.get_system_status())
        
        @app.route('/api/component/<component_name>/start', methods=['POST'])
        def api_start_component(component_name):
            """API endpoint to start a component."""
            success = self.component_manager.start_component(component_name)
            return jsonify({"success": success, "component": component_name})
        
        @app.route('/api/component/<component_name>/stop', methods=['POST'])
        def api_stop_component(component_name):
            """API endpoint to stop a component."""
            success = self.component_manager.stop_component(component_name)
            return jsonify({"success": success, "component": component_name})
        
        @socketio.on('request_status')
        def handle_status_request():
            """Handle WebSocket status requests."""
            emit('status_update', self.component_manager.get_system_status())
        
        self.app = app
        self.socketio = socketio
        return app
    
    def start_dashboard(self):
        """Start the web dashboard server."""
        if not self.app:
            self.create_web_app()
        
        if self.app:
            logger.info(f"🌐 Starting web dashboard on port {self.config.web_dashboard_port}")
            self.socketio.run(self.app, 
                            host='0.0.0.0', 
                            port=self.config.web_dashboard_port,
                            debug=False)

class MasterLauncher:
    """Main launcher class orchestrating all components."""
    
    def __init__(self):
        self.config = SystemConfiguration()
        self.dependency_manager = DependencyManager()
        self.component_manager = ComponentManager(self.config)
        self.web_dashboard = WebDashboardManager(self.config, self.component_manager)
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("🛑 Shutdown signal received")
        self.shutdown()
    
    def load_configuration(self, config_path: str = "config/master_config.json") -> bool:
        """Load configuration from file."""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration
                for key, value in config_data.items():
                    if hasattr(self.config, key):
                        setattr(self.config, key, value)
                
                logger.info(f"✅ Configuration loaded from {config_path}")
                return True
            else:
                logger.warning(f"⚠️ Configuration file not found: {config_path}")
                self.save_configuration(config_path)
                return False
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            return False
    
    def save_configuration(self, config_path: str = "config/master_config.json") -> bool:
        """Save configuration to file."""
        try:
            config_file = Path(config_path)
            config_file.parent.mkdir(exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2, default=str)
            
            logger.info(f"✅ Configuration saved to {config_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install all required dependencies."""
        required, optional = self.dependency_manager.install_dependencies()
        
        if required < len(self.dependency_manager.REQUIRED_PACKAGES):
            logger.error("❌ Not all required dependencies could be installed")
            return False
        
        return True
    
    def start_all_components(self) -> bool:
        """Start all enabled components."""
        logger.info("🚀 Starting all enabled components...")
        
        success_count = 0
        total_count = 0
        
        if self.config.ai_engine_enabled:
            total_count += 1
            if self.component_manager.start_component("ai_engine"):
                success_count += 1
        
        if self.config.performance_optimizer_enabled:
            total_count += 1
            if self.component_manager.start_component("performance_optimizer"):
                success_count += 1
        
        if self.config.windows_optimizer_enabled and os.name == 'nt':
            total_count += 1
            if self.component_manager.start_component("windows_optimizer"):
                success_count += 1
        
        if self.config.discord_bot_enabled and self.config.discord_bot_token:
            total_count += 1
            if self.component_manager.start_component("discord_bot"):
                success_count += 1
        
        logger.info(f"📊 Started {success_count}/{total_count} components")
        
        # Start web dashboard last
        if self.config.web_dashboard_enabled:
            threading.Thread(target=self.web_dashboard.start_dashboard, daemon=True).start()
            time.sleep(2)  # Give web server time to start
            logger.info(f"🌐 Web dashboard available at http://localhost:{self.config.web_dashboard_port}")
        
        return success_count > 0
    
    def monitor_components(self):
        """Continuously monitor component health."""
        logger.info("📊 Starting component monitoring...")
        
        while self.running:
            for component_name in self.component_manager.components.keys():
                if self.component_manager.components[component_name].running:
                    self.component_manager.check_component_health(component_name)
            
            time.sleep(self.config.performance_monitoring_interval)
    
    def shutdown(self):
        """Graceful shutdown of all components."""
        logger.info("🛑 Initiating system shutdown...")
        self.running = False
        
        # Stop all components
        for component_name in list(self.component_manager.processes.keys()):
            self.component_manager.stop_component(component_name)
        
        logger.info("✅ System shutdown complete")
    
    def run_interactive_mode(self):
        """Run in interactive menu mode."""
        while True:
            self.display_menu()
            choice = input("\n👉 Enter your choice (1-12): ").strip()
            
            if choice == '1':
                self.quick_start()
            elif choice == '2':
                self.configure_system()
            elif choice == '3':
                self.display_component_status()
            elif choice == '4':
                self.install_dependencies()
            elif choice == '5':
                self.start_all_components()
            elif choice == '6':
                self.open_web_dashboard()
            elif choice == '7':
                self.run_health_check()
            elif choice == '8':
                self.view_logs()
            elif choice == '9':
                self.backup_configuration()
            elif choice == '10':
                self.reset_system()
            elif choice == '11':
                self.shutdown()
                break
            elif choice == '12':
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def display_menu(self):
        """Display the main menu."""
        status = self.component_manager.get_system_status()
        running_count = sum(1 for comp in status['components'].values() if comp['running'])
        
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                           SUHA FPS+ v4.0 MASTER LAUNCHER                ║
║                      Neural Gaming Performance System                    ║
║                                                                          ║
║  🤖 AI Engine v4.0        ⚡ Performance Optimizer v4.0               ║
║  🖥️  Windows Optimizer     🌐 Enhanced Web Interface                   ║ 
║  🤖 Discord Bot v4.0      📊 Real-time System Monitoring               ║
║                                                                          ║
║  Status: {running_count}/6 components running                                      ║
╚══════════════════════════════════════════════════════════════════════════╝

════════════════════════════════════════════════════════════════════════════
🚀 MASTER CONTROL PANEL
════════════════════════════════════════════════════════════════════════════
1.  ⚡ Quick Start (Install + Launch All)
2.  ⚙️  System Configuration
3.  📊 Component Status
4.  🔧 Install Dependencies
5.  🚀 Start All Components
6.  🌐 Open Web Dashboard
7.  🏥 Run Health Check
8.  📝 View System Logs
9.  💾 Backup Configuration
10. 🔄 Reset System
11. 🛑 Shutdown All
12. ❌ Exit
════════════════════════════════════════════════════════════════════════════""")
    
    def quick_start(self):
        """Quick start: install dependencies and launch all components."""
        print("\n🚀 Quick Start: Installing dependencies and launching system...")
        
        if self.install_dependencies():
            print("✅ Dependencies installed successfully")
            
            if self.start_all_components():
                print("✅ System launched successfully!")
                self.running = True
                
                # Start monitoring in background
                monitor_thread = threading.Thread(target=self.monitor_components, daemon=True)
                monitor_thread.start()
                
                print(f"🌐 Web dashboard: http://localhost:{self.config.web_dashboard_port}")
                print("📊 Monitoring started. Press Ctrl+C to stop.")
                
                try:
                    while self.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    self.shutdown()
            else:
                print("❌ Failed to start some components")
        else:
            print("❌ Failed to install required dependencies")
    
    def configure_system(self):
        """Interactive system configuration."""
        print("\n⚙️ System Configuration")
        print("=" * 50)
        
        # Component toggles
        self.config.ai_engine_enabled = input(f"Enable AI Engine? (y/n) [current: {'y' if self.config.ai_engine_enabled else 'n'}]: ").lower().startswith('y')
        self.config.performance_optimizer_enabled = input(f"Enable Performance Optimizer? (y/n) [current: {'y' if self.config.performance_optimizer_enabled else 'n'}]: ").lower().startswith('y')
        self.config.windows_optimizer_enabled = input(f"Enable Windows Optimizer? (y/n) [current: {'y' if self.config.windows_optimizer_enabled else 'n'}]: ").lower().startswith('y')
        self.config.web_dashboard_enabled = input(f"Enable Web Dashboard? (y/n) [current: {'y' if self.config.web_dashboard_enabled else 'n'}]: ").lower().startswith('y')
        
        # Discord bot token
        token_input = input(f"Discord Bot Token (leave empty to skip) [current: {'***' if self.config.discord_bot_token else 'none'}]: ").strip()
        if token_input:
            self.config.discord_bot_token = token_input
            self.config.discord_bot_enabled = True
        
        self.save_configuration()
        print("✅ Configuration updated successfully")
    
    def display_component_status(self):
        """Display detailed component status."""
        status = self.component_manager.get_system_status()
        
        print("\n📊 Component Status")
        print("=" * 80)
        print(f"{'Component':<20} {'Status':<10} {'PID':<8} {'Health':<10} {'CPU%':<8} {'Memory%':<8}")
        print("-" * 80)
        
        for name, comp in status['components'].items():
            status_icon = "🟢" if comp['running'] else "🔴"
            health_icon = {"healthy": "💚", "warning": "🟡", "error": "❌", "unknown": "⚫"}.get(comp['health'], "⚫")
            
            print(f"{name:<20} {status_icon} {'ON' if comp['running'] else 'OFF':<8} {comp['pid'] or 'N/A':<8} {health_icon} {comp['health']:<6} {comp['cpu_usage']:<7.1f} {comp['memory_usage']:<7.1f}")
        
        print("\n" + "=" * 80)
    
    def open_web_dashboard(self):
        """Open the web dashboard in browser."""
        url = f"http://localhost:{self.config.web_dashboard_port}"
        try:
            webbrowser.open(url)
            print(f"🌐 Opening web dashboard: {url}")
        except Exception as e:
            print(f"❌ Failed to open browser: {e}")
            print(f"🌐 Please manually open: {url}")
    
    def run_health_check(self):
        """Run comprehensive system health check."""
        print("\n🏥 Running System Health Check...")
        print("=" * 50)
        
        # Check Python version
        print(f"Python Version: {sys.version}")
        
        # Check dependencies
        print("\nDependency Check:")
        for package in self.dependency_manager.REQUIRED_PACKAGES:
            if self.dependency_manager.check_package_installed(package):
                print(f"✅ {package}")
            else:
                print(f"❌ {package} - MISSING")
        
        # Check component health
        print("\nComponent Health:")
        for component_name in self.component_manager.components.keys():
            health = self.component_manager.check_component_health(component_name)
            print(f"{'✅' if health else '❌'} {component_name}")
        
        print("\n✅ Health check complete")
    
    def view_logs(self):
        """Display recent log entries."""
        log_file = Path('logs/master_launcher.log')
        if log_file.exists():
            print("\n📝 Recent Log Entries (last 20 lines):")
            print("=" * 80)
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for line in lines[-20:]:
                    print(line.rstrip())
        else:
            print("📝 No log file found")
    
    def backup_configuration(self):
        """Backup current configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"config/backup_config_{timestamp}.json"
        self.save_configuration(backup_path)
        print(f"💾 Configuration backed up to: {backup_path}")
    
    def reset_system(self):
        """Reset system to default configuration."""
        confirm = input("⚠️ This will reset all configuration. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            self.config = SystemConfiguration()
            self.save_configuration()
            print("✅ System reset to default configuration")
        else:
            print("❌ Reset cancelled")

def main():
    """Main entry point."""
    print("🚀 SUHA FPS+ v4.0 Master Launcher Starting...")
    
    # Ensure required directories exist
    for directory in ['logs', 'config', 'models', 'web_templates']:
        Path(directory).mkdir(exist_ok=True)
    
    launcher = MasterLauncher()
    
    # Load configuration
    launcher.load_configuration()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick-start':
            launcher.quick_start()
        elif sys.argv[1] == '--install-deps':
            launcher.install_dependencies()
        elif sys.argv[1] == '--health-check':
            launcher.run_health_check()
        elif sys.argv[1] == '--daemon':
            launcher.quick_start()
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                launcher.shutdown()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Available options: --quick-start, --install-deps, --health-check, --daemon")
    else:
        # Interactive mode
        launcher.run_interactive_mode()

if __name__ == "__main__":
    main()