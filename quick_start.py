#!/usr/bin/env python3
"""SUHA FPS+ Quick Start Script"""
import sys
import os
import time
import subprocess
from pathlib import Path

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SUHA FPS+ v4.0 QUICK START                           ║
║                  Neural Gaming Performance System                        ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    
    print("🚀 Starting SUHA FPS+ v4.0...")
    
    # Check if we're in the right directory
    if not Path("master_launcher.py").exists():
        print("❌ master_launcher.py not found. Please run from the project directory.")
        return False
    
    print("1. Starting system status check...")
    try:
        import system_status
        status = system_status.check_system_status()
        print(f"   System health: {status['health']}")
    except Exception as e:
        print(f"   Status check failed: {e}")
    
    print("2. Starting web dashboard...")
    try:
        # Start web dashboard in background
        subprocess.Popen([sys.executable, "web_dashboard.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        time.sleep(2)
        print("   ✅ Web dashboard started on http://localhost:5000")
    except Exception as e:
        print(f"   ⚠️  Web dashboard failed: {e}")
    
    print("3. Starting master launcher...")
    try:
        os.system(f"{sys.executable} master_launcher.py")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"   ❌ Master launcher failed: {e}")
    
    print("✅ SUHA FPS+ session complete")
    return True

if __name__ == "__main__":
    main()
