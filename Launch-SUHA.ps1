# SUHA FPS+ v4.0 - Neural Gaming Performance System
# Advanced PowerShell Launcher for Windows
# Requires PowerShell 5.1 or higher

param(
    [switch]$QuickStart,
    [switch]$InstallDeps,
    [switch]$HealthCheck,
    [switch]$Daemon,
    [switch]$AdminCheck,
    [string]$Component = ""
)

# Set execution policy for the session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# ASCII Art Header
$Header = @"

   ╔══════════════════════════════════════════════════════════════════════════╗
   ║                          SUHA FPS+ v4.0 LAUNCHER                        ║
   ║                     Neural Gaming Performance System                     ║
   ║                                                                          ║
   ║  🤖 AI Engine v4.0        ⚡ Performance Optimizer v4.0                 ║
   ║  🖥️  Windows Optimizer     🌐 Enhanced Web Interface                     ║ 
   ║  🤖 Discord Bot v4.0      📊 Real-time System Monitoring                ║
   ║                                                                          ║
   ║  PowerShell Edition - Advanced Windows Integration                       ║
   ╚══════════════════════════════════════════════════════════════════════════╝

"@

Write-Host $Header -ForegroundColor Cyan

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to restart as administrator
function Restart-AsAdmin {
    if (-not (Test-Administrator)) {
        Write-Host "⚠️  Administrator privileges recommended for full optimization" -ForegroundColor Yellow
        $response = Read-Host "Restart as administrator? (Y/N)"
        if ($response -match "^[Yy]") {
            $scriptPath = $MyInvocation.MyCommand.Path
            Start-Process PowerShell -ArgumentList "-ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
            exit 0
        } else {
            Write-Host "Continuing without administrator privileges..." -ForegroundColor Yellow
            Write-Host "Some Windows optimizations may not work properly." -ForegroundColor Yellow
        }
    } else {
        Write-Host "✅ Running with administrator privileges" -ForegroundColor Green
    }
}

# Function to check Python installation
function Test-PythonInstallation {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
            return $true
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
        Write-Host "Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
}

# Function to setup virtual environment
function Setup-VirtualEnvironment {
    if (Test-Path "venv") {
        Write-Host "✅ Virtual environment found" -ForegroundColor Green
        & ".\venv\Scripts\Activate.ps1"
    } else {
        Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Virtual environment created" -ForegroundColor Green
            & ".\venv\Scripts\Activate.ps1"
        } else {
            Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
            return $false
        }
    }
    return $true
}

# Function to check system requirements
function Test-SystemRequirements {
    Write-Host "🔍 Checking system requirements..." -ForegroundColor Cyan
    
    # Check Windows version
    $osVersion = [System.Environment]::OSVersion.Version
    if ($osVersion.Major -ge 10) {
        Write-Host "✅ Windows 10/11 detected" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Windows 10/11 recommended for best performance" -ForegroundColor Yellow
    }
    
    # Check RAM
    $totalRAM = [math]::Round((Get-WmiObject -Class Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    if ($totalRAM -ge 8) {
        Write-Host "✅ RAM: ${totalRAM}GB (Sufficient)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  RAM: ${totalRAM}GB (8GB+ recommended)" -ForegroundColor Yellow
    }
    
    # Check CPU cores
    $cpuCores = (Get-WmiObject -Class Win32_Processor).NumberOfLogicalProcessors
    Write-Host "ℹ️  CPU Cores: $cpuCores" -ForegroundColor Cyan
    
    # Check GPU
    $gpu = Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -notmatch "Microsoft" } | Select-Object -First 1
    if ($gpu) {
        Write-Host "ℹ️  GPU: $($gpu.Name)" -ForegroundColor Cyan
    }
    
    # Check available disk space
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
    $freeSpaceGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    if ($freeSpaceGB -ge 5) {
        Write-Host "✅ Free Disk Space: ${freeSpaceGB}GB" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Free Disk Space: ${freeSpaceGB}GB (5GB+ recommended)" -ForegroundColor Yellow
    }
}

# Function to install dependencies
function Install-Dependencies {
    Write-Host "🔧 Installing system dependencies..." -ForegroundColor Yellow
    
    # Create requirements installer script
    $installScript = @"
import subprocess
import sys

# Core dependencies for basic functionality
core_deps = [
    'psutil>=5.9.0',
    'flask>=2.3.0',
    'flask-socketio>=5.3.0',
    'pyyaml>=6.0',
    'requests>=2.28.0',
    'colorlog>=6.7.0'
]

# AI/ML dependencies (optional)
ai_deps = [
    'numpy>=1.21.0',
    'scipy>=1.9.0',
    'torch',
    'torchvision',
    'scikit-learn>=1.1.0',
    'pandas>=1.5.0'
]

# Communication dependencies
comm_deps = [
    'discord.py>=2.3.0',
    'aiohttp>=3.8.0',
    'aiofiles>=22.1.0'
]

# Visualization dependencies
viz_deps = [
    'matplotlib>=3.6.0',
    'plotly>=5.15.0'
]

def install_package_list(packages, description):
    print(f"\n🔧 Installing {description}...")
    for package in packages:
        try:
            print(f"  Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ Failed to install {package}: {e}")

# Install in order of importance
install_package_list(core_deps, "core dependencies")
install_package_list(ai_deps, "AI/ML dependencies (optional)")
install_package_list(comm_deps, "communication dependencies")  
install_package_list(viz_deps, "visualization dependencies (optional)")

print("\n✅ Dependency installation completed!")
"@

    $installScript | Out-File -FilePath "temp_install.py" -Encoding UTF8
    python temp_install.py
    Remove-Item "temp_install.py" -Force
}

# Function to run health check
function Invoke-HealthCheck {
    Write-Host "🏥 Running comprehensive system health check..." -ForegroundColor Cyan
    
    # System information
    Write-Host "`n📊 System Information:" -ForegroundColor Yellow
    Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory, CsProcessors | Format-List
    
    # Python and dependencies check
    python master_launcher.py --health-check
    
    # Windows-specific checks
    Write-Host "`n🖥️  Windows-specific checks:" -ForegroundColor Yellow
    
    # Check Windows Game Mode
    $gameModeKey = "HKCU:\Software\Microsoft\GameBar"
    if (Test-Path $gameModeKey) {
        $gameMode = Get-ItemProperty -Path $gameModeKey -Name "UseNexusForGameBarEnabled" -ErrorAction SilentlyContinue
        if ($gameMode) {
            Write-Host "✅ Game Mode: Available" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Game Mode: Not configured" -ForegroundColor Yellow
        }
    }
    
    # Check Hardware Accelerated GPU Scheduling
    $gpuSchedulingKey = "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    $gpuScheduling = Get-ItemProperty -Path $gpuSchedulingKey -Name "HwSchMode" -ErrorAction SilentlyContinue
    if ($gpuScheduling -and $gpuScheduling.HwSchMode -eq 2) {
        Write-Host "✅ Hardware Accelerated GPU Scheduling: Enabled" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Hardware Accelerated GPU Scheduling: Disabled or not available" -ForegroundColor Yellow
    }
    
    # Check running processes
    $pythonProcesses = Get-Process -Name "python" -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        Write-Host "`n🔄 Running Python processes:" -ForegroundColor Yellow
        $pythonProcesses | Select-Object Id, ProcessName, CPU, WorkingSet | Format-Table
    } else {
        Write-Host "`n💤 No Python processes currently running" -ForegroundColor Gray
    }
}

# Function to launch specific component
function Start-Component {
    param([string]$ComponentName)
    
    $componentMap = @{
        "ai" = "ai_engine_v4.py"
        "perf" = "advanced_performance_optimizer_v4.py"
        "windows" = "windows_optimizer_v4.py"
        "web" = "web_dashboard.py"
        "discord" = "discord_bot_v4.py"
        "launcher" = "neural_launcher_v4.py"
        "master" = "master_launcher.py"
    }
    
    if ($componentMap.ContainsKey($ComponentName.ToLower())) {
        $scriptName = $componentMap[$ComponentName.ToLower()]
        if (Test-Path $scriptName) {
            Write-Host "🚀 Starting $ComponentName component..." -ForegroundColor Green
            python $scriptName
        } else {
            Write-Host "❌ Component script not found: $scriptName" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Unknown component: $ComponentName" -ForegroundColor Red
        Write-Host "Available components: ai, perf, windows, web, discord, launcher, master" -ForegroundColor Yellow
    }
}

# Function to show interactive menu
function Show-InteractiveMenu {
    do {
        Clear-Host
        Write-Host $Header -ForegroundColor Cyan
        
        # Show system status
        $pythonProcesses = @(Get-Process -Name "python" -ErrorAction SilentlyContinue)
        Write-Host "Status: $($pythonProcesses.Count) Python processes running`n" -ForegroundColor Gray
        
        Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkCyan
        Write-Host "🚀 POWERSHELL LAUNCHER MENU" -ForegroundColor Yellow
        Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkCyan
        Write-Host "1.  ⚡ Quick Start (Install + Launch All)"
        Write-Host "2.  🔧 Install Dependencies Only"
        Write-Host "3.  🏥 System Health Check"
        Write-Host "4.  🚀 Launch Master System"
        Write-Host "5.  🤖 Launch AI Engine"
        Write-Host "6.  ⚡ Launch Performance Optimizer"
        Write-Host "7.  🖥️  Launch Windows Optimizer"
        Write-Host "8.  🌐 Launch Web Dashboard"
        Write-Host "9.  🤖 Launch Discord Bot"
        Write-Host "10. 📊 System Information"
        Write-Host "11. 🔄 Process Manager"
        Write-Host "12. ⚙️  Windows Optimization Tools"
        Write-Host "13. 📝 View Logs"
        Write-Host "14. 🔐 Security Check"
        Write-Host "15. 🛑 Stop All Components"
        Write-Host "16. ❌ Exit"
        Write-Host "════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkCyan
        
        $choice = Read-Host "`n👉 Enter your choice (1-16)"
        
        switch ($choice) {
            "1" { 
                Write-Host "`n🚀 Quick Start..." -ForegroundColor Green
                Install-Dependencies
                python master_launcher.py --quick-start
                Read-Host "Press Enter to continue..."
            }
            "2" { 
                Install-Dependencies
                Read-Host "Press Enter to continue..."
            }
            "3" { 
                Invoke-HealthCheck
                Read-Host "Press Enter to continue..."
            }
            "4" { 
                python master_launcher.py
                Read-Host "Press Enter to continue..."
            }
            "5" { Start-Component "ai" }
            "6" { Start-Component "perf" }
            "7" { Start-Component "windows" }
            "8" { Start-Component "web" }
            "9" { 
                $token = Read-Host "Enter Discord Bot Token (or press Enter to skip)"
                if ($token) {
                    $env:DISCORD_BOT_TOKEN = $token
                    Start-Component "discord"
                } else {
                    Write-Host "❌ Discord bot token required" -ForegroundColor Red
                }
            }
            "10" { 
                Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory, CsProcessors | Format-List
                Get-WmiObject -Class Win32_VideoController | Where-Object { $_.Name -notmatch "Microsoft" } | Select-Object Name | Format-List
                Read-Host "Press Enter to continue..."
            }
            "11" { 
                Write-Host "`n🔄 Python Process Manager:" -ForegroundColor Yellow
                $processes = Get-Process -Name "python" -ErrorAction SilentlyContinue
                if ($processes) {
                    $processes | Select-Object Id, ProcessName, CPU, WorkingSet, StartTime | Format-Table
                    $killChoice = Read-Host "Kill all Python processes? (y/N)"
                    if ($killChoice -match "^[Yy]") {
                        $processes | Stop-Process -Force
                        Write-Host "✅ All Python processes stopped" -ForegroundColor Green
                    }
                } else {
                    Write-Host "💤 No Python processes running" -ForegroundColor Gray
                }
                Read-Host "Press Enter to continue..."
            }
            "12" { 
                Write-Host "`n⚙️  Windows Optimization Tools:" -ForegroundColor Yellow
                Write-Host "1. Enable Hardware Accelerated GPU Scheduling"
                Write-Host "2. Enable Game Mode"
                Write-Host "3. Set High Performance Power Plan"
                Write-Host "4. Disable Windows Defender Real-time Protection (Temporary)"
                Write-Host "5. Clean Temp Files"
                Write-Host "6. Return to main menu"
                
                $optChoice = Read-Host "Select option"
                switch ($optChoice) {
                    "1" { 
                        if (Test-Administrator) {
                            Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" -Name "HwSchMode" -Value 2 -Type DWord
                            Write-Host "✅ Hardware Accelerated GPU Scheduling enabled (restart required)" -ForegroundColor Green
                        } else {
                            Write-Host "❌ Administrator privileges required" -ForegroundColor Red
                        }
                    }
                    "2" { 
                        Set-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "UseNexusForGameBarEnabled" -Value 1 -Type DWord
                        Write-Host "✅ Game Mode enabled" -ForegroundColor Green
                    }
                    "3" { 
                        if (Test-Administrator) {
                            powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
                            Write-Host "✅ High Performance power plan activated" -ForegroundColor Green
                        } else {
                            Write-Host "❌ Administrator privileges required" -ForegroundColor Red
                        }
                    }
                    "4" { 
                        if (Test-Administrator) {
                            Set-MpPreference -DisableRealtimeMonitoring $true
                            Write-Host "✅ Windows Defender real-time protection temporarily disabled" -ForegroundColor Green
                            Write-Host "⚠️  Remember to re-enable after gaming!" -ForegroundColor Yellow
                        } else {
                            Write-Host "❌ Administrator privileges required" -ForegroundColor Red
                        }
                    }
                    "5" { 
                        Get-ChildItem -Path $env:TEMP -Recurse | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
                        Write-Host "✅ Temp files cleaned" -ForegroundColor Green
                    }
                }
                Read-Host "Press Enter to continue..."
            }
            "13" { 
                if (Test-Path "logs\master_launcher.log") {
                    Write-Host "`n📝 Recent log entries:" -ForegroundColor Yellow
                    Get-Content "logs\master_launcher.log" -Tail 20
                } else {
                    Write-Host "❌ No log file found" -ForegroundColor Red
                }
                Read-Host "Press Enter to continue..."
            }
            "14" { 
                Write-Host "`n🔐 Security Check:" -ForegroundColor Yellow
                Write-Host "Administrator: $(if (Test-Administrator) { "✅ Yes" } else { "❌ No" })"
                Write-Host "Execution Policy: $(Get-ExecutionPolicy)"
                Write-Host "Windows Defender: $(if (Get-MpPreference | Select-Object -ExpandProperty DisableRealtimeMonitoring) { "❌ Disabled" } else { "✅ Enabled" })"
                Read-Host "Press Enter to continue..."
            }
            "15" { 
                Write-Host "`n🛑 Stopping all components..." -ForegroundColor Red
                Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
                Write-Host "✅ All Python processes stopped" -ForegroundColor Green
                Read-Host "Press Enter to continue..."
            }
            "16" { 
                Write-Host "`n🛑 Shutting down..." -ForegroundColor Red
                Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
                Write-Host "✅ SUHA FPS+ v4.0 shutdown complete" -ForegroundColor Green
                Write-Host "Thank you for using Neural Gaming Performance System!" -ForegroundColor Cyan
                break
            }
            default { 
                Write-Host "❌ Invalid choice. Please try again." -ForegroundColor Red
                Start-Sleep -Seconds 2
            }
        }
    } while ($true)
}

# Main execution logic
try {
    # Change to script directory
    Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
    
    # Check administrator privileges if requested
    if ($AdminCheck) {
        Restart-AsAdmin
    }
    
    # Check system requirements
    Test-SystemRequirements
    
    # Check Python installation
    if (-not (Test-PythonInstallation)) {
        Read-Host "Press Enter to exit..."
        exit 1
    }
    
    # Setup virtual environment
    if (-not (Setup-VirtualEnvironment)) {
        Read-Host "Press Enter to exit..."
        exit 1
    }
    
    # Handle command line arguments
    if ($QuickStart) {
        Install-Dependencies
        python master_launcher.py --quick-start
    } elseif ($InstallDeps) {
        Install-Dependencies
    } elseif ($HealthCheck) {
        Invoke-HealthCheck
    } elseif ($Daemon) {
        python master_launcher.py --daemon
    } elseif ($Component) {
        Start-Component $Component
    } else {
        # Show interactive menu
        Show-InteractiveMenu
    }
    
} catch {
    Write-Host "❌ An error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Gray
    Read-Host "Press Enter to exit..."
    exit 1
}