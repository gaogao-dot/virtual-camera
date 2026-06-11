# 虚拟摄像头直播系统 (Virtual Camera Live System)

一个基于 Windows 的虚拟摄像头软件，支持视频/图片加载、人脸检测、实时效果处理和直播推流。

## 功能特性

✨ **核心功能**
- 🎥 支持本地视频文件加载（MP4, AVI, MOV 等）
- 🖼️ 支持图片文件加载（JPG, PNG, BMP 等）
- 😊 实时人脸检测和标注
- 🎨 多种实时效果处理（模糊、灰度、美颜等）
- 📡 虚拟摄像头输出到系统（支持 Zoom, Teams, OBS 等）
- 🔴 直播推流支持
- 🎛️ Web 控制面板

## 系统要求

- **操作系统**: Windows 7/10/11（64位）
- **Python**: 3.8+
- **内存**: 最少 2GB
- **摄像头驱动**: VirtualCam 驱动已集成

## 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 安装虚拟摄像头驱动
```bash
python setup_driver.py
```

### 3. 启动应用
```bash
python main.py
```

应用启动后会在 `http://localhost:5000` 提供 Web 界面。

## 使用说明

### 命令行使用
```bash
# 加载视频文件
python main.py --video input_video.mp4 --effect blur

# 加载图片
python main.py --image input_image.jpg --enable-face-detection

# 推流直播（RTMP）
python main.py --video input.mp4 --stream rtmp://your-server/live/stream

# 指定输出分辨率和帧率
python main.py --video input.mp4 --width 1280 --height 720 --fps 30

# 启用 Web 界面
python main.py --web
```

### Web 界面功能
- 📁 上传视频/图片文件
- 🎛️ 调整实时效果参数
- 😊 启用/禁用人脸检测
- 📊 实时性能监控
- 🔴 推流配置

## 效果类型

| 效果 | 说明 |
|------|------|
| `none` | 无效果 |
| `blur` | 模糊处理 |
| `grayscale` | 灰度处理 |
| `cartoon` | 卡通效果 |
| `beauty` | 美颜效果 |
| `edge` | 边缘检测 |
| `bilateral` | 双边滤波 |
| `vignette` | 晕影效果 |
| `sepia` | 棕褐色效果 |

## 项目结构

```
virtual-camera/
├── main.py                 # 主程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── setup_driver.py        # 驱动安装脚本
├── README.md              # 项目说明
│
├── core/
│   ├── __init__.py
│   ├── camera_manager.py  # 虚拟摄像头管理
│   ├── face_detector.py   # 人脸检测模块
│   ├── effect_processor.py # 效果处理模块
│   └── video_loader.py    # 视频/图片加载
│
├── streaming/
│   ├── __init__.py
│   ├── stream_manager.py  # 推流管理
│
├── web/
│   ├── __init__.py
│   ├── app.py             # Flask 应用
│   ├── routes.py          # 路由定义
│
└── utils/
    ├── __init__.py
    ├── logger.py          # 日志管理
    └── validators.py      # 数据验证
```

## 许可证

MIT License
