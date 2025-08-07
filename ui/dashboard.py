"""
Dashboard GUI for the gaming performance monitor.
Real-time display of system metrics, game performance, and optimization status.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import logging
from typing import Dict, Any, Optional, List
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class Dashboard:
    """Main GUI dashboard for the gaming performance monitor."""
    
    def __init__(self, monitors: Dict, optimizers: Dict):
        self.monitors = monitors
        self.optimizers = optimizers
        self.logger = logging.getLogger(__name__)
        
        # GUI state
        self.root = None
        self.running = False
        self.update_interval = 500  # milliseconds
        
        # Data storage for graphs
        self.graph_history_size = 300  # 5 minutes at 1Hz
        self.metrics_history = {
            'timestamps': deque(maxlen=self.graph_history_size),
            'fps': deque(maxlen=self.graph_history_size),
            'cpu_usage': deque(maxlen=self.graph_history_size),
            'gpu_usage': deque(maxlen=self.graph_history_size),
            'memory_usage': deque(maxlen=self.graph_history_size),
            'cpu_temp': deque(maxlen=self.graph_history_size),
            'gpu_temp': deque(maxlen=self.graph_history_size),
            'ping': deque(maxlen=self.graph_history_size)
        }
        
        # GUI components
        self.status_labels = {}
        self.metric_labels = {}
        self.progress_bars = {}
        self.graphs = {}
        
        self.logger.info("Dashboard initialized")
    
    def run(self):
        """Start the GUI dashboard."""
        try:
            self.root = tk.Tk()
            self.root.title("Gaming Performance Monitor - i7-9700K + RTX 3080")
            self.root.geometry("1400x900")
            self.root.configure(bg='#1e1e1e')  # Dark theme
            
            # Set minimum window size
            self.root.minsize(1200, 800)
            
            # Configure style for dark theme
            self.setup_dark_theme()
            
            # Create GUI layout
            self.create_layout()
            
            # Start update loop
            self.running = True
            self.start_update_loop()
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            
            # Run the GUI
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Dashboard startup failed: {e}")
            raise
    
    def setup_dark_theme(self):
        """Setup dark theme for the dashboard."""
        try:
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure dark theme colors
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
            style.configure('TButton', background='#404040', foreground='#ffffff')
            style.configure('TNotebook', background='#2d2d2d')
            style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff')
            style.configure('Horizontal.TProgressbar', background='#00ff00')
            
            # Configure treeview for dark theme
            style.configure("Treeview", background="#2d2d2d", foreground="#ffffff", fieldbackground="#2d2d2d")
            style.configure("Treeview.Heading", background="#404040", foreground="#ffffff")
            
        except Exception as e:
            self.logger.warning(f"Dark theme setup failed: {e}")
    
    def create_layout(self):
        """Create the main dashboard layout."""
        try:
            # Create main container
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Configure grid weights
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.rowconfigure(1, weight=1)
            
            # Create header
            self.create_header(main_frame)
            
            # Create notebook for different sections
            notebook = ttk.Notebook(main_frame)
            notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
            
            # Create tabs
            self.create_overview_tab(notebook)
            self.create_system_tab(notebook)
            self.create_game_tab(notebook)
            self.create_network_tab(notebook)
            self.create_optimization_tab(notebook)
            self.create_settings_tab(notebook)
            
        except Exception as e:
            self.logger.error(f"Layout creation failed: {e}")
    
    def create_header(self, parent):
        """Create the header with key metrics."""
        try:
            header_frame = ttk.Frame(parent)
            header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            header_frame.columnconfigure(1, weight=1)
            
            # Title
            title_label = ttk.Label(header_frame, text="Gaming Performance Monitor", 
                                  font=('Arial', 16, 'bold'))
            title_label.grid(row=0, column=0, sticky=tk.W)
            
            # System status
            status_frame = ttk.Frame(header_frame)
            status_frame.grid(row=0, column=1, sticky=tk.E)
            
            self.status_labels['system'] = ttk.Label(status_frame, text="System: Starting...", 
                                                   font=('Arial', 10))
            self.status_labels['system'].grid(row=0, column=0, padx=(0, 20))
            
            self.status_labels['game'] = ttk.Label(status_frame, text="Game: Not Detected", 
                                                 font=('Arial', 10))
            self.status_labels['game'].grid(row=0, column=1, padx=(0, 20))
            
            # Quick metrics
            metrics_frame = ttk.Frame(header_frame)
            metrics_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
            
            # FPS
            ttk.Label(metrics_frame, text="FPS:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=(0, 5))
            self.metric_labels['fps'] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
            self.metric_labels['fps'].grid(row=0, column=1, padx=(0, 20))
            
            # CPU
            ttk.Label(metrics_frame, text="CPU:", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=(0, 5))
            self.metric_labels['cpu'] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
            self.metric_labels['cpu'].grid(row=0, column=3, padx=(0, 20))
            
            # GPU
            ttk.Label(metrics_frame, text="GPU:", font=('Arial', 10, 'bold')).grid(row=0, column=4, padx=(0, 5))
            self.metric_labels['gpu'] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
            self.metric_labels['gpu'].grid(row=0, column=5, padx=(0, 20))
            
            # Memory
            ttk.Label(metrics_frame, text="RAM:", font=('Arial', 10, 'bold')).grid(row=0, column=6, padx=(0, 5))
            self.metric_labels['memory'] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
            self.metric_labels['memory'].grid(row=0, column=7, padx=(0, 20))
            
            # Ping
            ttk.Label(metrics_frame, text="Ping:", font=('Arial', 10, 'bold')).grid(row=0, column=8, padx=(0, 5))
            self.metric_labels['ping'] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
            self.metric_labels['ping'].grid(row=0, column=9)
            
        except Exception as e:
            self.logger.error(f"Header creation failed: {e}")
    
    def create_overview_tab(self, notebook):
        """Create the overview tab with key metrics and graphs."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="Overview")
            
            # Configure grid
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.columnconfigure(1, weight=1)
            tab_frame.rowconfigure(0, weight=1)
            tab_frame.rowconfigure(1, weight=1)
            
            # Performance graphs
            self.create_performance_graphs(tab_frame)
            
            # System overview
            self.create_system_overview(tab_frame)
            
        except Exception as e:
            self.logger.error(f"Overview tab creation failed: {e}")
    
    def create_performance_graphs(self, parent):
        """Create performance monitoring graphs."""
        try:
            # Graph frame
            graph_frame = ttk.LabelFrame(parent, text="Performance Graphs", padding="10")
            graph_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
            
            # Create matplotlib figure
            fig = Figure(figsize=(12, 6), facecolor='#2d2d2d')
            fig.patch.set_facecolor('#2d2d2d')
            
            # Create subplots
            ax1 = fig.add_subplot(2, 2, 1, facecolor='#2d2d2d')
            ax2 = fig.add_subplot(2, 2, 2, facecolor='#2d2d2d')
            ax3 = fig.add_subplot(2, 2, 3, facecolor='#2d2d2d')
            ax4 = fig.add_subplot(2, 2, 4, facecolor='#2d2d2d')
            
            # Configure subplot styling
            for ax, title in zip([ax1, ax2, ax3, ax4], ['FPS', 'CPU/GPU Usage', 'Temperature', 'Network']):
                ax.set_facecolor('#2d2d2d')
                ax.tick_params(colors='white')
                ax.set_title(title, color='white')
                ax.grid(True, alpha=0.3)
                
                # Set label colors
                ax.xaxis.label.set_color('white')
                ax.yaxis.label.set_color('white')
            
            # Store axes for updates
            self.graphs['axes'] = {
                'fps': ax1,
                'usage': ax2,
                'temperature': ax3,
                'network': ax4
            }
            
            # Create canvas
            canvas = FigureCanvasTkAgg(fig, graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            self.graphs['canvas'] = canvas
            
        except Exception as e:
            self.logger.error(f"Performance graphs creation failed: {e}")
    
    def create_system_overview(self, parent):
        """Create system overview panel."""
        try:
            # System info frame
            system_frame = ttk.LabelFrame(parent, text="System Information", padding="10")
            system_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
            
            # Hardware info
            hardware_info = [
                ("CPU:", "Intel i7-9700K"),
                ("GPU:", "NVIDIA RTX 3080"),
                ("RAM:", "16GB DDR4"),
                ("Storage:", "M.2 NVMe SSD"),
                ("OS:", "Windows 11")
            ]
            
            for i, (label, value) in enumerate(hardware_info):
                ttk.Label(system_frame, text=label, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky=tk.W, pady=2)
                ttk.Label(system_frame, text=value, font=('Arial', 10)).grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
            # Status indicators
            status_frame = ttk.LabelFrame(parent, text="System Status", padding="10")
            status_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
            
            # Progress bars for key metrics
            metrics = ['CPU Usage', 'GPU Usage', 'Memory Usage', 'CPU Temp', 'GPU Temp']
            
            for i, metric in enumerate(metrics):
                ttk.Label(status_frame, text=f"{metric}:", font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=5)
                
                progress = ttk.Progressbar(status_frame, length=200, mode='determinate')
                progress.grid(row=i, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
                
                value_label = ttk.Label(status_frame, text="0%", font=('Arial', 10))
                value_label.grid(row=i, column=2, sticky=tk.W, pady=5)
                
                self.progress_bars[metric.lower().replace(' ', '_')] = {
                    'bar': progress,
                    'label': value_label
                }
            
            # Configure column weights
            status_frame.columnconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.error(f"System overview creation failed: {e}")
    
    def create_system_tab(self, notebook):
        """Create detailed system monitoring tab."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="System")
            
            # Create treeview for detailed metrics
            columns = ('Metric', 'Value', 'Status')
            tree = ttk.Treeview(tab_frame, columns=columns, show='headings', height=20)
            
            # Configure columns
            tree.heading('Metric', text='Metric')
            tree.heading('Value', text='Value')
            tree.heading('Status', text='Status')
            
            tree.column('Metric', width=250, anchor=tk.W)
            tree.column('Value', width=150, anchor=tk.E)
            tree.column('Status', width=100, anchor=tk.CENTER)
            
            # Add scrollbar
            scrollbar = ttk.Scrollbar(tab_frame, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            # Configure grid weights
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(0, weight=1)
            
            # Store tree for updates
            self.system_tree = tree
            
        except Exception as e:
            self.logger.error(f"System tab creation failed: {e}")
    
    def create_game_tab(self, notebook):
        """Create game monitoring tab."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="Game")
            
            # Game detection frame
            game_frame = ttk.LabelFrame(tab_frame, text="Game Detection", padding="10")
            game_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            
            self.game_labels = {}
            self.game_labels['detected'] = ttk.Label(game_frame, text="No game detected", font=('Arial', 12, 'bold'))
            self.game_labels['detected'].grid(row=0, column=0, sticky=tk.W)
            
            # FPS monitoring
            fps_frame = ttk.LabelFrame(tab_frame, text="FPS Monitoring", padding="10")
            fps_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
            
            fps_metrics = [
                ('Current FPS', 'fps_current'),
                ('Average FPS', 'fps_average'),
                ('1% Low FPS', 'fps_1_low'),
                ('0.1% Low FPS', 'fps_0_1_low'),
                ('Frame Time', 'frame_time'),
                ('Frame Variance', 'frame_variance')
            ]
            
            self.fps_labels = {}
            for i, (label, key) in enumerate(fps_metrics):
                ttk.Label(fps_frame, text=f"{label}:", font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=2)
                self.fps_labels[key] = ttk.Label(fps_frame, text="--", font=('Arial', 10))
                self.fps_labels[key].grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
            
            # Performance issues
            issues_frame = ttk.LabelFrame(tab_frame, text="Performance Issues", padding="10")
            issues_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
            
            # Issues listbox
            self.issues_listbox = tk.Listbox(issues_frame, height=10, bg='#2d2d2d', fg='white')
            self.issues_listbox.pack(fill=tk.BOTH, expand=True)
            
            # Configure grid weights
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.columnconfigure(1, weight=1)
            tab_frame.rowconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.error(f"Game tab creation failed: {e}")
    
    def create_network_tab(self, notebook):
        """Create network monitoring tab."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="Network")
            
            # Network metrics
            metrics_frame = ttk.LabelFrame(tab_frame, text="Network Performance", padding="10")
            metrics_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            
            network_metrics = [
                ('Ping Average', 'ping_avg'),
                ('Ping Jitter', 'ping_jitter'),
                ('Packet Loss', 'packet_loss'),
                ('Download Speed', 'download_speed'),
                ('Upload Speed', 'upload_speed'),
                ('Network Health', 'network_health')
            ]
            
            self.network_labels = {}
            for i, (label, key) in enumerate(network_metrics):
                row = i // 2
                col = (i % 2) * 2
                
                ttk.Label(metrics_frame, text=f"{label}:", font=('Arial', 10)).grid(row=row, column=col, sticky=tk.W, pady=5, padx=(0, 10))
                self.network_labels[key] = ttk.Label(metrics_frame, text="--", font=('Arial', 10))
                self.network_labels[key].grid(row=row, column=col+1, sticky=tk.W, pady=5, padx=(0, 40))
            
            # Network optimization status
            opt_frame = ttk.LabelFrame(tab_frame, text="Optimization Status", padding="10")
            opt_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.network_status_tree = ttk.Treeview(opt_frame, columns=('Status',), show='tree headings', height=10)
            self.network_status_tree.heading('#0', text='Optimization')
            self.network_status_tree.heading('Status', text='Status')
            self.network_status_tree.column('#0', width=300)
            self.network_status_tree.column('Status', width=100)
            
            self.network_status_tree.pack(fill=tk.BOTH, expand=True)
            
            # Configure grid weights
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.error(f"Network tab creation failed: {e}")
    
    def create_optimization_tab(self, notebook):
        """Create optimization control tab."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="Optimizations")
            
            # Optimization controls
            controls_frame = ttk.LabelFrame(tab_frame, text="Optimization Controls", padding="10")
            controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            # Buttons for different optimizations
            opt_buttons = [
                ("Windows Optimization", self.apply_windows_optimization),
                ("Hardware Optimization", self.apply_hardware_optimization),
                ("Network Optimization", self.apply_network_optimization),
                ("Full Optimization", self.apply_full_optimization),
                ("Rollback Changes", self.rollback_optimizations)
            ]
            
            for i, (text, command) in enumerate(opt_buttons):
                btn = ttk.Button(controls_frame, text=text, command=command)
                btn.grid(row=0, column=i, padx=5, pady=5)
            
            # Optimization status
            status_frame = ttk.LabelFrame(tab_frame, text="Applied Optimizations", padding="10")
            status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self.optimization_tree = ttk.Treeview(status_frame, columns=('Status', 'Applied'), show='tree headings', height=15)
            self.optimization_tree.heading('#0', text='Optimization')
            self.optimization_tree.heading('Status', text='Status')
            self.optimization_tree.heading('Applied', text='Applied Time')
            
            self.optimization_tree.column('#0', width=300)
            self.optimization_tree.column('Status', width=100)
            self.optimization_tree.column('Applied', width=150)
            
            self.optimization_tree.pack(fill=tk.BOTH, expand=True)
            
            # Configure grid weights
            tab_frame.columnconfigure(0, weight=1)
            tab_frame.rowconfigure(1, weight=1)
            
        except Exception as e:
            self.logger.error(f"Optimization tab creation failed: {e}")
    
    def create_settings_tab(self, notebook):
        """Create settings and configuration tab."""
        try:
            tab_frame = ttk.Frame(notebook, padding="10")
            notebook.add(tab_frame, text="Settings")
            
            # Settings will be implemented here
            ttk.Label(tab_frame, text="Settings and configuration options will be available here.", 
                     font=('Arial', 12)).pack(pady=20)
            
        except Exception as e:
            self.logger.error(f"Settings tab creation failed: {e}")
    
    def start_update_loop(self):
        """Start the GUI update loop."""
        if self.running:
            try:
                self.update_dashboard()
                self.root.after(self.update_interval, self.start_update_loop)
            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                self.root.after(self.update_interval * 2, self.start_update_loop)  # Slower retry
    
    def update_dashboard(self):
        """Update all dashboard components with current data."""
        try:
            # Get current metrics from monitors
            system_metrics = self.monitors['system'].get_current_metrics()
            game_metrics = self.monitors['game'].get_current_metrics()
            network_metrics = self.monitors['network'].get_current_metrics()
            
            # Update header metrics
            self.update_header_metrics(system_metrics, game_metrics, network_metrics)
            
            # Update graphs
            self.update_performance_graphs(system_metrics, game_metrics, network_metrics)
            
            # Update system tree
            self.update_system_tree(system_metrics)
            
            # Update game tab
            self.update_game_tab(game_metrics)
            
            # Update network tab
            self.update_network_tab(network_metrics)
            
            # Store data for graphs
            self.store_metrics_data(system_metrics, game_metrics, network_metrics)
            
        except Exception as e:
            self.logger.error(f"Dashboard update error: {e}")
    
    def update_header_metrics(self, system_metrics, game_metrics, network_metrics):
        """Update header quick metrics."""
        try:
            # FPS
            fps = game_metrics.get('fps', 0) or game_metrics.get('avg_fps_calculated', 0)
            self.metric_labels['fps'].config(text=f"{fps:.1f}" if fps > 0 else "--")
            
            # CPU
            cpu_usage = system_metrics.get('cpu_usage_total', 0)
            cpu_temp = system_metrics.get('cpu_temperature', 0) or system_metrics.get('temp_cpu_package', 0)
            cpu_text = f"{cpu_usage:.1f}%"
            if cpu_temp > 0:
                cpu_text += f" ({cpu_temp:.1f}°C)"
            self.metric_labels['cpu'].config(text=cpu_text)
            
            # GPU
            gpu_usage = system_metrics.get('gpu_usage', 0)
            gpu_temp = system_metrics.get('gpu_temperature', 0)
            gpu_text = f"{gpu_usage:.1f}%"
            if gpu_temp > 0:
                gpu_text += f" ({gpu_temp:.1f}°C)"
            self.metric_labels['gpu'].config(text=gpu_text)
            
            # Memory
            memory_percent = system_metrics.get('memory_percent', 0)
            memory_gb = system_metrics.get('memory_used', 0) / (1024**3) if system_metrics.get('memory_used') else 0
            self.metric_labels['memory'].config(text=f"{memory_percent:.1f}% ({memory_gb:.1f}GB)")
            
            # Ping
            ping = network_metrics.get('ping_avg', 0)
            self.metric_labels['ping'].config(text=f"{ping:.0f}ms" if ping > 0 else "--")
            
            # System status
            current_game = self.monitors['game'].get_current_game()
            if current_game:
                self.status_labels['game'].config(text=f"Game: {current_game}")
            else:
                self.status_labels['game'].config(text="Game: Not Detected")
            
        except Exception as e:
            self.logger.debug(f"Header metrics update error: {e}")
    
    def update_performance_graphs(self, system_metrics, game_metrics, network_metrics):
        """Update performance graphs."""
        try:
            if 'canvas' not in self.graphs:
                return
            
            # Update graph data would go here
            # This is a simplified version - full implementation would plot real-time data
            
        except Exception as e:
            self.logger.debug(f"Graphs update error: {e}")
    
    def update_system_tree(self, system_metrics):
        """Update system metrics tree."""
        try:
            if not hasattr(self, 'system_tree'):
                return
            
            # Clear existing items
            for item in self.system_tree.get_children():
                self.system_tree.delete(item)
            
            # Add system metrics
            metrics_to_show = [
                ('CPU Usage', f"{system_metrics.get('cpu_usage_total', 0):.1f}%", 'Normal'),
                ('GPU Usage', f"{system_metrics.get('gpu_usage', 0):.1f}%", 'Normal'),
                ('Memory Usage', f"{system_metrics.get('memory_percent', 0):.1f}%", 'Normal'),
                ('CPU Temperature', f"{system_metrics.get('cpu_temperature', 0):.1f}°C", 'Normal'),
                ('GPU Temperature', f"{system_metrics.get('gpu_temperature', 0):.1f}°C", 'Normal'),
            ]
            
            for metric, value, status in metrics_to_show:
                self.system_tree.insert('', 'end', values=(metric, value, status))
            
        except Exception as e:
            self.logger.debug(f"System tree update error: {e}")
    
    def update_game_tab(self, game_metrics):
        """Update game monitoring tab."""
        try:
            if not hasattr(self, 'game_labels'):
                return
            
            # Update game detection
            current_game = self.monitors['game'].get_current_game()
            if current_game:
                self.game_labels['detected'].config(text=f"Detected: {current_game}")
            else:
                self.game_labels['detected'].config(text="No game detected")
            
            # Update FPS metrics
            if hasattr(self, 'fps_labels'):
                fps_data = {
                    'fps_current': game_metrics.get('fps', 0) or game_metrics.get('avg_fps_calculated', 0),
                    'fps_average': game_metrics.get('avg_fps_calculated', 0),
                    'fps_1_low': game_metrics.get('1_percent_low_fps', 0),
                    'fps_0_1_low': game_metrics.get('0_1_percent_low_fps', 0),
                    'frame_time': game_metrics.get('frame_time', 0),
                    'frame_variance': game_metrics.get('frame_time_variance', 0)
                }
                
                for key, value in fps_data.items():
                    if key in self.fps_labels:
                        if key.startswith('fps'):
                            text = f"{value:.1f}" if value > 0 else "--"
                        else:
                            text = f"{value:.2f}ms" if value > 0 else "--"
                        self.fps_labels[key].config(text=text)
            
            # Update performance issues
            if hasattr(self, 'issues_listbox'):
                issues = self.monitors['game'].get_performance_issues()
                self.issues_listbox.delete(0, tk.END)
                
                if issues:
                    for issue in issues:
                        self.issues_listbox.insert(tk.END, issue.replace('_', ' ').title())
                else:
                    self.issues_listbox.insert(tk.END, "No performance issues detected")
            
        except Exception as e:
            self.logger.debug(f"Game tab update error: {e}")
    
    def update_network_tab(self, network_metrics):
        """Update network monitoring tab."""
        try:
            if not hasattr(self, 'network_labels'):
                return
            
            # Update network metrics
            network_data = {
                'ping_avg': f"{network_metrics.get('ping_avg', 0):.0f}ms",
                'ping_jitter': f"{network_metrics.get('ping_jitter', 0):.1f}ms",
                'packet_loss': f"{network_metrics.get('packet_loss_estimated', 0):.1f}%",
                'download_speed': f"{network_metrics.get('download_speed_mbps', 0):.1f} Mbps",
                'upload_speed': f"{network_metrics.get('upload_speed_mbps', 0):.1f} Mbps",
                'network_health': f"{network_metrics.get('network_health_score', 100):.0f}/100"
            }
            
            for key, value in network_data.items():
                if key in self.network_labels:
                    self.network_labels[key].config(text=value if any(c.isdigit() for c in value) else "--")
            
        except Exception as e:
            self.logger.debug(f"Network tab update error: {e}")
    
    def store_metrics_data(self, system_metrics, game_metrics, network_metrics):
        """Store metrics data for graphing."""
        try:
            current_time = time.time()
            
            self.metrics_history['timestamps'].append(current_time)
            self.metrics_history['fps'].append(game_metrics.get('fps', 0) or game_metrics.get('avg_fps_calculated', 0))
            self.metrics_history['cpu_usage'].append(system_metrics.get('cpu_usage_total', 0))
            self.metrics_history['gpu_usage'].append(system_metrics.get('gpu_usage', 0))
            self.metrics_history['memory_usage'].append(system_metrics.get('memory_percent', 0))
            self.metrics_history['cpu_temp'].append(system_metrics.get('cpu_temperature', 0) or system_metrics.get('temp_cpu_package', 0))
            self.metrics_history['gpu_temp'].append(system_metrics.get('gpu_temperature', 0))
            self.metrics_history['ping'].append(network_metrics.get('ping_avg', 0))
            
        except Exception as e:
            self.logger.debug(f"Metrics storage error: {e}")
    
    # Optimization button handlers
    def apply_windows_optimization(self):
        """Apply Windows optimizations."""
        try:
            threading.Thread(target=self._apply_windows_opt_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply Windows optimization: {e}")
    
    def _apply_windows_opt_thread(self):
        """Windows optimization thread."""
        try:
            result = self.optimizers['windows'].optimize_for_gaming()
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Windows optimization completed: {result}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Windows optimization failed: {e}"))
    
    def apply_hardware_optimization(self):
        """Apply hardware optimizations."""
        try:
            threading.Thread(target=self._apply_hardware_opt_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply hardware optimization: {e}")
    
    def _apply_hardware_opt_thread(self):
        """Hardware optimization thread."""
        try:
            result = self.optimizers['hardware'].boost_performance()
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Hardware optimization completed: {result}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Hardware optimization failed: {e}"))
    
    def apply_network_optimization(self):
        """Apply network optimizations."""
        try:
            threading.Thread(target=self._apply_network_opt_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply network optimization: {e}")
    
    def _apply_network_opt_thread(self):
        """Network optimization thread."""
        try:
            result = self.optimizers['network'].optimize_connection()
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Network optimization completed: {result}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Network optimization failed: {e}"))
    
    def apply_full_optimization(self):
        """Apply all optimizations."""
        try:
            threading.Thread(target=self._apply_full_opt_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply full optimization: {e}")
    
    def _apply_full_opt_thread(self):
        """Full optimization thread."""
        try:
            results = {}
            results['windows'] = self.optimizers['windows'].optimize_for_gaming()
            results['hardware'] = self.optimizers['hardware'].boost_performance()
            results['network'] = self.optimizers['network'].optimize_connection()
            
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Full optimization completed: {results}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Full optimization failed: {e}"))
    
    def rollback_optimizations(self):
        """Rollback all optimizations."""
        try:
            result = messagebox.askyesno("Confirm Rollback", "Are you sure you want to rollback all optimizations?")
            if result:
                threading.Thread(target=self._rollback_thread, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rollback optimizations: {e}")
    
    def _rollback_thread(self):
        """Rollback thread."""
        try:
            results = {}
            results['windows'] = self.optimizers['windows'].rollback_optimizations()
            results['network'] = self.optimizers['network'].rollback_optimizations()
            
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Rollback completed: {results}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Rollback failed: {e}"))
    
    def on_close(self):
        """Handle window close event."""
        try:
            self.running = False
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"Dashboard close error: {e}")
            self.root.destroy()