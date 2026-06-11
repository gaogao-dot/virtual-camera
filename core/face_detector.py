"""
人脸检测模块 - Face Detection Module
使用 OpenCV 的 Haar Cascade 进行实时人脸检测
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional

from config import FACE_DETECTION, LOGGING_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__, LOGGING_CONFIG)


class FaceDetector:
    """人脸检测器"""

    def __init__(self, cascade_path: str = None):
        """
        初始化人脸检测器
        
        Args:
            cascade_path: Haar Cascade 分类器文件路径
        """
        self.cascade_path = cascade_path
        self.cascade = None
        self.enabled = FACE_DETECTION['enabled']
        self.frame_skip = FACE_DETECTION['frame_skip']
        self.frame_count = 0
        
        self._load_cascade()

    def _load_cascade(self) -> bool:
        """
        加载 Haar Cascade 分类器
        
        Returns:
            bool: 是否成功加载
        """
        try:
            if self.cascade_path:
                cascade_file = Path(self.cascade_path)
                if not cascade_file.exists():
                    raise FileNotFoundError(f"Cascade file not found: {self.cascade_path}")
            else:
                cascade_file = cv2.data.haarcascades + FACE_DETECTION['cascade_file']
            
            self.cascade = cv2.CascadeClassifier(str(cascade_file))
            
            if self.cascade.empty():
                raise RuntimeError(f"Failed to load cascade classifier: {cascade_file}")
            
            logger.info(f"Face detector loaded: {cascade_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load cascade: {e}")
            self.enabled = False
            return False

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        检测图像中的人脸
        
        Args:
            frame: 输入图像 (BGR 格式)
            
        Returns:
            List[Tuple[int, int, int, int]]: 人脸位置列表 [(x, y, w, h), ...]
        """
        if not self.enabled or self.cascade is None:
            return []

        try:
            self.frame_count += 1
            if self.frame_count % (self.frame_skip + 1) != 0:
                return []

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = self.cascade.detectMultiScale(
                gray,
                scaleFactor=FACE_DETECTION['scale_factor'],
                minNeighbors=FACE_DETECTION['min_neighbors'],
                minSize=FACE_DETECTION['min_face_size'],
                maxSize=FACE_DETECTION['max_face_size'],
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return []

    def draw_faces(self, frame: np.ndarray, faces: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        在图像上绘制人脸矩形和信息
        
        Args:
            frame: 输入图像
            faces: 人脸位置列表
            
        Returns:
            np.ndarray: 标注后的图像
        """
        if not faces:
            return frame

        frame_copy = frame.copy()
        
        try:
            for i, (x, y, w, h) in enumerate(faces):
                if FACE_DETECTION['draw_rectangle']:
                    cv2.rectangle(
                        frame_copy,
                        (x, y),
                        (x + w, y + h),
                        FACE_DETECTION['rectangle_color'],
                        FACE_DETECTION['rectangle_thickness']
                    )
                
                if FACE_DETECTION['draw_info']:
                    label = f"Face {i + 1}"
                    confidence = f"({w}x{h})"
                    
                    cv2.putText(
                        frame_copy,
                        label,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        FACE_DETECTION['rectangle_color'],
                        2
                    )
                    
                    cv2.putText(
                        frame_copy,
                        confidence,
                        (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        FACE_DETECTION['rectangle_color'],
                        1
                    )
            
            return frame_copy
            
        except Exception as e:
            logger.error(f"Failed to draw faces: {e}")
            return frame

    def detect_and_draw(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Tuple[int, int, int, int]]]:
        """
        检测并绘制人脸
        
        Args:
            frame: 输入图像
            
        Returns:
            Tuple[np.ndarray, List]: (标注后的图像, 人脸列表)
        """
        faces = self.detect_faces(frame)
        annotated_frame = self.draw_faces(frame, faces)
        return annotated_frame, faces

    def enable(self) -> None:
        """启用人脸检测"""
        self.enabled = True
        logger.info("Face detection enabled")

    def disable(self) -> None:
        """禁用人脸检测"""
        self.enabled = False
        logger.info("Face detection disabled")

    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'enabled': self.enabled,
            'cascade_loaded': self.cascade is not None and not self.cascade.empty(),
            'frame_count': self.frame_count,
        }
