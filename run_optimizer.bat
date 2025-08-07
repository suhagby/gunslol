@echo off
REM Gaming Performance Optimizer Launcher
REM Automatically run with administrator privileges for full functionality

echo ========================================================
echo    ULTIMATE GAMING PERFORMANCE OPTIMIZER v5.0
echo    Maximum FPS - Minimum Latency - Competitive Gaming
echo ========================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Not running as administrator!
    echo Some optimizations may not work properly.
    echo.
    echo Attempting to restart with administrator privileges...
    echo.
    
    REM Try to restart with admin privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo [OK] Running with administrator privileges
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python is available
echo.

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM Install required packages if they don't exist
echo Checking required packages...
python -c "import psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing psutil...
    pip install psutil
)

python -c "import winreg" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] winreg not available (normal on non-Windows systems)
)

echo.
echo ========================================================
echo Select optimization mode:
echo.
echo 1. Interactive Mode (Full Control)
echo 2. Auto Mode (Run and Monitor)
echo 3. Quick Competitive Profile
echo 4. Quick Streaming Profile  
echo 5. Quick Maximum Performance
echo 6. GUI Mode (Visual Interface)
echo 7. CS2 Specific Optimizations
echo 8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" (
    echo.
    echo Starting Interactive Mode...
    python ultimate_performance_optimizer.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Auto Mode...
    python startup_optimizer.py auto
) else if "%choice%"=="3" (
    echo.
    echo Applying Competitive Gaming Profile...
    python ultimate_performance_optimizer.py competitive
) else if "%choice%"=="4" (
    echo.
    echo Applying Gaming + Streaming Profile...
    python ultimate_performance_optimizer.py streaming
) else if "%choice%"=="5" (
    echo.
    echo Applying Maximum Performance Profile...
    python ultimate_performance_optimizer.py maximum
) else if "%choice%"=="6" (
    echo.
    echo Starting GUI Mode...
    python startup_optimizer.py gui
) else if "%choice%"=="7" (
    echo.
    echo Applying CS2 Specific Optimizations...
    python -c "from ultimate_performance_optimizer import UltimatePerformanceOptimizer; opt = UltimatePerformanceOptimizer(); opt.apply_cs2_specific_optimizations(); print('CS2 optimizations applied!')"
) else if "%choice%"=="8" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo Invalid choice! Please run the script again.
)

echo.
echo ========================================================
echo Optimization complete!
echo.
echo IMPORTANT NOTES:
echo - Some changes may require a system restart
echo - Registry changes are applied immediately
echo - Game-specific optimizations activate when games are detected
echo - Background monitoring continues until stopped
echo.
echo For best results:
echo 1. Restart your system after first run
echo 2. Run this script before gaming sessions
echo 3. Keep background monitoring active during gaming
echo.
pause