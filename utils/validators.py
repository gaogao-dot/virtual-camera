"""
数据验证 - Data Validators
"""

from pathlib import Path
from config import VIDEO_CONFIG, IMAGE_CONFIG, CAMERA_CONFIG


def validate_file(file_path: str) -> tuple:
    """
    验证文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        tuple: (is_valid, error_message, file_type)
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return False, "File not found", None
        
        if not path.is_file():
            return False, "Not a file", None
        
        suffix = path.suffix.lower()
        
        if suffix in VIDEO_CONFIG['supported_formats']:
            size = path.stat().st_size
            if size > VIDEO_CONFIG['max_file_size']:
                return False, f"Video file too large: {size / 1024 / 1024:.2f}MB", None
            return True, "", "video"
        
        if suffix in IMAGE_CONFIG['supported_formats']:
            size = path.stat().st_size
            if size > IMAGE_CONFIG['max_file_size']:
                return False, f"Image file too large: {size / 1024 / 1024:.2f}MB", None
            return True, "", "image"
        
        return False, f"Unsupported format: {suffix}", None
        
    except Exception as e:
        return False, str(e), None


def validate_resolution(width: int, height: int) -> tuple:
    """
    验证分辨率
    
    Args:
        width: 宽度
        height: 高度
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not isinstance(width, int) or not isinstance(height, int):
            return False, "Width and height must be integers"
        
        if width < 320 or width > 3840:
            return False, "Width must be between 320 and 3840"
        
        if height < 240 or height > 2160:
            return False, "Height must be between 240 and 2160"
        
        return True, ""
        
    except Exception as e:
        return False, str(e)


def validate_fps(fps: int) -> tuple:
    """
    验证帧率
    
    Args:
        fps: 帧率
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if not isinstance(fps, int):
            return False, "FPS must be an integer"
        
        if fps < 1 or fps > 60:
            return False, "FPS must be between 1 and 60"
        
        return True, ""
        
    except Exception as e:
        return False, str(e)
