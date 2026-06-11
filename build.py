#!/usr/bin/env python3
"""
Build script for Virtual Camera System
Converts Python application to standalone Windows executable
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_requirements():
    """Check if all required packages are installed"""
    print_header("Checking Requirements")
    
    required_packages = {
        'pyinstaller': 'PyInstaller',
        'cv2': 'opencv-python',
        'pyvirtualcam': 'pyvirtualcam',
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install them with: pip install {' '.join(missing)}")
        return False
    
    print("\n✓ All requirements are satisfied!")
    return True

def clean_build():
    """Clean previous build artifacts"""
    print_header("Cleaning Previous Builds")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ Removed {dir_name}")
            except Exception as e:
                print(f"⚠ Failed to remove {dir_name}: {e}")
    
    # Clean .spec file
    if os.path.exists('main.spec'):
        try:
            os.remove('main.spec')
            print("✓ Removed main.spec")
        except Exception as e:
            print(f"⚠ Failed to remove main.spec: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print_header("Building Executable")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=VirtualCamera',
        '--icon=app.ico',  # Optional: if you have an icon file
        '--add-data=config.py:.',
        '--add-data=core:core',
        '--add-data=web:web',
        '--add-data=utils:utils',
        '--collect-all=cv2',
        '--collect-all=pyvirtualcam',
        '--hidden-import=cv2',
        '--hidden-import=pyvirtualcam',
        '--hidden-import=flask',
        '--hidden-import=flask_cors',
        '--noconfirm',
        '--clean',
        'main.py'
    ]
    
    print("Running PyInstaller...")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error: {e}")
        return False

def verify_build():
    """Verify the build was successful"""
    print_header("Verifying Build")
    
    exe_path = Path('dist/VirtualCamera.exe')
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Executable created successfully!")
        print(f"  Location: {exe_path.absolute()}")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print("❌ Executable not found in dist/ directory")
        return False

def create_batch_runner():
    """Create batch files for easy launching"""
    print_header("Creating Launcher Scripts")
    
    # Batch file for running with Web interface
    batch_content = """@echo off
REM Virtual Camera System Launcher with Web Interface
cd /d "%~dp0"
VirtualCamera.exe --web
pause
"""
    
    with open('dist/Run_with_Web.bat', 'w') as f:
        f.write(batch_content)
    print("✓ Created Run_with_Web.bat")
    
    # Batch file for normal run
    batch_content = """@echo off
REM Virtual Camera System Launcher
cd /d "%~dp0"
VirtualCamera.exe
pause
"""
    
    with open('dist/Run.bat', 'w') as f:
        f.write(batch_content)
    print("✓ Created Run.bat")

def print_summary():
    """Print build summary and instructions"""
    print_header("Build Summary")
    
    print("✓ Build process completed!\n")
    print("📍 Output Location: dist/VirtualCamera.exe\n")
    print("🚀 How to Use:")
    print("-" * 60)
    print("1. Run the executable:")
    print("   Double-click VirtualCamera.exe\n")
    print("2. Run with Web interface:")
    print("   Double-click Run_with_Web.bat")
    print("   Then open http://localhost:5000\n")
    print("3. Command line usage:")
    print("   VirtualCamera.exe --video input.mp4 --effect blur")
    print("   VirtualCamera.exe --image input.jpg --enable-face-detection")
    print("   VirtualCamera.exe --web\n")
    print("-" * 60)
    print("📦 Package Contents:")
    print("  - VirtualCamera.exe (main application)")
    print("  - Run.bat (simple launcher)")
    print("  - Run_with_Web.bat (web interface launcher)\n")

def main():
    """Main build process"""
    print("\n" + "=" * 60)
    print("  Virtual Camera System - Build Process")
    print("=" * 60)
    
    # Step 1: Check requirements
    if not check_requirements():
        return 1
    
    # Step 2: Clean previous builds
    clean_build()
    
    # Step 3: Build executable
    if not build_executable():
        return 1
    
    # Step 4: Verify build
    if not verify_build():
        return 1
    
    # Step 5: Create batch runners
    create_batch_runner()
    
    # Step 6: Print summary
    print_summary()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
