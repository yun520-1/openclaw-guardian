"""
OpenClaw Guardian - 自动修复模块
"""
import os
import re
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from utils.logger import logger
from utils.config import Config

class Healer:
    """自动修复类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.workspace = Path(config.get('paths', 'workspace'))
        self.backup_dir = Path(config.get('paths', 'backups'))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, file_path: Path, reason: str = 'manual') -> Optional[Path]:
        """创建文件备份"""
        if not file_path.exists():
            return None
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            logger.success(f"创建备份：{file_path.name} -> {backup_name} (原因：{reason})")
            
            self._cleanup_old_backups(file_path.stem)
            return backup_path
        except Exception as e:
            logger.error(f"创建备份失败：{e}")
            return None
    
    def _cleanup_old_backups(self, file_stem: str):
        """清理旧备份"""
        max_backups = self.config.get('healing', 'max_backups', default=10)
        try:
            backups = sorted(
                self.backup_dir.glob(f'{file_stem}_*'),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            for old_backup in backups[max_backups:]:
                old_backup.unlink()
                logger.debug(f"清理旧备份：{old_backup.name}")
        except Exception as e:
            logger.debug(f"清理备份失败：{e}")
    
    def restore_backup(self, file_path: Path, backup_path: Optional[Path] = None) -> bool:
        """恢复备份"""
        try:
            if backup_path is None:
                file_stem = file_path.stem
                backups = sorted(
                    self.backup_dir.glob(f'{file_stem}_*'),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if not backups:
                    logger.error(f"未找到备份文件：{file_path.name}")
                    return False
                backup_path = backups[0]
            
            shutil.copy2(backup_path, file_path)
            logger.success(f"恢复备份：{backup_path.name} -> {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"恢复备份失败：{e}")
            return False
    
    def fix_config_syntax(self, file_path: Path) -> Dict:
        """尝试修复配置文件语法错误"""
        result = {
            'success': False,
            'message': '',
            'backup_created': False,
        }
        
        if not file_path.exists():
            result['message'] = '文件不存在'
            return result
        
        try:
            backup_path = self.create_backup(file_path, reason='syntax_fix')
            if backup_path:
                result['backup_created'] = True
            
            content = file_path.read_text(encoding='utf-8')
            
            if file_path.suffix == '.json':
                import json
                try:
                    json.loads(content)
                    result['success'] = True
                    result['message'] = 'JSON 格式正确，无需修复'
                    return result
                except json.JSONDecodeError as e:
                    fixed_content = re.sub(r',(\s*[}\]])', r'\1', content)
                    try:
                        json.loads(fixed_content)
                        file_path.write_text(fixed_content, encoding='utf-8')
                        result['success'] = True
                        result['message'] = '已修复 JSON 格式错误（移除末尾逗号）'
                        return result
                    except:
                        if backup_path:
                            self.restore_backup(file_path, backup_path)
                        result['message'] = f'无法自动修复 JSON 错误：{str(e)[:100]}'
            
            elif file_path.suffix in ['.yaml', '.yml']:
                import yaml
                try:
                    yaml.safe_load(content)
                    result['success'] = True
                    result['message'] = 'YAML 格式正确，无需修复'
                    return result
                except yaml.YAMLError as e:
                    result['message'] = f'YAML 语法错误，需要手动修复：{str(e)[:100]}'
            
            return result
        except Exception as e:
            result['message'] = f'修复失败：{str(e)}'
            return result
    
    def restart_openclaw(self) -> Dict:
        """重启 OpenClaw 服务"""
        result = {
            'success': False,
            'message': '',
            'pid': None,
        }
        
        try:
            import psutil
            openclaw_proc = None
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []) or [])
                    if 'openclaw' in cmdline.lower():
                        openclaw_proc = proc
                        break
                except:
                    continue
            
            if openclaw_proc:
                openclaw_proc.terminate()
                try:
                    openclaw_proc.wait(timeout=10)
                except:
                    openclaw_proc.kill()
                logger.info(f"已停止 OpenClaw 进程：PID={openclaw_proc.pid}")
            
            restart_commands = [
                ['openclaw', 'gateway', 'restart'],
                ['npm', 'run', 'openclaw:restart'],
            ]
            
            for cmd in restart_commands:
                try:
                    subprocess.run(cmd, check=True, capture_output=True, timeout=30)
                    result['success'] = True
                    result['message'] = 'OpenClaw 重启成功'
                    logger.success('OpenClaw 重启成功')
                    return result
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            
            result['message'] = '尝试了所有重启命令，但未成功'
            return result
            
        except Exception as e:
            result['message'] = f'重启失败：{str(e)}'
            logger.error(result['message'])
            return result
    
    def cleanup_logs(self, max_age_days: int = 7, max_size_mb: int = 100) -> Dict:
        """清理日志文件"""
        result = {
            'deleted_files': [],
            'freed_space': 0,
        }
        
        log_dir = Path('/tmp/openclaw')
        if not log_dir.exists():
            return result
        
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_days * 86400)
            
            for log_file in log_dir.glob('openclaw-*.log'):
                try:
                    stat = log_file.stat()
                    
                    if stat.st_mtime < cutoff_time:
                        size = stat.st_size
                        log_file.unlink()
                        result['deleted_files'].append(str(log_file))
                        result['freed_space'] += size
                        logger.debug(f"删除旧日志：{log_file.name}")
                    
                    elif stat.st_size > max_size_mb * 1024 * 1024:
                        size = stat.st_size
                        log_file.unlink()
                        result['deleted_files'].append(str(log_file))
                        result['freed_space'] += size
                        logger.debug(f"删除大日志：{log_file.name} ({size/1024/1024:.1f}MB)")
                except Exception as e:
                    logger.debug(f"处理日志文件失败：{e}")
            
            if result['freed_space'] > 0:
                logger.success(f"清理日志完成，释放空间：{result['freed_space']/1024/1024:.1f}MB")
            
            return result
        except Exception as e:
            logger.error(f"清理日志失败：{e}")
            return result
    
    def apply_healing(self, issues: List[Dict]) -> Dict:
        """根据问题列表应用修复"""
        results = {
            'attempted': 0,
            'successful': 0,
            'failed': 0,
            'details': [],
        }
        
        for issue in issues:
            results['attempted'] += 1
            
            if issue.get('type') == 'config_syntax':
                file_path = Path(issue['file'])
                fix_result = self.fix_config_syntax(file_path)
                results['details'].append(fix_result)
                if fix_result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            
            elif issue.get('type') == 'process_stopped':
                restart_result = self.restart_openclaw()
                results['details'].append(restart_result)
                if restart_result['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            
            elif issue.get('type') == 'logs_full':
                cleanup_result = self.cleanup_logs()
                results['details'].append(cleanup_result)
                results['successful'] += 1
        
        return results
