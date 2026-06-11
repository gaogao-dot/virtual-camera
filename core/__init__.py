"""
Core module for Virtual Camera System
"""

from .camera_manager import CameraManager
from .face_detector import FaceDetector
from .effect_processor import EffectProcessor
from .video_loader import VideoLoader

__all__ = [
    'CameraManager',
    'FaceDetector',
    'EffectProcessor',
    'VideoLoader',
]
