#!/usr/bin/env python3
"""
SUHA FPS+ v3.0 - Main Launcher
The ultimate gaming performance optimizer with AI and Discord integration.
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

def print_banner():
    """Print the SUHA FPS+ banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                           🎮 SUHA FPS+ VERSION 3.0 🎮                            ║
║                     Next-Generation Gaming Performance Optimizer                 ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║                                                                                   ║
║  ⚡ REVOLUTIONARY 2025+ GAMING TECHNOLOGY                                        ║
║                                                                                   ║
║  🤖 Advanced AI System              🎯 Discord Bot Integration                   ║
║  📊 Real-time Analytics             🔔 Smart Notifications                      ║
║  🌐 Enhanced Web Dashboard          ⚡ Intelligent Optimization                 ║
║  🎨 Beautiful Interface             🚀 Future-Ready Architecture                ║
║  📈 Predictive Performance          🎮 Gaming-First Design                      ║
║                                                                                   ║
║                        🏆 TOP-TIER GAMING PERFORMANCE 🏆                        ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    
    # Show system info
    try:
        import psutil
        cpu_count = psutil.cpu_count()
        memory_gb = round(psutil.virtual_memory().total / (1024**3), 1)
        print(f"🖥️  System: {cpu_count} cores, {memory_gb}GB RAM")
    except ImportError:
        print("🖥️  System: Information not available")
    
    print(f"🐍 Python: {sys.version.split()[0]}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def show_main_menu():
    """Show the main menu options."""
    print("┌────────────────────── MAIN MENU ──────────────────────┐")
    print("│                                                        │")
    print("│  1. 🚀 Quick Start (Launch All Components)           │") 
    print("│  2. ⚙️  Configuration & Setup                          │")
    print("│  3. 🤖 AI System Only                                 │")
    print("│  4. 🎮 Discord Bot Only                               │")
    print("│  5. 🌐 Web Dashboard Only                             │")
    print("│  6. 📊 Performance Monitor Only                       │")
    print("│  7. 🔧 Component Manager                              │")
    print("│  8. 📝 View System Status                             │")
    print("│  9. 🆘 Help & Documentation                           │")
    print("│  0. 🚪 Exit                                           │")
    print("│                                                        │")
    print("└────────────────────────────────────────────────────────┘")

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = {
        'psutil': 'System monitoring',
        'flask': 'Web dashboard',
        'discord': 'Discord bot',
        'numpy': 'AI system'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}: OK")
        except ImportError:
            missing_packages.append((package, description))
            print(f"❌ {package}: Missing ({description})")
    
    if missing_packages:
        print("\n⚠️ Missing dependencies detected!")
        print("Install with:")
        packages = ' '.join([pkg for pkg, _ in missing_packages])
        print(f"pip install {packages}")
        return False
    
    return True

def launch_component(component_name: str, script_name: str):
    """Launch a specific component."""
    script_path = project_root / script_name
    
    if not script_path.exists():
        print(f"❌ Component script not found: {script_name}")
        return False
    
    try:
        print(f"🚀 Launching {component_name}...")
        
        # Launch in new process
        if sys.platform.startswith('win'):
            # Windows
            subprocess.Popen([sys.executable, str(script_path)], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            # Unix/Linux
            subprocess.Popen([sys.executable, str(script_path)])
        
        print(f"✅ {component_name} launched successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to launch {component_name}: {e}")
        return False

def quick_start():
    """Quick start - launch all components."""
    print("\n🚀 SUHA FPS+ Quick Start")
    print("─" * 30)
    
    if not check_dependencies():
        print("\n❌ Cannot start - missing dependencies")
        input("Press Enter to continue...")
        return
    
    print("\n🔄 Starting all components...")
    
    # Launch configuration script (which handles everything)
    config_script = project_root / "suha_fps_config.py"
    
    if config_script.exists():
        try:
            print("🚀 Launching SUHA FPS+ Configuration Manager...")
            subprocess.run([sys.executable, str(config_script)])
        except KeyboardInterrupt:
            print("\n🛑 Startup cancelled by user")
        except Exception as e:
            print(f"❌ Failed to start configuration manager: {e}")
    else:
        print("❌ Configuration script not found!")
        print("Falling back to individual components...")
        
        # Fallback to individual launches
        components = [
            ("AI System", "advanced_ai_system.py"),
            ("Web Dashboard", "enhanced_web_dashboard.py"),
            ("Performance Monitor", "main.py")
        ]
        
        for name, script in components:
            launch_component(name, script)
            time.sleep(1)
    
    input("\nPress Enter to continue...")

def configuration_setup():
    """Launch configuration setup."""
    print("\n⚙️ Configuration & Setup")
    print("─" * 25)
    
    config_script = project_root / "suha_fps_config.py"
    
    if config_script.exists():
        try:
            subprocess.run([sys.executable, str(config_script)])
        except KeyboardInterrupt:
            print("\n🛑 Configuration cancelled")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    else:
        print("❌ Configuration script not found!")
    
    input("Press Enter to continue...")

def show_system_status():
    """Show system status."""
    print("\n📊 SUHA FPS+ System Status")
    print("─" * 30)
    
    try:
        import psutil
        
        # System info
        print("🖥️  System Information:")
        print(f"   CPU: {psutil.cpu_count()} cores at {psutil.cpu_percent()}% usage")
        
        memory = psutil.virtual_memory()
        print(f"   Memory: {memory.percent}% used ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
        
        # Check for running processes
        print("\n🔄 Component Status:")
        
        component_keywords = {
            'suha_fps_config.py': 'Configuration Manager',
            'discord_bot.py': 'Discord Bot',
            'advanced_ai_system.py': 'AI System', 
            'enhanced_web_dashboard.py': 'Web Dashboard',
            'main.py': 'Performance Monitor'
        }
        
        running_components = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline:
                    cmdline_str = ' '.join(cmdline)
                    for keyword, component_name in component_keywords.items():
                        if keyword in cmdline_str:
                            running_components.append((component_name, proc.info['pid']))
                            break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if running_components:
            for component_name, pid in running_components:
                print(f"   ✅ {component_name} (PID: {pid})")
        else:
            print("   ❌ No SUHA FPS+ components currently running")
        
        # Check network status
        print(f"\n🌐 Network Status:")
        try:
            network = psutil.net_io_counters()
            print(f"   Sent: {network.bytes_sent / (1024**2):.1f}MB")
            print(f"   Received: {network.bytes_recv / (1024**2):.1f}MB")
        except:
            print("   Network info unavailable")
        
    except ImportError:
        print("❌ psutil not available for detailed system info")
    
    # Check log files
    log_dir = project_root / "logs"
    if log_dir.exists():
        log_files = list(log_dir.glob("*.log"))
        print(f"\n📝 Log Files: {len(log_files)} found in logs/")
        
        # Show recent log entries
        if log_files:
            latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
            print(f"   Latest: {latest_log.name}")
    
    input("\nPress Enter to continue...")

def show_help():
    """Show help and documentation."""
    print("\n🆘 SUHA FPS+ Help & Documentation")
    print("═" * 40)
    
    help_text = """
🎮 SUHA FPS+ v3.0 - Next-Generation Gaming Optimizer

📋 FEATURES:
  🤖 Advanced AI System - Intelligent performance analysis and optimization
  🎯 Discord Bot - Real-time notifications and remote monitoring  
  🌐 Web Dashboard - Beautiful real-time performance visualization
  📊 Performance Monitor - Comprehensive system monitoring
  ⚡ Smart Optimization - Automatic performance improvements

🚀 QUICK START:
  1. Select "Quick Start" from main menu
  2. Follow configuration prompts
  3. Set up Discord bot token (optional)
  4. Launch all components

⚙️ CONFIGURATION:
  • All settings stored in suha_fps_config.json
  • Use Configuration & Setup menu for easy setup
  • Discord bot requires token from Discord Developer Portal

🎯 DISCORD BOT SETUP:
  1. Go to https://discord.com/developers/applications
  2. Create new application
  3. Go to 'Bot' section and create bot
  4. Copy bot token
  5. Invite bot to server with admin permissions
  6. Enter token in SUHA FPS+ configuration

📊 WEB DASHBOARD:
  • Access at http://localhost:5000 (default)
  • Real-time system monitoring
  • Performance graphs and charts
  • Mobile-friendly responsive design

🤖 AI SYSTEM:
  • Learns your system's performance patterns
  • Predicts potential issues before they occur  
  • Provides intelligent optimization recommendations
  • Adapts to your gaming habits

📝 LOGS:
  • All logs stored in logs/ directory
  • Separate log files for each component
  • Debug information for troubleshooting

🔧 TROUBLESHOOTING:
  • Check system status for running components
  • View logs for error messages
  • Ensure all dependencies are installed
  • Run with administrator privileges on Windows

📞 SUPPORT:
  • Check logs/ directory for error details
  • Report issues with system information
  • Include configuration file (suha_fps_config.json)
    """
    
    print(help_text)
    input("\nPress Enter to continue...")

def main():
    """Main application loop."""
    while True:
        try:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Show banner and menu
            print_banner()
            show_main_menu()
            
            # Get user choice
            choice = input("\n🎯 Select option: ").strip()
            
            if choice == '1':
                quick_start()
            elif choice == '2':
                configuration_setup()
            elif choice == '3':
                launch_component("AI System", "advanced_ai_system.py")
                input("Press Enter to continue...")
            elif choice == '4':
                launch_component("Discord Bot", "discord_bot.py")
                input("Press Enter to continue...")
            elif choice == '5':
                launch_component("Web Dashboard", "enhanced_web_dashboard.py")
                input("Press Enter to continue...")
            elif choice == '6':
                launch_component("Performance Monitor", "main.py")
                input("Press Enter to continue...")
            elif choice == '7':
                configuration_setup()  # Component manager is in config
            elif choice == '8':
                show_system_status()
            elif choice == '9':
                show_help()
            elif choice == '0':
                print("\n👋 Thank you for using SUHA FPS+!")
                print("🎮 Keep gaming at peak performance!")
                break
            else:
                print("❌ Invalid option. Please try again.")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("Press Enter to continue...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())