"""
OpenClaw Guardian - 监控模块
"""
import psutil
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from utils.logger import logger
from utils.config import Config

class Monitor:
    """系统监控类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.openclaw_process = None
        self._find_openclaw_process()
    
    def _find_openclaw_process(self):
        """查找 OpenClaw 进程"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info.get('cmdline', []) or [])
                if 'openclaw' in cmdline.lower() or 'jvs' in cmdline.lower():
                    self.openclaw_process = proc
                    logger.info(f"找到 OpenClaw 进程：PID={proc.info['pid']}")
                    return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.warning("未找到运行中的 OpenClaw 进程")
    
    def check_process(self) -> Dict:
        """检查 OpenClaw 进程状态"""
        result = {
            'status': 'unknown',
            'pid': None,
            'cpu_percent': 0,
            'memory_percent': 0,
            'running_time': None,
        }
        
        if self.openclaw_process and self.openclaw_process.is_running():
            try:
                result['status'] = 'running'
                result['pid'] = self.openclaw_process.pid
                result['cpu_percent'] = self.openclaw_process.cpu_percent(interval=0.1)
                result['memory_percent'] = self.openclaw_process.memory_percent()
                
                create_time = datetime.fromtimestamp(self.openclaw_process.create_time())
                result['running_time'] = str(datetime.now() - create_time)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                result['status'] = 'error'
                self.openclaw_process = None
                self._find_openclaw_process()
        else:
            result['status'] = 'stopped'
            self.openclaw_process = None
            self._find_openclaw_process()
        
        return result
    
    def check_resources(self) -> Dict:
        """检查系统资源使用"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_total': psutil.virtual_memory().total,
            'memory_used': psutil.virtual_memory().used,
            'memory_percent': psutil.virtual_memory().percent,
            'disk_total': psutil.disk_usage('/').total,
            'disk_used': psutil.disk_usage('/').used,
            'disk_percent': psutil.disk_usage('/').percent,
        }
    
    def check_logs(self) -> Dict:
        """检查日志文件异常"""
        log_dir = Path('/tmp/openclaw')
        result = {
            'log_files': [],
            'errors_found': [],
            'warnings_count': 0,
            'errors_count': 0,
        }
        
        if not log_dir.exists():
            return result
        
        try:
            log_files = list(log_dir.glob('openclaw-*.log'))
            for log_file in log_files[-5:]:  # 只检查最近 5 个日志文件
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[-100:]  # 只检查最后 100 行
                        for line in lines:
                            if 'ERROR' in line or 'CRITICAL' in line:
                                result['errors_found'].append({
                                    'file': str(log_file),
                                    'line': line.strip()[:200]
                                })
                                result['errors_count'] += 1
                            elif 'WARNING' in line:
                                result['warnings_count'] += 1
                except Exception as e:
                    logger.debug(f"读取日志文件失败：{e}")
        except Exception as e:
            logger.debug(f"检查日志失败：{e}")
        
        return result
    
    def check_files(self) -> Dict:
        """检查关键文件完整性"""
        workspace = Path.home() / '.jvs' / '.openclaw' / 'workspace'
        result = {
            'critical_files': [],
            'missing_files': [],
            'modified_files': [],
        }
        
        critical_files = [
            workspace / 'MEMORY.md',
            workspace / 'AGENTS.md',
            workspace / 'SOUL.md',
            workspace / 'openclaw.json',
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                stat = file_path.stat()
                result['critical_files'].append({
                    'path': str(file_path),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
            else:
                result['missing_files'].append(str(file_path))
        
        return result
    
    def run_full_check(self) -> Dict:
        """执行完整检查"""
        logger.info("开始执行系统检查...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'process': self.check_process(),
            'resources': self.check_resources(),
            'logs': self.check_logs(),
            'files': self.check_files(),
        }
        
        # 评估状态
        issues = []
        if results['process']['status'] != 'running':
            issues.append({
                'level': 'critical',
                'message': 'OpenClaw 进程未运行'
            })
        
        if results['resources']['memory_percent'] > 90:
            issues.append({
                'level': 'warning',
                'message': f"内存使用率过高：{results['resources']['memory_percent']}%"
            })
        
        if results['resources']['disk_percent'] > 90:
            issues.append({
                'level': 'warning',
                'message': f"磁盘使用率过高：{results['resources']['disk_percent']}%"
            })
        
        if results['logs']['errors_count'] > 0:
            issues.append({
                'level': 'warning',
                'message': f"发现 {results['logs']['errors_count']} 个错误日志"
            })
        
        results['issues'] = issues
        results['status'] = 'critical' if any(i['level'] == 'critical' for i in issues) else ('warning' if issues else 'ok')
        
        logger.info(f"检查完成，状态：{results['status']}, 发现 {len(issues)} 个问题")
        return results
