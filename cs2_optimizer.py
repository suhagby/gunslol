#!/usr/bin/env python3
"""
Counter-Strike 2 Performance Optimizer
Specialized optimizations for CS2 competitive gaming with maximum FPS and minimum latency.

Features:
- CS2-specific registry tweaks
- Optimal launch options generation
- Network optimization for competitive play
- Video settings optimization
- Audio optimization for positional awareness
- Input lag minimization
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import configparser

try:
    import winreg
    WINDOWS_PLATFORM = True
except ImportError:
    WINDOWS_PLATFORM = False

class CS2Optimizer:
    """Counter-Strike 2 performance optimizer."""
    
    def __init__(self):
        self.steam_path = self._find_steam_path()
        self.cs2_path = self._find_cs2_path()
        self.userdata_path = self._find_userdata_path()
        
        # CS2 optimization settings
        self.video_settings = self._get_optimal_video_settings()
        self.audio_settings = self._get_optimal_audio_settings()
        self.network_settings = self._get_optimal_network_settings()
        self.launch_options = self._get_optimal_launch_options()
        
    def _find_steam_path(self) -> Optional[Path]:
        """Find Steam installation path."""
        possible_paths = [
            Path("C:\\Program Files (x86)\\Steam"),
            Path("C:\\Program Files\\Steam"),
            Path("C:\\Steam"),
            Path.home() / ".steam",
            Path.home() / ".local/share/Steam"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Try registry on Windows
        if WINDOWS_PLATFORM:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam") as key:
                    steam_path, _ = winreg.QueryValueEx(key, "InstallPath")
                    return Path(steam_path)
            except:
                pass
        
        return None
    
    def _find_cs2_path(self) -> Optional[Path]:
        """Find Counter-Strike 2 installation path."""
        if not self.steam_path:
            return None
            
        possible_cs2_paths = [
            self.steam_path / "steamapps" / "common" / "Counter-Strike Global Offensive",
            self.steam_path / "steamapps" / "common" / "Counter-Strike 2",
        ]
        
        for path in possible_cs2_paths:
            if path.exists():
                return path
        
        return None
    
    def _find_userdata_path(self) -> Optional[Path]:
        """Find Steam userdata path for CS2 configurations."""
        if not self.steam_path:
            return None
            
        userdata_path = self.steam_path / "userdata"
        if userdata_path.exists():
            return userdata_path
        
        return None
    
    def _get_optimal_video_settings(self) -> Dict[str, Any]:
        """Get optimal video settings for competitive CS2."""
        return {
            # Performance-focused settings
            "setting.gpu_mem_priority": "1",  # High GPU memory priority
            "setting.mat_vsync": "0",         # Disable VSync
            "setting.fps_max": "0",           # Unlimited FPS
            "setting.mat_queue_mode": "2",    # Multi-threaded rendering
            "setting.engine_low_latency_sleep_after_client_tick": "false",
            
            # Video quality settings (performance optimized)
            "setting.defaultres": "1920",
            "setting.defaultresheight": "1080",
            "setting.mat_monitorgamma": "2.2",
            "setting.mat_monitorgamma_tv_enabled": "0",
            
            # Advanced settings
            "setting.r_dynamic": "0",         # Disable dynamic lighting
            "setting.r_drawtracers_firstperson": "1",
            "setting.r_eyegloss": "0",
            "setting.r_eyemove": "0",
            "setting.r_eyeshift_x": "0",
            "setting.r_eyeshift_y": "0",
            "setting.r_eyeshift_z": "0",
            "setting.r_eyesize": "0"
        }
    
    def _get_optimal_audio_settings(self) -> Dict[str, Any]:
        """Get optimal audio settings for competitive CS2."""
        return {
            "snd_musicvolume": "0.0",          # Disable music
            "snd_mixahead": "0.025",           # Low audio buffer
            "snd_headphone_pan_exponent": "2", # Headphone optimization
            "snd_hwcompat": "0",               # Disable hardware compatibility
            "snd_pitchquality": "1",           # High pitch quality
            "snd_disable_mixer_duck": "1",     # Disable audio ducking
            "voice_enable": "1",               # Enable voice chat
            "voice_scale": "1.0",              # Voice volume
            "snd_deathcamera": "0"             # Disable death cam audio
        }
    
    def _get_optimal_network_settings(self) -> Dict[str, Any]:
        """Get optimal network settings for competitive CS2."""
        return {
            "rate": "786432",                  # Maximum bandwidth
            "cl_cmdrate": "128",               # Command rate
            "cl_updaterate": "128",            # Update rate  
            "cl_interp": "0",                  # No interpolation delay
            "cl_interp_ratio": "1",            # Interpolation ratio
            "cl_lagcompensation": "1",         # Enable lag compensation
            "cl_predict": "1",                 # Enable client prediction
            "cl_predictweapons": "1",          # Predict weapons
            "net_client_steamdatagram_enable_override": "1",
            "net_steamcnx_allowrelay": "0"     # Direct connections only
        }
    
    def _get_optimal_launch_options(self) -> List[str]:
        """Get optimal launch options for CS2."""
        cpu_count = os.cpu_count() or 4
        
        return [
            "-novid",                          # Skip intro videos
            "-nojoy",                          # Disable joystick
            "-high",                           # High process priority
            f"-threads {cpu_count}",           # Use all CPU threads
            "+fps_max 0",                      # Unlimited FPS
            "+cl_forcepreload 1",              # Preload maps
            "+mat_queue_mode 2",               # Multithreaded rendering
            "-freq 240",                       # Monitor refresh rate (adjust as needed)
            "+rate 786432",                    # Network rate
            "+cl_cmdrate 128",                 # Command rate
            "+cl_updaterate 128",              # Update rate
            "+cl_interp_ratio 1",              # Interpolation
            "+cl_interp 0",                    # Interpolation time
            "-worldwide",                      # Access all servers
            "-tickrate 128",                   # 128 tick servers
            "+exec autoexec.cfg"               # Execute autoexec config
        ]
    
    def create_autoexec_config(self) -> bool:
        """Create optimized autoexec.cfg file."""
        if not self.cs2_path:
            print("❌ CS2 installation path not found")
            return False
        
        # Find CS2 config directory
        config_paths = [
            self.cs2_path / "game" / "csgo" / "cfg",
            self.cs2_path / "csgo" / "cfg"
        ]
        
        config_dir = None
        for path in config_paths:
            if path.exists():
                config_dir = path
                break
        
        if not config_dir:
            config_dir = self.cs2_path / "game" / "csgo" / "cfg"
            config_dir.mkdir(parents=True, exist_ok=True)
        
        autoexec_path = config_dir / "autoexec.cfg"
        
        try:
            with open(autoexec_path, 'w', encoding='utf-8') as f:
                f.write("// CS2 Performance Optimization Config\n")
                f.write("// Generated by Ultimate Performance Optimizer v5.0\n\n")
                
                f.write("// === NETWORK SETTINGS ===\n")
                for setting, value in self.network_settings.items():
                    f.write(f'{setting} "{value}"\n')
                f.write("\n")
                
                f.write("// === AUDIO SETTINGS ===\n")
                for setting, value in self.audio_settings.items():
                    f.write(f'{setting} "{value}"\n')
                f.write("\n")
                
                f.write("// === PERFORMANCE SETTINGS ===\n")
                f.write('fps_max "0"\n')
                f.write('cl_forcepreload "1"\n')
                f.write('mat_queue_mode "2"\n')
                f.write('engine_low_latency_sleep_after_client_tick "false"\n')
                f.write('mat_vsync "0"\n')
                f.write("\n")
                
                f.write("// === MOUSE SETTINGS ===\n")
                f.write('m_rawinput "1"\n')
                f.write('m_mouseaccel1 "0"\n')
                f.write('m_mouseaccel2 "0"\n')
                f.write('m_mousespeed "0"\n')
                f.write("\n")
                
                f.write("// === CROSSHAIR SETTINGS ===\n")
                f.write('cl_crosshair_recoil "0"\n')
                f.write('cl_crosshair_sniper_width "1"\n')
                f.write('cl_crosshairalpha "255"\n')
                f.write('cl_crosshaircolor "1"\n')
                f.write('cl_crosshairdot "0"\n')
                f.write('cl_crosshairgap "-1"\n')
                f.write('cl_crosshairsize "2"\n')
                f.write('cl_crosshairstyle "4"\n')
                f.write('cl_crosshairthickness "0"\n')
                f.write("\n")
                
                f.write("// === RADAR SETTINGS ===\n")
                f.write('cl_radar_always_centered "0"\n')
                f.write('cl_radar_scale "0.3"\n')
                f.write('cl_hud_radar_scale "1.15"\n')
                f.write('cl_radar_icon_scale_min "1"\n')
                f.write("\n")
                
                f.write("// === HUD SETTINGS ===\n")
                f.write('cl_hud_color "1"\n')
                f.write('cl_hud_healthammo_style "0"\n')
                f.write('cl_hud_playercount_showcount "1"\n')
                f.write('cl_hud_playercount_pos "0"\n')
                f.write("\n")
                
                f.write("// === VIEWMODEL SETTINGS ===\n")
                f.write('viewmodel_fov "68"\n')
                f.write('viewmodel_offset_x "2.5"\n')
                f.write('viewmodel_offset_y "0"\n')
                f.write('viewmodel_offset_z "-1.5"\n')
                f.write('viewmodel_presetpos "3"\n')
                f.write("\n")
                
                f.write("// === BIND SETTINGS ===\n")
                f.write('bind "w" "+forward"\n')
                f.write('bind "s" "+back"\n')
                f.write('bind "a" "+moveleft"\n')
                f.write('bind "d" "+moveright"\n')
                f.write('bind "SPACE" "+jump"\n')
                f.write('bind "CTRL" "+duck"\n')
                f.write('bind "SHIFT" "+speed"\n')
                f.write('bind "mouse1" "+attack"\n')
                f.write('bind "mouse2" "+attack2"\n')
                f.write('bind "r" "+reload"\n')
                f.write('bind "g" "drop"\n')
                f.write('bind "b" "buymenu"\n')
                f.write('bind "m" "teammenu"\n')
                f.write('bind "TAB" "+showscores"\n')
                f.write("\n")
                
                f.write('echo "CS2 Performance Config Loaded Successfully!"\n')
            
            print(f"✅ Created autoexec.cfg: {autoexec_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create autoexec.cfg: {e}")
            return False
    
    def apply_video_settings(self) -> bool:
        """Apply optimal video settings via config file."""
        if not self.userdata_path:
            print("❌ Steam userdata path not found")
            return False
        
        # Find CS2 video config file
        try:
            for user_dir in self.userdata_path.iterdir():
                if user_dir.is_dir() and user_dir.name.isdigit():
                    cs2_config_dir = user_dir / "730" / "local" / "cfg"
                    if cs2_config_dir.exists():
                        video_txt_path = cs2_config_dir / "video.txt"
                        
                        if video_txt_path.exists():
                            # Backup original
                            backup_path = cs2_config_dir / "video.txt.backup"
                            if not backup_path.exists():
                                video_txt_path.rename(backup_path)
                        
                        # Create optimized video.txt
                        with open(video_txt_path, 'w') as f:
                            f.write('"VideoConfig"\n{\n')
                            for setting, value in self.video_settings.items():
                                f.write(f'\t"{setting}"\t\t"{value}"\n')
                            f.write('}\n')
                        
                        print(f"✅ Applied video settings: {video_txt_path}")
                        return True
            
        except Exception as e:
            print(f"❌ Failed to apply video settings: {e}")
            return False
        
        print("❌ CS2 config directory not found")
        return False
    
    def set_launch_options(self) -> bool:
        """Set optimal launch options in Steam."""
        if not WINDOWS_PLATFORM:
            print("❌ Launch options setting only supported on Windows")
            return False
        
        launch_options_str = " ".join(self.launch_options)
        
        try:
            # Try to set via Steam registry
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam\Apps\730", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "LaunchOptions", 0, winreg.REG_SZ, launch_options_str)
            
            print(f"✅ Set launch options: {launch_options_str}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to set launch options via registry: {e}")
            
            # Create a file with launch options for manual setup
            launch_options_file = Path(__file__).parent / "cs2_launch_options.txt"
            try:
                with open(launch_options_file, 'w') as f:
                    f.write("CS2 Optimal Launch Options:\n")
                    f.write("Copy this line to Steam > Right-click CS2 > Properties > Launch Options\n\n")
                    f.write(launch_options_str)
                
                print(f"✅ Created launch options file: {launch_options_file}")
                print("   Please manually copy the launch options to Steam")
                return True
                
            except Exception as e2:
                print(f"❌ Failed to create launch options file: {e2}")
                return False
    
    def optimize_nvidia_settings(self) -> bool:
        """Apply NVIDIA-specific optimizations for CS2."""
        if not WINDOWS_PLATFORM:
            return False
        
        optimizations_applied = []
        
        try:
            # NVIDIA Control Panel settings via registry
            nvidia_settings = [
                # CS2-specific NVIDIA profile
                (r"SOFTWARE\NVIDIA Corporation\Global\NVTweak\Devices\154954644_0\OGL", "AAModeSelector", 0),
                (r"SOFTWARE\NVIDIA Corporation\Global\NVTweak\Devices\154954644_0\OGL", "PowerMizerEnable", 0x1),
                (r"SOFTWARE\NVIDIA Corporation\Global\NVTweak\Devices\154954644_0\OGL", "PowerMizerLevel", 0x1),
                (r"SOFTWARE\NVIDIA Corporation\Global\NVTweak\Devices\154954644_0\OGL", "PerfLevelSrc", 0x2222),
            ]
            
            for subkey, name, value in nvidia_settings:
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                        optimizations_applied.append(f"NVIDIA: {name}")
                except:
                    pass
            
        except Exception as e:
            print(f"⚠️ NVIDIA optimizations error: {e}")
        
        if optimizations_applied:
            print(f"✅ Applied NVIDIA optimizations: {len(optimizations_applied)} settings")
            return True
        else:
            print("⚠️ No NVIDIA optimizations applied")
            return False
    
    def apply_windows_cs2_tweaks(self) -> bool:
        """Apply Windows-specific CS2 tweaks."""
        if not WINDOWS_PLATFORM:
            return False
        
        optimizations_applied = []
        
        try:
            # CS2 process-specific optimizations
            cs2_registry_tweaks = [
                # Game scheduling
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cs2.exe\PerfOptions", "CpuPriorityClass", 3),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cs2.exe\PerfOptions", "IoPriority", 3),
                
                # Memory management for CS2
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\cs2.exe", "UseLargePages", 1),
            ]
            
            for hkey, subkey, name, value in cs2_registry_tweaks:
                try:
                    # Create the key if it doesn't exist
                    with winreg.CreateKeyEx(hkey, subkey, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
                        optimizations_applied.append(f"CS2 Process: {name}")
                except Exception as e:
                    print(f"⚠️ Failed to set {name}: {e}")
            
        except Exception as e:
            print(f"❌ Windows CS2 tweaks error: {e}")
        
        if optimizations_applied:
            print(f"✅ Applied Windows CS2 tweaks: {len(optimizations_applied)} settings")
            return True
        else:
            print("⚠️ No Windows CS2 tweaks applied")
            return False
    
    def create_practice_configs(self) -> bool:
        """Create practice and training configs."""
        if not self.cs2_path:
            return False
        
        config_paths = [
            self.cs2_path / "game" / "csgo" / "cfg",
            self.cs2_path / "csgo" / "cfg"
        ]
        
        config_dir = None
        for path in config_paths:
            if path.exists():
                config_dir = path
                break
        
        if not config_dir:
            return False
        
        try:
            # Practice config
            practice_config = config_dir / "practice.cfg"
            with open(practice_config, 'w') as f:
                f.write("// CS2 Practice Config\n")
                f.write("sv_cheats 1\n")
                f.write("mp_limitteams 0\n")
                f.write("mp_autoteambalance 0\n")
                f.write("mp_maxmoney 60000\n")
                f.write("mp_startmoney 60000\n")
                f.write("mp_buytime 9999\n")
                f.write("mp_buy_anywhere 1\n")
                f.write("mp_freezetime 0\n")
                f.write("mp_roundtime 60\n")
                f.write("mp_roundtime_defuse 60\n")
                f.write("sv_infinite_ammo 1\n")
                f.write("sv_showimpacts 1\n")
                f.write("sv_showimpacts_time 10\n")
                f.write("god\n")
                f.write('echo "Practice mode enabled"\n')
            
            # Aim training config
            aim_config = config_dir / "aim.cfg"
            with open(aim_config, 'w') as f:
                f.write("// CS2 Aim Training Config\n")
                f.write("exec practice\n")
                f.write("mp_warmup_end\n")
                f.write("mp_respawn_on_death_ct 1\n")
                f.write("mp_respawn_on_death_t 1\n")
                f.write("sv_infinite_ammo 2\n")
                f.write("ammo_grenade_limit_total 5\n")
                f.write("bot_kick\n")
                f.write('echo "Aim training mode enabled"\n')
            
            print(f"✅ Created practice configs in: {config_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create practice configs: {e}")
            return False
    
    def apply_all_optimizations(self) -> Dict[str, bool]:
        """Apply all CS2 optimizations."""
        results = {}
        
        print("🚀 Applying CS2 Performance Optimizations...")
        print("=" * 50)
        
        print("\n📝 Creating autoexec.cfg...")
        results['autoexec'] = self.create_autoexec_config()
        
        print("\n🎥 Applying video settings...")
        results['video_settings'] = self.apply_video_settings()
        
        print("\n🚀 Setting launch options...")
        results['launch_options'] = self.set_launch_options()
        
        print("\n🎮 Applying NVIDIA optimizations...")
        results['nvidia_settings'] = self.optimize_nvidia_settings()
        
        print("\n🔧 Applying Windows CS2 tweaks...")
        results['windows_tweaks'] = self.apply_windows_cs2_tweaks()
        
        print("\n📚 Creating practice configs...")
        results['practice_configs'] = self.create_practice_configs()
        
        # Summary
        successful = sum(results.values())
        total = len(results)
        
        print("\n" + "=" * 50)
        print(f"CS2 Optimization Results: {successful}/{total} successful")
        
        for optimization, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {optimization.replace('_', ' ').title()}")
        
        return results
    
    def show_recommendations(self):
        """Show additional recommendations for CS2 performance."""
        print("\n" + "=" * 60)
        print("📋 ADDITIONAL CS2 PERFORMANCE RECOMMENDATIONS")
        print("=" * 60)
        
        print("\n🖥️ MONITOR SETTINGS:")
        print("  • Set monitor to highest refresh rate (144Hz, 240Hz, etc.)")
        print("  • Disable Windows Game Mode if causing issues")
        print("  • Use exclusive fullscreen mode in CS2")
        
        print("\n🖱️ MOUSE SETTINGS:")
        print("  • Use 400-800 DPI with low in-game sensitivity")
        print("  • Disable mouse acceleration in Windows")
        print("  • Use a high polling rate mouse (1000Hz)")
        
        print("\n🔊 AUDIO SETTINGS:")
        print("  • Use good headphones for positional audio")
        print("  • Set Windows audio to 16-bit, 44100Hz")
        print("  • Disable all audio enhancements")
        
        print("\n🌐 NETWORK:")
        print("  • Use wired ethernet connection")
        print("  • Forward CS2 ports: 27015-27030 TCP/UDP")
        print("  • Consider using gaming VPN for routing optimization")
        
        print("\n💻 SYSTEM:")
        print("  • Close unnecessary background programs")
        print("  • Keep GPU drivers updated")
        print("  • Monitor CPU/GPU temperatures")
        print("  • Use Game Mode in Windows (if stable)")
        
        print("\n🎯 IN-GAME SETTINGS:")
        print("  • Use 4:3 stretched or native 16:9")
        print("  • Lower video settings for higher FPS")
        print("  • Disable motion blur and film grain")
        print("  • Use preloaded maps (+cl_forcepreload 1)")

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("🎯 CS2 PERFORMANCE OPTIMIZER")
    print("   Maximum FPS & Minimum Latency for Competitive Gaming")
    print("=" * 60)
    
    optimizer = CS2Optimizer()
    
    if not optimizer.steam_path:
        print("❌ Steam installation not found!")
        print("   Please ensure Steam is installed and try again.")
        return
    
    print(f"✅ Steam found: {optimizer.steam_path}")
    
    if optimizer.cs2_path:
        print(f"✅ CS2 found: {optimizer.cs2_path}")
    else:
        print("⚠️ CS2 installation not found")
        print("   Some optimizations may not work properly")
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "auto":
        # Automatic mode
        results = optimizer.apply_all_optimizations()
        optimizer.show_recommendations()
    else:
        # Interactive mode
        while True:
            print("\n📋 CS2 OPTIMIZATION OPTIONS:")
            print("  1. Apply All Optimizations (Recommended)")
            print("  2. Create autoexec.cfg")
            print("  3. Apply Video Settings")
            print("  4. Set Launch Options")
            print("  5. NVIDIA Optimizations")
            print("  6. Windows CS2 Tweaks")
            print("  7. Create Practice Configs")
            print("  8. Show Performance Recommendations")
            print("  9. Exit")
            
            try:
                choice = int(input("\n➤ Select option: "))
                
                if choice == 1:
                    optimizer.apply_all_optimizations()
                elif choice == 2:
                    optimizer.create_autoexec_config()
                elif choice == 3:
                    optimizer.apply_video_settings()
                elif choice == 4:
                    optimizer.set_launch_options()
                elif choice == 5:
                    optimizer.optimize_nvidia_settings()
                elif choice == 6:
                    optimizer.apply_windows_cs2_tweaks()
                elif choice == 7:
                    optimizer.create_practice_configs()
                elif choice == 8:
                    optimizer.show_recommendations()
                elif choice == 9:
                    break
                else:
                    print("❌ Invalid choice!")
                    
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break
    
    print("\n🎯 CS2 optimization complete!")
    print("   Restart CS2 for all changes to take effect.")

if __name__ == "__main__":
    main()