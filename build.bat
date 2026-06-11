@echo off
REM Virtual Camera System - One-Click Build Script
REM This script will compile the Python application to a Windows executable

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ============================================================
echo   Virtual Camera System - Build Process
echo ============================================================
echo.

REM Step 1: Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo OK - Python found
echo.

REM Step 2: Install/upgrade pip
echo [2/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    pause
    exit /b 1
)
echo OK - pip upgraded
echo.

REM Step 3: Install requirements
echo [3/6] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)
echo OK - Dependencies installed
echo.

REM Step 4: Install PyInstaller
echo [4/6] Installing PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)
echo OK - PyInstaller installed
echo.

REM Step 5: Build executable
echo [5/6] Building executable...
echo This may take 2-5 minutes...
pyinstaller --onefile --windowed --name=VirtualCamera ^
  --add-data config.py:. ^
  --add-data core:core ^
  --add-data web:web ^
  --add-data utils:utils ^
  --collect-all=cv2 ^
  --collect-all=pyvirtualcam ^
  --hidden-import=cv2 ^
  --hidden-import=pyvirtualcam ^
  --hidden-import=flask ^
  --hidden-import=flask_cors ^
  --noconfirm ^
  --clean ^
  main.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)
echo OK - Executable built successfully
echo.

REM Step 6: Create batch runners
echo [6/6] Creating launcher scripts...

(
    @echo off
    REM Virtual Camera System Launcher with Web Interface
    cd /d "%%~dp0"
    VirtualCamera.exe --web
    pause
) > dist\Run_with_Web.bat

(
    @echo off
    REM Virtual Camera System Launcher
    cd /d "%%~dp0"
    VirtualCamera.exe
    pause
) > dist\Run.bat

echo OK - Launcher scripts created
echo.

REM Success message
echo ============================================================
echo   Build Complete!
echo ============================================================
echo.
echo Location: %CD%\dist\VirtualCamera.exe
echo.
echo Files created:
echo   - VirtualCamera.exe (main application)
echo   - Run.bat (simple launcher)
echo   - Run_with_Web.bat (web interface launcher)
echo.
echo Next steps:
echo   1. Go to the dist\ folder
echo   2. Double-click VirtualCamera.exe to run
echo   3. Or double-click Run_with_Web.bat to open web interface
echo.
echo Command line examples:
echo   VirtualCamera.exe --video input.mp4 --effect blur
echo   VirtualCamera.exe --image input.jpg --enable-face-detection
echo   VirtualCamera.exe --web
echo.
pause
