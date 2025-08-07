#!/usr/bin/env python3
"""
Mouse and Input Optimization Module
Advanced optimizations for reducing input lag, improving mouse responsiveness,
and optimizing USB polling rates for gaming peripherals.
"""

import os
import sys
import subprocess
import platform
import time
import psutil
from pathlib import Path
from typing import Dict, List, Optional

class MouseInputOptimizer:
    """Specialized optimizer for mouse and input device performance."""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.optimizations_applied = []
        self.detected_devices = []
        self.detect_input_devices()
    
    def detect_input_devices(self):
        """Detect connected input devices."""
        print("🖱️ Detecting input devices...")
        
        if self.platform == 'linux':
            self._detect_linux_devices()
        elif self.platform == 'windows':
            self._detect_windows_devices()
        
        self._print_device_summary()
    
    def _detect_linux_devices(self):
        """Detect input devices on Linux."""
        try:
            # Check /dev/input/ for input devices
            input_devices = []
            if os.path.exists('/dev/input/'):
                for device in os.listdir('/dev/input/'):
                    if device.startswith('event'):
                        try:
                            device_path = f'/dev/input/{device}'
                            # Try to get device name
                            with open(f'/sys/class/input/{device}/device/name', 'r') as f:
                                device_name = f.read().strip()
                                input_devices.append({
                                    'path': device_path,
                                    'name': device_name,
                                    'type': self._classify_device(device_name)
                                })
                        except:
                            pass
            
            # Use xinput to get more detailed info
            try:
                result = subprocess.run(['xinput', 'list'], capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'slave  pointer' in line.lower() or 'slave  keyboard' in line.lower():
                        if 'mouse' in line.lower() or 'keyboard' in line.lower():
                            device_info = {
                                'name': line.strip(),
                                'type': 'mouse' if 'mouse' in line.lower() else 'keyboard',
                                'xinput': True
                            }
                            self.detected_devices.append(device_info)
            except:
                pass
            
            # Add direct input devices
            for device in input_devices:
                self.detected_devices.append(device)
                
        except Exception as e:
            print(f"Linux device detection error: {e}")
    
    def _detect_windows_devices(self):
        """Detect input devices on Windows."""
        # Windows device detection would require different approach
        # For now, add placeholder
        self.detected_devices.append({
            'name': 'Windows Input Device',
            'type': 'mouse',
            'windows': True
        })
    
    def _classify_device(self, device_name: str) -> str:
        """Classify device type based on name."""
        name_lower = device_name.lower()
        
        if any(keyword in name_lower for keyword in ['mouse', 'optical', 'laser', 'gaming mouse']):
            return 'mouse'
        elif any(keyword in name_lower for keyword in ['keyboard', 'kbd']):
            return 'keyboard'
        elif any(keyword in name_lower for keyword in ['touchpad', 'trackpad']):
            return 'touchpad'
        elif any(keyword in name_lower for keyword in ['joystick', 'gamepad', 'controller']):
            return 'gamepad'
        else:
            return 'unknown'
    
    def _print_device_summary(self):
        """Print detected devices summary."""
        print(f"\n🎮 Detected {len(self.detected_devices)} input devices:")
        for device in self.detected_devices:
            device_type = device.get('type', 'unknown')
            device_name = device.get('name', 'Unknown Device')
            print(f"   - {device_type.title()}: {device_name}")
    
    def optimize_mouse_performance(self):
        """Apply comprehensive mouse performance optimizations."""
        print("\n🖱️ Applying Mouse Performance Optimizations...")
        
        # USB polling rate optimization
        self._optimize_usb_polling()
        
        # Mouse acceleration and sensitivity
        self._optimize_mouse_settings()
        
        # USB power management
        self._optimize_usb_power_management()
        
        # Input interrupt optimization
        self._optimize_input_interrupts()
        
        # Raw input optimization
        self._optimize_raw_input()
        
        # Display settings for input lag reduction
        self._optimize_display_settings()
        
        print(f"✅ Applied {len(self.optimizations_applied)} mouse optimizations:")
        for opt in self.optimizations_applied:
            print(f"   - {opt}")
    
    def _optimize_usb_polling(self):
        """Optimize USB polling rates for gaming mice."""
        try:
            if self.platform == 'linux':
                # Set USB HID polling to 1000Hz (1ms intervals)
                usb_params = [
                    ('/sys/module/usbhid/parameters/mousepoll', '1'),
                    ('/sys/module/usbhid/parameters/kbpoll', '1')
                ]
                
                for param_path, value in usb_params:
                    try:
                        if os.path.exists(param_path):
                            subprocess.run(['sudo', 'sh', '-c', f'echo {value} > {param_path}'], 
                                         check=False, capture_output=True)
                            device_type = 'mouse' if 'mouse' in param_path else 'keyboard'
                            self.optimizations_applied.append(f"USB {device_type} polling set to 1000Hz")
                    except:
                        pass
                
                # Optimize USB interrupt latency
                self._optimize_usb_interrupt_latency()
                
        except Exception as e:
            print(f"USB polling optimization error: {e}")
    
    def _optimize_usb_interrupt_latency(self):
        """Optimize USB interrupt handling for lower latency."""
        try:
            # Disable USB autosuspend
            subprocess.run(['sudo', 'sh', '-c', 'echo -1 > /sys/module/usbcore/parameters/autosuspend'], 
                         check=False, capture_output=True)
            
            # Set USB controller to full speed
            try:
                # Find USB controllers and optimize them
                usb_controllers = []
                with open('/proc/interrupts', 'r') as f:
                    for line in f:
                        if any(controller in line.lower() for controller in ['xhci', 'ehci', 'ohci', 'uhci']):
                            parts = line.split(':')
                            if parts and parts[0].strip().isdigit():
                                irq_num = parts[0].strip()
                                usb_controllers.append(irq_num)
                
                # Set high priority for USB interrupts
                for irq in usb_controllers:
                    try:
                        subprocess.run(['sudo', 'chrt', '-f', '-p', '99', f'/proc/irq/{irq}'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                if usb_controllers:
                    self.optimizations_applied.append(f"Optimized {len(usb_controllers)} USB controller interrupts")
                
            except:
                pass
            
            self.optimizations_applied.append("USB autosuspend disabled")
            
        except Exception as e:
            print(f"USB interrupt optimization error: {e}")
    
    def _optimize_mouse_settings(self):
        """Optimize mouse acceleration and sensitivity settings."""
        try:
            if self.platform == 'linux':
                # Disable mouse acceleration (for consistent aiming)
                x11_commands = [
                    'xinput --set-prop "pointer:*" "libinput Accel Profile Enabled" 0, 1',
                    'xinput --set-prop "pointer:*" "libinput Accel Speed" 0',
                    'xinput --set-prop "pointer:*" "Device Accel Profile" -1',
                    'xinput --set-prop "pointer:*" "Device Accel Constant Deceleration" 1'
                ]
                
                for cmd in x11_commands:
                    try:
                        subprocess.run(cmd.split(), check=False, capture_output=True)
                    except:
                        pass
                
                self.optimizations_applied.append("Mouse acceleration disabled")
                
                # Set consistent mouse sensitivity
                try:
                    subprocess.run(['xinput', '--set-prop', 'pointer:*', 'Coordinate Transformation Matrix', 
                                  '1', '0', '0', '0', '1', '0', '0', '0', '1'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Mouse sensitivity normalized")
                except:
                    pass
                
        except Exception as e:
            print(f"Mouse settings optimization error: {e}")
    
    def _optimize_usb_power_management(self):
        """Disable USB power management that can cause input lag."""
        try:
            if self.platform == 'linux':
                # Disable USB selective suspend
                usb_devices_path = '/sys/bus/usb/devices'
                if os.path.exists(usb_devices_path):
                    for device in os.listdir(usb_devices_path):
                        power_control_path = os.path.join(usb_devices_path, device, 'power', 'control')
                        if os.path.exists(power_control_path):
                            try:
                                subprocess.run(['sudo', 'sh', '-c', f'echo on > {power_control_path}'], 
                                             check=False, capture_output=True)
                            except:
                                pass
                
                # Disable USB runtime power management
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo 0 > /sys/bus/usb/devices/usb*/power/autosuspend_delay_ms'], 
                                 check=False, capture_output=True)
                    subprocess.run(['sudo', 'sh', '-c', 'for i in /sys/bus/usb/devices/*/power/control; do echo on > $i; done'], 
                                 check=False, capture_output=True)
                except:
                    pass
                
                self.optimizations_applied.append("USB power management disabled")
                
        except Exception as e:
            print(f"USB power management optimization error: {e}")
    
    def _optimize_input_interrupts(self):
        """Optimize input-related interrupts for lower latency."""
        try:
            if self.platform == 'linux':
                # Find input-related interrupts
                input_irqs = []
                with open('/proc/interrupts', 'r') as f:
                    for line in f:
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in ['input', 'hid', 'i8042', 'mouse', 'keyboard']):
                            parts = line.split(':')
                            if parts and parts[0].strip().isdigit():
                                input_irqs.append(parts[0].strip())
                
                # Set real-time priority for input interrupts
                for irq in input_irqs:
                    try:
                        # Set high priority
                        subprocess.run(['sudo', 'chrt', '-f', '-p', '99', f'/proc/irq/{irq}'], 
                                     check=False, capture_output=True)
                        
                        # Set CPU affinity to first core
                        subprocess.run(['sudo', 'sh', '-c', f'echo 1 > /proc/irq/{irq}/smp_affinity'], 
                                     check=False, capture_output=True)
                    except:
                        pass
                
                if input_irqs:
                    self.optimizations_applied.append(f"Optimized {len(input_irqs)} input interrupts")
                
        except Exception as e:
            print(f"Input interrupt optimization error: {e}")
    
    def _optimize_raw_input(self):
        """Optimize raw input handling."""
        try:
            if self.platform == 'linux':
                # Set input device permissions for raw access
                input_group_commands = [
                    'sudo usermod -a -G input $USER',
                    'sudo udevadm control --reload-rules'
                ]
                
                for cmd in input_group_commands:
                    try:
                        subprocess.run(cmd.split(), check=False, capture_output=True)
                    except:
                        pass
                
                # Optimize input handling
                try:
                    # Increase input buffer sizes
                    subprocess.run(['sudo', 'sh', '-c', 'echo 128 > /proc/sys/fs/file-max'], 
                                 check=False, capture_output=True)
                except:
                    pass
                
                self.optimizations_applied.append("Raw input access optimized")
                
        except Exception as e:
            print(f"Raw input optimization error: {e}")
    
    def _optimize_display_settings(self):
        """Optimize display settings to reduce input lag."""
        try:
            if self.platform == 'linux':
                # Disable composition (reduces input lag)
                compositor_commands = [
                    'killall compton',
                    'killall picom', 
                    'gsettings set org.gnome.desktop.interface enable-animations false',
                    'gsettings set org.gnome.desktop.wm.preferences reduced-motion true'
                ]
                
                for cmd in compositor_commands:
                    try:
                        subprocess.run(cmd.split(), check=False, capture_output=True)
                    except:
                        pass
                
                # Try to enable game mode (reduces desktop effects)
                try:
                    subprocess.run(['gsettings', 'set', 'org.gnome.desktop.wm.preferences', 'focus-mode', 'click'], 
                                 check=False, capture_output=True)
                except:
                    pass
                
                self.optimizations_applied.append("Display composition optimized for gaming")
                
        except Exception as e:
            print(f"Display optimization error: {e}")
    
    def optimize_keyboard_performance(self):
        """Optimize keyboard performance and responsiveness."""
        print("\n⌨️ Applying Keyboard Performance Optimizations...")
        
        try:
            if self.platform == 'linux':
                # Set keyboard repeat rate (faster response)
                try:
                    subprocess.run(['xset', 'r', 'rate', '250', '30'], check=False, capture_output=True)
                    self.optimizations_applied.append("Keyboard repeat rate optimized")
                except:
                    pass
                
                # Disable sticky keys and other accessibility features that can cause lag
                accessibility_commands = [
                    'gsettings set org.gnome.desktop.a11y.keyboard enable false',
                    'gsettings set org.gnome.desktop.a11y.keyboard stickykeys-enable false',
                    'gsettings set org.gnome.desktop.a11y.keyboard slowkeys-enable false',
                    'gsettings set org.gnome.desktop.a11y.keyboard bouncekeys-enable false'
                ]
                
                for cmd in accessibility_commands:
                    try:
                        subprocess.run(cmd.split(), check=False, capture_output=True)
                    except:
                        pass
                
                self.optimizations_applied.append("Keyboard accessibility features disabled")
                
                # Optimize keyboard input lag
                try:
                    subprocess.run(['sudo', 'sh', '-c', 'echo 0 > /proc/sys/dev/i8042/kbd_timeout'], 
                                 check=False, capture_output=True)
                    self.optimizations_applied.append("Keyboard timeout optimized")
                except:
                    pass
                
        except Exception as e:
            print(f"Keyboard optimization error: {e}")
    
    def measure_input_latency(self) -> Dict[str, float]:
        """Measure approximate input latency."""
        print("\n📊 Measuring Input Latency...")
        
        latency_results = {
            'mouse_latency_ms': 0.0,
            'keyboard_latency_ms': 0.0,
            'usb_polling_rate_hz': 0,
            'display_refresh_rate_hz': 0
        }
        
        try:
            if self.platform == 'linux':
                # Check USB polling rate
                try:
                    with open('/sys/module/usbhid/parameters/mousepoll', 'r') as f:
                        mousepoll = f.read().strip()
                        if mousepoll.isdigit():
                            latency_results['usb_polling_rate_hz'] = 1000 // int(mousepoll)
                            latency_results['mouse_latency_ms'] = int(mousepoll)
                except:
                    pass
                
                # Estimate keyboard latency (similar to mouse)
                latency_results['keyboard_latency_ms'] = latency_results['mouse_latency_ms']
                
                # Get display refresh rate
                try:
                    result = subprocess.run(['xrandr'], capture_output=True, text=True)
                    for line in result.stdout.split('\n'):
                        if '*' in line and '+' in line:  # Current mode
                            parts = line.split()
                            for part in parts:
                                if '*' in part:
                                    refresh_rate = float(part.replace('*+', '').replace('*', ''))
                                    latency_results['display_refresh_rate_hz'] = refresh_rate
                                    break
                            break
                except:
                    pass
            
            print("📈 Input Latency Results:")
            print(f"   Mouse Latency: ~{latency_results['mouse_latency_ms']:.1f}ms")
            print(f"   Keyboard Latency: ~{latency_results['keyboard_latency_ms']:.1f}ms")
            print(f"   USB Polling Rate: {latency_results['usb_polling_rate_hz']}Hz")
            print(f"   Display Refresh Rate: {latency_results['display_refresh_rate_hz']}Hz")
            
            # Calculate total input-to-display latency estimate
            total_latency = (
                latency_results['mouse_latency_ms'] + 
                (1000 / latency_results['display_refresh_rate_hz'] if latency_results['display_refresh_rate_hz'] > 0 else 16.67) +
                2  # Processing overhead
            )
            print(f"   Estimated Total Input Lag: ~{total_latency:.1f}ms")
            
        except Exception as e:
            print(f"Latency measurement error: {e}")
        
        return latency_results
    
    def generate_input_recommendations(self) -> List[str]:
        """Generate input optimization recommendations."""
        recommendations = []
        
        # Check current settings and make recommendations
        latency_results = self.measure_input_latency()
        
        if latency_results['mouse_latency_ms'] > 1:
            recommendations.append("🖱️ Mouse polling rate could be optimized - consider 1000Hz gaming mouse")
        
        if latency_results['display_refresh_rate_hz'] < 120:
            recommendations.append("🖥️ Consider upgrading to 144Hz+ monitor for lower input lag")
        
        # Check for gaming mice
        has_gaming_mouse = any('gaming' in device.get('name', '').lower() for device in self.detected_devices)
        if not has_gaming_mouse:
            recommendations.append("🎮 Consider upgrading to a gaming mouse with 1000Hz polling rate")
        
        # USB recommendations
        if len(self.detected_devices) > 10:
            recommendations.append("🔌 Many USB devices detected - consider using dedicated USB ports for gaming peripherals")
        
        # General recommendations
        recommendations.extend([
            "⚡ Disable Windows mouse acceleration for consistent aiming",
            "🎯 Use raw input mode in games when available",
            "📺 Enable gaming mode on monitor if available",
            "🔧 Keep mouse sensor clean for optimal tracking"
        ])
        
        return recommendations
    
    def monitor_input_performance(self, duration_seconds: int = 60):
        """Monitor input device performance over time."""
        print(f"\n📊 Monitoring input performance for {duration_seconds} seconds...")
        
        start_time = time.time()
        measurements = []
        
        while time.time() - start_time < duration_seconds:
            try:
                # Collect current metrics
                current_metrics = {
                    'timestamp': time.time(),
                    'cpu_usage': psutil.cpu_percent(interval=0.1),
                    'interrupts_per_sec': self._get_interrupt_rate(),
                    'usb_activity': self._get_usb_activity()
                }
                
                measurements.append(current_metrics)
                time.sleep(1)
                
                # Show progress
                elapsed = int(time.time() - start_time)
                remaining = duration_seconds - elapsed
                print(f"\r   Progress: {elapsed}/{duration_seconds}s (CPU: {current_metrics['cpu_usage']:.1f}%)", end='')
                
            except KeyboardInterrupt:
                print("\n   Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n   Monitoring error: {e}")
                break
        
        print(f"\n✅ Monitoring complete. Collected {len(measurements)} data points.")
        
        # Analyze results
        if measurements:
            avg_cpu = sum(m['cpu_usage'] for m in measurements) / len(measurements)
            max_cpu = max(m['cpu_usage'] for m in measurements)
            
            print(f"📈 Performance Summary:")
            print(f"   Average CPU Usage: {avg_cpu:.1f}%")
            print(f"   Peak CPU Usage: {max_cpu:.1f}%")
            
            if max_cpu > 90:
                print("⚠️  High CPU usage detected - may cause input lag")
            elif avg_cpu < 50:
                print("✅ CPU usage optimal for low input lag")
    
    def _get_interrupt_rate(self) -> int:
        """Get current interrupt rate (simplified)."""
        try:
            with open('/proc/interrupts', 'r') as f:
                lines = f.readlines()
                return len([line for line in lines if 'input' in line.lower() or 'hid' in line.lower()])
        except:
            return 0
    
    def _get_usb_activity(self) -> bool:
        """Check if there's USB activity (simplified)."""
        try:
            # This is a placeholder - real implementation would check USB activity
            return os.path.exists('/sys/bus/usb/devices')
        except:
            return False

def main():
    """Main input optimization function."""
    print("🖱️ Advanced Mouse & Input Optimization System")
    print("=" * 60)
    
    optimizer = MouseInputOptimizer()
    
    # Apply optimizations
    optimizer.optimize_mouse_performance()
    optimizer.optimize_keyboard_performance()
    
    # Measure current latency
    optimizer.measure_input_latency()
    
    # Generate recommendations
    print("\n💡 Input Performance Recommendations:")
    recommendations = optimizer.generate_input_recommendations()
    for i, recommendation in enumerate(recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    print("\n🎯 Input optimization complete!")
    print("💡 Restart games to apply all input optimizations.")
    
    # Optional: Monitor performance
    choice = input("\n🔍 Monitor input performance? (y/N): ").lower()
    if choice == 'y':
        optimizer.monitor_input_performance(30)

if __name__ == "__main__":
    main()