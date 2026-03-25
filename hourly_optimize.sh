#!/bin/bash
# OpenClaw Guardian - 每小时自我优化脚本
# 由 cron 定时调用

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 执行自我优化
python3 core/self_optimizer.py >> logs/optimization.log 2>&1

echo "✅ 自我优化完成 - $(date)"
