#!/usr/bin/env python3
"""
Enhanced Web Dashboard with Real-time Performance Monitoring
Advanced interface for gaming performance optimization with live recommendations.
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, render_template, jsonify, request, Response
    from flask_socketio import SocketIO, emit, Namespace
    HAS_FLASK = True
except ImportError as e:
    HAS_FLASK = False
    print(f"Flask not available: {e}")

import psutil
import yaml
from optimizers.advanced_performance_optimizer import AdvancedPerformanceOptimizer

class EnhancedWebDashboard:
    """Enhanced web dashboard with advanced monitoring and optimization features."""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'advanced-gaming-monitor-2024'
        
        try:
            self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='threading')
        except:
            self.socketio = None
            
        self.running = False
        self.current_metrics = {}
        self.performance_history = []
        self.max_history_points = 300  # 5 minutes at 1-second intervals
        
        # Initialize advanced optimizer
        try:
            self.optimizer = AdvancedPerformanceOptimizer()
        except:
            self.optimizer = None
        
        # Setup routes and socket handlers
        self.setup_routes()
        self.setup_socket_handlers()
        
        # Start monitoring thread
        self.monitoring_thread = None
        self.last_optimization_check = 0
        
    def setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def dashboard():
            return self.render_enhanced_dashboard()
        
        @self.app.route('/api/metrics')
        def get_metrics():
            return jsonify(self.current_metrics)
        
        @self.app.route('/api/history')
        def get_history():
            return jsonify({
                'history': self.performance_history[-60:],  # Last 60 seconds
                'max_points': self.max_history_points
            })
        
        @self.app.route('/api/recommendations')
        def get_recommendations():
            if self.optimizer:
                recommendations = self.optimizer.generate_recommendations()
                return jsonify({'recommendations': recommendations})
            return jsonify({'recommendations': ['Optimizer not available']})
        
        @self.app.route('/api/hardware')
        def get_hardware():
            if self.optimizer:
                return jsonify(self.optimizer.hardware_info)
            return jsonify({'error': 'Hardware info not available'})
        
        @self.app.route('/api/optimize', methods=['POST'])
        def apply_optimizations():
            if self.optimizer:
                try:
                    self.optimizer.optimize_low_latency_gaming()
                    return jsonify({
                        'success': True,
                        'message': 'Optimizations applied successfully',
                        'optimizations': self.optimizer.optimizations_applied
                    })
                except Exception as e:
                    return jsonify({
                        'success': False,
                        'message': f'Optimization failed: {str(e)}'
                    })
            return jsonify({
                'success': False,
                'message': 'Optimizer not available'
            })
    
    def setup_socket_handlers(self):
        """Setup SocketIO handlers for real-time communication."""
        if not self.socketio:
            return
            
        @self.socketio.on('connect')
        def handle_connect():
            emit('metrics', self.current_metrics)
            emit('hardware', self.optimizer.hardware_info if self.optimizer else {})
        
        @self.socketio.on('request_optimization')
        def handle_optimization_request():
            if self.optimizer:
                try:
                    self.optimizer.optimize_low_latency_gaming()
                    emit('optimization_complete', {
                        'success': True,
                        'optimizations': self.optimizer.optimizations_applied
                    })
                except Exception as e:
                    emit('optimization_complete', {
                        'success': False,
                        'error': str(e)
                    })
    
    def render_enhanced_dashboard(self):
        """Render the enhanced dashboard HTML with advanced features."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Gaming Performance Monitor</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            background: radial-gradient(circle at 20% 50%, #1a0033 0%, #0a0a0a 50%, #001122 100%);
            color: #ffffff;
            overflow-x: hidden;
            min-height: 100vh;
            position: relative;
        }
        
        /* Animated background effect */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><circle cx="200" cy="200" r="3" fill="%2300d4ff" opacity="0.3"/><circle cx="800" cy="300" r="2" fill="%23ff00c3" opacity="0.4"/><circle cx="400" cy="600" r="1.5" fill="%2300ff88" opacity="0.2"/><circle cx="700" cy="800" r="2.5" fill="%23ffaa00" opacity="0.3"/></svg>');
            animation: drift 20s linear infinite;
            pointer-events: none;
            z-index: -1;
        }
        
        @keyframes drift {
            0% { transform: translate(0, 0); }
            50% { transform: translate(-50px, -30px); }
            100% { transform: translate(0, 0); }
        }
        
        .container {
            padding: 15px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            background: rgba(0,0,0,0.8);
            border-radius: 12px;
            border: 2px solid transparent;
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), linear-gradient(45deg, #00d4ff, #ff00c3, #00ff88);
            background-origin: border-box;
            background-clip: content-box, border-box;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }
        
        .header h1 {
            font-size: 2.8em;
            background: linear-gradient(45deg, #00d4ff, #ff00c3, #00ff88, #ffaa00);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-shift 3s ease infinite;
            margin-bottom: 10px;
        }
        
        @keyframes gradient-shift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 15px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            background: linear-gradient(45deg, #00d4ff, #0099cc);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
        }
        
        .btn.danger {
            background: linear-gradient(45deg, #ff4444, #cc0000);
            box-shadow: 0 4px 16px rgba(255, 68, 68, 0.3);
        }
        
        .btn.success {
            background: linear-gradient(45deg, #00ff88, #00cc66);
            box-shadow: 0 4px 16px rgba(0, 255, 136, 0.3);
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(0,0,0,0.7);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
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
            background: linear-gradient(90deg, #00d4ff, #ff00c3, #00ff88);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.15);
        }
        
        .card:hover::before {
            opacity: 1;
        }
        
        .card h3 {
            color: #00d4ff;
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 8px 0;
            padding: 8px 12px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
            border-left: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .metric:hover {
            background: rgba(255,255,255,0.08);
            border-left-color: #00d4ff;
        }
        
        .metric-label {
            color: #cccccc;
            font-size: 0.9em;
        }
        
        .metric-value {
            font-weight: bold;
            color: #00ff88;
            font-size: 1.1em;
        }
        
        .metric-value.warning {
            color: #ffaa00;
        }
        
        .metric-value.critical {
            color: #ff4444;
            animation: pulse-critical 1s infinite;
        }
        
        @keyframes pulse-critical {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(0,0,0,0.3);
            border-radius: 3px;
            overflow: hidden;
            margin: 8px 0;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00d4ff);
            transition: width 0.5s ease;
            border-radius: 3px;
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .progress-fill.warning {
            background: linear-gradient(90deg, #ffaa00, #ff6600);
        }
        
        .progress-fill.critical {
            background: linear-gradient(90deg, #ff4444, #cc0000);
        }
        
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ff88;
            animation: pulse 2s infinite;
            margin-right: 8px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .chart-container {
            position: relative;
            height: 200px;
            margin: 15px 0;
        }
        
        .recommendations {
            background: rgba(0,0,0,0.5);
            border-left: 4px solid #00ff88;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .recommendations h4 {
            color: #00ff88;
            margin-bottom: 10px;
        }
        
        .recommendation-item {
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.05);
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .timestamp {
            text-align: center;
            margin-top: 15px;
            color: #888;
            font-size: 0.8em;
            opacity: 0.7;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.9);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            border-left: 4px solid #00ff88;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .hardware-overview {
            grid-column: 1 / -1;
            background: rgba(0,20,40,0.8);
            border: 1px solid rgba(0, 212, 255, 0.3);
        }
        
        .performance-charts {
            grid-column: 1 / -1;
        }
        
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 2em; }
            .controls { flex-direction: column; align-items: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="status-indicator"></span> Advanced Gaming Performance Monitor</h1>
            <p>Real-time system optimization with AI-powered recommendations</p>
            <div class="controls">
                <button class="btn success" onclick="applyOptimizations()">🚀 Optimize System</button>
                <button class="btn" onclick="toggleMonitoring()">⏸️ Pause Monitoring</button>
                <button class="btn danger" onclick="resetOptimizations()">🔄 Reset Settings</button>
            </div>
            <p class="timestamp">Last updated: <span id="lastUpdate">--</span></p>
        </div>
        
        <div class="grid">
            <div class="card hardware-overview">
                <h3>💻 Hardware Configuration</h3>
                <div id="hardware-info">
                    <div class="metric">
                        <span class="metric-label">Loading hardware information...</span>
                        <span class="metric-value">--</span>
                    </div>
                </div>
            </div>
            
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
                    <span class="metric-label">Frequency:</span>
                    <span class="metric-value" id="cpu-freq">-- MHz</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Per-Core Usage:</span>
                    <div id="cpu-cores"></div>
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
                    <span class="metric-label">Used:</span>
                    <span class="metric-value" id="mem-used">-- GB</span>
                </div>
            </div>
            
            <div class="card">
                <h3>💾 Storage Performance</h3>
                <div class="metric">
                    <span class="metric-label">Read Speed:</span>
                    <span class="metric-value" id="disk-read">-- MB/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Write Speed:</span>
                    <span class="metric-value" id="disk-write">-- MB/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">IOPS:</span>
                    <span class="metric-value" id="disk-iops">--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🌐 Network Performance</h3>
                <div class="metric">
                    <span class="metric-label">Upload:</span>
                    <span class="metric-value" id="net-upload">-- KB/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Download:</span>
                    <span class="metric-value" id="net-download">-- KB/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Packets/sec:</span>
                    <span class="metric-value" id="net-packets">--</span>
                </div>
            </div>
            
            <div class="card">
                <h3>💡 Performance Recommendations</h3>
                <div id="recommendations">
                    <div class="recommendation-item">Loading recommendations...</div>
                </div>
                <button class="btn" onclick="refreshRecommendations()">🔄 Refresh</button>
            </div>
            
            <div class="card performance-charts">
                <h3>📊 Performance History</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <div id="notification" class="notification"></div>
    
    <script>
        // Global variables
        let socket;
        let performanceChart;
        let monitoringEnabled = true;
        let lastNetworkBytes = { sent: 0, recv: 0, timestamp: Date.now() };
        let lastDiskBytes = { read: 0, write: 0, timestamp: Date.now() };
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeSocket();
            initializeChart();
            updateMetrics();
            setInterval(updateMetrics, 1000);
            loadHardwareInfo();
            refreshRecommendations();
        });
        
        function initializeSocket() {
            if (typeof io !== 'undefined') {
                socket = io();
                
                socket.on('connect', function() {
                    console.log('Connected to server');
                });
                
                socket.on('metrics', function(data) {
                    updateDisplay(data);
                });
                
                socket.on('optimization_complete', function(data) {
                    if (data.success) {
                        showNotification('✅ Optimizations applied successfully!', 'success');
                    } else {
                        showNotification('❌ Optimization failed: ' + data.error, 'error');
                    }
                });
            }
        }
        
        function initializeChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU Usage %',
                            data: [],
                            borderColor: '#00d4ff',
                            backgroundColor: 'rgba(0, 212, 255, 0.1)',
                            tension: 0.4
                        },
                        {
                            label: 'Memory Usage %',
                            data: [],
                            borderColor: '#00ff88',
                            backgroundColor: 'rgba(0, 255, 136, 0.1)',
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { color: '#cccccc' }
                        },
                        x: {
                            ticks: { color: '#cccccc' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#cccccc' }
                        }
                    }
                }
            });
        }
        
        function updateMetrics() {
            if (!monitoringEnabled) return;
            
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    updateDisplay(data);
                    updateChart(data);
                    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching metrics:', error);
                });
        }
        
        function updateDisplay(data) {
            // CPU metrics
            const cpu = data.cpu || {};
            updateMetric('cpu-usage', cpu.usage_percent, '%');
            updateProgress('cpu-progress', cpu.usage_percent, 100);
            updateMetric('cpu-freq', Math.round(cpu.frequency || 0), ' MHz');
            
            // Update per-core usage
            if (cpu.usage_per_core) {
                const coresContainer = document.getElementById('cpu-cores');
                coresContainer.innerHTML = '';
                cpu.usage_per_core.forEach((usage, index) => {
                    const coreDiv = document.createElement('div');
                    coreDiv.className = 'metric';
                    coreDiv.innerHTML = `
                        <span class="metric-label">Core ${index}:</span>
                        <span class="metric-value ${usage > 80 ? 'critical' : usage > 60 ? 'warning' : ''}">${usage.toFixed(1)}%</span>
                    `;
                    coresContainer.appendChild(coreDiv);
                });
            }
            
            // Memory metrics
            const memory = data.memory || {};
            updateMetric('mem-usage', memory.usage_percent, '%');
            updateProgress('mem-progress', memory.usage_percent, 100);
            updateMetric('mem-available', (memory.available_gb || 0).toFixed(1), ' GB');
            updateMetric('mem-used', (memory.used_gb || 0).toFixed(1), ' GB');
            
            // Network metrics (calculate rates)
            const network = data.network || {};
            const now = Date.now();
            const timeDiff = (now - lastNetworkBytes.timestamp) / 1000;
            
            if (timeDiff > 0 && lastNetworkBytes.timestamp > 0) {
                const uploadRate = ((network.bytes_sent - lastNetworkBytes.sent) / timeDiff / 1024).toFixed(1);
                const downloadRate = ((network.bytes_recv - lastNetworkBytes.recv) / timeDiff / 1024).toFixed(1);
                updateMetric('net-upload', uploadRate, ' KB/s');
                updateMetric('net-download', downloadRate, ' KB/s');
            }
            
            lastNetworkBytes = {
                sent: network.bytes_sent || 0,
                recv: network.bytes_recv || 0,
                timestamp: now
            };
            
            // Disk metrics (calculate rates)
            const disk = data.disk || {};
            if (timeDiff > 0 && lastDiskBytes.timestamp > 0) {
                const readRate = ((disk.read_bytes - lastDiskBytes.read) / timeDiff / 1024 / 1024).toFixed(1);
                const writeRate = ((disk.write_bytes - lastDiskBytes.write) / timeDiff / 1024 / 1024).toFixed(1);
                const iops = Math.round((disk.read_count + disk.write_count - lastDiskBytes.read_count - lastDiskBytes.write_count) / timeDiff);
                
                updateMetric('disk-read', readRate, ' MB/s');
                updateMetric('disk-write', writeRate, ' MB/s');
                updateMetric('disk-iops', iops, '');
            }
            
            lastDiskBytes = {
                read: disk.read_bytes || 0,
                write: disk.write_bytes || 0,
                read_count: disk.read_count || 0,
                write_count: disk.write_count || 0,
                timestamp: now
            };
        }
        
        function updateMetric(elementId, value, unit) {
            const element = document.getElementById(elementId);
            if (element && value !== undefined && value !== null) {
                element.textContent = value + unit;
                
                // Color coding
                element.className = 'metric-value';
                if (elementId.includes('usage') || elementId.includes('mem-usage')) {
                    if (value > 90) element.classList.add('critical');
                    else if (value > 75) element.classList.add('warning');
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
        
        function updateChart(data) {
            const cpu = data.cpu || {};
            const memory = data.memory || {};
            
            const chart = performanceChart;
            const now = new Date().toLocaleTimeString();
            
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(cpu.usage_percent || 0);
            chart.data.datasets[1].data.push(memory.usage_percent || 0);
            
            // Keep only last 30 data points
            if (chart.data.labels.length > 30) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => dataset.data.shift());
            }
            
            chart.update('none');
        }
        
        function loadHardwareInfo() {
            fetch('/api/hardware')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('hardware-info');
                    container.innerHTML = '';
                    
                    if (data.error) {
                        container.innerHTML = '<div class="metric"><span class="metric-label">Hardware info unavailable</span></div>';
                        return;
                    }
                    
                    // CPU info
                    if (data.cpu) {
                        const cpu = data.cpu;
                        container.innerHTML += `
                            <div class="metric">
                                <span class="metric-label">CPU:</span>
                                <span class="metric-value">${cpu.physical_cores}C/${cpu.logical_cores}T @ ${Math.round(cpu.max_frequency || 0)}MHz</span>
                            </div>
                        `;
                    }
                    
                    // Memory info
                    if (data.memory) {
                        const memory = data.memory;
                        container.innerHTML += `
                            <div class="metric">
                                <span class="metric-label">Memory:</span>
                                <span class="metric-value">${memory.total_gb}GB ${memory.type || 'DDR4'} @ ${memory.speed || 3200}MHz</span>
                            </div>
                        `;
                    }
                    
                    // Storage info
                    if (data.storage && data.storage.length > 0) {
                        data.storage.forEach(storage => {
                            const type = storage.is_ssd ? 'SSD' : 'HDD';
                            container.innerHTML += `
                                <div class="metric">
                                    <span class="metric-label">${storage.device}:</span>
                                    <span class="metric-value">${storage.total_gb}GB ${type}</span>
                                </div>
                            `;
                        });
                    }
                })
                .catch(error => {
                    console.error('Error loading hardware info:', error);
                });
        }
        
        function refreshRecommendations() {
            fetch('/api/recommendations')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('recommendations');
                    container.innerHTML = '';
                    
                    data.recommendations.forEach(recommendation => {
                        const div = document.createElement('div');
                        div.className = 'recommendation-item';
                        div.textContent = recommendation;
                        container.appendChild(div);
                    });
                })
                .catch(error => {
                    console.error('Error loading recommendations:', error);
                });
        }
        
        function applyOptimizations() {
            showNotification('🔄 Applying optimizations...', 'info');
            
            fetch('/api/optimize', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ ' + data.message, 'success');
                        refreshRecommendations();
                    } else {
                        showNotification('❌ ' + data.message, 'error');
                    }
                })
                .catch(error => {
                    showNotification('❌ Optimization request failed', 'error');
                });
        }
        
        function toggleMonitoring() {
            monitoringEnabled = !monitoringEnabled;
            const btn = event.target;
            btn.textContent = monitoringEnabled ? '⏸️ Pause Monitoring' : '▶️ Resume Monitoring';
            btn.className = monitoringEnabled ? 'btn' : 'btn warning';
        }
        
        function resetOptimizations() {
            showNotification('🔄 Reset functionality not implemented yet', 'info');
        }
        
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification show';
            
            // Auto hide after 3 seconds
            setTimeout(() => {
                notification.className = 'notification';
            }, 3000);
        }
    </script>
</body>
</html>
        """
    
    def collect_enhanced_metrics(self):
        """Collect enhanced system metrics with more detailed information."""
        try:
            metrics = {}
            
            if self.optimizer:
                # Use the advanced optimizer's metrics
                metrics = self.optimizer.get_performance_metrics()
            else:
                # Fallback to basic metrics
                metrics = {
                    'timestamp': time.time(),
                    'cpu': {
                        'usage_percent': psutil.cpu_percent(interval=0.1),
                        'usage_per_core': psutil.cpu_percent(interval=0.1, percpu=True),
                        'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0
                    },
                    'memory': {
                        'usage_percent': psutil.virtual_memory().percent,
                        'available_gb': psutil.virtual_memory().available / (1024**3),
                        'used_gb': psutil.virtual_memory().used / (1024**3),
                        'total_gb': psutil.virtual_memory().total / (1024**3)
                    },
                    'network': {
                        'bytes_sent': psutil.net_io_counters().bytes_sent,
                        'bytes_recv': psutil.net_io_counters().bytes_recv,
                        'packets_sent': psutil.net_io_counters().packets_sent,
                        'packets_recv': psutil.net_io_counters().packets_recv
                    },
                    'disk': {
                        'read_bytes': psutil.disk_io_counters().read_bytes,
                        'write_bytes': psutil.disk_io_counters().write_bytes,
                        'read_count': psutil.disk_io_counters().read_count,
                        'write_count': psutil.disk_io_counters().write_count
                    }
                }
            
            self.current_metrics = metrics
            
            # Add to history
            self.performance_history.append({
                'timestamp': metrics.get('timestamp', time.time()),
                'cpu_usage': metrics.get('cpu', {}).get('usage_percent', 0),
                'memory_usage': metrics.get('memory', {}).get('usage_percent', 0)
            })
            
            # Limit history size
            if len(self.performance_history) > self.max_history_points:
                self.performance_history.pop(0)
            
            # Emit to connected clients
            if self.socketio:
                self.socketio.emit('metrics', metrics)
                
        except Exception as e:
            print(f"Error collecting enhanced metrics: {e}")
    
    def monitoring_loop(self):
        """Enhanced monitoring loop with more frequent updates."""
        self.start_time = time.time()
        
        while self.running:
            try:
                self.collect_enhanced_metrics()
                
                # Check if we should run optimization check (every 30 seconds)
                current_time = time.time()
                if current_time - self.last_optimization_check > 30:
                    self._check_for_optimization_opportunities()
                    self.last_optimization_check = current_time
                
                time.sleep(1)  # Update every second for real-time feel
                
            except Exception as e:
                print(f"Enhanced monitoring error: {e}")
                time.sleep(5)
    
    def _check_for_optimization_opportunities(self):
        """Check for automatic optimization opportunities."""
        if not self.current_metrics:
            return
            
        cpu_usage = self.current_metrics.get('cpu', {}).get('usage_percent', 0)
        memory_usage = self.current_metrics.get('memory', {}).get('usage_percent', 0)
        
        # Auto-optimize if system is under heavy load
        if cpu_usage > 95 or memory_usage > 95:
            if self.optimizer and self.socketio:
                self.socketio.emit('auto_optimization_suggested', {
                    'reason': f'High system load detected (CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%)',
                    'recommended_actions': ['Apply CPU optimizations', 'Free memory', 'Prioritize gaming processes']
                })
    
    def start(self):
        """Start the enhanced web dashboard."""
        if not HAS_FLASK:
            print("Flask is not available. Please install Flask and Flask-SocketIO:")
            print("pip install flask flask-socketio")
            return False
        
        self.running = True
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        print(f"🚀 Starting Enhanced Gaming Performance Dashboard")
        print(f"📊 Real-time monitoring with AI recommendations")
        print(f"🌐 Access at: http://localhost:{self.port}")
        print("💡 Open this URL on your secondary display for optimal monitoring.")
        
        try:
            if self.socketio:
                self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=False)
            else:
                self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down enhanced dashboard...")
        finally:
            self.running = False
        
        return True

if __name__ == "__main__":
    dashboard = EnhancedWebDashboard(port=5000)
    dashboard.start()