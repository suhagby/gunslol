@echo off
title SUHA FPS+ v4.0 - Neural Gaming Performance System
color 0A

echo.
echo   ╔══════════════════════════════════════════════════════════════════════════╗
echo   ║                           SUHA FPS+ v4.0 LAUNCHER                       ║
echo   ║                      Neural Gaming Performance System                    ║
echo   ║                                                                          ║
echo   ║  🤖 AI Engine v4.0        ⚡ Performance Optimizer v4.0                 ║
echo   ║  🖥️  Windows Optimizer     🌐 Enhanced Web Interface                     ║ 
echo   ║  🤖 Discord Bot v4.0      📊 Real-time System Monitoring                ║
echo   ╚══════════════════════════════════════════════════════════════════════════╝
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running with administrator privileges
    goto :main
) else (
    echo ⚠️  Administrator privileges recommended for full optimization
    echo.
    echo Do you want to restart as administrator? ^(Y/N^)
    set /p admin_choice=
    if /i "%admin_choice%"=="Y" (
        echo Restarting as administrator...
        powershell -Command "Start-Process '%~f0' -Verb RunAs"
        exit /b
    ) else (
        echo Continuing without administrator privileges...
        echo Some Windows optimizations may not work properly.
        pause
        goto :main
    )
)

:main
:: Set working directory
cd /d "%~dp0"

:: Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python found

:: Check if virtual environment exists
if exist "venv" (
    echo ✅ Virtual environment found
    call venv\Scripts\activate.bat
) else (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment created
)

:: Display main menu
:menu
cls
echo.
echo   ╔══════════════════════════════════════════════════════════════════════════╗
echo   ║                    SUHA FPS+ v4.0 WINDOWS LAUNCHER                      ║
echo   ╚══════════════════════════════════════════════════════════════════════════╝
echo.
echo   ════════════════════════════════════════════════════════════════════════════
echo   🚀 LAUNCHER MENU
echo   ════════════════════════════════════════════════════════════════════════════
echo   1. ⚡ Quick Start ^(Install + Launch All^)
echo   2. 🔧 Install Dependencies Only
echo   3. 🚀 Launch System ^(Interactive Mode^)
echo   4. 🌐 Launch Web Dashboard Only
echo   5. 🤖 Launch AI Engine Only
echo   6. ⚡ Launch Performance Optimizer Only
echo   7. 🖥️  Launch Windows Optimizer Only
echo   8. 🤖 Launch Discord Bot Only
echo   9. 🏥 System Health Check
echo  10. 📊 View System Status
echo  11. ⚙️  Configuration Manager
echo  12. 📝 View Logs
echo  13. 🔄 Reset System
echo  14. ❌ Exit
echo   ════════════════════════════════════════════════════════════════════════════
echo.
set /p choice="👉 Enter your choice (1-14): "

if "%choice%"=="1" goto :quick_start
if "%choice%"=="2" goto :install_deps
if "%choice%"=="3" goto :launch_interactive
if "%choice%"=="4" goto :launch_web
if "%choice%"=="5" goto :launch_ai
if "%choice%"=="6" goto :launch_perf
if "%choice%"=="7" goto :launch_windows
if "%choice%"=="8" goto :launch_discord
if "%choice%"=="9" goto :health_check
if "%choice%"=="10" goto :system_status
if "%choice%"=="11" goto :config_manager
if "%choice%"=="12" goto :view_logs
if "%choice%"=="13" goto :reset_system
if "%choice%"=="14" goto :exit
echo ❌ Invalid choice. Please try again.
pause
goto :menu

:quick_start
echo.
echo 🚀 Quick Start: Installing dependencies and launching system...
echo ════════════════════════════════════════════════════════════════════════════
python master_launcher.py --quick-start
pause
goto :menu

:install_deps
echo.
echo 🔧 Installing system dependencies...
echo ════════════════════════════════════════════════════════════════════════════
python master_launcher.py --install-deps
pause
goto :menu

:launch_interactive
echo.
echo 🚀 Launching interactive system...
echo ════════════════════════════════════════════════════════════════════════════
python master_launcher.py
pause
goto :menu

:launch_web
echo.
echo 🌐 Launching web dashboard...
echo ════════════════════════════════════════════════════════════════════════════
if not exist "web_dashboard.py" (
    echo Creating web dashboard launcher...
    python -c "
from master_launcher import MasterLauncher
launcher = MasterLauncher()
launcher.web_dashboard.start_dashboard()
"
) else (
    python web_dashboard.py
)
pause
goto :menu

:launch_ai
echo.
echo 🤖 Launching AI Engine...
echo ════════════════════════════════════════════════════════════════════════════
python ai_engine_v4.py
pause
goto :menu

:launch_perf
echo.
echo ⚡ Launching Performance Optimizer...
echo ════════════════════════════════════════════════════════════════════════════
python advanced_performance_optimizer_v4.py
pause
goto :menu

:launch_windows
echo.
echo 🖥️  Launching Windows Optimizer...
echo ════════════════════════════════════════════════════════════════════════════
python windows_optimizer_v4.py
pause
goto :menu

:launch_discord
echo.
echo 🤖 Launching Discord Bot...
echo ════════════════════════════════════════════════════════════════════════════
set /p token="Enter Discord Bot Token (or press Enter to skip): "
if not "%token%"=="" (
    set DISCORD_BOT_TOKEN=%token%
    python discord_bot_v4.py
) else (
    echo ❌ Discord bot token required
)
pause
goto :menu

:health_check
echo.
echo 🏥 Running system health check...
echo ════════════════════════════════════════════════════════════════════════════
python master_launcher.py --health-check
pause
goto :menu

:system_status
echo.
echo 📊 System Status
echo ════════════════════════════════════════════════════════════════════════════
echo Python Version:
python --version
echo.
echo Virtual Environment:
if "%VIRTUAL_ENV%"=="" (
    echo ❌ Not activated
) else (
    echo ✅ Activated: %VIRTUAL_ENV%
)
echo.
echo System Information:
systeminfo | findstr /C:"OS Name" /C:"System Type" /C:"Total Physical Memory"
echo.
echo Running Processes:
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
pause
goto :menu

:config_manager
echo.
echo ⚙️  Configuration Manager
echo ════════════════════════════════════════════════════════════════════════════
if exist "config\master_config.json" (
    echo Current configuration:
    type "config\master_config.json"
    echo.
    echo 1. Edit configuration
    echo 2. Backup configuration  
    echo 3. Reset to defaults
    echo 4. Return to menu
    set /p config_choice="Enter choice: "
    
    if "%config_choice%"=="1" (
        notepad "config\master_config.json"
    )
    if "%config_choice%"=="2" (
        copy "config\master_config.json" "config\backup_config_%date:~-4,4%%date:~-10,2%%date:~-7,2%.json"
        echo ✅ Configuration backed up
    )
    if "%config_choice%"=="3" (
        del "config\master_config.json"
        echo ✅ Configuration reset
    )
) else (
    echo ❌ No configuration file found
    echo Creating default configuration...
    python -c "from master_launcher import MasterLauncher; MasterLauncher().save_configuration()"
    echo ✅ Default configuration created
)
pause
goto :menu

:view_logs
echo.
echo 📝 System Logs
echo ════════════════════════════════════════════════════════════════════════════
if exist "logs\master_launcher.log" (
    echo Last 20 lines of master launcher log:
    echo ────────────────────────────────────────────────────────────────────────────
    powershell -Command "Get-Content 'logs\master_launcher.log' -Tail 20"
) else (
    echo ❌ No log file found
)
echo.
if exist "logs" (
    echo Available log files:
    dir logs\*.log /B
)
pause
goto :menu

:reset_system
echo.
echo 🔄 System Reset
echo ════════════════════════════════════════════════════════════════════════════
echo ⚠️  WARNING: This will reset all configuration and stop all components!
set /p confirm="Are you sure you want to continue? (yes/no): "
if /i "%confirm%"=="yes" (
    echo Stopping all Python processes...
    taskkill /F /IM python.exe >nul 2>&1
    
    echo Resetting configuration...
    if exist "config\master_config.json" del "config\master_config.json"
    
    echo Clearing logs...
    if exist "logs" (
        del /Q "logs\*.*" >nul 2>&1
    )
    
    echo ✅ System reset complete
) else (
    echo ❌ Reset cancelled
)
pause
goto :menu

:exit
echo.
echo 🛑 Shutting down system...
echo ════════════════════════════════════════════════════════════════════════════

:: Try graceful shutdown first
python -c "
import sys
sys.path.append('.')
try:
    from master_launcher import MasterLauncher
    launcher = MasterLauncher()
    launcher.shutdown()
    print('✅ Graceful shutdown completed')
except Exception as e:
    print(f'⚠️  Error during graceful shutdown: {e}')
    print('Forcing shutdown...')
"

:: Force stop any remaining processes
taskkill /F /IM python.exe >nul 2>&1

echo ✅ SUHA FPS+ v4.0 shutdown complete
echo Thank you for using Neural Gaming Performance System!
pause
exit /b 0