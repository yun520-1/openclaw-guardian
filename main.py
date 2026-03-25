#!/usr/bin/env python3
"""
OpenClaw Guardian - OpenClaw 安全卫士
主入口文件

功能：
- 后台运行监控 OpenClaw 安全
- 自动检测和修复问题
- 智能搜索协助
- 最小化 token 消耗
"""

import sys
import os
import json
import time
import signal
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.monitor import Monitor
from core.scanner import Scanner
from core.healer import Healer
from core.optimizer import TokenOptimizer
from utils.config import Config
from utils.logger import logger
from utils.searcher import Searcher

class OpenClawGuardian:
    """OpenClaw 安全卫士主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        logger.info("=" * 60)
        logger.info("🛡️  OpenClaw Guardian 启动")
        logger.info("=" * 60)
        
        # 加载配置
        self.config = Config(config_path)
        
        # 初始化模块
        self.monitor = Monitor(self.config)
        self.scanner = Scanner(self.config)
        self.healer = Healer(self.config)
        self.optimizer = TokenOptimizer(self.config)
        self.searcher = Searcher(self.config)
        
        # 运行状态
        self.running = False
        self.last_check_time = None
        self.last_deep_scan_time = None
        self.check_history = []
        
        # 信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理停止信号"""
        logger.warning("收到停止信号，准备退出...")
        self.running = False
    
    def _should_run_check(self) -> bool:
        """判断是否应该执行检查"""
        interval = self.config.get('monitoring', 'interval_seconds', default=1800)
        
        if self.last_check_time is None:
            return True
        
        return datetime.now() - self.last_check_time > timedelta(seconds=interval)
    
    def _should_run_deep_scan(self) -> bool:
        """判断是否应该执行深度扫描"""
        if not self.config.get('scanning', 'daily_deep_scan', default=True):
            return False
        
        # 检查是否到达深度扫描时间
        scan_time_str = self.config.get('scanning', 'deep_scan_time', default='03:00')
        scan_hour, scan_minute = map(int, scan_time_str.split(':'))
        
        now = datetime.now()
        scan_time = now.replace(hour=scan_hour, minute=scan_minute, second=0, microsecond=0)
        
        # 如果是凌晨时间且还没扫描过
        if now.hour == scan_hour and now.minute >= scan_minute:
            if self.last_deep_scan_time is None or \
               self.last_deep_scan_time.date() != now.date():
                return True
        
        return False
    
    def run_check(self) -> Dict:
        """执行一次检查"""
        logger.info("开始执行安全检查...")
        
        # 监控检查
        monitor_result = self.monitor.run_full_check()
        
        # 评估问题等级
        issues = []
        for issue in monitor_result.get('issues', []):
            issues.append({
                'type': 'monitor',
                'level': issue['level'],
                'message': issue['message'],
            })
        
        # 尝试自动修复
        if self.config.get('healing', 'enabled', default=True):
            fixable_issues = [i for i in issues if i['level'] == 'critical']
            if fixable_issues:
                logger.info(f"发现 {len(fixable_issues)} 个可修复的严重问题")
                healing_result = self.healer.apply_healing(fixable_issues)
                logger.info(f"修复结果：成功{healing_result['successful']}/{healing_result['attempted']}")
        
        # 记录检查结果
        check_result = {
            'timestamp': datetime.now().isoformat(),
            'type': 'regular_check',
            'status': monitor_result.get('status', 'unknown'),
            'issues': issues,
            'summary': monitor_result,
        }
        
        self.check_history.append(check_result)
        self.last_check_time = datetime.now()
        
        # 生成摘要报告
        report = self.optimizer.create_summary_report([check_result])
        logger.info(report)
        
        return check_result
    
    def run_deep_scan(self) -> Dict:
        """执行深度安全扫描"""
        logger.info("开始执行深度安全扫描...")
        
        # 漏洞扫描
        scan_result = self.scanner.run_full_scan()
        
        # 评估风险
        issues = []
        if scan_result.get('risk_level') in ['medium', 'high']:
            issues.append({
                'type': 'scan',
                'level': 'warning' if scan_result['risk_level'] == 'medium' else 'critical',
                'message': f"安全扫描发现 {scan_result['total_issues']} 个问题，风险等级：{scan_result['risk_level']}",
            })
        
        # 记录结果
        scan_result['timestamp'] = datetime.now().isoformat()
        scan_result['type'] = 'deep_scan'
        
        self.last_deep_scan_time = datetime.now()
        
        logger.info(f"深度扫描完成，风险等级：{scan_result.get('risk_level', 'unknown')}")
        return scan_result
    
    async def search_assistance(self, problem: str, context: Dict):
        """搜索问题解决方案（需要 agent 协助）"""
        logger.info(f"需要搜索协助：{problem[:100]}...")
        
        # 检查缓存
        cached = self.optimizer.get_cached_solution(problem)
        if cached:
            logger.info("使用缓存的解决方案")
            self.optimizer.increment_cache_use(problem)
            return cached
        
        # 创建搜索任务
        search_result = await self.searcher.search_problem(problem, context)
        
        if search_result.get('status') == 'requires_agent':
            # 需要通过 sessions_spawn 调用 deep-research
            # 这里记录任务，由外部触发
            logger.info(f"搜索任务已创建：{search_result.get('search_prompt', '')[:200]}")
        
        return search_result
    
    def run_once(self) -> Dict:
        """执行一次完整检查（用于测试或手动触发）"""
        result = {
            'check': self.run_check(),
            'scan': None,
        }
        
        if self._should_run_deep_scan():
            result['scan'] = self.run_deep_scan()
        
        return result
    
    def run_daemon(self):
        """以守护进程模式运行"""
        logger.info("进入守护模式，持续监控中...")
        self.running = True
        
        while self.running:
            try:
                # 执行检查
                if self._should_run_check():
                    self.run_check()
                
                # 执行深度扫描
                if self._should_run_deep_scan():
                    self.run_deep_scan()
                
                # 等待下一次检查
                time.sleep(60)  # 每分钟检查一次是否需要执行任务
                
            except KeyboardInterrupt:
                logger.info("用户中断，退出...")
                break
            except Exception as e:
                logger.error(f"守护进程错误：{e}")
                time.sleep(60)
        
        logger.info("Guardian 已停止")
    
    def generate_status_report(self) -> str:
        """生成状态报告"""
        now = datetime.now()
        
        report = [
            "🛡️ **OpenClaw Guardian 状态报告**",
            "",
            f"**运行时间**: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**总检查次数**: {len(self.check_history)}",
        ]
        
        if self.last_check_time:
            report.append(f"**上次检查**: {self.last_check_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.last_deep_scan_time:
            report.append(f"**上次深度扫描**: {self.last_deep_scan_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 最近问题统计
        recent_issues = []
        for check in self.check_history[-10:]:
            recent_issues.extend(check.get('issues', []))
        
        if recent_issues:
            report.append("")
            report.append("**最近问题**:")
            for issue in recent_issues[-5:]:
                icon = '🔴' if issue['level'] == 'critical' else '⚠️'
                report.append(f"- {icon} {issue['message']}")
        else:
            report.append("")
            report.append("✨ 最近没有发现问题")
        
        return '\n'.join(report)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw Guardian - OpenClaw 安全卫士')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--daemon', '-d', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--check', action='store_true', help='执行一次检查')
    parser.add_argument('--scan', action='store_true', help='执行一次深度扫描')
    parser.add_argument('--status', action='store_true', help='显示状态报告')
    parser.add_argument('--version', '-v', action='version', version='OpenClaw Guardian v1.0.0')
    
    args = parser.parse_args()
    
    # 创建 Guardian 实例
    guardian = OpenClawGuardian(args.config)
    
    if args.check:
        # 执行一次检查
        result = guardian.run_once()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.scan:
        # 执行深度扫描
        result = guardian.run_deep_scan()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.status:
        # 显示状态
        print(guardian.generate_status_report())
    
    elif args.daemon:
        # 守护模式
        guardian.run_daemon()
    
    else:
        # 默认守护模式
        guardian.run_daemon()


if __name__ == '__main__':
    main()
