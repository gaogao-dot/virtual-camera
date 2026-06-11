"""
虚拟摄像头管理器 - Virtual Camera Manager
处理虚拟摄像头的创建、帧输出和管理
"""

import threading
import time
import logging
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pyvirtualcam
import cv2

from config import CAMERA_CONFIG, LOGGING_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__, LOGGING_CONFIG)


class CameraManager:
    """虚拟摄像头管理器"""

    def __init__(self, width: int = None, height: int = None, fps: int = None):
        """
        初始化摄像头管理器
        
        Args:
            width: 输出宽度（像素）
            height: 输出高度（像素）
            fps: 输出帧率
        """
        self.width = width or CAMERA_CONFIG['width']
        self.height = height or CAMERA_CONFIG['height']
        self.fps = fps or CAMERA_CONFIG['fps']
        
        self.camera = None
        self.is_running = False
        self.frame_lock = threading.Lock()
        self.current_frame = None
        self.frame_count = 0
        self.start_time = None
        
        logger.info(f"CameraManager initialized: {self.width}x{self.height}@{self.fps}fps")

    def start(self) -> bool:
        """
        启动虚拟摄像头
        
        Returns:
            bool: 是否成功启动
        """
        try:
            if self.camera is not None:
                logger.warning("Camera already started")
                return False

            self.camera = pyvirtualcam.Camera(
                width=self.width,
                height=self.height,
                fps=self.fps,
                fmt=pyvirtualcam.PixelFormat.BGR
            )
            
            self.is_running = True
            self.start_time = time.time()
            logger.info(f"Virtual camera started: {self.width}x{self.height}@{self.fps}fps")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera: {e}")
            return False

    def stop(self) -> bool:
        """
        停止虚拟摄像头
        
        Returns:
            bool: 是否成功停止
        """
        try:
            if self.camera is None:
                return False

            self.is_running = False
            self.camera.close()
            self.camera = None
            logger.info("Virtual camera stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop camera: {e}")
            return False

    def send_frame(self, frame: np.ndarray) -> bool:
        """
        发送帧到虚拟摄像头
        
        Args:
            frame: OpenCV 图像帧 (BGR格式)
            
        Returns:
            bool: 是否成功发送
        """
        if not self.is_running or self.camera is None:
            logger.warning("Camera not running")
            return False

        try:
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))

            if frame.dtype != np.uint8:
                frame = np.uint8(frame)
            
            frame = np.ascontiguousarray(frame)

            with self.frame_lock:
                self.camera.send(frame)
                self.current_frame = frame.copy()
                self.frame_count += 1

            return True
            
        except Exception as e:
            logger.error(f"Failed to send frame: {e}")
            return False

    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        获取当前帧
        
        Returns:
            Optional[np.ndarray]: 当前帧，如果没有则返回 None
        """
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None

    def get_stats(self) -> dict:
        """
        获取摄像头统计信息
        
        Returns:
            dict: 统计信息
        """
        elapsed = time.time() - self.start_time if self.start_time else 0
        actual_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            'width': self.width,
            'height': self.height,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'elapsed_time': elapsed,
            'actual_fps': actual_fps,
            'is_running': self.is_running,
        }

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()
