#!/usr/bin/env python3
"""
虚拟摄像头直播系统 - Virtual Camera Live System
主程序入口
"""

import argparse
import time
import sys
import logging
from pathlib import Path
import threading

from core import CameraManager, VideoLoader, FaceDetector, EffectProcessor
from core.video_loader import ImageLoader
from config import LOGGING_CONFIG, CAMERA_CONFIG, FACE_DETECTION, EFFECTS_CONFIG
from utils.logger import setup_logger
from utils.validators import validate_file, validate_resolution, validate_fps

logger = setup_logger(__name__, LOGGING_CONFIG)


class VirtualCameraApp:
    """虚拟摄像头应用"""

    def __init__(self, width: int = None, height: int = None, fps: int = None):
        self.width = width or CAMERA_CONFIG['width']
        self.height = height or CAMERA_CONFIG['height']
        self.fps = fps or CAMERA_CONFIG['fps']
        
        self.camera_manager = None
        self.video_loader = None
        self.image_loader = None
        self.face_detector = None
        self.effect_processor = None
        
        self.is_running = False
        self.processing_thread = None
        
        self._init_components()

    def _init_components(self) -> bool:
        try:
            logger.info("Initializing components...")
            self.camera_manager = CameraManager(self.width, self.height, self.fps)
            self.face_detector = FaceDetector()
            self.effect_processor = EffectProcessor()
            logger.info("Components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False

    def load_video(self, video_path: str) -> bool:
        is_valid, error, file_type = validate_file(video_path)
        if not is_valid:
            logger.error(f"Invalid file: {error}")
            return False
        if file_type != 'video':
            logger.error("File is not a video")
            return False
        self.video_loader = VideoLoader(video_path)
        return self.video_loader.is_loaded

    def load_image(self, image_path: str) -> bool:
        is_valid, error, file_type = validate_file(image_path)
        if not is_valid:
            logger.error(f"Invalid file: {error}")
            return False
        if file_type != 'image':
            logger.error("File is not an image")
            return False
        self.image_loader = ImageLoader(image_path)
        return self.image_loader.is_loaded

    def _processing_loop(self):
        frame_time = 1.0 / self.fps
        while self.is_running:
            start_time = time.time()
            try:
                frame = None
                if self.video_loader and self.video_loader.is_loaded:
                    frame = self.video_loader.get_next_frame()
                elif self.image_loader and self.image_loader.is_loaded:
                    frame = self.image_loader.get_image()
                
                if frame is None:
                    logger.warning("No frame available")
                    time.sleep(0.1)
                    continue
                
                if self.effect_processor and self.effect_processor.is_enabled():
                    frame = self.effect_processor.apply_effect(frame)
                
                if self.face_detector and self.face_detector.is_enabled():
                    frame, faces = self.face_detector.detect_and_draw(frame)
                
                self.camera_manager.send_frame(frame)
                
                elapsed = time.time() - start_time
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(0.1)

    def start(self) -> bool:
        try:
            if not self.camera_manager.start():
                logger.error("Failed to start camera manager")
                return False
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            logger.info("Virtual Camera App started")
            return True
        except Exception as e:
            logger.error(f"Failed to start app: {e}")
            return False

    def stop(self) -> bool:
        try:
            self.is_running = False
            if self.processing_thread:
                self.processing_thread.join(timeout=2)
            if self.camera_manager:
                self.camera_manager.stop()
            if self.video_loader:
                self.video_loader.release()
            if self.image_loader:
                self.image_loader.release()
            logger.info("Virtual Camera App stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop app: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Virtual Camera Live System')
    parser.add_argument('--video', type=str, help='Video file path')
    parser.add_argument('--image', type=str, help='Image file path')
    parser.add_argument('--width', type=int, default=CAMERA_CONFIG['width'])
    parser.add_argument('--height', type=int, default=CAMERA_CONFIG['height'])
    parser.add_argument('--fps', type=int, default=CAMERA_CONFIG['fps'])
    parser.add_argument('--effect', type=str, default='none')
    parser.add_argument('--enable-face-detection', action='store_true')
    parser.add_argument('--disable-effects', action='store_true')
    parser.add_argument('--web', action='store_true')
    
    args = parser.parse_args()
    
    is_valid, error = validate_resolution(args.width, args.height)
    if not is_valid:
        logger.error(f"Invalid resolution: {error}")
        return 1
    
    is_valid, error = validate_fps(args.fps)
    if not is_valid:
        logger.error(f"Invalid FPS: {error}")
        return 1
    
    app = VirtualCameraApp(args.width, args.height, args.fps)
    
    if args.video:
        logger.info(f"Loading video: {args.video}")
        if not app.load_video(args.video):
            logger.error("Failed to load video")
            return 1
    elif args.image:
        logger.info(f"Loading image: {args.image}")
        if not app.load_image(args.image):
            logger.error("Failed to load image")
            return 1
    
    if args.enable_face_detection and app.face_detector:
        app.face_detector.enable()
    
    if args.disable_effects and app.effect_processor:
        app.effect_processor.disable()
    elif args.effect and app.effect_processor:
        app.effect_processor.set_current_effect(args.effect)
    
    if not app.start():
        logger.error("Failed to start application")
        return 1
    
    if args.web:
        try:
            from web.app import create_app
            web_app = create_app(app)
            logger.info("Starting web interface on http://localhost:5000")
            web_app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e:
            logger.error(f"Failed to start web interface: {e}")
    else:
        try:
            logger.info("Virtual Camera App is running. Press Ctrl+C to stop...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            app.stop()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
