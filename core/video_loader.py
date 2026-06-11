"""
视频/图片加载器 - Video & Image Loader
处理视频和图片文件的加载和帧提取
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple
import threading
import time

from config import VIDEO_CONFIG, IMAGE_CONFIG, LOGGING_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__, LOGGING_CONFIG)


class VideoLoader:
    """视频加载器"""

    def __init__(self, video_path: str = None):
        """
        初始化视频加载器
        
        Args:
            video_path: 视频文件路径
        """
        self.video_path = video_path
        self.capture = None
        self.total_frames = 0
        self.current_frame_idx = 0
        self.fps = 30
        self.frame_width = 0
        self.frame_height = 0
        self.is_loaded = False
        self.is_playing = False
        self.frame_buffer = []
        self.buffer_lock = threading.Lock()
        
        if video_path:
            self.load(video_path)

    def load(self, video_path: str) -> bool:
        """
        加载视频文件
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            path = Path(video_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            if path.suffix.lower() not in VIDEO_CONFIG['supported_formats']:
                raise ValueError(f"Unsupported format: {path.suffix}")
            
            if path.stat().st_size > VIDEO_CONFIG['max_file_size']:
                raise ValueError(f"File too large: {path.stat().st_size} bytes")
            
            if self.capture is not None:
                self.capture.release()
            
            self.capture = cv2.VideoCapture(str(path))
            
            if not self.capture.isOpened():
                raise RuntimeError(f"Failed to open video: {video_path}")
            
            self.total_frames = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.capture.get(cv2.CAP_PROP_FPS)
            self.frame_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.current_frame_idx = 0
            self.is_loaded = True
            
            logger.info(
                f"Video loaded: {path.name} "
                f"({self.frame_width}x{self.frame_height}@{self.fps}fps, "
                f"{self.total_frames} frames)"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to load video: {e}")
            self.is_loaded = False
            return False

    def get_next_frame(self) -> Optional[np.ndarray]:
        """
        获取下一帧
        
        Returns:
            Optional[np.ndarray]: 下一帧，如果没有则返回 None
        """
        if not self.is_loaded or self.capture is None:
            return None

        try:
            ret, frame = self.capture.read()
            
            if ret:
                self.current_frame_idx += 1
                
                if self.current_frame_idx >= self.total_frames and VIDEO_CONFIG['loop_video']:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_idx = 0
                
                return frame
            else:
                if VIDEO_CONFIG['loop_video']:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_idx = 0
                    ret, frame = self.capture.read()
                    return frame if ret else None
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get next frame: {e}")
            return None

    def get_progress(self) -> float:
        """
        获取播放进度（0-1）
        
        Returns:
            float: 进度比例
        """
        if self.total_frames <= 0:
            return 0.0
        return self.current_frame_idx / self.total_frames

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'is_loaded': self.is_loaded,
            'video_path': str(self.video_path),
            'total_frames': self.total_frames,
            'current_frame': self.current_frame_idx,
            'fps': self.fps,
            'width': self.frame_width,
            'height': self.frame_height,
            'duration': self.total_frames / self.fps if self.fps > 0 else 0,
            'progress': self.get_progress(),
        }

    def release(self) -> None:
        """释放视频资源"""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
            self.is_loaded = False
            logger.info("Video released")

    def __del__(self):
        """析构函数"""
        self.release()


class ImageLoader:
    """图片加载器"""

    def __init__(self, image_path: str = None):
        """
        初始化图片加载器
        
        Args:
            image_path: 图片文件路径
        """
        self.image_path = image_path
        self.current_image = None
        self.is_loaded = False
        
        if image_path:
            self.load(image_path)

    def load(self, image_path: str) -> bool:
        """
        加载图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            path = Path(image_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            if path.suffix.lower() not in IMAGE_CONFIG['supported_formats']:
                raise ValueError(f"Unsupported format: {path.suffix}")
            
            if path.stat().st_size > IMAGE_CONFIG['max_file_size']:
                raise ValueError(f"File too large: {path.stat().st_size} bytes")
            
            self.current_image = cv2.imread(str(path))
            
            if self.current_image is None:
                raise RuntimeError(f"Failed to load image: {image_path}")
            
            self.image_path = image_path
            self.is_loaded = True
            
            logger.info(
                f"Image loaded: {path.name} "
                f"({self.current_image.shape[1]}x{self.current_image.shape[0]})"
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            self.is_loaded = False
            return False

    def get_image(self) -> Optional[np.ndarray]:
        """
        获取当前图片
        
        Returns:
            Optional[np.ndarray]: 当前图片，如果未加载则返回 None
        """
        if not self.is_loaded:
            return None
        return self.current_image.copy() if self.current_image is not None else None

    def get_stats(self) -> dict:
        """获取统计信息"""
        if not self.is_loaded or self.current_image is None:
            return {'is_loaded': False}
        
        return {
            'is_loaded': self.is_loaded,
            'image_path': str(self.image_path),
            'width': self.current_image.shape[1],
            'height': self.current_image.shape[0],
        }

    def release(self) -> None:
        """释放图片资源"""
        self.current_image = None
        self.is_loaded = False
        logger.info("Image released")

    def __del__(self):
        """析构函数"""
        self.release()
