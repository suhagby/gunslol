#!/usr/bin/env python3
"""SUHA FPS+ System Status Checker"""
import os
import sys
import psutil
import json
from pathlib import Path
from typing import Dict, Any

def check_system_status() -> Dict[str, Any]:
    """Check comprehensive system status."""
    status = {
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "system": {
            "os": __import__('platform').system(),
            "python_version": sys.version,
            "cpu_count": os.cpu_count(),
        },
        "resources": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0
        },
        "components": {},
        "health": "unknown"
    }
    
    # Check component files
    components = [
        "master_launcher.py",
        "web_dashboard.py", 
        "ai_engine_v4.py",
        "advanced_performance_optimizer_v4.py",
        "windows_optimizer_v4.py",
        "discord_bot_v4.py"
    ]
    
    for component in components:
        if Path(component).exists():
            status["components"][component] = "available"
        else:
            status["components"][component] = "missing"
    
    # Overall health
    available_count = sum(1 for v in status["components"].values() if v == "available")
    if available_count >= 4:
        status["health"] = "good"
    elif available_count >= 2:
        status["health"] = "fair"
    else:
        status["health"] = "poor"
    
    return status

def main():
    status = check_system_status()
    print("🔍 SUHA FPS+ System Status")
    print("=" * 40)
    print(f"Health: {status['health'].upper()}")
    print(f"OS: {status['system']['os']}")
    print(f"CPU Usage: {status['resources']['cpu_percent']}%")
    print(f"Memory Usage: {status['resources']['memory_percent']}%")
    print()
    print("Components:")
    for comp, stat in status['components'].items():
        icon = "✅" if stat == "available" else "❌"
        print(f"  {icon} {comp}")
    
    return status

if __name__ == "__main__":
    main()
