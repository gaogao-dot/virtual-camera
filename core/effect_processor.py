"""
效果处理模块 - Effect Processor Module
提供各种实时视频效果处理功能
"""

import logging
import cv2
import numpy as np
from typing import Optional, Callable
from enum import Enum

from config import EFFECTS_CONFIG, LOGGING_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__, LOGGING_CONFIG)


class EffectType(Enum):
    """效果类型枚举"""
    NONE = "none"
    BLUR = "blur"
    GRAYSCALE = "grayscale"
    CARTOON = "cartoon"
    BEAUTY = "beauty"
    EDGE = "edge"
    BILATERAL = "bilateral"
    VIGNETTE = "vignette"
    SEPIA = "sepia"


class EffectProcessor:
    """效果处理器"""

    def __init__(self):
        """初始化效果处理器"""
        self.enabled = EFFECTS_CONFIG['enabled']
        self.current_effect = EFFECTS_CONFIG['default_effect']
        self.custom_effects = {}
        
        logger.info("EffectProcessor initialized")

    def apply_effect(self, frame: np.ndarray, effect: str = None) -> np.ndarray:
        """
        应用效果到帧
        
        Args:
            frame: 输入图像
            effect: 效果名称（如果为 None 则使用当前效果）
            
        Returns:
            np.ndarray: 处理后的图像
        """
        if not self.enabled:
            return frame

        effect_name = effect or self.current_effect
        
        try:
            effect_func = self._get_effect_function(effect_name)
            if effect_func:
                return effect_func(frame)
            return frame
            
        except Exception as e:
            logger.error(f"Failed to apply effect '{effect_name}': {e}")
            return frame

    def _get_effect_function(self, effect_name: str) -> Optional[Callable]:
        """获取效果处理函数"""
        effect_map = {
            'none': self._effect_none,
            'blur': self._effect_blur,
            'grayscale': self._effect_grayscale,
            'cartoon': self._effect_cartoon,
            'beauty': self._effect_beauty,
            'edge': self._effect_edge,
            'bilateral': self._effect_bilateral,
            'vignette': self._effect_vignette,
            'sepia': self._effect_sepia,
        }
        
        if effect_name in self.custom_effects:
            return self.custom_effects[effect_name]
        
        return effect_map.get(effect_name)

    @staticmethod
    def _effect_none(frame: np.ndarray) -> np.ndarray:
        """无效果"""
        return frame

    @staticmethod
    def _effect_blur(frame: np.ndarray) -> np.ndarray:
        """模糊效果"""
        kernel_size = EFFECTS_CONFIG['blur']['kernel_size']
        return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)

    @staticmethod
    def _effect_grayscale(frame: np.ndarray) -> np.ndarray:
        """灰度效果"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _effect_cartoon(frame: np.ndarray) -> np.ndarray:
        """卡通效果"""
        d = EFFECTS_CONFIG['cartoon']['d']
        sigma_color = EFFECTS_CONFIG['cartoon']['sigma_color']
        sigma_space = EFFECTS_CONFIG['cartoon']['sigma_space']
        
        bilateral = cv2.bilateralFilter(frame, d, sigma_color, sigma_space)
        gray = cv2.cvtColor(bilateral, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)
        edges = cv2.bitwise_not(edges)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cartoon = cv2.bitwise_and(bilateral, edges_bgr)
        return cartoon

    @staticmethod
    def _effect_beauty(frame: np.ndarray) -> np.ndarray:
        """美颜效果"""
        blur_strength = EFFECTS_CONFIG['beauty']['blur_strength']
        brightness = EFFECTS_CONFIG['beauty']['brightness']
        contrast = EFFECTS_CONFIG['beauty']['contrast']
        bilateral = cv2.bilateralFilter(frame, 9, 75, 75)
        blurred = cv2.GaussianBlur(bilateral, (blur_strength, blur_strength), 0)
        beauty = cv2.addWeighted(frame, 0.5, blurred, 0.5, 0)
        beauty = cv2.convertScaleAbs(beauty, alpha=contrast, beta=brightness)
        return beauty

    @staticmethod
    def _effect_edge(frame: np.ndarray) -> np.ndarray:
        """边缘检测效果"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def _effect_bilateral(frame: np.ndarray) -> np.ndarray:
        """双边滤波效果"""
        d = EFFECTS_CONFIG['bilateral']['d']
        sigma_color = EFFECTS_CONFIG['bilateral']['sigma_color']
        sigma_space = EFFECTS_CONFIG['bilateral']['sigma_space']
        return cv2.bilateralFilter(frame, d, sigma_color, sigma_space)

    @staticmethod
    def _effect_vignette(frame: np.ndarray) -> np.ndarray:
        """晕影效果"""
        rows, cols = frame.shape[:2]
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        frame_float = frame.astype(float)
        for i in range(3):
            frame_float[:, :, i] = frame_float[:, :, i] * mask
        return np.uint8(frame_float)

    @staticmethod
    def _effect_sepia(frame: np.ndarray) -> np.ndarray:
        """棕褐色效果"""
        sepia_matrix = np.array([
            [0.272, 0.534, 0.131],
            [0.349, 0.686, 0.168],
            [0.393, 0.769, 0.189]
        ])
        sepia = cv2.transform(frame, sepia_matrix)
        return np.uint8(np.clip(sepia, 0, 255))

    def register_custom_effect(self, name: str, effect_func: Callable) -> bool:
        """注册自定义效果"""
        try:
            self.custom_effects[name] = effect_func
            logger.info(f"Custom effect registered: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register custom effect '{name}': {e}")
            return False

    def set_current_effect(self, effect: str) -> bool:
        """设置当前效果"""
        if self._get_effect_function(effect) is None:
            logger.warning(f"Unknown effect: {effect}")
            return False
        self.current_effect = effect
        logger.info(f"Effect changed to: {effect}")
        return True

    def get_available_effects(self) -> list:
        """获取所有可用效果"""
        effects = [e.value for e in EffectType]
        effects.extend(self.custom_effects.keys())
        return effects

    def enable(self) -> None:
        """启用效果处理"""
        self.enabled = True
        logger.info("Effect processing enabled")

    def disable(self) -> None:
        """禁用效果处理"""
        self.enabled = False
        logger.info("Effect processing disabled")

    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.enabled

    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'enabled': self.enabled,
            'current_effect': self.current_effect,
            'available_effects': self.get_available_effects(),
            'custom_effects_count': len(self.custom_effects),
        }
