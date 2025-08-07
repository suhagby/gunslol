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

def main_menu():
    """Display main menu and handle user selection."""
    while True:
        print_banner()
        print("\nSelect an option:")
        print("1. 🚀 Run Enhanced System Optimization")
        print("2. 📊 Start Web Monitoring Dashboard") 
        print("3. 🖥️  Run Full Performance Monitor (GUI)")
        print("4. 📈 System Status Check")
        print("5. 🔧 Quick System Cleanup")
        print("6. ❌ Exit")
        
        try:
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                run_enhanced_optimization()
            elif choice == '2':
                run_web_dashboard()
            elif choice == '3':
                run_full_monitor()
            elif choice == '4':
                system_status_check()
            elif choice == '5':
                quick_cleanup()
            elif choice == '6':
                print("👋 Goodbye! Game on!")
                sys.exit(0)
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Game on!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
        print()  # Add spacing

def run_enhanced_optimization():
    """Run the enhanced system optimization."""
    print("🚀 Starting Enhanced System Optimization...")
    try:
        result = subprocess.run([sys.executable, 'enhanced_optimizer.py'], 
                              capture_output=False)
        if result.returncode == 0:
            print("✅ Optimization completed successfully!")
        else:
            print("⚠️ Optimization completed with warnings.")
    except Exception as e:
        print(f"❌ Optimization failed: {e}")

def run_web_dashboard():
    """Start the web monitoring dashboard."""
    print("📊 Starting Web Monitoring Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print("💡 Open this URL on your secondary display for monitoring.")
    print("⚠️ Press Ctrl+C to stop the dashboard")
    
    try:
        subprocess.run([sys.executable, 'web_dashboard.py'])
    except KeyboardInterrupt:
        print("\n📊 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Dashboard failed to start: {e}")

def run_full_monitor():
    """Run the full performance monitor with GUI."""
    print("🖥️ Starting Full Performance Monitor...")
    try:
        result = subprocess.run([sys.executable, 'main.py'], 
                              capture_output=False)
        if result.returncode == 0:
            print("✅ Monitor stopped successfully!")
        else:
            print("⚠️ Monitor stopped with warnings.")
    except Exception as e:
        print(f"❌ Monitor failed to start: {e}")

def system_status_check():
    """Quick system status check."""
    print("📈 Checking System Status...")
    
    try:
        import psutil
        
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        
        # Memory info
        memory = psutil.virtual_memory()
        
        # Disk info
        disk = psutil.disk_usage('/')
        
        print(f"\n🖥️ CPU Usage: {cpu_percent:.1f}%")
        if cpu_freq:
            print(f"🔄 CPU Frequency: {cpu_freq.current:.0f} MHz")
        print(f"🧠 Memory Usage: {memory.percent:.1f}% ({memory.used/1024**3:.1f} GB / {memory.total/1024**3:.1f} GB)")
        print(f"💾 Disk Usage: {(disk.used/disk.total)*100:.1f}% ({disk.free/1024**3:.1f} GB free)")
        
        # Temperature (if available)
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    print(f"\n🌡️ Temperatures:")
                    for name, entries in temps.items():
                        if entries:
                            max_temp = max(entry.current for entry in entries)
                            print(f"   {name}: {max_temp:.1f}°C")
        except:
            print("🌡️ Temperature monitoring not available")
        
        # Network info
        try:
            net_io = psutil.net_io_counters()
            print(f"\n🌐 Network: {net_io.bytes_sent/1024**2:.1f} MB sent, {net_io.bytes_recv/1024**2:.1f} MB received")
        except:
            pass
        
        # Performance recommendations
        print(f"\n💡 Performance Tips:")
        if cpu_percent > 80:
            print("   ⚠️ High CPU usage detected - consider closing background applications")
        if memory.percent > 85:
            print("   ⚠️ High memory usage detected - consider running memory cleanup")
        if (disk.used/disk.total) > 0.9:
            print("   ⚠️ Low disk space - consider cleaning up files")
        if cpu_percent < 50 and memory.percent < 70:
            print("   ✅ System performance looks good!")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def quick_cleanup():
    """Perform quick system cleanup."""
    print("🔧 Running Quick System Cleanup...")
    
    try:
        import psutil
        import subprocess
        
        cleanup_actions = []
        
        # Clear system caches (Linux)
        try:
            result = subprocess.run(['sync'], capture_output=True, text=True)
            if result.returncode == 0:
                cleanup_actions.append("System buffers synced")
        except:
            pass
        
        # Clear temporary files
        try:
            import tempfile
            import shutil
            temp_dir = tempfile.gettempdir()
            temp_files = [f for f in Path(temp_dir).iterdir() if f.is_file() and f.stat().st_mtime < time.time() - 86400]  # Files older than 1 day
            for temp_file in temp_files[:10]:  # Limit to 10 files for safety
                try:
                    temp_file.unlink()
                    cleanup_actions.append(f"Removed temp file: {temp_file.name}")
                except:
                    pass
        except:
            pass
        
        # Memory cleanup
        try:
            before_memory = psutil.virtual_memory()
            # Force garbage collection
            import gc
            gc.collect()
            after_memory = psutil.virtual_memory()
            freed_memory = before_memory.used - after_memory.used
            if freed_memory > 0:
                cleanup_actions.append(f"Freed {freed_memory/1024**2:.1f} MB of memory")
        except:
            pass
        
        print(f"\n✅ Cleanup completed! Actions performed:")
        for action in cleanup_actions:
            print(f"   - {action}")
        
        if not cleanup_actions:
            print("   - No cleanup actions needed at this time")
            
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)