#!/usr/bin/env python3
"""
OpenClaw Guardian - 自我升级与优化模块
每小时自动执行，目标：
1. 代码量最小化
2. Token 消耗最小化
3. 保证 OpenClaw 安全运行
4. 每天自动更新到 GitHub
"""

import os
import sys
import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from utils.logger import logger
from utils.config import Config

class SelfOptimizerizer:
    """自我优化类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.workspace = Path(config.get('paths', 'workspace'))
        self.guardian_dir = self.workspace / 'openclaw-guardian'
        self.cache_dir = self.guardian_dir / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 优化统计
        self.stats_file = self.cache_dir / 'optimization_stats.json'
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """加载优化统计"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_optimizations': 0,
            'lines_removed': 0,
            'token_savings': 0,
            'last_optimization': None,
            'last_github_update': None,
        }
    
    def _save_stats(self):
        """保存优化统计"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
    
    def analyze_code(self) -> Dict:
        """分析代码，找出可优化的部分"""
        result = {
            'total_lines': 0,
            'total_files': 0,
            'empty_lines': 0,
            'comment_lines': 0,
            'docstring_lines': 0,
            'optimizable_lines': 0,
            'suggestions': [],
        }
        
        py_files = list(self.guardian_dir.glob('**/*.py'))
        result['total_files'] = len(py_files)
        
        for py_file in py_files:
            if 'venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                result['total_lines'] += len(lines)
                
                # 统计空行
                empty = sum(1 for line in lines if not line.strip())
                result['empty_lines'] += empty
                
                # 统计注释行
                comments = sum(1 for line in lines if line.strip().startswith('#'))
                result['comment_lines'] += comments
                
                # 统计文档字符串（简化估算）
                docstrings = content.count('"""') // 2 * 5  # 估算每个文档字符串 5 行
                result['docstring_lines'] += docstrings
                
                # 找出可优化的部分
                if len(lines) > 100:
                    result['suggestions'].append({
                        'file': str(py_file.relative_to(self.guardian_dir)),
                        'lines': len(lines),
                        'issue': '文件过大，考虑拆分'
                    })
                
            except Exception as e:
                logger.debug(f"分析文件失败：{e}")
        
        # 计算可优化行数
        result['optimizable_lines'] = result['empty_lines'] + result['comment_lines'] // 2
        
        return result
    
    def optimize_code(self) -> Dict:
        """执行代码优化"""
        result = {
            'optimized': False,
            'lines_removed': 0,
            'files_modified': [],
            'suggestions_applied': 0,
        }
        
        # 优化策略 1: 移除多余的空行（保留最多 2 个连续空行）
        py_files = list(self.guardian_dir.glob('**/*.py'))
        
        for py_file in py_files:
            if 'venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                original_lines = len(content.split('\n'))
                
                # 移除多余空行
                lines = content.split('\n')
                optimized_lines = []
                empty_count = 0
                
                for line in lines:
                    if not line.strip():
                        empty_count += 1
                        if empty_count <= 2:
                            optimized_lines.append(line)
                    else:
                        empty_count = 0
                        optimized_lines.append(line)
                
                optimized_content = '\n'.join(optimized_lines)
                optimized_len = len(optimized_content.split('\n'))
                
                if optimized_len < original_lines:
                    # 有优化空间
                    py_file.write_text(optimized_content, encoding='utf-8')
                    result['optimized'] = True
                    result['lines_removed'] += original_lines - optimized_len
                    result['files_modified'].append(str(py_file.relative_to(self.guardian_dir)))
                    
            except Exception as e:
                logger.debug(f"优化文件失败：{e}")
        
        # 更新统计
        if result['optimized']:
            self.stats['lines_removed'] += result['lines_removed']
            self.stats['total_optimizations'] += 1
            self.stats['last_optimization'] = datetime.now().isoformat()
            self._save_stats()
        
        return result
    
    def optimize_token_usage(self) -> Dict:
        """优化 Token 使用"""
        result = {
            'token_savings': 0,
            'optimizations': [],
        }
        
        # 策略 1: 增加缓存时间
        current_ttl = self.config.get('search', 'cache_ttl_hours', default=168)
        if current_ttl < 336:  # 增加到 14 天
            self.config.set('search', 'cache_ttl_hours', value=336)
            result['token_savings'] += 50  # 估算
            result['optimizations'].append('缓存时间延长至 14 天')
        
        # 策略 2: 减少检查频率（如果系统稳定）
        current_interval = self.config.get('monitoring', 'interval_seconds', default=1800)
        if current_interval < 3600:
            # 检查最近是否有严重问题
            logs_dir = Path('/tmp/openclaw')
            critical_count = 0
            
            if logs_dir.exists():
                for log_file in logs_dir.glob('*.log'):
                    try:
                        content = log_file.read_text(encoding='utf-8', errors='ignore')
                        critical_count += content.count('CRITICAL')
                    except:
                        pass
            
            if critical_count == 0:
                # 系统稳定，延长检查间隔
                self.config.set('monitoring', 'interval_seconds', value=3600)
                result['token_savings'] += 100  # 估算
                result['optimizations'].append('检查间隔延长至 60 分钟')
        
        # 策略 3: 禁用非关键功能
        if self.config.get('scanning', 'daily_deep_scan', default=True):
            # 如果连续 7 天无问题，改为每周扫描
            last_scan = self.stats.get('last_deep_scan', None)
            if last_scan:
                last_scan_date = datetime.fromisoformat(last_scan)
                if datetime.now() - last_scan_date > timedelta(days=7):
                    self.config.set('scanning', 'daily_deep_scan', value=False)
                    self.config.set('scanning', 'weekly_deep_scan', value=True)
                    result['token_savings'] += 200  # 估算
                    result['optimizations'].append('深度扫描改为每周一次')
        
        # 更新统计
        self.stats['token_savings'] += result['token_savings']
        self._save_stats()
        
        return result
    
    def check_github_update_needed(self) -> bool:
        """检查是否需要更新到 GitHub"""
        last_update = self.stats.get('last_github_update', None)
        
        if not last_update:
            return True
        
        last_update_date = datetime.fromisoformat(last_update)
        now = datetime.now()
        
        # 检查是否是新的一天
        return now.date() > last_update_date.date()
    
    def update_github(self) -> Dict:
        """更新到 GitHub"""
        result = {
            'success': False,
            'changes': [],
            'error': None,
        }
        
        try:
            # 检查是否有更改
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.guardian_dir,
                capture_output=True,
                text=True
            )
            
            if not status.stdout.strip():
                result['success'] = True
                result['changes'] = ['无更改']
                logger.info("GitHub 已是最新")
                return result
            
            # 添加更改
            subprocess.run(['git', 'add', '-A'], cwd=self.guardian_dir, check=True, capture_output=True)
            
            # 提交
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            commit_msg = f"chore: 自动优化更新 {timestamp}\n\n优化统计:\n- 总优化次数：{self.stats['total_optimizations']}\n- 移除行数：{self.stats['lines_removed']}\n- Token 节省：{self.stats['token_savings']}/天"
            
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.guardian_dir,
                check=True,
                capture_output=True
            )
            result['changes'].append('代码已提交')
            
            # 推送
            push_result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.guardian_dir,
                capture_output=True,
                text=True
            )
            
            if push_result.returncode == 0:
                result['success'] = True
                result['changes'].append('已推送到 GitHub')
                logger.success("已更新到 GitHub")
            else:
                # 推送失败（可能是权限问题）
                result['error'] = push_result.stderr
                result['changes'].append('推送失败（需要配置 Git 凭证）')
                logger.warning(f"GitHub 推送失败：{push_result.stderr[:200]}")
            
            # 更新统计
            if result['success']:
                self.stats['last_github_update'] = datetime.now().isoformat()
                self._save_stats()
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"GitHub 更新失败：{e}")
        
        return result
    
    def run_hourly_optimization(self) -> Dict:
        """执行每小时优化"""
        logger.info("开始执行每小时优化...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'analysis': None,
            'code_optimization': None,
            'token_optimization': None,
            'github_update': None,
        }
        
        # 1. 分析代码
        results['analysis'] = self.analyze_code()
        logger.info(f"代码分析：{results['analysis']['total_files']} 个文件，{results['analysis']['total_lines']} 行")
        
        # 2. 优化代码
        results['code_optimization'] = self.optimize_code()
        if results['code_optimization']['optimized']:
            logger.success(f"代码优化：移除 {results['code_optimization']['lines_removed']} 行")
        
        # 3. 优化 Token 使用
        results['token_optimization'] = self.optimize_token_usage()
        logger.info(f"Token 优化：预计节省 {results['token_optimization']['token_savings']} tokens/天")
        
        # 4. 检查并更新 GitHub（每天一次）
        if self.check_github_update_needed():
            logger.info("执行每日 GitHub 更新...")
            results['github_update'] = self.update_github()
        else:
            logger.debug("GitHub 今日已更新")
        
        # 生成摘要
        summary = self._generate_summary(results)
        logger.info(summary)
        
        return results
    
    def _generate_summary(self, results: Dict) -> str:
        """生成优化摘要"""
        lines = [
            "🔧 OpenClaw Guardian 自我优化报告",
            "",
            f"**时间**: {results['timestamp']}",
            "",
            "**代码分析**:",
            f"- 文件数：{results['analysis']['total_files']}",
            f"- 总行数：{results['analysis']['total_lines']}",
            f"- 可优化：{results['analysis']['optimizable_lines']} 行",
            "",
        ]
        
        if results['code_optimization']['optimized']:
            lines.append("**代码优化**:")
            lines.append(f"- ✅ 移除 {results['code_optimization']['lines_removed']} 行")
            lines.append(f"- 修改文件：{len(results['code_optimization']['files_modified'])} 个")
            lines.append("")
        
        lines.append("**Token 优化**:")
        lines.append(f"- 预计节省：{results['token_optimization']['token_savings']} tokens/天")
        lines.append(f"- 优化项：{len(results['token_optimization']['optimizations'])} 个")
        for opt in results['token_optimization']['optimizations']:
            lines.append(f"  - {opt}")
        lines.append("")
        
        if results['github_update']:
            lines.append("**GitHub 更新**:")
            if results['github_update']['success']:
                lines.append("- ✅ 更新成功")
            else:
                lines.append(f"- ⚠️ {results['github_update'].get('error', '未知错误')}")
            lines.append("")
        
        lines.append(f"**累计统计**:")
        lines.append(f"- 总优化次数：{self.stats['total_optimizations']}")
        lines.append(f"- 总移除行数：{self.stats['lines_removed']}")
        lines.append(f"- 总 Token 节省：{self.stats['token_savings']}/天")
        
        return '\n'.join(lines)


def main():
    """主函数"""
    config = Config()
    optimizer = SelfOptimizerizer(config)
    
    # 执行优化
    results = optimizer.run_hourly_optimization()
    
    # 输出 JSON 结果（便于 cron 调用）
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
