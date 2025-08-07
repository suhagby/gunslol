#!/usr/bin/env python3
"""
Web-based monitoring dashboard for PC optimization system.
Displays real-time system metrics on a web interface for secondary display.
"""

import os
import sys
import time
import json
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, render_template, jsonify
    HAS_FLASK = True
    print("Flask loaded successfully")
except ImportError as e:
    HAS_FLASK = False
    print(f"Flask not available: {e}")

try:
    from flask_socketio import SocketIO, emit
    HAS_SOCKETIO = True
except ImportError as e:
    HAS_SOCKETIO = False
    print(f"SocketIO not available: {e}")

import psutil
import yaml

class WebMonitoringDashboard:
    """Web-based monitoring dashboard for real-time PC performance monitoring."""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'gaming-monitor-2024'
        
        if HAS_SOCKETIO:
            try:
                self.socketio = SocketIO(self.app, cors_allowed_origins="*")
            except:
                self.socketio = None
        else:
            self.socketio = None
            
        self.running = False
        self.current_metrics = {}
        
        # Load hardware profile
        self.load_hardware_profile()
        
        # Setup routes
        self.setup_routes()
        
        # Start monitoring thread
        self.monitoring_thread = None
    
    def load_hardware_profile(self):
        """Load hardware configuration."""
        try:
            with open(project_root / 'config' / 'settings.yaml', 'r') as f:
                config = yaml.safe_load(f)
                self.hardware_profile = config
        except:
            # Default profile
            self.hardware_profile = {
                'thresholds': {
                    'max_cpu_temp': 85,
                    'max_gpu_temp': 83,
                    'max_memory_usage': 90,
                    'min_fps': 60,
                    'max_ping': 50
                }
            }
    
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            return self.render_dashboard()
        
        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.current_metrics)
        
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'status': 'running' if self.running else 'stopped',
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            })
        
        if self.socketio and HAS_SOCKETIO:
            @self.socketio.on('connect')
            def handle_connect():
                emit('metrics', self.current_metrics)
    
    def render_dashboard(self):
        """Render the main dashboard HTML."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PC Gaming Performance Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0a0a, #1a1a2e, #16213e);
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh;
        }
        
        .container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, #00d4ff, #ff00c3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 1.4em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: rgba(0,0,0,0.3);
            border-radius: 8px;
        }
        
        .metric-label {
            color: #cccccc;
        }
        
        .metric-value {
            font-weight: bold;
            color: #00ff88;
        }
        
        .metric-value.warning {
            color: #ffaa00;
        }
        
        .metric-value.critical {
            color: #ff4444;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .progress-fill.warning {
            background: linear-gradient(90deg, #ffaa00, #ff6600);
        }
        
        .progress-fill.critical {
            background: linear-gradient(90deg, #ff4444, #cc0000);
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        
        .timestamp {
            text-align: center;
            margin-top: 20px;
            color: #888;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="status-indicator"></span> PC Gaming Performance Monitor</h1>
            <p>Real-time system monitoring and optimization dashboard</p>
            <p class="timestamp">Last updated: <span id="lastUpdate">--</span></p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🖥️ CPU Performance</h3>
                <div class="metric">
                    <span class="metric-label">Usage:</span>
                    <span class="metric-value" id="cpu-usage">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-progress"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperature:</span>
                    <span class="metric-value" id="cpu-temp">--°C</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Frequency:</span>
                    <span class="metric-value" id="cpu-freq">-- GHz</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎮 GPU Performance</h3>
                <div class="metric">
                    <span class="metric-label">Usage:</span>
                    <span class="metric-value" id="gpu-usage">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="gpu-progress"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Temperature:</span>
                    <span class="metric-value" id="gpu-temp">--°C</span>
                </div>
                <div class="metric">
                    <span class="metric-label">VRAM Usage:</span>
                    <span class="metric-value" id="gpu-vram">-- MB</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🧠 Memory Status</h3>
                <div class="metric">
                    <span class="metric-label">Usage:</span>
                    <span class="metric-value" id="mem-usage">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="mem-progress"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Available:</span>
                    <span class="metric-value" id="mem-available">-- GB</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total:</span>
                    <span class="metric-value" id="mem-total">-- GB</span>
                </div>
            </div>
            
            <div class="card">
                <h3>💾 Storage I/O</h3>
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value" id="disk-usage">--%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">Read Speed:</span>
                    <span class="metric-value" id="disk-read">-- MB/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Write Speed:</span>
                    <span class="metric-value" id="disk-write">-- MB/s</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🌐 Network Status</h3>
                <div class="metric">
                    <span class="metric-label">Ping:</span>
                    <span class="metric-value" id="net-ping">-- ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Download:</span>
                    <span class="metric-value" id="net-down">-- Mbps</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Upload:</span>
                    <span class="metric-value" id="net-up">-- Mbps</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🎯 Gaming Performance</h3>
                <div class="metric">
                    <span class="metric-label">FPS:</span>
                    <span class="metric-value" id="game-fps">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Frame Time:</span>
                    <span class="metric-value" id="game-frametime">-- ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Input Lag:</span>
                    <span class="metric-value" id="game-inputlag">-- ms</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Update metrics every 2 seconds
        function updateMetrics() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    updateDisplay(data);
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching metrics:', error);
                });
        }
        
        function updateDisplay(data) {
            // CPU metrics
            updateMetric('cpu-usage', data.cpu_usage, '%');
            updateProgress('cpu-progress', data.cpu_usage, 100);
            updateMetric('cpu-temp', data.cpu_temperature, '°C');
            updateMetric('cpu-freq', (data.cpu_frequency / 1000).toFixed(2), ' GHz');
            
            // GPU metrics
            updateMetric('gpu-usage', data.gpu_usage, '%');
            updateProgress('gpu-progress', data.gpu_usage, 100);
            updateMetric('gpu-temp', data.gpu_temperature, '°C');
            updateMetric('gpu-vram', Math.round(data.gpu_memory_used), ' MB');
            
            // Memory metrics
            updateMetric('mem-usage', data.memory_percent, '%');
            updateProgress('mem-progress', data.memory_percent, 100);
            updateMetric('mem-available', (data.memory_available / (1024**3)).toFixed(1), ' GB');
            updateMetric('mem-total', (data.memory_total / (1024**3)).toFixed(1), ' GB');
            
            // Disk metrics
            updateMetric('disk-usage', data.disk_usage, '%');
            updateProgress('disk-progress', data.disk_usage, 100);
            updateMetric('disk-read', (data.disk_read_speed / (1024**2)).toFixed(1), ' MB/s');
            updateMetric('disk-write', (data.disk_write_speed / (1024**2)).toFixed(1), ' MB/s');
            
            // Network metrics
            updateMetric('net-ping', data.ping, ' ms');
            updateMetric('net-down', data.download_speed, ' Mbps');
            updateMetric('net-up', data.upload_speed, ' Mbps');
            
            // Gaming metrics
            updateMetric('game-fps', data.fps || 0, '');
            updateMetric('game-frametime', data.frame_time || 0, ' ms');
            updateMetric('game-inputlag', data.input_lag || 0, ' ms');
        }
        
        function updateMetric(elementId, value, unit) {
            const element = document.getElementById(elementId);
            if (element && value !== undefined && value !== null) {
                element.textContent = value + unit;
                
                // Color coding based on value
                element.className = 'metric-value';
                if (elementId.includes('temp')) {
                    if (value > 80) element.classList.add('critical');
                    else if (value > 70) element.classList.add('warning');
                } else if (elementId.includes('usage') || elementId.includes('mem-usage') || elementId.includes('disk-usage')) {
                    if (value > 90) element.classList.add('critical');
                    else if (value > 75) element.classList.add('warning');
                } else if (elementId === 'net-ping') {
                    if (value > 100) element.classList.add('critical');
                    else if (value > 50) element.classList.add('warning');
                }
            }
        }
        
        function updateProgress(elementId, value, max) {
            const element = document.getElementById(elementId);
            if (element && value !== undefined && value !== null) {
                const percentage = Math.min((value / max) * 100, 100);
                element.style.width = percentage + '%';
                
                element.className = 'progress-fill';
                if (percentage > 90) element.classList.add('critical');
                else if (percentage > 75) element.classList.add('warning');
            }
        }
        
        // Start monitoring
        updateMetrics();
        setInterval(updateMetrics, 2000);
    </script>
</body>
</html>
        """
        return html_template
    
    def collect_system_metrics(self):
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics (basic)
            network_io = psutil.net_io_counters()
            
            # Try to get temperature (Linux systems)
            cpu_temp = 0
            try:
                if hasattr(psutil, 'sensors_temperatures'):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for name, entries in temps.items():
                            if entries:
                                cpu_temp = max(entry.current for entry in entries)
                                break
            except:
                pass
            
            self.current_metrics = {
                'timestamp': time.time(),
                'cpu_usage': cpu_percent,
                'cpu_frequency': cpu_freq.current if cpu_freq else 0,
                'cpu_temperature': cpu_temp,
                'memory_percent': memory.percent,
                'memory_total': memory.total,
                'memory_available': memory.available,
                'disk_usage': (disk_usage.used / disk_usage.total) * 100,
                'disk_read_speed': getattr(disk_io, 'read_bytes', 0),
                'disk_write_speed': getattr(disk_io, 'write_bytes', 0),
                'gpu_usage': 0,  # Would need GPU monitoring library
                'gpu_temperature': 0,
                'gpu_memory_used': 0,
                'ping': 25,  # Simulated
                'download_speed': 100,  # Simulated
                'upload_speed': 50,  # Simulated
                'fps': None,
                'frame_time': None,
                'input_lag': None
            }
            
        except Exception as e:
            print(f"Error collecting metrics: {e}")
    
    def monitoring_loop(self):
        """Main monitoring loop."""
        self.start_time = time.time()
        
        while self.running:
            try:
                self.collect_system_metrics()
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the web dashboard."""
        if not HAS_FLASK:
            print("Flask is not available. Please install Flask and Flask-SocketIO:")
            print("pip install flask flask-socketio")
            return False
        
        self.running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"Starting web dashboard on http://localhost:{self.port}")
        print("Open this URL on your secondary display for monitoring.")
        
        try:
            # Use simple development server
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
        finally:
            self.running = False
        
        return True

if __name__ == "__main__":
    dashboard = WebMonitoringDashboard(port=5000)
    dashboard.start()