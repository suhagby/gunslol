# Gaming Performance Monitor

A comprehensive 24/7 PC gaming performance monitoring and optimization system specifically designed for high-end gaming setups. This system continuously monitors system performance, detects issues, and applies automatic optimizations to maintain optimal gaming performance.

## Target Hardware Configuration

This monitor is specifically optimized for:
- **CPU**: Intel i7-9700K (8 cores, 8 threads)
- **GPU**: NVIDIA RTX 3080 (10GB VRAM)
- **RAM**: 16GB DDR4
- **Storage**: M.2 NVMe SSD (7000MB/s)
- **OS**: Windows 10/11

## Features

### 🖥️ Real-time System Monitoring
- **CPU Metrics**: Usage per core, temperatures, frequencies, boost states
- **GPU Metrics**: Usage, VRAM, temperatures, clock speeds, power consumption
- **Memory**: RAM usage, virtual memory, cache performance
- **Storage**: I/O rates, disk usage, SSD health monitoring
- **Temperatures**: CPU, GPU, and other system sensors

### 🎮 Game Performance Analysis
- **FPS Monitoring**: Real-time FPS, 1% low, 0.1% low calculations
- **Frame Timing**: Frame time analysis, stutter detection
- **Input Latency**: Estimated input lag measurement
- **Game Detection**: Automatic detection of running games
- **Performance Issues**: Automatic detection of FPS drops, stuttering

### 🌐 Network Performance Monitoring
- **Latency**: Ping to gaming servers, jitter measurement
- **Connectivity**: Packet loss detection, connection stability
- **Bandwidth**: Download/upload speed testing
- **DNS Performance**: DNS resolution time optimization
- **Gaming Server Monitoring**: Specific game server ping monitoring

### ⚡ Automatic Optimizations

#### Windows System Optimizations
- Game Mode activation and optimization
- Windows Defender real-time scanning control
- Background service management
- Visual effects optimization for performance
- Power plan optimization (High Performance)
- Process priority management
- Memory management optimization

#### Hardware-Specific Optimizations
- **Intel i7-9700K**: Turbo Boost management, thermal control
- **RTX 3080**: Power limit optimization, memory clock tuning
- **DDR4 RAM**: XMP profile optimization, timing adjustments
- **M.2 SSD**: TRIM optimization, write cache settings

#### Network Stack Optimizations
- TCP/IP stack tuning for gaming
- Nagle algorithm disable
- DNS optimization (Cloudflare/Google DNS)
- QoS gaming traffic prioritization
- Network adapter optimization

### 📊 Dashboard and Interface
- **Real-time Dashboard**: Live performance metrics display
- **Performance Graphs**: Historical data visualization
- **System Information**: Detailed hardware information
- **Optimization Controls**: Manual optimization triggers
- **Issue Alerts**: Performance problem notifications
- **Gaming Session Tracking**: Session-based performance analysis

## Installation

### Prerequisites
1. **Administrator Privileges**: Required for system optimizations
2. **Windows 10/11**: Primary supported OS
3. **Python 3.9+**: Required runtime
4. **NVIDIA Drivers**: Latest drivers for RTX 3080 monitoring

### Quick Install
```bash
# Install requirements
pip install -r requirements.txt

# Run the monitor
python main.py
```

## Usage

### Starting the Monitor
```bash
# Basic start
python main.py

# With specific log level
python main.py --log-level DEBUG
```

### Dashboard Interface
1. **Overview Tab**: Real-time performance metrics and graphs
2. **System Tab**: Detailed system monitoring
3. **Game Tab**: Game-specific performance analysis
4. **Network Tab**: Network performance monitoring
5. **Optimizations Tab**: Manual optimization controls

## Configuration

The system uses `config/settings.yaml` for configuration. Key settings include:

```yaml
# Performance thresholds
thresholds:
  min_fps: 60
  target_fps: 120
  max_cpu_temp: 85
  max_gpu_temp: 83
  max_memory_usage: 90
  max_ping: 50
```

## Supported Games
- League of Legends
- Counter-Strike 2  
- Valorant
- Fortnite
- Call of Duty series
- Apex Legends
- Overwatch 2
- Cyberpunk 2077
- Elden Ring

## System Requirements
- **Minimum**: Windows 10, 4GB RAM, Intel i5
- **Recommended**: Windows 11, 8GB RAM, Intel i7
- **Optimal**: Windows 11, 16GB RAM, Intel i7-9700K + RTX 3080

## Performance Impact
- **CPU Usage**: <2% during normal monitoring
- **Memory Usage**: <100MB typical
- **Disk Usage**: <1MB/day for metrics storage

## License

This project is licensed under the MIT License.


