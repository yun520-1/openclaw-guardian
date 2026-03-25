"""
OpenClaw Guardian - Token 优化模块
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from utils.logger import logger
from utils.config import Config

class TokenOptimizer:
    """Token 消耗优化类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = Path(config.get('paths', 'cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 问题缓存
        self.solution_cache = self._load_solution_cache()
        
        # 批量处理队列
        self.batch_queue = []
        self.last_batch_time = datetime.now()
    
    def _load_solution_cache(self) -> Dict:
        """加载解决方案缓存"""
        cache_file = self.cache_dir / 'solution_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_solution_cache(self):
        """保存解决方案缓存"""
        cache_file = self.cache_dir / 'solution_cache.json'
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.solution_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"保存缓存失败：{e}")
    
    def _generate_cache_key(self, problem: str) -> str:
        """生成问题缓存键"""
        return hashlib.md5(problem.encode()).hexdigest()
    
    def get_cached_solution(self, problem: str) -> Optional[Dict]:
        """获取缓存的解决方案"""
        if not self.config.get('search', 'cache_solutions', default=True):
            return None
        
        cache_key = self._generate_cache_key(problem)
        
        if cache_key in self.solution_cache:
            cached = self.solution_cache[cache_key]
            cached_time = datetime.fromisoformat(cached['timestamp'])
            ttl_hours = self.config.get('search', 'cache_ttl_hours', default=168)
            
            # 检查是否过期
            if datetime.now() - cached_time < timedelta(hours=ttl_hours):
                logger.debug(f"使用缓存的解决方案：{problem[:50]}...")
                return cached['solution']
            else:
                # 删除过期缓存
                del self.solution_cache[cache_key]
                self._save_solution_cache()
        
        return None
    
    def cache_solution(self, problem: str, solution: Dict):
        """缓存解决方案"""
        if not self.config.get('search', 'cache_solutions', default=True):
            return
        
        cache_key = self._generate_cache_key(problem)
        self.solution_cache[cache_key] = {
            'problem': problem,
            'solution': solution,
            'timestamp': datetime.now().isoformat(),
            'use_count': 0,
        }
        self._save_solution_cache()
        logger.debug(f"缓存解决方案：{problem[:50]}...")
    
    def increment_cache_use(self, problem: str):
        """增加缓存使用计数"""
        cache_key = self._generate_cache_key(problem)
        if cache_key in self.solution_cache:
            self.solution_cache[cache_key]['use_count'] += 1
            self._save_solution_cache()
    
    def should_search(self, problem: str, level: str = 'warning') -> bool:
        """判断是否需要搜索（优化 token 使用）"""
        # 紧急问题总是搜索
        if level == 'critical':
            return True
        
        # 检查是否有缓存
        if self.get_cached_solution(problem):
            return False
        
        # 非紧急问题，检查批量处理设置
        if self.config.get('optimization', 'batch_non_critical', default=True):
            # 加入批量队列
            self.batch_queue.append({
                'problem': problem,
                'level': level,
                'time': datetime.now(),
            })
            return False
        
        return True
    
    def get_batch_queue(self) -> List[Dict]:
        """获取批量处理队列"""
        batch_interval = self.config.get('optimization', 'batch_interval_minutes', default=60)
        
        # 检查是否到达批量处理时间
        if datetime.now() - self.last_batch_time < timedelta(minutes=batch_interval):
            return []
        
        # 返回队列并重置
        batch = self.batch_queue.copy()
        self.batch_queue = []
        self.last_batch_time = datetime.now()
        
        return batch
    
    def create_summary_report(self, checks: List[Dict]) -> str:
        """创建摘要报告（减少 token 消耗）"""
        if not checks:
            return "无检查记录"
        
        # 统计信息
        total_checks = len(checks)
        critical_count = sum(1 for c in checks if c.get('status') == 'critical')
        warning_count = sum(1 for c in checks if c.get('status') == 'warning')
        ok_count = sum(1 for c in checks if c.get('status') == 'ok')
        
        # 生成摘要
        report = [
            f"📊 OpenClaw 安全卫士 - 检查摘要",
            f"",
            f"**检查次数**: {total_checks}",
            f"**状态统计**:",
            f"- ✅ 正常：{ok_count}",
            f"- ⚠️ 警告：{warning_count}",
            f"- 🔴 严重：{critical_count}",
            f"",
        ]
        
        # 只包含严重和警告问题
        issues = [c for c in checks if c.get('status') in ['critical', 'warning']]
        if issues:
            report.append("**需要关注的问题**:")
            for issue in issues[-5:]:  # 只显示最近 5 个
                icon = '🔴' if issue.get('status') == 'critical' else '⚠️'
                report.append(f"- {icon} {issue.get('summary', '未知问题')}")
        else:
            report.append("✨ 所有检查通过，系统运行正常")
        
        return '\n'.join(report)
    
    def estimate_token_usage(self, text: str) -> int:
        """估算 token 使用量（粗略估算）"""
        # 中文约 1.5 tokens/字，英文约 0.75 tokens/词
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        other_chars = len(text) - chinese_chars
        
        return int(chinese_chars * 1.5 + other_chars * 0.25)
    
    def optimize_message(self, message: str, max_tokens: int = 500) -> str:
        """优化消息长度（控制 token 消耗）"""
        if self.estimate_token_usage(message) <= max_tokens:
            return message
        
        # 简化消息
        lines = message.split('\n')
        optimized = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.estimate_token_usage(line)
            if current_tokens + line_tokens <= max_tokens:
                optimized.append(line)
                current_tokens += line_tokens
            else:
                optimized.append(f"... (省略 {len(lines) - len(optimized) - 1} 行)")
                break
        
        return '\n'.join(optimized)
