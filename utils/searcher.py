"""
OpenClaw Guardian - 网络搜索模块
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from utils.logger import logger
from utils.config import Config

class Searcher:
    """网络搜索协助类"""
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = Path(config.get('paths', 'cache'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 搜索历史
        self.search_history = self._load_search_history()
    
    def _load_search_history(self) -> List[Dict]:
        """加载搜索历史"""
        history_file = self.cache_dir / 'search_history.json'
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def _save_search_history(self):
        """保存搜索历史"""
        history_file = self.cache_dir / 'search_history.json'
        try:
            # 只保留最近 100 条
            history = self.search_history[-100:]
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"保存搜索历史失败：{e}")
    
    async def search_problem(self, problem: str, context: Optional[Dict] = None) -> Dict:
        """
        搜索问题解决方案
        
        这个方法需要通过 sessions_spawn 调用 deep-research skill
        返回搜索结果和解决方案
        """
        logger.info(f"开始搜索问题解决方案：{problem[:100]}...")
        
        search_result = {
            'problem': problem,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'solution': None,
            'sources': [],
            'confidence': 'unknown',
        }
        
        # 构建搜索提示
        search_prompt = f"""
请帮我搜索以下 OpenClaw 安全问题的解决方案：

**问题描述**: {problem}

**上下文信息**: {json.dumps(context, ensure_ascii=False) if context else '无'}

请：
1. 搜索类似的 OpenClaw 问题和解决方案
2. 查找相关的 GitHub issues、论坛讨论
3. 提供详细的解决步骤
4. 评估解决方案的可靠性

请用结构化格式返回解决方案。
"""
        
        # 记录搜索
        self.search_history.append({
            'problem': problem,
            'timestamp': search_result['timestamp'],
            'status': 'searching',
        })
        self._save_search_history()
        
        # 注意：实际搜索需要通过 sessions_spawn 调用 deep-research skill
        # 这里返回一个占位结果，实际使用由 main.py 处理
        search_result['status'] = 'requires_agent'
        search_result['search_prompt'] = search_prompt
        
        logger.info(f"搜索任务已创建，需要 agent 执行")
        return search_result
    
    def record_solution(self, problem: str, solution: Dict, success: bool):
        """记录解决方案"""
        self.search_history.append({
            'problem': problem,
            'timestamp': datetime.now().isoformat(),
            'solution': solution,
            'success': success,
            'status': 'completed',
        })
        self._save_search_history()
        
        if success:
            logger.success(f"解决方案已记录：{problem[:50]}...")
        else:
            logger.warning(f"解决方案失败：{problem[:50]}...")
    
    def get_similar_solutions(self, problem: str, limit: int = 3) -> List[Dict]:
        """获取类似的已解决案例"""
        similar = []
        
        for record in reversed(self.search_history):
            if record.get('success') and record.get('problem'):
                # 简单的相似度判断（可以改进）
                if any(keyword in record['problem'] for keyword in problem.split()[:5]):
                    similar.append(record)
                    if len(similar) >= limit:
                        break
        
        return similar
