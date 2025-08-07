"""
Hardware-specific profiles for gaming performance optimization.
Contains detailed configurations for different hardware combinations.
"""

class HardwareProfiles:
    """Hardware configuration profiles for different gaming setups."""
    
    @staticmethod
    def get_i7_9700k_rtx3080_profile():
        """
        Optimized profile for Intel i7-9700K + RTX 3080 + 16GB RAM + M.2 SSD.
        Target hardware configuration specified in the requirements.
        """
        return {
            "profile_name": "i7-9700K_RTX3080_16GB",
            "description": "High-end gaming configuration with i7-9700K and RTX 3080",
            
            # CPU Configuration
            "cpu": {
                "model": "Intel Core i7-9700K",
                "architecture": "Coffee Lake",
                "cores": 8,
                "threads": 8,  # No hyperthreading on 9700K
                "base_clock": 3600,  # MHz
                "boost_clock": 4900,  # MHz
                "tdp": 95,  # Watts
                "socket": "LGA1151",
                
                # Optimization settings
                "enable_turbo_boost": True,
                "enable_speedstep": True,
                "power_profile": "maximum_performance",
                "c_states": "disabled",  # For gaming
                "voltage_mode": "auto",
                
                # Temperature management
                "temp_warning": 80,
                "temp_critical": 85,
                "throttle_temp": 90,
                "fan_curve": "aggressive",
                
                # Performance tweaks
                "ring_ratio": "auto",
                "cache_ratio": "auto",
                "memory_controller": "optimized"
            },
            
            # GPU Configuration
            "gpu": {
                "model": "NVIDIA GeForce RTX 3080",
                "architecture": "Ampere",
                "vram": 10240,  # MB
                "base_clock": 1440,  # MHz
                "boost_clock": 1710,  # MHz
                "memory_clock": 19000,  # MHz effective
                "memory_bus": 320,  # bit
                "cuda_cores": 8704,
                "rt_cores": 68,
                "tensor_cores": 272,
                
                # Power settings
                "tdp": 320,  # Watts
                "power_limit": 100,  # Percentage (can go up to ~115%)
                "temp_limit": 83,
                "fan_speed": "auto",
                
                # Optimization settings
                "gpu_boost": True,
                "memory_transfer_rate_optimization": True,
                "shader_cache": True,
                "threaded_optimization": True,
                "triple_buffering": False,  # Prefer lower latency
                
                # NVIDIA Control Panel settings
                "prefer_maximum_performance": True,
                "texture_filtering_quality": "performance",
                "anisotropic_filtering": "off",
                "antialiasing_gamma_correction": "on",
                "cuda_gpus": "all",
                
                # Temperature management
                "temp_warning": 78,
                "temp_critical": 83,
                "throttle_temp": 87,
                "fan_curve_aggressive": True
            },
            
            # Memory Configuration
            "memory": {
                "capacity": 16384,  # MB
                "type": "DDR4",
                "speed": 3200,  # MHz
                "channels": 2,  # Dual channel
                "cas_latency": 16,
                "voltage": 1.35,  # V
                
                # XMP Profile
                "xmp_enabled": True,
                "xmp_profile": 1,
                
                # Timings (typical for DDR4-3200 CL16)
                "timings": {
                    "cl": 16,
                    "trcd": 18,
                    "trp": 18,
                    "tras": 36,
                    "trc": 54,
                    "twr": 12,
                    "trfc": 560
                },
                
                # Optimization
                "enable_memory_compression": True,
                "prefetch_parameters": "optimized",
                "virtual_memory": {
                    "initial_size": 16384,  # MB
                    "maximum_size": 32768   # MB
                }
            },
            
            # Storage Configuration
            "storage": {
                "type": "NVMe M.2 SSD",
                "capacity": 1000,  # GB
                "interface": "PCIe 4.0 x4",
                "max_sequential_read": 7000,  # MB/s
                "max_sequential_write": 6000,  # MB/s
                "max_random_read_iops": 1000000,
                "max_random_write_iops": 1000000,
                
                # Optimization settings
                "enable_write_cache": True,
                "disable_indexing": True,
                "disable_defrag": True,  # Not needed for SSD
                "enable_trim": True,
                "over_provisioning": 7,  # Percentage
                
                # Windows settings
                "disable_hibernation": True,
                "disable_system_restore": False,  # Keep for safety
                "disable_prefetch": True,
                "disable_superfetch": True
            },
            
            # Performance Thresholds
            "thresholds": {
                # FPS targets
                "min_fps": 60,
                "target_fps": 120,
                "max_fps": 240,  # Monitor dependent
                "fps_consistency": 95,  # Percentage of frames within target
                
                # Frame timing
                "max_frame_time": 16.67,  # ms (60 FPS)
                "target_frame_time": 8.33,  # ms (120 FPS)
                "frame_time_variance": 2.0,  # ms
                
                # System performance
                "max_cpu_temp": 85,
                "max_gpu_temp": 83,
                "max_cpu_usage": 90,
                "max_gpu_usage": 95,
                "max_memory_usage": 90,
                "max_vram_usage": 90,
                
                # Network performance
                "max_ping": 50,
                "max_jitter": 10,
                "max_packet_loss": 1.0,
                "min_bandwidth": 100,
                
                # System responsiveness
                "max_input_lag": 20,  # ms
                "max_system_latency": 10,  # ms
                "max_disk_response": 5  # ms
            },
            
            # Game-specific optimizations
            "game_optimizations": {
                "fps_games": {
                    "priority": "realtime",
                    "affinity": [0, 1, 2, 3, 4, 5],  # Use 6 cores
                    "disable_dwm": False,  # Keep DWM for Windows 10/11
                    "exclusive_fullscreen": True,
                    "vsync": False,
                    "reduce_input_lag": True
                },
                
                "competitive_games": {
                    "priority": "high",
                    "network_priority": "gaming",
                    "disable_notifications": True,
                    "optimize_network": True,
                    "reduce_system_latency": True
                },
                
                "aaa_games": {
                    "priority": "high",
                    "enable_all_cores": True,
                    "optimize_graphics": True,
                    "manage_thermals": True
                }
            },
            
            # Monitoring intervals
            "monitoring": {
                "cpu_interval": 1.0,      # seconds
                "gpu_interval": 1.0,      # seconds
                "memory_interval": 2.0,   # seconds
                "network_interval": 1.0,  # seconds
                "temperature_interval": 2.0,  # seconds
                "fps_interval": 0.1,      # seconds
                "disk_interval": 5.0      # seconds
            },
            
            # Safety limits
            "safety": {
                "max_overclock_cpu": 5,     # Percentage above base
                "max_overclock_gpu": 10,    # Percentage above base
                "emergency_throttle_cpu": 95,   # Celsius
                "emergency_throttle_gpu": 90,   # Celsius
                "power_limit_safety": 110,      # Percentage
                "voltage_limit": 1.4,           # Volts (CPU)
            }
        }
    
    @staticmethod
    def get_default_profile():
        """Get a conservative default profile for unknown hardware."""
        return {
            "profile_name": "default",
            "description": "Conservative default profile",
            
            "thresholds": {
                "min_fps": 30,
                "target_fps": 60,
                "max_cpu_temp": 80,
                "max_gpu_temp": 85,
                "max_memory_usage": 85,
                "max_ping": 100
            },
            
            "monitoring": {
                "cpu_interval": 2.0,
                "gpu_interval": 2.0,
                "memory_interval": 5.0,
                "network_interval": 2.0,
                "temperature_interval": 3.0,
                "fps_interval": 1.0,
                "disk_interval": 10.0
            }
        }
    
    @staticmethod
    def detect_hardware():
        """
        Attempt to detect current hardware configuration.
        Returns appropriate profile or default.
        """
        try:
            import platform
            import subprocess
            import psutil
            
            # Get CPU info
            cpu_info = platform.processor()
            
            # Check if it's the target i7-9700K system
            if "i7-9700K" in cpu_info or "9700K" in cpu_info:
                return HardwareProfiles.get_i7_9700k_rtx3080_profile()
            
            # Add more hardware detection logic here
            # For now, return default
            return HardwareProfiles.get_default_profile()
            
        except Exception:
            return HardwareProfiles.get_default_profile()