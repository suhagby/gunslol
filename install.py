#!/usr/bin/env python3
"""
SUHA FPS+ v4.0 - Smart Installation and Setup Script
Intelligent installation with dependency management and system optimization
"""

import os
import sys
import subprocess
import json
import time
import platform
import shutil
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SUHAInstaller:
    """Smart installer for SUHA FPS+ v4.0."""
    
    def __init__(self):
        self.system_info = self.detect_system()
        self.installation_path = Path.cwd()
        self.python_executable = sys.executable
        self.log_entries = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log installation progress."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log_entries.append(log_entry)
        
        # Color coding for terminal output
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"     # Reset
        }
        
        color = colors.get(level, colors["RESET"])
        print(f"{color}{log_entry}{colors['RESET']}")
    
    def detect_system(self) -> Dict[str, str]:
        """Detect system information."""
        return {
            "os": platform.system(),
            "os_version": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "processor": platform.processor() or "Unknown"
        }
    
    def display_header(self):
        """Display installation header."""
        header = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SUHA FPS+ v4.0 SMART INSTALLER                       ║
║                   Neural Gaming Performance System                       ║
║                                                                          ║
║  🤖 AI Engine v4.0        ⚡ Performance Optimizer v4.0                 ║
║  🖥️  Windows Optimizer     🌐 Enhanced Web Interface                     ║
║  🤖 Discord Bot v4.0      📊 Real-time System Monitoring                ║
╚══════════════════════════════════════════════════════════════════════════╝

System Information:
  OS: {self.system_info['os']} {self.system_info['os_version']}
  Architecture: {self.system_info['architecture']}
  Python: {self.system_info['python_version']}
  Processor: {self.system_info['processor']}
"""
        print(header)
    
    def check_python_version(self) -> bool:
        """Check if Python version is supported."""
        self.log("Checking Python version...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.log("Python 3.8+ required. Please upgrade Python.", "ERROR")
            return False
        
        self.log(f"Python {version.major}.{version.minor}.{version.micro} - Compatible ✅", "SUCCESS")
        return True
    
    def check_system_requirements(self) -> bool:
        """Check system requirements."""
        self.log("Checking system requirements...")
        
        try:
            # Check available RAM
            if self.system_info['os'] == 'Windows':
                import psutil
                total_ram_gb = psutil.virtual_memory().total / (1024**3)
            else:
                # For Linux/Mac, try to get memory info
                try:
                    with open('/proc/meminfo', 'r') as f:
                        meminfo = f.read()
                        total_kb = int([line for line in meminfo.split('\n') if 'MemTotal' in line][0].split()[1])
                        total_ram_gb = total_kb / (1024**2)
                except:
                    total_ram_gb = 8  # Assume minimum
            
            if total_ram_gb < 4:
                self.log(f"RAM: {total_ram_gb:.1f}GB - Insufficient (4GB minimum)", "WARNING")
            elif total_ram_gb < 8:
                self.log(f"RAM: {total_ram_gb:.1f}GB - Basic (8GB recommended)", "WARNING")
            else:
                self.log(f"RAM: {total_ram_gb:.1f}GB - Excellent ✅", "SUCCESS")
            
            # Check disk space
            disk_free_gb = shutil.disk_usage('.').free / (1024**3)
            if disk_free_gb < 2:
                self.log(f"Disk space: {disk_free_gb:.1f}GB - Insufficient", "ERROR")
                return False
            else:
                self.log(f"Disk space: {disk_free_gb:.1f}GB available ✅", "SUCCESS")
            
        except ImportError:
            self.log("Could not check system resources (missing psutil)", "WARNING")
        
        return True
    
    def create_directory_structure(self) -> bool:
        """Create necessary directories."""
        self.log("Creating directory structure...")
        
        directories = [
            'logs',
            'config', 
            'models',
            'web_templates',
            'data',
            'backups',
            'temp'
        ]
        
        try:
            for directory in directories:
                dir_path = self.installation_path / directory
                dir_path.mkdir(exist_ok=True)
                self.log(f"  📁 {directory}/")
            
            self.log("Directory structure created ✅", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"Failed to create directories: {e}", "ERROR")
            return False
    
    def create_virtual_environment(self) -> bool:
        """Create Python virtual environment."""
        self.log("Setting up virtual environment...")
        
        venv_path = self.installation_path / "venv"
        
        try:
            if venv_path.exists():
                self.log("Virtual environment already exists", "INFO")
            else:
                subprocess.run([
                    self.python_executable, "-m", "venv", str(venv_path)
                ], check=True)
                self.log("Virtual environment created ✅", "SUCCESS")
            
            # Determine activation script path
            if self.system_info['os'] == 'Windows':
                activate_script = venv_path / "Scripts" / "activate.bat"
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:
                activate_script = venv_path / "bin" / "activate"
                pip_path = venv_path / "bin" / "pip"
            
            if not pip_path.exists():
                # Fallback for different Python installations
                pip_path = venv_path / "Scripts" / "pip" if self.system_info['os'] == 'Windows' else venv_path / "bin" / "pip"
            
            self.pip_executable = str(pip_path)
            return True
            
        except subprocess.CalledProcessError as e:
            self.log(f"Failed to create virtual environment: {e}", "ERROR")
            return False
    
    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        self.log("Installing dependencies...")
        
        # Core dependencies that must be installed
        core_deps = [
            "psutil>=5.9.0",
            "flask>=2.3.0", 
            "flask-socketio>=5.3.0",
            "pyyaml>=6.0",
            "requests>=2.28.0",
            "colorlog>=6.7.0"
        ]
        
        # AI/ML dependencies (install if possible)
        ai_deps = [
            "numpy>=1.21.0",
            "scipy>=1.9.0",
            "scikit-learn>=1.1.0",
            "pandas>=1.5.0"
        ]
        
        # Communication dependencies
        comm_deps = [
            "aiohttp>=3.8.0",
            "aiofiles>=22.1.0"
        ]
        
        # Optional dependencies
        optional_deps = [
            "discord.py>=2.3.0",
            "matplotlib>=3.6.0",
            "plotly>=5.15.0"
        ]
        
        def install_package_list(packages: List[str], description: str, required: bool = True) -> int:
            """Install a list of packages."""
            self.log(f"Installing {description}...")
            success_count = 0
            
            for package in packages:
                try:
                    self.log(f"  Installing {package}...")
                    subprocess.run([
                        self.pip_executable, "install", package, 
                        "--quiet", "--no-cache-dir"
                    ], check=True, timeout=120)
                    
                    self.log(f"  ✅ {package}", "SUCCESS")
                    success_count += 1
                    
                except subprocess.TimeoutExpired:
                    self.log(f"  ⏱️ Timeout installing {package}", "WARNING")
                except subprocess.CalledProcessError:
                    if required:
                        self.log(f"  ❌ Failed to install {package}", "ERROR")
                    else:
                        self.log(f"  ⚠️ Optional package {package} failed", "WARNING")
                except Exception as e:
                    self.log(f"  ❌ Error installing {package}: {e}", "ERROR")
            
            return success_count
        
        # Install dependencies in order of importance
        core_success = install_package_list(core_deps, "core dependencies", required=True)
        ai_success = install_package_list(ai_deps, "AI/ML dependencies", required=False)
        comm_success = install_package_list(comm_deps, "communication dependencies", required=False)
        opt_success = install_package_list(optional_deps, "optional dependencies", required=False)
        
        total_expected = len(core_deps)
        total_installed = core_success
        
        self.log(f"Dependency installation complete:", "INFO")
        self.log(f"  Core: {core_success}/{len(core_deps)}", "INFO")
        self.log(f"  AI/ML: {ai_success}/{len(ai_deps)}", "INFO")
        self.log(f"  Communication: {comm_success}/{len(comm_deps)}", "INFO")
        self.log(f"  Optional: {opt_success}/{len(optional_deps)}", "INFO")
        
        if core_success < len(core_deps):
            self.log("⚠️ Some core dependencies failed to install", "WARNING")
            return False
        
        self.log("✅ Essential dependencies installed successfully", "SUCCESS")
        return True
    
    def create_configuration_files(self) -> bool:
        """Create default configuration files."""
        self.log("Creating configuration files...")
        
        try:
            # Master configuration
            master_config = {
                "ai_engine_enabled": True,
                "performance_optimizer_enabled": True,
                "windows_optimizer_enabled": self.system_info['os'] == 'Windows',
                "web_dashboard_enabled": True,
                "discord_bot_enabled": False,
                "neural_launcher_enabled": True,
                "web_dashboard_port": 5000,
                "api_port": 5001,
                "websocket_port": 5002,
                "ai_learning_enabled": True,
                "ai_prediction_horizon": 60,
                "performance_monitoring_interval": 1.0,
                "auto_optimization_enabled": True,
                "max_workers": min(8, os.cpu_count() or 4),
                "api_rate_limit": 60,
                "secure_mode": False,
                "require_admin": False
            }
            
            config_path = self.installation_path / "config" / "master_config.json"
            with open(config_path, 'w') as f:
                json.dump(master_config, f, indent=2)
            
            self.log("  📄 master_config.json", "SUCCESS")
            
            # Environment template
            env_template = """# SUHA FPS+ v4.0 Environment Configuration
# Copy this to .env and configure your settings

# Discord Bot Token (optional)
DISCORD_BOT_TOKEN=

# AI Engine Settings
AI_LEARNING_ENABLED=true
AI_MODEL_PATH=models/neural_performance_v4.pth

# Performance Settings
PERFORMANCE_MONITORING_INTERVAL=1.0
AUTO_OPTIMIZATION_ENABLED=true

# Security Settings
API_RATE_LIMIT=60
SECURE_MODE=false

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
"""
            
            env_path = self.installation_path / ".env.example"
            with open(env_path, 'w') as f:
                f.write(env_template)
            
            self.log("  📄 .env.example", "SUCCESS")
            
            # Create launcher scripts for Windows
            if self.system_info['os'] == 'Windows':
                self.create_windows_shortcuts()
            
            return True
            
        except Exception as e:
            self.log(f"Failed to create configuration files: {e}", "ERROR")
            return False
    
    def create_windows_shortcuts(self):
        """Create Windows desktop shortcuts."""
        try:
            # Create a simple batch file for easy launching
            batch_content = f'''@echo off
cd /d "{self.installation_path}"
call venv\\Scripts\\activate.bat
python master_launcher.py
pause
'''
            
            batch_path = self.installation_path / "Launch_SUHA_FPS.bat"
            with open(batch_path, 'w') as f:
                f.write(batch_content)
            
            self.log("  📄 Launch_SUHA_FPS.bat", "SUCCESS")
            
            # Web dashboard launcher
            web_batch_content = f'''@echo off
cd /d "{self.installation_path}"
call venv\\Scripts\\activate.bat
python web_dashboard.py
pause
'''
            
            web_batch_path = self.installation_path / "Launch_Web_Dashboard.bat"
            with open(web_batch_path, 'w') as f:
                f.write(web_batch_content)
            
            self.log("  📄 Launch_Web_Dashboard.bat", "SUCCESS")
            
        except Exception as e:
            self.log(f"Failed to create Windows shortcuts: {e}", "WARNING")
    
    def run_initial_tests(self) -> bool:
        """Run initial system tests."""
        self.log("Running initial system tests...")
        
        try:
            # Test basic imports
            test_imports = [
                "psutil",
                "flask", 
                "yaml",
                "json",
                "requests"
            ]
            
            failed_imports = []
            for module in test_imports:
                try:
                    __import__(module)
                    self.log(f"  ✅ {module}")
                except ImportError:
                    failed_imports.append(module)
                    self.log(f"  ❌ {module}")
            
            if failed_imports:
                self.log(f"Some imports failed: {failed_imports}", "WARNING")
                return False
            
            # Test basic functionality
            try:
                import psutil
                cpu_count = psutil.cpu_count()
                memory = psutil.virtual_memory()
                self.log(f"  System test: {cpu_count} CPU cores, {memory.total/1024**3:.1f}GB RAM", "SUCCESS")
            except Exception as e:
                self.log(f"  System test failed: {e}", "WARNING")
            
            self.log("Initial tests completed ✅", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Initial tests failed: {e}", "ERROR")
            return False
    
    def display_completion_message(self):
        """Display installation completion message."""
        message = f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    🎉 INSTALLATION COMPLETED SUCCESSFULLY! 🎉              ║
╚══════════════════════════════════════════════════════════════════════════╝

🚀 SUHA FPS+ v4.0 Neural Gaming Performance System is ready!

📁 Installation Location: {self.installation_path}

🎮 Quick Start Options:
  
  Option 1 - Master Launcher (Recommended):
    python master_launcher.py --quick-start
  
  Option 2 - Interactive Menu:
    python master_launcher.py
  
  Option 3 - Web Dashboard Only:
    python web_dashboard.py
"""

        if self.system_info['os'] == 'Windows':
            message += """
  Option 4 - Windows Batch Files:
    Double-click: Launch_SUHA_FPS.bat
    Or: Launch_Web_Dashboard.bat
"""

        message += f"""
🌐 Web Dashboard: http://localhost:5000
📊 System Monitor: Real-time performance tracking
🤖 AI Engine: Neural performance optimization
⚡ Performance Optimizer: Automated system tuning

⚙️ Configuration:
  Edit: config/master_config.json
  Environment: Copy .env.example to .env

📝 Logs: Check logs/ directory for system logs

🆘 Need Help?
  - Check README.md for detailed documentation
  - Run: python master_launcher.py --health-check
  - View logs in logs/master_launcher.log

Ready to transform your gaming experience! 🎮✨
"""
        
        print(message)
    
    def save_installation_log(self):
        """Save installation log to file."""
        try:
            log_path = self.installation_path / "logs" / "installation.log"
            with open(log_path, 'w') as f:
                f.write("SUHA FPS+ v4.0 Installation Log\n")
                f.write("=" * 50 + "\n\n")
                for entry in self.log_entries:
                    f.write(entry + "\n")
            
            self.log(f"Installation log saved to: {log_path}", "INFO")
        except Exception as e:
            self.log(f"Failed to save installation log: {e}", "WARNING")
    
    def run_installation(self) -> bool:
        """Run the complete installation process."""
        self.display_header()
        
        # Installation steps
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking system requirements", self.check_system_requirements),
            ("Creating directory structure", self.create_directory_structure),
            ("Setting up virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Creating configuration files", self.create_configuration_files),
            ("Running initial tests", self.run_initial_tests),
        ]
        
        self.log("Starting SUHA FPS+ v4.0 installation...", "INFO")
        start_time = time.time()
        
        for step_name, step_function in steps:
            self.log(f"\n{'='*60}", "INFO")
            self.log(f"Step: {step_name}", "INFO")
            self.log(f"{'='*60}", "INFO")
            
            try:
                if not step_function():
                    self.log(f"Installation failed at step: {step_name}", "ERROR")
                    self.save_installation_log()
                    return False
            except Exception as e:
                self.log(f"Error in step '{step_name}': {e}", "ERROR")
                self.save_installation_log()
                return False
        
        # Calculate installation time
        install_time = time.time() - start_time
        self.log(f"\n🎉 Installation completed in {install_time:.1f} seconds!", "SUCCESS")
        
        self.save_installation_log()
        self.display_completion_message()
        return True

def main():
    """Main installation entry point."""
    print("🤖 SUHA FPS+ v4.0 Smart Installer Starting...")
    
    installer = SUHAInstaller()
    
    try:
        success = installer.run_installation()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Installation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()