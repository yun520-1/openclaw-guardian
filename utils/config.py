"""
OpenClaw Guardian - 配置管理
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """配置管理类"""
    
    DEFAULT_CONFIG = {
        'monitoring': {
            'enabled': True,
            'interval_seconds': 1800,  # 30 分钟
            'check_processes': True,
            'check_resources': True,
            'check_logs': True,
            'check_files': True,
        },
        'scanning': {
            'enabled': True,
            'daily_deep_scan': True,
            'deep_scan_time': '03:00',  # 凌晨 3 点
            'scan_skills': True,
            'scan_configs': True,
            'scan_sensitive_data': True,
        },
        'healing': {
            'enabled': True,
            'auto_backup': True,
            'auto_restore': False,  # 默认不自动恢复，需要确认
            'max_backups': 10,
            'auto_restart': True,
        },
        'search': {
            'enabled': True,
            'cache_solutions': True,
            'cache_ttl_hours': 168,  # 7 天
        },
        'optimization': {
            'batch_non_critical': True,
            'batch_interval_minutes': 60,
            'summary_reports': True,
            'min_token_mode': True,
        },
        'paths': {
            'workspace': str(Path.home() / '.jvs' / '.openclaw' / 'workspace'),
            'logs': str(Path.home() / '.jvs' / '.openclaw' / 'workspace' / 'openclaw-guardian' / 'logs'),
            'cache': str(Path.home() / '.jvs' / '.openclaw' / 'workspace' / 'openclaw-guardian' / 'cache'),
            'backups': str(Path.home() / '.jvs' / '.openclaw' / 'workspace' / 'openclaw-guardian' / 'backups'),
        },
        'alerts': {
            'critical': True,  # 立即通知
            'warning': True,   # 批量通知
            'info': False,     # 仅记录
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._default_config_path()
        self.config = self._load_or_create()
    
    def _default_config_path(self) -> str:
        return str(Path.home() / '.jvs' / '.openclaw' / 'workspace' / 'openclaw-guardian' / 'config' / 'guardian.yaml')
    
    def _load_or_create(self) -> Dict[str, Any]:
        """加载配置或创建默认配置"""
        path = Path(self.config_path)
        
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    # 合并默认配置确保完整性
                    return self._merge_configs(self.DEFAULT_CONFIG, config)
            except Exception as e:
                print(f"配置文件加载失败，使用默认配置：{e}")
                self._save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG
        else:
            # 创建默认配置
            path.parent.mkdir(parents=True, exist_ok=True)
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """递归合并配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _save_config(self, config: Dict):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    def get(self, *keys, default=None):
        """获取配置值，支持多级键"""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, *keys, value):
        """设置配置值"""
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def __getitem__(self, key):
        return self.config[key]
    
    def __contains__(self, key):
        return key in self.config
