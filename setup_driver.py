#!/usr/bin/env python3
"""
虚拟摄像头驱动安装脚本
"""

import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_pyvirtualcam():
    try:
        import pyvirtualcam
        logger.info(f"✓ pyvirtualcam is installed: {pyvirtualcam.__version__}")
        return True
    except ImportError:
        logger.error("✗ pyvirtualcam is not installed")
        return False

def check_opencv():
    try:
        import cv2
        logger.info(f"✓ OpenCV is installed: {cv2.__version__}")
        return True
    except ImportError:
        logger.error("✗ OpenCV is not installed")
        return False

def check_windows():
    import platform
    if platform.system() == 'Windows':
        logger.info("✓ Running on Windows")
        return True
    return False

def main():
    print("\n" + "="*60)
    print("Virtual Camera System - Setup Script")
    print("="*60 + "\n")
    
    results = {
        'Windows': check_windows(),
        'OpenCV': check_opencv(),
        'pyvirtualcam': check_pyvirtualcam(),
    }
    
    print("\n" + "="*60)
    print("Installation Summary")
    print("="*60)
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}: {'OK' if result else 'FAILED'}")
    
    if all(results.values()):
        print("\n✓ All checks passed!")
        return 0
    return 1

if __name__ == '__main__':
    sys.exit(main())
