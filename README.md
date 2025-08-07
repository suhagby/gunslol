# PC Gaming Performance Monitor & Optimizer

A comprehensive 24/7 PC gaming performance monitoring and optimization system specifically designed for high-end gaming setups. This system continuously monitors system performance, detects issues, and applies automatic optimizations to maintain optimal gaming performance.

## 🎮 New Features

### Web-Based Monitoring Dashboard
- **Real-time monitoring** on a separate display
- **Beautiful web interface** with live metrics
- **Mobile-friendly** responsive design
- **Auto-refresh** every 2 seconds
- Access via: `http://localhost:5000`

### Enhanced Optimization Suite
- **Advanced CPU optimization** with scheduler tuning
- **Memory management** with cache optimization
- **Network performance** tuning for gaming
- **Process priority** management for games
- **System cleanup** and maintenance tools

### Easy-to-Use Launcher
- **Interactive menu** system
- **One-click optimizations**
- **System status monitoring**
- **Quick cleanup tools**

## 🚀 Quick Start

### Option 1: Use the Launcher (Recommended)
```bash
python3 launcher.py
```

### Option 2: Start Web Dashboard Directly
```bash
python3 web_dashboard.py
```
Then open `http://localhost:5000` on your secondary display.

### Option 3: Run Enhanced Optimization
```bash
python3 enhanced_optimizer.py
```

### Option 4: Full System Monitor
```bash
python3 main.py
```

## 📦 Installation

### Prerequisites
- **Linux/Windows**: Primary supported OS
- **Python 3.9+**: Required runtime  
- **Administrator/Root privileges**: Required for system optimizations

### Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3-psutil python3-matplotlib python3-numpy python3-flask python3-yaml

# Or using pip (if apt packages not available)
pip install psutil matplotlib numpy flask PyYAML
```

## 🎯 Target Hardware Configuration

This system is optimized for:
- **CPU**: Intel i7-9700K (8 cores, 8 threads) or similar
- **GPU**: NVIDIA RTX 3080 (10GB VRAM) or equivalent
- **RAM**: 16GB DDR4 or more
- **Storage**: M.2 NVMe SSD (7000MB/s) 
- **OS**: Windows 10/11 or Linux

## 🌟 Features

### Real-time System Monitoring
- **CPU**: Usage per core, temperatures, frequencies, boost states
- **GPU**: Usage, VRAM, temperatures, clock speeds, power consumption
- **Memory**: RAM usage, virtual memory, cache performance
- **Storage**: I/O rates, disk usage, SSD health monitoring
- **Network**: Latency, bandwidth, packet loss monitoring

### Game Performance Analysis  
- **FPS Monitoring**: Real-time FPS tracking and analysis
- **Frame Timing**: Frame time analysis with stutter detection
- **Input Latency**: Estimated input lag measurement
- **Game Detection**: Automatic detection of running games
- **Performance Issues**: Auto-detection of FPS drops and stuttering

### Automatic Optimizations

#### System-Level Optimizations
- CPU governor and frequency scaling optimization
- Memory management parameter tuning
- Disk I/O scheduler optimization for SSDs
- Network TCP/IP stack optimization for gaming
- Process priority management for gaming applications

#### Gaming-Specific Optimizations  
- Game Mode activation and optimization
- Background service management during gaming
- Visual effects optimization for performance
- Power plan optimization (High Performance mode)
- Real-time process priority adjustments

### Web Dashboard Features
- **Modern UI**: Dark theme with gaming aesthetics
- **Real-time Metrics**: Live CPU, GPU, memory, and network stats
- **Progress Bars**: Visual representation of system load
- **Color Coding**: Green/Yellow/Red indicators for performance levels
- **Responsive Design**: Works on tablets and secondary displays
- **Auto-refresh**: Updates every 2 seconds automatically

## 📊 Web Dashboard

The web dashboard provides a beautiful, real-time monitoring interface perfect for secondary displays:

- **System Overview**: CPU usage, temperature, and frequency
- **GPU Monitoring**: Usage, VRAM, temperature tracking  
- **Memory Status**: RAM usage with available memory display
- **Storage I/O**: Disk usage and read/write speeds
- **Network Performance**: Ping, download/upload speeds
- **Gaming Metrics**: FPS, frame time, input lag (when gaming)

### Dashboard Screenshots

Access the dashboard at `http://localhost:5000` after starting the web dashboard.

## 🔧 Configuration

The system uses `config/settings.yaml` for configuration:

```yaml
# Performance thresholds
thresholds:
  min_fps: 60
  target_fps: 120  
  max_cpu_temp: 85
  max_gpu_temp: 83
  max_memory_usage: 90
  max_ping: 50

# Hardware-specific settings  
hardware:
  cpu:
    model: "Intel i7-9700K"
    enable_turbo_boost: true
    power_profile: "high_performance"
  gpu:
    model: "NVIDIA RTX 3080"
    power_limit: 100
    enable_gpu_boost: true
```

## 🎮 Supported Games

- League of Legends
- Counter-Strike 2
- Valorant  
- Fortnite
- Call of Duty series
- Apex Legends
- Overwatch 2
- Cyberpunk 2077
- Elden Ring
- And many more...

## 📈 Performance Impact

- **CPU Usage**: <2% during normal monitoring
- **Memory Usage**: <100MB typical
- **Network**: Minimal bandwidth for web dashboard
- **Disk Usage**: <1MB/day for metrics storage

## 🛠️ Troubleshooting

### Web Dashboard Not Loading
```bash
# Check if Flask is installed
python3 -c "import flask; print('Flask OK')"

# Check if port is available
netstat -tulpn | grep :5000
```

### Optimization Not Working
```bash
# Check permissions
sudo -v

# Check system compatibility  
uname -a
python3 --version
```

### High System Usage
```bash
# Check running processes
python3 launcher.py
# Select option 4 for system status
```

## 🤝 Contributing

This is an optimization system for PC gaming performance. Focus areas for improvement:

- Additional hardware compatibility
- More game-specific optimizations
- Enhanced monitoring metrics
- Better web dashboard features

## 📄 License

This project is licensed under the MIT License.

---

## 🚀 What's New in This Version

### ✅ Repository Cleanup
- **Removed**: Photography website and unrelated web applications  
- **Removed**: URL shortener applications
- **Removed**: Unnecessary Node.js dependencies
- **Kept**: Core optimization and monitoring system

### ✅ New Tools Added
- **Web Dashboard**: Real-time monitoring for secondary displays
- **Enhanced Optimizer**: Advanced system optimization beyond base system
- **Interactive Launcher**: Easy-to-use menu system for all tools
- **Quick System Status**: Instant performance overview

### ✅ Improved Performance  
- **Memory optimization**: Cache management and parameter tuning
- **CPU optimization**: Scheduler and frequency scaling improvements  
- **Network optimization**: TCP/IP stack tuning for gaming
- **Process management**: Auto-prioritization of gaming applications

The repository is now focused purely on PC optimization and monitoring, making it much cleaner and more efficient for its intended purpose.

