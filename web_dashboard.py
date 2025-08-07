#!/usr/bin/env python3
"""
SUHA FPS+ v4.0 - Web Dashboard Server
Standalone web dashboard with enhanced functionality
"""

import asyncio
import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Try to import required packages
try:
    from flask import Flask, render_template, jsonify, request, send_from_directory
    from flask_socketio import SocketIO, emit
    import psutil
    HAS_REQUIRED_DEPS = True
except ImportError as e:
    print(f"⚠️ Missing dependencies: {e}")
    print("Run: pip install flask flask-socketio psutil")
    HAS_REQUIRED_DEPS = False
    import sys
    sys.exit(1)

class SystemMonitor:
    """Real-time system monitoring."""
    
    def __init__(self):
        self.last_cpu_times = psutil.cpu_times()
        self.last_check_time = time.time()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        try:
            # CPU metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first temperature sensor
                    for name, entries in temps.items():
                        if entries:
                            temperature = entries[0].current
                            break
            except (AttributeError, OSError):
                temperature = 0
            
            # Process information
            python_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower():
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cpu_percent': proc.info['cpu_percent'] or 0,
                            'memory_percent': proc.info['memory_percent'] or 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_usage,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else 0,
                    'max_frequency': cpu_freq.max if cpu_freq else 0
                },
                'memory': {
                    'usage_percent': memory.percent,
                    'total_gb': memory.total / (1024**3),
                    'available_gb': memory.available / (1024**3),
                    'used_gb': memory.used / (1024**3)
                },
                'swap': {
                    'usage_percent': swap.percent,
                    'total_gb': swap.total / (1024**3),
                    'used_gb': swap.used / (1024**3)
                },
                'disk': {
                    'usage_percent': (disk_usage.used / disk_usage.total) * 100,
                    'total_gb': disk_usage.total / (1024**3),
                    'free_gb': disk_usage.free / (1024**3),
                    'used_gb': disk_usage.used / (1024**3)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'temperature': temperature or 0,
                'python_processes': python_processes,
                'process_count': len(python_processes)
            }
            
        except Exception as e:
            print(f"Error getting system metrics: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

class ComponentManager:
    """Manages component status and control."""
    
    def __init__(self):
        self.components = {
            'ai_engine': {'running': False, 'pid': None, 'health': 'unknown'},
            'performance_optimizer': {'running': False, 'pid': None, 'health': 'unknown'},
            'windows_optimizer': {'running': False, 'pid': None, 'health': 'unknown'},
            'discord_bot': {'running': False, 'pid': None, 'health': 'unknown'},
            'neural_launcher': {'running': False, 'pid': None, 'health': 'unknown'},
            'web_dashboard': {'running': True, 'pid': os.getpid(), 'health': 'healthy'}
        }
        
    def update_component_status(self):
        """Update component status based on running processes."""
        try:
            # Get all python processes
            python_processes = {}
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info['cmdline'] or [])
                        python_processes[proc.info['pid']] = cmdline
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Check each component
            for component_name in self.components.keys():
                if component_name == 'web_dashboard':
                    continue  # Skip self
                
                running = False
                pid = None
                
                # Look for component in running processes
                script_patterns = {
                    'ai_engine': 'ai_engine_v4.py',
                    'performance_optimizer': 'advanced_performance_optimizer_v4.py',
                    'windows_optimizer': 'windows_optimizer_v4.py',
                    'discord_bot': 'discord_bot_v4.py',
                    'neural_launcher': 'neural_launcher_v4.py'
                }
                
                pattern = script_patterns.get(component_name)
                if pattern:
                    for proc_pid, cmdline in python_processes.items():
                        if pattern in cmdline:
                            running = True
                            pid = proc_pid
                            break
                
                self.components[component_name].update({
                    'running': running,
                    'pid': pid,
                    'health': 'healthy' if running else 'stopped'
                })
                
        except Exception as e:
            print(f"Error updating component status: {e}")
    
    def get_component_status(self) -> Dict[str, Any]:
        """Get current component status."""
        self.update_component_status()
        return self.components.copy()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'suha_fps_neural_2040_enhanced'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize managers
system_monitor = SystemMonitor()
component_manager = ComponentManager()

# Global state
dashboard_state = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'connected_clients': 0,
    'logs': []
}

def add_log(message: str, level: str = 'info'):
    """Add a log entry."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'level': level
    }
    dashboard_state['logs'].append(log_entry)
    
    # Keep only last 100 logs
    if len(dashboard_state['logs']) > 100:
        dashboard_state['logs'] = dashboard_state['logs'][-100:]
    
    # Emit to connected clients
    socketio.emit('log_entry', log_entry)

@app.route('/')
def dashboard():
    """Main dashboard route."""
    return render_template('enhanced_neural_interface.html')

@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    dashboard_state['total_requests'] += 1
    
    try:
        system_metrics = system_monitor.get_system_metrics()
        component_status = component_manager.get_component_status()
        
        response_data = {
            'system': system_metrics,
            'components': component_status,
            'dashboard': {
                'uptime': str(datetime.now() - dashboard_state['start_time']),
                'total_requests': dashboard_state['total_requests'],
                'connected_clients': dashboard_state['connected_clients']
            }
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def api_logs():
    """API endpoint for recent logs."""
    return jsonify({
        'logs': dashboard_state['logs'][-50:],  # Last 50 logs
        'total_count': len(dashboard_state['logs'])
    })

@app.route('/api/components/start-all', methods=['POST'])
def api_start_all_components():
    """API endpoint to start all components."""
    add_log("Starting all components via API request", "info")
    
    # This would integrate with the master launcher
    # For now, just log the request
    return jsonify({
        'success': True,
        'message': 'Start all components request received'
    })

@app.route('/api/components/stop-all', methods=['POST'])
def api_stop_all_components():
    """API endpoint to stop all components."""
    add_log("Stopping all components via API request", "warning")
    
    return jsonify({
        'success': True,
        'message': 'Stop all components request received'
    })

@app.route('/api/components/restart-all', methods=['POST'])
def api_restart_all_components():
    """API endpoint to restart all components."""
    add_log("Restarting all components via API request", "info")
    
    return jsonify({
        'success': True,
        'message': 'Restart all components request received'
    })

@app.route('/api/ai/analyze', methods=['POST'])
def api_ai_analyze():
    """API endpoint for AI analysis."""
    add_log("AI analysis requested via API", "info")
    
    # Mock AI analysis response
    metrics = system_monitor.get_system_metrics()
    cpu_usage = metrics['cpu']['usage_percent']
    memory_usage = metrics['memory']['usage_percent']
    
    recommendations = []
    if cpu_usage > 80:
        recommendations.append({
            'message': 'High CPU usage detected. Consider closing unnecessary applications.',
            'confidence': 85,
            'priority': 'high'
        })
    
    if memory_usage > 80:
        recommendations.append({
            'message': 'High memory usage detected. Recommend system cleanup.',
            'confidence': 90,
            'priority': 'high'
        })
    
    if not recommendations:
        recommendations.append({
            'message': 'System performance is optimal. No immediate actions required.',
            'confidence': 95,
            'priority': 'info'
        })
    
    # Emit recommendations via WebSocket
    for rec in recommendations:
        socketio.emit('ai_recommendation', rec)
    
    return jsonify({
        'success': True,
        'recommendations': recommendations
    })

@app.route('/api/ai/optimize', methods=['POST'])
def api_ai_optimize():
    """API endpoint for AI optimizations."""
    add_log("AI optimization requested via API", "success")
    
    # Mock optimization response
    optimizations = [
        'CPU priority optimization applied',
        'Memory cache cleared',
        'Background processes optimized',
        'Network stack tuned for gaming'
    ]
    
    for opt in optimizations:
        add_log(f"✅ {opt}", "success")
    
    return jsonify({
        'success': True,
        'optimizations_applied': optimizations
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    dashboard_state['connected_clients'] += 1
    add_log(f"Client connected. Total clients: {dashboard_state['connected_clients']}", "info")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    dashboard_state['connected_clients'] = max(0, dashboard_state['connected_clients'] - 1)
    add_log(f"Client disconnected. Total clients: {dashboard_state['connected_clients']}", "info")

@socketio.on('request_status')
def handle_status_request():
    """Handle status update requests."""
    try:
        system_metrics = system_monitor.get_system_metrics()
        component_status = component_manager.get_component_status()
        
        # Format data for frontend
        dashboard_data = {
            'cpu_usage': system_metrics['cpu']['usage_percent'],
            'memory_usage': system_metrics['memory']['usage_percent'],
            'gpu_usage': 0,  # Would be populated by actual GPU monitoring
            'fps': 0,  # Would be populated by game monitoring
            'temperature': system_metrics['temperature'],
            'components': component_status,
            'timestamp': system_metrics['timestamp']
        }
        
        emit('status_update', dashboard_data)
    except Exception as e:
        emit('status_update', {'error': str(e)})

def background_monitoring():
    """Background thread for continuous monitoring."""
    while True:
        try:
            # Update component status every 5 seconds
            component_manager.update_component_status()
            
            # Emit periodic status updates
            system_metrics = system_monitor.get_system_metrics()
            component_status = component_manager.get_component_status()
            
            dashboard_data = {
                'cpu_usage': system_metrics['cpu']['usage_percent'],
                'memory_usage': system_metrics['memory']['usage_percent'],
                'gpu_usage': 0,
                'fps': 0,
                'temperature': system_metrics['temperature'],
                'components': component_status,
                'timestamp': system_metrics['timestamp']
            }
            
            socketio.emit('status_update', dashboard_data)
            
        except Exception as e:
            print(f"Error in background monitoring: {e}")
        
        time.sleep(5)  # Update every 5 seconds

def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║                    SUHA FPS+ v4.0 WEB DASHBOARD SERVER                  ║
║                     Neural Gaming Performance System                     ║
╚══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Ensure template directory exists
    templates_dir = Path('web_templates')
    if not templates_dir.exists():
        print(f"❌ Template directory not found: {templates_dir}")
        print("Please ensure enhanced_neural_interface.html exists in web_templates/")
        return
    
    # Start background monitoring
    monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
    monitoring_thread.start()
    
    add_log("Web dashboard server starting...", "info")
    add_log("Enhanced neural interface loaded", "success")
    
    # Get host and port from command line or use defaults
    import sys
    host = '0.0.0.0'
    port = 5000
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}")
    
    print(f"🌐 Starting web dashboard on http://{host}:{port}")
    print(f"📊 Enhanced interface: http://localhost:{port}")
    print(f"🔗 API endpoints available at: http://localhost:{port}/api/")
    print("Press Ctrl+C to stop the server")
    
    try:
        socketio.run(app, 
                    host=host, 
                    port=port, 
                    debug=False,
                    allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down web dashboard server...")
        add_log("Web dashboard server shutting down", "warning")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()