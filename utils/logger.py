"""
日志管理 - Logger Setup
"""

import logging
import logging.handlers
from pathlib import Path
from config import LOGGING_CONFIG


def setup_logger(name: str, config: dict) -> logging.Logger:
    """
    设��日志记录器
    
    Args:
        name: 记录器名称
        config: 日志配置字典
        
    Returns:
        logging.Logger: 配置好的记录器
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger
    
    log_level = getattr(logging, config.get('level', 'INFO'))
    logger.setLevel(log_level)
    
    formatter = logging.Formatter(config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    log_file = config.get('file')
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.get('max_bytes', 10 * 1024 * 1024),
            backupCount=config.get('backup_count', 5)
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger
