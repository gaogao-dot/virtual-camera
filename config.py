"""
配置文件 - Virtual Camera System Configuration
"""

import os
from pathlib import Path

# ==================== 基础配置 ====================
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = DATA_DIR / 'uploads'

# 创建必要的目录
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== 虚拟摄像头配置 ====================
CAMERA_CONFIG = {
    'width': 1280,              # 输出宽度（像素）
    'height': 720,              # 输出高度（像素）
    'fps': 30,                  # 输出帧率
    'fourcc': 'I420',           # 编码格式
}

# ==================== 视频加载配置 ====================
VIDEO_CONFIG = {
    'supported_formats': ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'],
    'max_file_size': 500 * 1024 * 1024,  # 500MB
    'auto_resize': True,         # 自动调整分辨率
    'loop_video': True,          # 循环播放
    'buffer_size': 30,           # 缓冲帧数
}

# ==================== 图片加载配置 ====================
IMAGE_CONFIG = {
    'supported_formats': ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'],
    'max_file_size': 50 * 1024 * 1024,   # 50MB
    'display_duration': 5,       # 显示时长（秒）
    'transition_effect': 'fade', # 过渡效果
}

# ==================== 人脸检测配置 ====================
FACE_DETECTION = {
    'enabled': True,             # 是否启用人脸检测
    'cascade_file': 'haarcascade_frontalface_default.xml',
    'scale_factor': 1.1,         # 图像金字塔缩放因子
    'min_neighbors': 5,          # 相邻矩形的最小数量
    'min_face_size': (20, 20),   # 最小人脸尺寸
    'max_face_size': (500, 500), # 最大人脸尺寸
    'draw_rectangle': True,      # 是否绘制矩形
    'rectangle_color': (0, 255, 0),    # 矩形颜色 (BGR)
    'rectangle_thickness': 2,    # 矩形厚度
    'draw_info': True,           # 是否显示人脸信息
    'frame_skip': 0,             # 跳帧数（提高性能）
}

# ==================== 效果处理配置 ====================
EFFECTS_CONFIG = {
    'enabled': True,
    'default_effect': 'none',    # 默认效果
    'blur': {
        'kernel_size': 21,       # 模糊核大小（必须为奇数）
    },
    'cartoon': {
        'd': 9,                  # 直径
        'sigma_color': 9,        # 颜色空间高斯函数标准差
        'sigma_space': 7,        # 坐标空间高斯函数标准差
    },
    'beauty': {
        'blur_strength': 15,     # 美颜强度
        'brightness': 1.1,       # 亮度
        'contrast': 1.2,         # 对比度
    },
    'bilateral': {
        'd': 9,
        'sigma_color': 75,
        'sigma_space': 75,
    },
}

# ==================== 推流配置 ====================
STREAMING_CONFIG = {
    'enabled': False,            # 是否启用推流
    'protocol': 'rtmp',          # 推流协议 (rtmp, http, udp)
    'server': 'rtmp://localhost/live',
    'stream_key': 'stream',
    'bitrate': '2500k',          # 比特率
    'preset': 'medium',          # 编码预设 (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
    'reconnect_attempts': 5,     # 重连次数
    'reconnect_interval': 5,     # 重连间隔（秒）
}

# ==================== Web 应用配置 ====================
WEB_CONFIG = {
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'threaded': True,
    'max_content_length': 500 * 1024 * 1024,  # 500MB
}

# ==================== 日志配置 ====================
LOGGING_CONFIG = {
    'level': 'INFO',             # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOG_DIR / 'app.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,           # 备份文件数
}

# ==================== 允许的文件类型 ====================
ALLOWED_EXTENSIONS = (
    VIDEO_CONFIG['supported_formats'] +
    IMAGE_CONFIG['supported_formats']
)

# ==================== 开发环境 ====================
DEBUG = False
ENV = os.getenv('ENV', 'development')  # development, production

# ==================== 安全配置 ====================
SECURITY = {
    'enable_auth': False,        # 是否启用身份验证
    'api_key_required': False,   # 是否需要 API 密钥
    'allowed_ips': [],           # 允许的 IP 地址（空表示允许所有）
    'cors_enabled': True,        # 是否启用 CORS
}
