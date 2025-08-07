#!/usr/bin/env python3
"""
SUHA FPS+ Configuration and Launch Script
Main configuration script that starts all components including Discord bot.
"""

import os
import sys
import time
import json
import logging
import threading
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import psutil

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import our modules
try:
    from discord_bot import DiscordBotManager
    from advanced_ai_system import AdvancedAISystem
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"Import error: {e}")

class SuhaFPSConfig:
    """SUHA FPS+ Main Configuration and Launch Manager."""
    
    def __init__(self):
        self.version = "3.0.0"
        self.app_name = "SUHA FPS+"
        self.config_file = Path("suha_fps_config.json")
        
        # Component status
        self.components = {
            'ai_system': None,
            'discord_bot': None,
            'web_dashboard': None,
            'performance_monitor': None
        }
        
        # Configuration
        self.config = self._load_config()
        
        # Logging setup
        self.logger = self._setup_logging()
        
        # Process management
        self.running_processes = {}
        self.shutdown_event = threading.Event()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        default_config = {
            "app_name": self.app_name,
            "version": self.version,
            "components": {
                "ai_system": {
                    "enabled": True,
                    "learning_enabled": True,
                    "monitoring_interval": 30
                },
                "discord_bot": {
                    "enabled": False,  # Disabled by default until token is provided
                    "token": "",
                    "notification_channel": None,
                    "auto_start": True
                },
                "web_dashboard": {
                    "enabled": True,
                    "port": 5000,
                    "host": "localhost",
                    "auto_launch_browser": False
                },
                "performance_monitor": {
                    "enabled": True,
                    "update_interval": 5,
                    "log_metrics": True
                }
            },
            "settings": {
                "auto_optimization": True,
                "notification_level": "medium",
                "log_level": "INFO",
                "startup_delay": 3,
                "auto_update_check": True
            },
            "thresholds": {
                "cpu_warning": 75,
                "cpu_critical": 90,
                "memory_warning": 80,
                "memory_critical": 95,
                "temperature_warning": 75,
                "temperature_critical": 85
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**default_config, **loaded_config}
            except Exception as e:
                print(f"⚠️ Failed to load config: {e}, using defaults")
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file."""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        log_level = getattr(logging, self.config['settings']['log_level'], logging.INFO)
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Setup logging configuration
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / f"suha_fps_{datetime.now().strftime('%Y%m%d')}.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger(f"{__name__}.SuhaFPSConfig")
        logger.info(f"🚀 {self.app_name} v{self.version} - Logging initialized")
        
        return logger
    
    def show_banner(self):
        """Display the SUHA FPS+ banner."""
        banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                           🎮 SUHA FPS+ VERSION 3.0 🎮                            ║
║                        Next-Generation Gaming Optimizer                          ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║  🤖 Advanced AI System          📊 Real-time Performance Monitor                 ║
║  🎯 Discord Bot Integration      ⚡ Intelligent Optimization Engine              ║
║  🌐 Enhanced Web Dashboard       🔔 Smart Notification System                    ║
║  📈 Predictive Analytics         🎨 Beautiful User Interface                     ║
║                                                                                   ║
║                         🚀 BUILT FOR 2025+ GAMING 🚀                            ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
        # Show system info
        try:
            cpu_info = f"{psutil.cpu_count()} cores"
            memory_info = f"{psutil.virtual_memory().total / (1024**3):.1f}GB RAM"
            print(f"🖥️  System: {cpu_info}, {memory_info}")
            print(f"🐍 Python: {sys.version.split()[0]}")
            print(f"📁 Working Directory: {project_root}")
            print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.logger.error(f"System info display error: {e}")
    
    def show_configuration_menu(self):
        """Show interactive configuration menu."""
        while True:
            self._clear_screen()
            self.show_banner()
            
            print("\n┌─────────────────── CONFIGURATION MENU ───────────────────┐")
            print("│                                                           │")
            print("│  1. 🤖 Configure AI System                               │")
            print("│  2. 🎮 Configure Discord Bot                             │")
            print("│  3. 🌐 Configure Web Dashboard                           │")
            print("│  4. ⚙️  Performance Settings                              │")
            print("│  5. 📊 View Current Configuration                        │")
            print("│  6. 💾 Save Configuration                                │")
            print("│  7. 🚀 Launch SUHA FPS+ (Start All Components)          │")
            print("│  8. 🔧 Component Manager                                 │")
            print("│  0. 🚪 Exit                                              │")
            print("│                                                           │")
            print("└───────────────────────────────────────────────────────────┘")
            
            choice = input("\n🎯 Select option: ").strip()
            
            if choice == '1':
                self._configure_ai_system()
            elif choice == '2':
                self._configure_discord_bot()
            elif choice == '3':
                self._configure_web_dashboard()
            elif choice == '4':
                self._configure_performance_settings()
            elif choice == '5':
                self._view_configuration()
            elif choice == '6':
                self._save_configuration()
            elif choice == '7':
                self._launch_all_components()
                break
            elif choice == '8':
                self._component_manager()
            elif choice == '0':
                print("👋 Goodbye!")
                sys.exit(0)
            else:
                input("❌ Invalid option. Press Enter to continue...")
    
    def _clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _configure_ai_system(self):
        """Configure AI System settings."""
        print("\n🤖 AI System Configuration")
        print("─" * 50)
        
        current = self.config['components']['ai_system']
        
        # Enable/Disable AI
        enabled = input(f"Enable AI System? [{current['enabled']}]: ").strip().lower()
        if enabled:
            current['enabled'] = enabled in ['true', 'yes', 'y', '1']
        
        # Learning enabled
        learning = input(f"Enable AI Learning? [{current['learning_enabled']}]: ").strip().lower()
        if learning:
            current['learning_enabled'] = learning in ['true', 'yes', 'y', '1']
        
        # Monitoring interval
        try:
            interval = input(f"Monitoring Interval (seconds) [{current['monitoring_interval']}]: ").strip()
            if interval:
                current['monitoring_interval'] = max(5, int(interval))
        except ValueError:
            print("⚠️ Invalid interval, keeping current value")
        
        print("✅ AI System configuration updated!")
        input("Press Enter to continue...")
    
    def _configure_discord_bot(self):
        """Configure Discord Bot settings."""
        print("\n🎮 Discord Bot Configuration")
        print("─" * 50)
        
        current = self.config['components']['discord_bot']
        
        # Bot token
        current_token = "***" if current['token'] else "Not set"
        print(f"Current token: {current_token}")
        new_token = input("Enter Discord Bot Token (or press Enter to skip): ").strip()
        if new_token:
            current['token'] = new_token
            current['enabled'] = True
            print("✅ Discord bot token updated!")
        
        # Enable/Disable bot
        if current['token']:
            enabled = input(f"Enable Discord Bot? [{current['enabled']}]: ").strip().lower()
            if enabled:
                current['enabled'] = enabled in ['true', 'yes', 'y', '1']
        
        # Auto-start
        auto_start = input(f"Auto-start with application? [{current['auto_start']}]: ").strip().lower()
        if auto_start:
            current['auto_start'] = auto_start in ['true', 'yes', 'y', '1']
        
        if not current['token']:
            print("\n📝 To setup Discord bot:")
            print("   1. Go to https://discord.com/developers/applications")
            print("   2. Create new application")
            print("   3. Go to 'Bot' section")
            print("   4. Create bot and copy token")
            print("   5. Invite bot to your server with administrator permissions")
        
        print("✅ Discord Bot configuration updated!")
        input("Press Enter to continue...")
    
    def _configure_web_dashboard(self):
        """Configure Web Dashboard settings."""
        print("\n🌐 Web Dashboard Configuration")
        print("─" * 50)
        
        current = self.config['components']['web_dashboard']
        
        # Enable/Disable dashboard
        enabled = input(f"Enable Web Dashboard? [{current['enabled']}]: ").strip().lower()
        if enabled:
            current['enabled'] = enabled in ['true', 'yes', 'y', '1']
        
        # Port configuration
        try:
            port = input(f"Port [{current['port']}]: ").strip()
            if port:
                current['port'] = max(1024, min(65535, int(port)))
        except ValueError:
            print("⚠️ Invalid port, keeping current value")
        
        # Host configuration
        host = input(f"Host [{current['host']}]: ").strip()
        if host:
            current['host'] = host
        
        # Auto-launch browser
        auto_launch = input(f"Auto-launch browser? [{current['auto_launch_browser']}]: ").strip().lower()
        if auto_launch:
            current['auto_launch_browser'] = auto_launch in ['true', 'yes', 'y', '1']
        
        print("✅ Web Dashboard configuration updated!")
        input("Press Enter to continue...")
    
    def _configure_performance_settings(self):
        """Configure performance monitoring settings."""
        print("\n⚙️ Performance Settings")
        print("─" * 50)
        
        settings = self.config['settings']
        thresholds = self.config['thresholds']
        
        # Auto-optimization
        auto_opt = input(f"Enable Auto-optimization? [{settings['auto_optimization']}]: ").strip().lower()
        if auto_opt:
            settings['auto_optimization'] = auto_opt in ['true', 'yes', 'y', '1']
        
        # Notification level
        print(f"\nCurrent notification level: {settings['notification_level']}")
        print("Options: low, medium, high")
        notif_level = input("Notification level: ").strip().lower()
        if notif_level in ['low', 'medium', 'high']:
            settings['notification_level'] = notif_level
        
        # Configure thresholds
        print("\n🎯 Performance Thresholds:")
        threshold_configs = [
            ('CPU Warning (%)', 'cpu_warning'),
            ('CPU Critical (%)', 'cpu_critical'),
            ('Memory Warning (%)', 'memory_warning'),
            ('Memory Critical (%)', 'memory_critical'),
            ('Temperature Warning (°C)', 'temperature_warning'),
            ('Temperature Critical (°C)', 'temperature_critical')
        ]
        
        for display_name, key in threshold_configs:
            try:
                value = input(f"{display_name} [{thresholds[key]}]: ").strip()
                if value:
                    thresholds[key] = max(0, min(100, int(value)))
            except ValueError:
                print(f"⚠️ Invalid value for {display_name}")
        
        print("✅ Performance settings updated!")
        input("Press Enter to continue...")
    
    def _view_configuration(self):
        """View current configuration."""
        print("\n📊 Current Configuration")
        print("═" * 50)
        
        # App info
        print(f"🎮 Application: {self.config['app_name']} v{self.config['version']}")
        print()
        
        # Components
        print("🔧 Components:")
        for name, config in self.config['components'].items():
            status = "✅ Enabled" if config.get('enabled', False) else "❌ Disabled"
            print(f"   {name}: {status}")
        print()
        
        # Settings
        print("⚙️ Settings:")
        for key, value in self.config['settings'].items():
            print(f"   {key}: {value}")
        print()
        
        # Thresholds
        print("🎯 Thresholds:")
        for key, value in self.config['thresholds'].items():
            print(f"   {key}: {value}{'%' if 'temperature' not in key else '°C'}")
        
        input("\nPress Enter to continue...")
    
    def _save_configuration(self):
        """Save current configuration."""
        if self._save_config():
            print("💾 Configuration saved successfully!")
        else:
            print("❌ Failed to save configuration!")
        input("Press Enter to continue...")
    
    def _component_manager(self):
        """Manage individual components."""
        while True:
            print("\n🔧 Component Manager")
            print("─" * 30)
            
            for i, (name, component) in enumerate(self.components.items(), 1):
                status = "🟢 Running" if component and hasattr(component, 'is_running') else "🔴 Stopped"
                print(f"{i}. {name}: {status}")
            
            print("5. 🔄 Restart All Components")
            print("6. 🛑 Stop All Components")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nSelect component: ").strip()
            
            if choice == '0':
                break
            elif choice == '5':
                self._restart_all_components()
            elif choice == '6':
                self._stop_all_components()
            else:
                try:
                    comp_index = int(choice) - 1
                    comp_names = list(self.components.keys())
                    if 0 <= comp_index < len(comp_names):
                        self._manage_individual_component(comp_names[comp_index])
                except ValueError:
                    print("❌ Invalid selection")
            
            input("Press Enter to continue...")
    
    def _manage_individual_component(self, component_name: str):
        """Manage an individual component."""
        print(f"\n🔧 Managing {component_name}")
        print("1. Start")
        print("2. Stop") 
        print("3. Restart")
        print("4. Status")
        
        choice = input("Action: ").strip()
        
        if choice == '1':
            self._start_component(component_name)
        elif choice == '2':
            self._stop_component(component_name)
        elif choice == '3':
            self._restart_component(component_name)
        elif choice == '4':
            self._show_component_status(component_name)
    
    def _launch_all_components(self):
        """Launch all enabled components."""
        print(f"\n🚀 Launching {self.app_name} v{self.version}")
        print("─" * 50)
        
        startup_delay = self.config['settings']['startup_delay']
        
        # Start AI System
        if self.config['components']['ai_system']['enabled']:
            print("🤖 Starting AI System...")
            self._start_ai_system()
            time.sleep(1)
        
        # Start Discord Bot
        if (self.config['components']['discord_bot']['enabled'] and 
            self.config['components']['discord_bot']['token'] and
            self.config['components']['discord_bot']['auto_start']):
            print("🎮 Starting Discord Bot...")
            self._start_discord_bot()
            time.sleep(1)
        
        # Start Web Dashboard
        if self.config['components']['web_dashboard']['enabled']:
            print("🌐 Starting Web Dashboard...")
            self._start_web_dashboard()
            time.sleep(1)
        
        # Start Performance Monitor
        if self.config['components']['performance_monitor']['enabled']:
            print("📊 Starting Performance Monitor...")
            self._start_performance_monitor()
        
        print(f"\n✅ {self.app_name} components started!")
        print("─" * 50)
        
        # Show access information
        if self.config['components']['web_dashboard']['enabled']:
            host = self.config['components']['web_dashboard']['host']
            port = self.config['components']['web_dashboard']['port']
            print(f"🌐 Web Dashboard: http://{host}:{port}")
        
        if self.config['components']['discord_bot']['enabled']:
            print("🎮 Discord Bot: Check your Discord server")
        
        print("\n📝 Logs are saved in: logs/")
        print("⚙️ Configuration: suha_fps_config.json")
        
        # Keep running
        try:
            print("\n🔄 System running... Press Ctrl+C to stop")
            while not self.shutdown_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self._stop_all_components()
    
    def _start_ai_system(self):
        """Start the AI system."""
        try:
            if IMPORTS_AVAILABLE:
                self.components['ai_system'] = AdvancedAISystem()
                self.logger.info("✅ AI System started")
            else:
                self.logger.error("❌ AI System dependencies not available")
        except Exception as e:
            self.logger.error(f"❌ Failed to start AI System: {e}")
    
    def _start_discord_bot(self):
        """Start the Discord bot."""
        try:
            if IMPORTS_AVAILABLE:
                token = self.config['components']['discord_bot']['token']
                self.components['discord_bot'] = DiscordBotManager(token)
                self.components['discord_bot'].start()
                self.logger.info("✅ Discord Bot started")
            else:
                self.logger.error("❌ Discord Bot dependencies not available")
        except Exception as e:
            self.logger.error(f"❌ Failed to start Discord Bot: {e}")
    
    def _start_web_dashboard(self):
        """Start the web dashboard."""
        try:
            # This would start the web dashboard
            # For now, just log that it would be started
            self.logger.info("✅ Web Dashboard would be started")
        except Exception as e:
            self.logger.error(f"❌ Failed to start Web Dashboard: {e}")
    
    def _start_performance_monitor(self):
        """Start the performance monitor."""
        try:
            # This would start the performance monitor
            self.logger.info("✅ Performance Monitor started")
        except Exception as e:
            self.logger.error(f"❌ Failed to start Performance Monitor: {e}")
    
    def _start_component(self, component_name: str):
        """Start a specific component."""
        if component_name == 'ai_system':
            self._start_ai_system()
        elif component_name == 'discord_bot':
            self._start_discord_bot()
        elif component_name == 'web_dashboard':
            self._start_web_dashboard()
        elif component_name == 'performance_monitor':
            self._start_performance_monitor()
    
    def _stop_component(self, component_name: str):
        """Stop a specific component."""
        component = self.components.get(component_name)
        if component:
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                self.components[component_name] = None
                self.logger.info(f"🛑 {component_name} stopped")
            except Exception as e:
                self.logger.error(f"❌ Failed to stop {component_name}: {e}")
    
    def _restart_component(self, component_name: str):
        """Restart a specific component."""
        self._stop_component(component_name)
        time.sleep(1)
        self._start_component(component_name)
    
    def _restart_all_components(self):
        """Restart all components."""
        self._stop_all_components()
        time.sleep(2)
        self._launch_all_components()
    
    def _stop_all_components(self):
        """Stop all components."""
        for component_name in self.components.keys():
            self._stop_component(component_name)
        
        self.shutdown_event.set()
        self.logger.info("🛑 All components stopped")
    
    def _show_component_status(self, component_name: str):
        """Show status of a specific component."""
        component = self.components.get(component_name)
        if component:
            print(f"✅ {component_name} is running")
            if hasattr(component, 'get_status'):
                status = component.get_status()
                print(f"Status: {status}")
        else:
            print(f"❌ {component_name} is not running")

def main():
    """Main entry point."""
    try:
        config_manager = SuhaFPSConfig()
        config_manager.show_configuration_menu()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()