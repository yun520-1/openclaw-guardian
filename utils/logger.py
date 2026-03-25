"""
OpenClaw Guardian - 日志工具
"""
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

class GuardianLogger:
    """专用日志类"""
    
    def __init__(self, name: str = 'openclaw-guardian', log_dir: Optional[str] = None):
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else Path.home() / '.jvs' / '.openclaw' / 'workspace' / 'openclaw-guardian' / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建日志文件（按日期分割）
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.log_dir / f'guardian-{today}.log'
        
        # 配置日志
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加 handler
        if not self.logger.handlers:
            # 文件处理器
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # 控制台只显示警告及以上
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self.logger.error(msg)
    
    def critical(self, msg: str):
        self.logger.critical(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)
    
    def success(self, msg: str):
        """成功日志"""
        self.logger.info(f"✅ {msg}")
    
    def alert(self, msg: str, level: str = 'warning'):
        """警报日志"""
        icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}.get(level, '🟡')
        self.logger.warning(f"{icon} {msg}")

# 全局日志实例
logger = GuardianLogger()
