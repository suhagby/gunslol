#!/usr/bin/env python3
"""
AI-Enhanced Web Dashboard
Real-time web interface with AI system analysis and intelligent notifications.
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    HAS_FLASK = True
except ImportError as e:
    HAS_FLASK = False
    print(f"Flask not available: {e}")

import psutil
from analyzers.ai_system_analyzer import AISystemAnalyzer
from ai_notification_manager import AINotificationManager

class AIEnhancedWebDashboard:
    """AI-enhanced web dashboard for real-time system monitoring and optimization."""
    
    def __init__(self, port=5000):
        self.port = port
        self.logger = self._setup_logger()
        
        if not HAS_FLASK:
            raise ImportError("Flask is required for the web dashboard")
        
        # Initialize Flask app
        self.app = Flask(__name__, static_folder='web_static', template_folder='web_templates')
        self.app.config['SECRET_KEY'] = 'ai-gaming-optimizer-2024'
        
        # Initialize SocketIO for real-time updates
        try:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        except Exception as e:
            self.logger.warning(f"SocketIO initialization failed: {e}")
            self.socketio = None
        
        # Initialize AI components
        self.ai_analyzer = AISystemAnalyzer()
        self.notification_manager = AINotificationManager(self.ai_analyzer)
        
        # Dashboard state
        self.dashboard_data = {
            'system_info': {},
            'analysis_results': {},
            'notifications': [],
            'performance_history': [],
            'optimization_status': {}
        }
        
        # Monitoring thread
        self.monitoring_thread = None
        self.monitoring_active = False
        
        # Setup routes
        self._setup_routes()
        self._setup_socketio_events()
        
        self.logger.info("AI Enhanced Web Dashboard initialized")
    
    def _setup_logger(self):
        """Setup logging for the dashboard."""
        import logging
        logger = logging.getLogger(f"{__name__}.AIEnhancedWebDashboard")
        return logger
    
    def _setup_routes(self):
        """Setup Flask routes for the web dashboard."""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page."""
            return render_template('ai_dashboard.html')
        
        @self.app.route('/api/system-status')
        def get_system_status():
            """Get current system status."""
            try:
                # Get basic system metrics
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                
                # Get AI analysis if available
                analysis_summary = {}
                if self.dashboard_data['analysis_results']:
                    analysis_summary = self.dashboard_data['analysis_results'].get('analysis_summary', {})
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'uptime': time.time() - psutil.boot_time(),
                        'health_score': analysis_summary.get('overall_health_score', 100),
                        'total_issues': analysis_summary.get('total_issues', 0),
                        'performance_impact': analysis_summary.get('performance_impact_level', 'low'),
                        'last_analysis': self.dashboard_data.get('last_analysis_time', 0)
                    }
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/analysis-results')
        def get_analysis_results():
            """Get latest AI analysis results."""
            try:
                return jsonify({
                    'status': 'success',
                    'data': self.dashboard_data['analysis_results']
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/notifications')
        def get_notifications():
            """Get recent notifications."""
            try:
                notifications = self.notification_manager.get_notification_history(limit=20)
                return jsonify({
                    'status': 'success',
                    'data': notifications
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/run-analysis', methods=['POST'])
        def run_analysis():
            """Trigger AI system analysis."""
            try:
                # Run analysis in background
                analysis_results = self.ai_analyzer.analyze_system(force=True)
                
                if analysis_results:
                    self.dashboard_data['analysis_results'] = analysis_results
                    self.dashboard_data['last_analysis_time'] = time.time()
                    
                    # Send notifications for detected issues
                    self.notification_manager.notify_ai_analysis_results(analysis_results)
                    
                    # Emit real-time update if SocketIO is available
                    if self.socketio:
                        self.socketio.emit('analysis_update', analysis_results)
                    
                    return jsonify({
                        'status': 'success',
                        'message': 'Analysis completed successfully',
                        'data': analysis_results.get('analysis_summary', {})
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Analysis failed'
                    })
                    
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/apply-optimizations', methods=['POST'])
        def apply_optimizations():
            """Apply automatic optimizations."""
            try:
                # Get optimization results
                optimization_results = self.ai_analyzer.apply_automatic_fixes()
                
                # Send notification about optimization completion
                self.notification_manager.notify_optimization_completed(optimization_results)
                
                # Update dashboard data
                self.dashboard_data['optimization_status'] = {
                    'last_optimization': time.time(),
                    'results': optimization_results
                }
                
                # Emit real-time update
                if self.socketio:
                    self.socketio.emit('optimization_update', optimization_results)
                
                return jsonify({
                    'status': 'success',
                    'message': 'Optimizations applied',
                    'data': optimization_results
                })
                
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/system-info')
        def get_system_info():
            """Get detailed system information."""
            try:
                # Get comprehensive system info
                cpu_info = {
                    'usage': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}
                }
                
                memory_info = psutil.virtual_memory()._asdict()
                
                disk_info = {}
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_info[partition.device] = {
                            'mountpoint': partition.mountpoint,
                            'usage': usage._asdict()
                        }
                    except:
                        continue
                
                network_info = psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
                
                return jsonify({
                    'status': 'success',
                    'data': {
                        'cpu': cpu_info,
                        'memory': memory_info,
                        'disk': disk_info,
                        'network': network_info,
                        'boot_time': psutil.boot_time(),
                        'timestamp': time.time()
                    }
                })
                
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
        
        @self.app.route('/api/performance-history')
        def get_performance_history():
            """Get performance history data."""
            try:
                return jsonify({
                    'status': 'success',
                    'data': self.dashboard_data.get('performance_history', [])
                })
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)})
    
    def _setup_socketio_events(self):
        """Setup SocketIO events for real-time communication."""
        if not self.socketio:
            return
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            emit('connected', {'status': 'Connected to AI Gaming Optimizer'})
            self.logger.info('Client connected to dashboard')
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.logger.info('Client disconnected from dashboard')
        
        @self.socketio.on('request_analysis')
        def handle_analysis_request():
            """Handle analysis request from client."""
            try:
                analysis_results = self.ai_analyzer.analyze_system(force=True)
                if analysis_results:
                    emit('analysis_results', analysis_results)
            except Exception as e:
                emit('error', {'message': str(e)})
        
        @self.socketio.on('request_optimization')
        def handle_optimization_request():
            """Handle optimization request from client."""
            try:
                optimization_results = self.ai_analyzer.apply_automatic_fixes()
                emit('optimization_results', optimization_results)
            except Exception as e:
                emit('error', {'message': str(e)})
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Background monitoring started")
    
    def stop_monitoring(self):
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("Background monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        last_analysis = 0
        analysis_interval = 60  # Run analysis every 60 seconds
        
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Collect basic metrics
                metrics = {
                    'timestamp': current_time,
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_percent': psutil.virtual_memory().percent,
                    'uptime': current_time - psutil.boot_time()
                }
                
                # Add to performance history
                self.dashboard_data['performance_history'].append(metrics)
                
                # Keep only last 100 samples
                if len(self.dashboard_data['performance_history']) > 100:
                    self.dashboard_data['performance_history'] = self.dashboard_data['performance_history'][-100:]
                
                # Run AI analysis periodically
                if current_time - last_analysis > analysis_interval:
                    try:
                        analysis_results = self.ai_analyzer.analyze_system()
                        if analysis_results:
                            self.dashboard_data['analysis_results'] = analysis_results
                            self.dashboard_data['last_analysis_time'] = current_time
                            
                            # Send notifications for detected issues
                            self.notification_manager.notify_ai_analysis_results(analysis_results)
                            
                            # Emit real-time update
                            if self.socketio:
                                self.socketio.emit('analysis_update', analysis_results)
                        
                        last_analysis = current_time
                        
                    except Exception as e:
                        self.logger.error(f"Error during background analysis: {e}")
                
                # Emit real-time metrics update
                if self.socketio:
                    self.socketio.emit('metrics_update', metrics)
                
                # Wait before next iteration
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Longer wait on error
    
    def create_web_templates(self):
        """Create HTML templates for the web dashboard."""
        templates_dir = Path('web_templates')
        templates_dir.mkdir(exist_ok=True)
        
        # Main dashboard template
        dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Gaming Performance Optimizer</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.7.2/socket.io.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        .header {
            background: rgba(0, 0, 0, 0.8);
            padding: 1rem 2rem;
            border-bottom: 2px solid #00ff88;
            position: sticky;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }

        .header h1 {
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 2rem;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            display: grid;
            gap: 2rem;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(0, 255, 136, 0.3);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #00ff88, #00ccff, #ff0088);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .card:hover::before {
            opacity: 1;
        }

        .card:hover {
            transform: translateY(-5px);
            border-color: #00ff88;
            box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .status-good { background-color: #00ff88; }
        .status-warning { background-color: #ffaa00; }
        .status-critical { background-color: #ff4444; }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0.5rem 0;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            transition: background 0.3s ease;
        }

        .metric:hover {
            background: rgba(0, 255, 136, 0.1);
        }

        .metric-value {
            font-weight: bold;
            font-size: 1.1rem;
        }

        .progress-bar {
            width: 100%;
            height: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            margin: 0.5rem 0;
            position: relative;
        }

        .progress-fill {
            height: 100%;
            transition: width 0.5s ease;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            animation: shimmer 2s infinite;
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .progress-good { background: linear-gradient(90deg, #00ff88, #00cc70); }
        .progress-warning { background: linear-gradient(90deg, #ffaa00, #ff8800); }
        .progress-critical { background: linear-gradient(90deg, #ff4444, #cc3333); }

        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            background: linear-gradient(45deg, #00ff88, #00cc70);
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s ease;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 255, 136, 0.4);
        }

        .btn-secondary {
            background: linear-gradient(45deg, #555, #777);
        }

        .btn-danger {
            background: linear-gradient(45deg, #ff4444, #cc3333);
        }

        .notification {
            margin: 0.5rem 0;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid;
            animation: slideIn 0.5s ease;
        }

        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        .notification-critical {
            background: rgba(255, 68, 68, 0.1);
            border-color: #ff4444;
        }

        .notification-warning {
            background: rgba(255, 170, 0, 0.1);
            border-color: #ffaa00;
        }

        .notification-info {
            background: rgba(0, 255, 136, 0.1);
            border-color: #00ff88;
        }

        .chart-container {
            position: relative;
            height: 200px;
            margin: 1rem 0;
        }

        .issues-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .issue-item {
            padding: 1rem;
            margin: 0.5rem 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 4px solid;
        }

        .issue-critical { border-color: #ff4444; }
        .issue-warning { border-color: #ffaa00; }
        .issue-info { border-color: #00ff88; }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #00ff88;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .health-score {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            margin: 1rem 0;
            background: linear-gradient(45deg, #00ff88, #00ccff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }

        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
                padding: 1rem;
            }
            
            .header {
                padding: 1rem;
            }
            
            .header h1 {
                font-size: 1.5rem;
            }
        }

        .scrollbar {
            scrollbar-width: thin;
            scrollbar-color: #00ff88 transparent;
        }

        .scrollbar::-webkit-scrollbar {
            width: 6px;
        }

        .scrollbar::-webkit-scrollbar-track {
            background: transparent;
        }

        .scrollbar::-webkit-scrollbar-thumb {
            background: #00ff88;
            border-radius: 3px;
        }

        .scrollbar::-webkit-scrollbar-thumb:hover {
            background: #00cc70;
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>
            <i class="fas fa-robot"></i>
            AI Gaming Performance Optimizer
            <span class="status-indicator status-good" id="connectionStatus"></span>
        </h1>
    </header>

    <div class="container">
        <!-- System Health Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-heartbeat"></i>
                    System Health
                </div>
                <button class="btn" onclick="runAnalysis()">
                    <i class="fas fa-sync-alt"></i>
                    Analyze
                </button>
            </div>
            <div class="health-score" id="healthScore">100</div>
            <div class="metric">
                <span>Performance Impact:</span>
                <span class="metric-value" id="performanceImpact">Low</span>
            </div>
            <div class="metric">
                <span>Total Issues:</span>
                <span class="metric-value" id="totalIssues">0</span>
            </div>
            <div class="metric">
                <span>Last Analysis:</span>
                <span class="metric-value" id="lastAnalysis">Never</span>
            </div>
        </div>

        <!-- System Metrics Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-chart-line"></i>
                    System Metrics
                </div>
            </div>
            <div class="metric">
                <span><i class="fas fa-microchip"></i> CPU Usage:</span>
                <span class="metric-value" id="cpuUsage">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill progress-good" id="cpuProgress" style="width: 0%"></div>
            </div>
            
            <div class="metric">
                <span><i class="fas fa-memory"></i> Memory Usage:</span>
                <span class="metric-value" id="memoryUsage">0%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill progress-good" id="memoryProgress" style="width: 0%"></div>
            </div>
            
            <div class="metric">
                <span><i class="fas fa-clock"></i> Uptime:</span>
                <span class="metric-value" id="uptime">0h 0m</span>
            </div>
        </div>

        <!-- Performance Chart Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-chart-area"></i>
                    Performance History
                </div>
            </div>
            <div class="chart-container">
                <canvas id="performanceChart"></canvas>
            </div>
        </div>

        <!-- AI Analysis Results Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-brain"></i>
                    AI Analysis
                </div>
                <button class="btn btn-secondary" onclick="applyOptimizations()">
                    <i class="fas fa-wrench"></i>
                    Optimize
                </button>
            </div>
            <div class="issues-list scrollbar" id="analysisResults">
                <div class="issue-item issue-info">
                    <i class="fas fa-info-circle"></i>
                    Run analysis to see AI recommendations
                </div>
            </div>
        </div>

        <!-- Notifications Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-bell"></i>
                    Notifications
                </div>
                <button class="btn btn-secondary" onclick="clearNotifications()">
                    <i class="fas fa-trash"></i>
                    Clear
                </button>
            </div>
            <div class="issues-list scrollbar" id="notificationsList">
                <div class="notification notification-info">
                    <i class="fas fa-check-circle"></i>
                    AI Gaming Optimizer is ready
                </div>
            </div>
        </div>

        <!-- Quick Actions Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <i class="fas fa-bolt"></i>
                    Quick Actions
                </div>
            </div>
            <div style="display: grid; gap: 1rem;">
                <button class="btn" onclick="runAnalysis()">
                    <i class="fas fa-search"></i>
                    Full System Analysis
                </button>
                <button class="btn" onclick="applyOptimizations()">
                    <i class="fas fa-magic"></i>
                    Apply Auto-Optimizations
                </button>
                <button class="btn btn-secondary" onclick="refreshData()">
                    <i class="fas fa-refresh"></i>
                    Refresh Data
                </button>
                <button class="btn btn-danger" onclick="testNotifications()">
                    <i class="fas fa-vial"></i>
                    Test Notifications
                </button>
            </div>
        </div>
    </div>

    <script>
        // Initialize Socket.IO connection
        const socket = io();
        let performanceChart = null;
        let performanceData = [];

        // Connection status
        socket.on('connect', function() {
            document.getElementById('connectionStatus').className = 'status-indicator status-good';
            addNotification('Connected to AI system', 'info');
        });

        socket.on('disconnect', function() {
            document.getElementById('connectionStatus').className = 'status-indicator status-critical';
            addNotification('Disconnected from AI system', 'critical');
        });

        // Real-time updates
        socket.on('metrics_update', function(data) {
            updateSystemMetrics(data);
            updatePerformanceChart(data);
        });

        socket.on('analysis_update', function(data) {
            updateAnalysisResults(data);
            updateSystemHealth(data.analysis_summary);
        });

        socket.on('optimization_update', function(data) {
            addNotification('Optimizations applied: ' + Object.keys(data).length + ' changes', 'info');
        });

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializePerformanceChart();
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });

        function initializePerformanceChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: '#00ff88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Memory %',
                        data: [],
                        borderColor: '#00ccff',
                        backgroundColor: 'rgba(0, 204, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' },
                            min: 0,
                            max: 100
                        }
                    }
                }
            });
        }

        function updateSystemMetrics(data) {
            document.getElementById('cpuUsage').textContent = data.cpu_percent.toFixed(1) + '%';
            document.getElementById('memoryUsage').textContent = data.memory_percent.toFixed(1) + '%';
            
            // Update progress bars
            const cpuProgress = document.getElementById('cpuProgress');
            const memoryProgress = document.getElementById('memoryProgress');
            
            cpuProgress.style.width = data.cpu_percent + '%';
            memoryProgress.style.width = data.memory_percent + '%';
            
            // Update progress bar colors based on usage
            cpuProgress.className = 'progress-fill ' + getProgressColor(data.cpu_percent);
            memoryProgress.className = 'progress-fill ' + getProgressColor(data.memory_percent);
            
            // Update uptime
            const uptime = formatUptime(data.uptime);
            document.getElementById('uptime').textContent = uptime;
        }

        function updatePerformanceChart(data) {
            if (!performanceChart) return;
            
            const now = new Date().toLocaleTimeString();
            
            performanceChart.data.labels.push(now);
            performanceChart.data.datasets[0].data.push(data.cpu_percent);
            performanceChart.data.datasets[1].data.push(data.memory_percent);
            
            // Keep only last 20 data points
            if (performanceChart.data.labels.length > 20) {
                performanceChart.data.labels.shift();
                performanceChart.data.datasets[0].data.shift();
                performanceChart.data.datasets[1].data.shift();
            }
            
            performanceChart.update('none');
        }

        function updateSystemHealth(summary) {
            if (!summary) return;
            
            const healthScore = summary.overall_health_score || 100;
            const performanceImpact = summary.performance_impact_level || 'low';
            const totalIssues = summary.total_issues || 0;
            
            document.getElementById('healthScore').textContent = healthScore;
            document.getElementById('performanceImpact').textContent = performanceImpact.charAt(0).toUpperCase() + performanceImpact.slice(1);
            document.getElementById('totalIssues').textContent = totalIssues;
            document.getElementById('lastAnalysis').textContent = new Date().toLocaleTimeString();
        }

        function updateAnalysisResults(data) {
            const container = document.getElementById('analysisResults');
            container.innerHTML = '';
            
            if (data.issues && Object.keys(data.issues).length > 0) {
                Object.values(data.issues).forEach(issue => {
                    const issueDiv = document.createElement('div');
                    issueDiv.className = 'issue-item issue-' + issue.severity;
                    issueDiv.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                            <i class="fas fa-${getSeverityIcon(issue.severity)}"></i>
                            <strong>${issue.title}</strong>
                        </div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">${issue.description}</div>
                        ${issue.auto_fixable ? '<div style="color: #00ff88; font-size: 0.8rem; margin-top: 0.5rem;"><i class="fas fa-check"></i> Auto-fixable</div>' : ''}
                    `;
                    container.appendChild(issueDiv);
                });
            } else {
                container.innerHTML = '<div class="issue-item issue-info"><i class="fas fa-check-circle"></i> No issues detected</div>';
            }
        }

        function addNotification(message, severity) {
            const container = document.getElementById('notificationsList');
            const notificationDiv = document.createElement('div');
            notificationDiv.className = 'notification notification-' + severity;
            notificationDiv.innerHTML = `
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <i class="fas fa-${getSeverityIcon(severity)}"></i>
                    <span>${message}</span>
                    <small style="margin-left: auto; opacity: 0.7;">${new Date().toLocaleTimeString()}</small>
                </div>
            `;
            
            container.insertBefore(notificationDiv, container.firstChild);
            
            // Keep only last 10 notifications
            while (container.children.length > 10) {
                container.removeChild(container.lastChild);
            }
        }

        function getProgressColor(percentage) {
            if (percentage < 70) return 'progress-good';
            if (percentage < 90) return 'progress-warning';
            return 'progress-critical';
        }

        function getSeverityIcon(severity) {
            switch(severity) {
                case 'critical': return 'exclamation-triangle';
                case 'warning': return 'exclamation-circle';
                case 'info': return 'info-circle';
                default: return 'circle';
            }
        }

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return hours + 'h ' + minutes + 'm';
        }

        // API Functions
        async function runAnalysis() {
            try {
                addNotification('Running AI system analysis...', 'info');
                const response = await fetch('/api/run-analysis', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'success') {
                    addNotification('Analysis completed successfully', 'info');
                    await refreshData();
                } else {
                    addNotification('Analysis failed: ' + result.message, 'critical');
                }
            } catch (error) {
                addNotification('Error running analysis: ' + error.message, 'critical');
            }
        }

        async function applyOptimizations() {
            try {
                addNotification('Applying optimizations...', 'info');
                const response = await fetch('/api/apply-optimizations', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'success') {
                    const successCount = Object.values(result.data).filter(v => v).length;
                    addNotification(`Applied ${successCount} optimizations successfully`, 'info');
                } else {
                    addNotification('Optimization failed: ' + result.message, 'critical');
                }
            } catch (error) {
                addNotification('Error applying optimizations: ' + error.message, 'critical');
            }
        }

        async function refreshData() {
            try {
                // Get system status
                const statusResponse = await fetch('/api/system-status');
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'success') {
                    updateSystemMetrics(statusData.data);
                    updateSystemHealth(statusData.data);
                }
                
                // Get analysis results
                const analysisResponse = await fetch('/api/analysis-results');
                const analysisData = await analysisResponse.json();
                
                if (analysisData.status === 'success' && analysisData.data) {
                    updateAnalysisResults(analysisData.data);
                }
                
                // Get notifications
                const notificationsResponse = await fetch('/api/notifications');
                const notificationsData = await notificationsResponse.json();
                
                if (notificationsData.status === 'success') {
                    // Update notifications display if needed
                }
                
            } catch (error) {
                console.error('Error refreshing data:', error);
            }
        }

        function clearNotifications() {
            document.getElementById('notificationsList').innerHTML = '<div class="notification notification-info"><i class="fas fa-check-circle"></i> Notifications cleared</div>';
        }

        function testNotifications() {
            addNotification('Test critical notification', 'critical');
            setTimeout(() => addNotification('Test warning notification', 'warning'), 1000);
            setTimeout(() => addNotification('Test info notification', 'info'), 2000);
        }
    </script>
</body>
</html>
        '''
        
        # Write the template file
        template_path = templates_dir / 'ai_dashboard.html'
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        self.logger.info(f"Created web template at {template_path}")
    
    def create_static_directory(self):
        """Create static directory for web assets."""
        static_dir = Path('web_static')
        static_dir.mkdir(exist_ok=True)
        self.logger.info(f"Created static directory at {static_dir}")
    
    def run(self, debug=False, host='0.0.0.0'):
        """Run the web dashboard server."""
        try:
            # Create necessary directories and files
            self.create_web_templates()
            self.create_static_directory()
            
            # Start background monitoring
            self.start_monitoring()
            
            # Send startup notification
            self.notification_manager.notify_system_monitoring_status('monitoring_started')
            
            self.logger.info(f"Starting AI Enhanced Web Dashboard on http://{host}:{self.port}")
            
            if self.socketio:
                # Run with SocketIO support
                self.socketio.run(self.app, host=host, port=self.port, debug=debug)
            else:
                # Run basic Flask app
                self.app.run(host=host, port=self.port, debug=debug)
                
        except KeyboardInterrupt:
            self.logger.info("Dashboard shutdown requested")
        except Exception as e:
            self.logger.error(f"Error running dashboard: {e}")
            raise
        finally:
            # Stop background monitoring
            self.stop_monitoring()
            
            # Send shutdown notification
            self.notification_manager.notify_system_monitoring_status('monitoring_stopped')

def main():
    """Main entry point for the AI-enhanced web dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Gaming Performance Optimizer Web Dashboard')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the web server to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    try:
        dashboard = AIEnhancedWebDashboard(port=args.port)
        dashboard.run(debug=args.debug, host=args.host)
    except ImportError as e:
        print(f"Error: Missing required dependencies: {e}")
        print("Please install Flask and SocketIO: pip install flask flask-socketio")
    except Exception as e:
        print(f"Error starting dashboard: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())