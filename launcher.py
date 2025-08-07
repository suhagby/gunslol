#!/usr/bin/env python3
"""
Enhanced Interactive launcher for the PC Gaming Performance Monitor.
Now redirects to the Ultimate Gaming Launcher with all advanced features.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║              🎮 PC Gaming Performance Monitor 🎮             ║
║                   Ultimate Launcher Redirect                 ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main entry point - redirect to ultimate launcher."""
    print_banner()
    print("🚀 Starting Ultimate Gaming Performance Optimizer...")
    
    # Path to the ultimate launcher
    project_root = Path(__file__).parent.absolute()
    ultimate_launcher_path = project_root / 'ultimate_gaming_launcher.py'
    
    if ultimate_launcher_path.exists():
        try:
            # Launch the ultimate launcher
            result = subprocess.run([sys.executable, str(ultimate_launcher_path)], 
                                  cwd=str(project_root))
            return result.returncode
        except Exception as e:
            print(f"❌ Error launching ultimate launcher: {e}")
            return 1
    else:
        # Fallback to basic menu
        print("⚠️ Ultimate launcher not found, using basic launcher...")
        return basic_launcher()

def basic_launcher():
    """Basic launcher fallback."""
    menu_options = [
        ("1", "📊 Launch Web Dashboard", "web_dashboard.py"),
        ("2", "🚀 Enhanced System Optimization", "enhanced_optimizer.py"), 
        ("3", "🖥️ Full System Monitor", "main.py"),
        ("4", "📈 Enhanced Web Dashboard", "enhanced_web_dashboard.py"),
        ("0", "🚪 Exit", None)
    ]
    
    project_root = Path(__file__).parent.absolute()
    
    while True:
        try:
            print("\n┌────────────────── MAIN MENU ──────────────────┐")
            for choice, description, _ in menu_options:
                print(f"│  {choice}. {description:<40} │")
            print("└───────────────────────────────────────────────┘")
            
            choice = input("\n🎮 Select an option: ").strip()
            
            if choice == '0':
                break
            
            # Find the selected option
            selected_option = next((opt for opt in menu_options if opt[0] == choice), None)
            
            if selected_option and selected_option[2]:
                tool_path = project_root / selected_option[2]
                if tool_path.exists():
                    print(f"🚀 Launching {selected_option[1]}...")
                    subprocess.run([sys.executable, str(tool_path)], cwd=str(project_root))
                else:
                    print(f"❌ Tool not found: {tool_path}")
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\n⏎ Press Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())