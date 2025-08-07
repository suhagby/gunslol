#!/usr/bin/env python3
"""
AI Gaming Optimizer - Main Launcher
Enhanced version with AI-powered system analysis and intelligent optimization.
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_gaming_optimizer.log'),
        logging.StreamHandler()
    ]
)

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = {
        'psutil': 'System monitoring',
        'flask': 'Web dashboard',
        'flask_socketio': 'Real-time updates'
    }
    
    missing_packages = []
    for package, description in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing_packages.append((package, description))
    
    if missing_packages:
        print("❌ Missing required dependencies:")
        for package, description in missing_packages:
            print(f"  - {package}: {description}")
        print("\nInstall with: pip install psutil flask flask-socketio")
        return False
    
    return True

def display_banner():
    """Display the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         🤖 AI GAMING PERFORMANCE OPTIMIZER v2.0 🤖          ║
    ║                                                              ║
    ║  🎯 Expert-Level PC Analysis & Optimization                  ║
    ║  🛡️ Anti-Cheat Safe (CS2, Valorant, etc.)                  ║
    ║  🧠 Machine Learning System Analysis                         ║
    ║  ⚡ Real-Time Performance Monitoring                         ║
    ║  📊 Professional Web Dashboard                               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_system_info():
    """Show basic system information."""
    try:
        import psutil
        
        print("\n📊 SYSTEM OVERVIEW")
        print("=" * 50)
        
        # CPU Information
        cpu_count = psutil.cpu_count(logical=False)
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_usage = psutil.cpu_percent(interval=1)
        
        print(f"🔥 CPU: {cpu_count} cores ({cpu_count_logical} threads)")
        if cpu_freq:
            print(f"   Frequency: {cpu_freq.current:.0f} MHz (Max: {cpu_freq.max:.0f} MHz)")
        print(f"   Usage: {cpu_usage}%")
        
        # Memory Information
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        memory_available_gb = memory.available / (1024**3)
        
        print(f"💾 Memory: {memory_gb:.1f} GB total")
        print(f"   Available: {memory_available_gb:.1f} GB ({memory.percent}% used)")
        
        # Storage Information
        print("💿 Storage:")
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total_gb = usage.total / (1024**3)
                free_gb = usage.free / (1024**3)
                print(f"   {partition.device} {total_gb:.1f} GB ({free_gb:.1f} GB free)")
            except:
                continue
        
        # Network Information
        network = psutil.net_io_counters()
        if network:
            sent_mb = network.bytes_sent / (1024**2)
            recv_mb = network.bytes_recv / (1024**2)
            print(f"🌐 Network: {sent_mb:.1f} MB sent, {recv_mb:.1f} MB received")
        
        # Uptime
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_hours = uptime_seconds / 3600
        print(f"🕒 Uptime: {uptime_hours:.1f} hours")
        
    except Exception as e:
        print(f"❌ Error getting system info: {e}")

def run_ai_analysis():
    """Run AI system analysis."""
    try:
        print("\n🧠 RUNNING AI SYSTEM ANALYSIS...")
        print("=" * 50)
        
        from analyzers.ai_system_analyzer import AISystemAnalyzer
        from ai_notification_manager import AINotificationManager
        
        # Initialize AI analyzer
        analyzer = AISystemAnalyzer()
        notification_manager = AINotificationManager(analyzer)
        
        print("🔍 Analyzing system components...")
        analysis_results = analyzer.analyze_system(force=True)
        
        if not analysis_results:
            print("❌ Analysis failed")
            return
        
        # Display results
        summary = analysis_results.get('analysis_summary', {})
        issues = analysis_results.get('issues', {})
        recommendations = analysis_results.get('recommendations', {})
        detected_anticheats = analysis_results.get('detected_anticheats', [])
        
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"🏥 Health Score: {summary.get('overall_health_score', 100)}/100")
        print(f"⚠️ Total Issues: {summary.get('total_issues', 0)}")
        print(f"🎮 Gaming-Affecting Issues: {summary.get('gaming_affecting_issues', 0)}")
        print(f"🔧 Available Recommendations: {summary.get('total_recommendations', 0)}")
        print(f"⚡ Auto-Applicable: {summary.get('auto_applicable_recommendations', 0)}")
        print(f"📈 Performance Impact: {summary.get('performance_impact_level', 'Low').title()}")
        
        # Show anti-cheat detection
        if detected_anticheats:
            print(f"\n🛡️ DETECTED ANTI-CHEAT SYSTEMS:")
            for anticheat in detected_anticheats:
                anticheat_names = {
                    'vac': 'Valve Anti-Cheat (Steam/CS2)',
                    'vanguard': 'Riot Vanguard (Valorant)',
                    'battleye': 'BattlEye',
                    'easyanticheat': 'Easy Anti-Cheat'
                }
                print(f"   🛡️ {anticheat_names.get(anticheat, anticheat.title())}")
            print("   ✅ Safe mode activated - only anti-cheat compatible optimizations will be applied")
        
        # Show critical issues
        critical_issues = [issue for issue in issues.values() if issue.get('severity') == 'critical']
        if critical_issues:
            print(f"\n🔴 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"   • {issue.get('title')}: {issue.get('description')}")
                if issue.get('auto_fixable'):
                    print(f"     ✅ Can be automatically fixed")
        
        # Show warning issues
        warning_issues = [issue for issue in issues.values() if issue.get('severity') == 'warning']
        if warning_issues:
            print(f"\n🟠 WARNING ISSUES:")
            for issue in warning_issues[:3]:  # Show top 3
                print(f"   • {issue.get('title')}: {issue.get('description')}")
            if len(warning_issues) > 3:
                print(f"   ... and {len(warning_issues) - 3} more")
        
        # Show top recommendations
        high_priority_recs = [rec for rec in recommendations.values() if rec.get('priority', 0) >= 8]
        if high_priority_recs:
            print(f"\n⚡ HIGH-PRIORITY RECOMMENDATIONS:")
            for rec in high_priority_recs[:3]:  # Show top 3
                print(f"   • {rec.get('title')}: {rec.get('expected_improvement')}")
                if rec.get('auto_applicable'):
                    print(f"     🔧 Can be applied automatically")
        
        # Send notifications
        notification_manager.notify_ai_analysis_results(analysis_results)
        
        print(f"\n✅ Analysis completed successfully!")
        
        # Ask if user wants to apply automatic fixes
        auto_fixable = summary.get('auto_fixable_issues', 0)
        if auto_fixable > 0:
            print(f"\n🔧 {auto_fixable} issues can be automatically fixed.")
            response = input("Would you like to apply automatic fixes? (y/N): ").lower()
            if response == 'y':
                apply_automatic_optimizations(analyzer, notification_manager)
        
    except Exception as e:
        print(f"❌ Error during AI analysis: {e}")
        import traceback
        traceback.print_exc()

def apply_automatic_optimizations(analyzer, notification_manager):
    """Apply automatic optimizations."""
    try:
        print("\n🔧 APPLYING AUTOMATIC OPTIMIZATIONS...")
        print("=" * 50)
        
        results = analyzer.apply_automatic_fixes()
        
        successful = sum(1 for result in results.values() if result)
        total = len(results)
        failed = total - successful
        
        if successful > 0:
            print(f"✅ Successfully applied {successful} optimization(s)")
        
        if failed > 0:
            print(f"❌ Failed to apply {failed} optimization(s)")
        
        # Send notification
        notification_manager.notify_optimization_completed(results)
        
        print("\n📊 Optimization Results:")
        for optimization, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {optimization}")
        
    except Exception as e:
        print(f"❌ Error applying optimizations: {e}")

def start_web_dashboard():
    """Start the AI-enhanced web dashboard."""
    try:
        print("\n🌐 STARTING AI WEB DASHBOARD...")
        print("=" * 50)
        
        from ai_web_dashboard import AIEnhancedWebDashboard
        
        dashboard = AIEnhancedWebDashboard(port=5000)
        
        print("🚀 Dashboard starting...")
        print("📱 Access the dashboard at: http://localhost:5000")
        print("🔄 Real-time monitoring and AI analysis active")
        print("⏹️  Press Ctrl+C to stop\n")
        
        dashboard.run(debug=False, host='0.0.0.0')
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting web dashboard: {e}")
        import traceback
        traceback.print_exc()

def run_performance_test():
    """Run a quick performance test."""
    try:
        print("\n⚡ RUNNING PERFORMANCE TEST...")
        print("=" * 50)
        
        import psutil
        import time
        
        print("🔍 Testing system responsiveness...")
        
        # CPU test
        print("🔥 CPU Performance Test:")
        start_time = time.time()
        cpu_samples = []
        for _ in range(5):
            cpu_samples.append(psutil.cpu_percent(interval=0.2))
        
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        cpu_test_time = time.time() - start_time
        print(f"   Average CPU usage: {avg_cpu:.1f}%")
        print(f"   Response time: {cpu_test_time:.2f}s")
        
        # Memory test
        print("\n💾 Memory Performance Test:")
        memory = psutil.virtual_memory()
        print(f"   Available memory: {memory.available / (1024**3):.1f} GB")
        print(f"   Memory usage: {memory.percent:.1f}%")
        
        # Disk test
        print("\n💿 Storage Performance Test:")
        start_time = time.time()
        disk_io_start = psutil.disk_io_counters()
        time.sleep(1)
        disk_io_end = psutil.disk_io_counters()
        
        if disk_io_start and disk_io_end:
            read_bytes = disk_io_end.read_bytes - disk_io_start.read_bytes
            write_bytes = disk_io_end.write_bytes - disk_io_start.write_bytes
            print(f"   Read activity: {read_bytes / (1024**2):.1f} MB/s")
            print(f"   Write activity: {write_bytes / (1024**2):.1f} MB/s")
        
        # Network test
        print("\n🌐 Network Performance Test:")
        network_start = psutil.net_io_counters()
        time.sleep(1)
        network_end = psutil.net_io_counters()
        
        if network_start and network_end:
            sent_bytes = network_end.bytes_sent - network_start.bytes_sent
            recv_bytes = network_end.bytes_recv - network_start.bytes_recv
            print(f"   Network send: {sent_bytes / 1024:.1f} KB/s")
            print(f"   Network receive: {recv_bytes / 1024:.1f} KB/s")
        
        # Overall assessment
        print(f"\n📊 PERFORMANCE ASSESSMENT:")
        performance_score = 100
        
        if avg_cpu > 80:
            performance_score -= 20
            print("   🔴 High CPU usage detected")
        elif avg_cpu > 60:
            performance_score -= 10
            print("   🟠 Moderate CPU usage")
        else:
            print("   🟢 CPU usage is optimal")
        
        if memory.percent > 85:
            performance_score -= 20
            print("   🔴 High memory usage detected")
        elif memory.percent > 70:
            performance_score -= 10
            print("   🟠 Moderate memory usage")
        else:
            print("   🟢 Memory usage is optimal")
        
        print(f"\n🏆 Overall Performance Score: {performance_score}/100")
        
        if performance_score >= 90:
            print("🎉 Excellent! Your system is performing optimally.")
        elif performance_score >= 70:
            print("👍 Good performance with room for improvement.")
        elif performance_score >= 50:
            print("⚠️ Moderate performance issues detected.")
        else:
            print("🔴 Significant performance issues need attention.")
        
    except Exception as e:
        print(f"❌ Error during performance test: {e}")

def show_menu():
    """Display the main menu."""
    print("\n🎮 MAIN MENU")
    print("=" * 30)
    print("1. 🧠 Run AI System Analysis")
    print("2. 🌐 Start Web Dashboard")
    print("3. 📊 Show System Information")
    print("4. ⚡ Run Performance Test")
    print("5. 🔧 Quick Optimization")
    print("6. ℹ️  About & Help")
    print("0. 👋 Exit")
    print("-" * 30)

def quick_optimization():
    """Run quick optimization without full analysis."""
    try:
        print("\n🔧 QUICK OPTIMIZATION...")
        print("=" * 50)
        
        from analyzers.ai_system_analyzer import AISystemAnalyzer
        from ai_notification_manager import AINotificationManager
        
        analyzer = AISystemAnalyzer()
        notification_manager = AINotificationManager(analyzer)
        
        print("🔍 Running lightweight analysis...")
        analysis_results = analyzer.analyze_system(force=True)
        
        if analysis_results:
            auto_fixable = analysis_results.get('analysis_summary', {}).get('auto_fixable_issues', 0)
            
            if auto_fixable > 0:
                print(f"🔧 Applying {auto_fixable} automatic optimizations...")
                results = analyzer.apply_automatic_fixes()
                
                successful = sum(1 for result in results.values() if result)
                print(f"✅ Applied {successful} optimizations successfully")
                
                notification_manager.notify_optimization_completed(results)
            else:
                print("✅ No immediate optimizations needed")
        else:
            print("❌ Analysis failed")
    
    except Exception as e:
        print(f"❌ Error during quick optimization: {e}")

def show_about():
    """Show about information."""
    about_text = """
🤖 AI GAMING PERFORMANCE OPTIMIZER v2.0

🎯 FEATURES:
• Expert-level PC analysis using AI algorithms
• Real-time system monitoring and optimization
• Anti-cheat safe optimizations (CS2, Valorant, etc.)
• Machine learning performance prediction
• Professional web dashboard with live metrics
• Comprehensive system health scoring
• Automatic issue detection and fixes

🛡️ SAFETY:
This optimizer is designed to be completely safe with anti-cheat systems.
All optimizations are tested for compatibility with major gaming platforms.

🎮 SUPPORTED GAMES:
• Counter-Strike 2 (CS2)
• Valorant  
• League of Legends
• Call of Duty series
• Apex Legends
• Fortnite
• And many more...

🔧 OPTIMIZATIONS INCLUDE:
• CPU performance tuning
• Memory management optimization
• Network latency reduction
• Storage I/O improvements
• Visual effects optimization
• Process priority management
• System service optimization

📊 AI CAPABILITIES:
• Predictive performance analysis
• Learning from system usage patterns
• Intelligent issue correlation
• Performance baseline establishment
• Automated optimization recommendations

💻 SYSTEM REQUIREMENTS:
• Windows 10/11 or Linux
• Python 3.7+
• Administrator privileges (recommended)
• Internet connection (for updates)

🆘 SUPPORT:
If you encounter any issues or need help, check the logs in ai_gaming_optimizer.log
    """
    print(about_text)

def main():
    """Main application entry point."""
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Display banner
    display_banner()
    
    # Show initial system info
    show_system_info()
    
    # Main menu loop
    while True:
        try:
            show_menu()
            choice = input("\n🎯 Select an option (0-6): ").strip()
            
            if choice == '0':
                print("\n👋 Thank you for using AI Gaming Performance Optimizer!")
                print("🎮 Happy Gaming!")
                break
            
            elif choice == '1':
                run_ai_analysis()
            
            elif choice == '2':
                start_web_dashboard()
            
            elif choice == '3':
                show_system_info()
            
            elif choice == '4':
                run_performance_test()
            
            elif choice == '5':
                quick_optimization()
            
            elif choice == '6':
                show_about()
            
            else:
                print("❌ Invalid option. Please select 0-6.")
            
            # Pause before returning to menu (except for web dashboard)
            if choice != '2':
                input("\n⏎ Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
            input("\n⏎ Press Enter to continue...")
    
    return 0

if __name__ == '__main__':
    exit(main())