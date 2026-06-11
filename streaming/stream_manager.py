"""
推流管理 - Stream Manager
处理 RTMP、HTTP 等直播推流
"""

import logging
import subprocess
import threading
import time
import queue
from typing import Optional
import numpy as np

from config import STREAMING_CONFIG, LOGGING_CONFIG
from utils.logger import setup_logger

logger = setup_logger(__name__, LOGGING_CONFIG)


class StreamManager:
    """推流管理器"""

    def __init__(self, stream_url: str = None, bitrate: str = None):
        self.stream_url = stream_url or STREAMING_CONFIG['server']
        self.bitrate = bitrate or STREAMING_CONFIG['bitrate']
        self.process = None
        self.is_streaming = False
        self.frame_queue = queue.Queue(maxsize=30)
        self.streaming_thread = None
        logger.info(f"StreamManager initialized: {self.stream_url}")

    def start(self, width: int, height: int, fps: int) -> bool:
        try:
            cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pixel_format', 'bgr24',
                   '-video_size', f'{width}x{height}', '-framerate', str(fps),
                   '-i', '-', '-c:v', 'libx264', '-preset', STREAMING_CONFIG['preset'],
                   '-b:v', self.bitrate, '-f', 'flv', self.stream_url]
            
            self.process = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
            self.is_streaming = True
            self.streaming_thread = threading.Thread(target=self._streaming_loop, daemon=True)
            self.streaming_thread.start()
            logger.info(f"Streaming started: {self.stream_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to start streaming: {e}")
            self.is_streaming = False
            return False

    def _streaming_loop(self):
        while self.is_streaming:
            try:
                frame = self.frame_queue.get(timeout=2)
                if frame is None:
                    break
                self.process.stdin.write(frame.tobytes())
            except queue.Empty:
                continue
            except BrokenPipeError:
                logger.warning("Streaming pipe broken")
                break
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                break

    def push_frame(self, frame: np.ndarray) -> bool:
        if not self.is_streaming:
            return False
        try:
            self.frame_queue.put_nowait(frame)
            return True
        except queue.Full:
            logger.warning("Frame queue full, dropping frame")
            return False
        except Exception as e:
            logger.error(f"Failed to push frame: {e}")
            return False

    def stop(self) -> bool:
        try:
            self.is_streaming = False
            if self.process:
                self.process.stdin.close()
                self.process.wait(timeout=5)
            if self.streaming_thread:
                self.streaming_thread.join(timeout=2)
            logger.info("Streaming stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop streaming: {e}")
            return False
