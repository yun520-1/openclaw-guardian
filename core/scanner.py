"""
OpenClaw Guardian - 漏洞扫描模块
"""
import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from utils.logger import logger
from utils.config import Config

class Scanner:
    """安全扫描类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.workspace = Path(config.get('paths', 'workspace'))
    
    def scan_skills(self) -> Dict:
        """扫描技能文件"""
        result = {
            'total_skills': 0,
            'syntax_errors': [],
            'missing_files': [],
            'suspicious_code': [],
        }
        
        skills_dir = self.workspace / 'skills'
        if not skills_dir.exists():
            return result
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            result['total_skills'] += 1
            skill_md = skill_dir / 'SKILL.md'
            
            # 检查 SKILL.md 是否存在
            if not skill_md.exists():
                result['missing_files'].append(str(skill_md))
                continue
            
            # 检查 YAML 格式
            try:
                content = skill_md.read_text(encoding='utf-8')
                # 尝试解析 YAML 部分（如果有）
                if '```yaml' in content:
                    yaml_blocks = re.findall(r'```yaml\n(.*?)\n```', content, re.DOTALL)
                    for block in yaml_blocks:
                        try:
                            yaml.safe_load(block)
                        except yaml.YAMLError as e:
                            result['syntax_errors'].append({
                                'file': str(skill_md),
                                'error': str(e)[:200]
                            })
            except Exception as e:
                result['syntax_errors'].append({
                    'file': str(skill_md),
                    'error': str(e)[:200]
                })
            
            # 检查可疑代码（简单的注入检测）
            try:
                py_files = list(skill_dir.glob('*.py'))
                for py_file in py_files:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    
                    # 检测 eval/exec 使用
                    if re.search(r'\beval\s*\(', content) or re.search(r'\bexec\s*\(', content):
                        result['suspicious_code'].append({
                            'file': str(py_file),
                            'issue': '使用 eval/exec，可能存在代码注入风险'
                        })
                    
                    # 检测硬编码的 URL
                    if re.search(r'https?://[^\s\'"]+', content):
                        # 这只是一个警告，不一定是问题
                        pass
            except Exception as e:
                logger.debug(f"扫描技能文件失败：{e}")
        
        return result
    
    def scan_configs(self) -> Dict:
        """扫描配置文件"""
        result = {
            'configs_checked': 0,
            'syntax_errors': [],
            'invalid_values': [],
        }
        
        config_files = [
            self.workspace / 'openclaw.json',
            self.workspace / 'openclaw-guardian' / 'config' / 'guardian.yaml',
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                continue
            
            result['configs_checked'] += 1
            
            try:
                if config_file.suffix == '.json':
                    with open(config_file, 'r', encoding='utf-8') as f:
                        json.load(f)
                elif config_file.suffix in ['.yaml', '.yml']:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        yaml.safe_load(f)
            except (json.JSONDecodeError, yaml.YAMLError) as e:
                result['syntax_errors'].append({
                    'file': str(config_file),
                    'error': str(e)[:200]
                })
        
        return result
    
    def scan_sensitive_data(self) -> Dict:
        """扫描敏感数据泄露"""
        result = {
            'exposed_keys': [],
            'exposed_passwords': [],
            'exposed_tokens': [],
        }
        
        # 定义敏感模式
        patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}["\']?',
            'token': r'(?i)(token|secret|auth)\s*[=:]\s*["\']?[a-zA-Z0-9]{20,}["\']?',
            'private_key': r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----',
        }
        
        # 扫描工作区文件（排除已知安全文件）
        exclude_dirs = {'__pycache__', '.git', 'node_modules', 'cache', 'logs', 'venv', 'site-packages', 'pip'}
        exclude_paths = {'temp'}  # 排除临时文件目录
        
        for file_path in self.workspace.rglob('*'):
            if not file_path.is_file():
                continue
            
            # 跳过排除目录
            if any(exclude in str(file_path) for exclude in exclude_dirs):
                continue
            
            # 跳过排除路径
            if any(exclude in str(file_path) for exclude in exclude_paths):
                continue
            
            # 跳过二进制文件和大文件
            try:
                if file_path.stat().st_size > 1024 * 1024:  # 1MB
                    continue
            except:
                continue
            
            # 只扫描文本文件
            if file_path.suffix not in ['.py', '.js', '.json', '.yaml', '.yml', '.md', '.txt', '.env', '.sh']:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        result[f'exposed_{pattern_name.split("_")[0]}s'].append({
                            'file': str(file_path),
                            'pattern': pattern_name,
                            'count': len(matches)
                        })
            except Exception:
                continue
        
        return result
    
    def run_full_scan(self) -> Dict:
        """执行完整扫描"""
        logger.info("开始执行安全扫描...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'skills': self.scan_skills(),
            'configs': self.scan_configs(),
            'sensitive_data': self.scan_sensitive_data(),
        }
        
        # 评估风险等级
        risk_level = 'low'
        issues_count = (
            len(results['skills']['syntax_errors']) +
            len(results['configs']['syntax_errors']) +
            len(results['sensitive_data']['exposed_keys']) +
            len(results['sensitive_data']['exposed_passwords']) +
            len(results['sensitive_data']['exposed_tokens'])
        )
        
        if issues_count > 10:
            risk_level = 'high'
        elif issues_count > 3:
            risk_level = 'medium'
        elif issues_count > 0:
            risk_level = 'low'
        
        results['risk_level'] = risk_level
        results['total_issues'] = issues_count
        
        logger.info(f"扫描完成，风险等级：{risk_level}, 发现 {issues_count} 个问题")
        return results
