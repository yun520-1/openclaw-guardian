#!/bin/bash
# OpenClaw Guardian - 快速启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

echo "🛡️  OpenClaw Guardian 启动中..."
echo ""

# 后台运行
nohup python3 main.py --daemon > logs/guardian.out 2>&1 &
PID=$!

echo "✅ Guardian 已在后台运行"
echo "   PID: $PID"
echo "   日志：logs/guardian-$(date +%Y-%m-%d).log"
echo ""
echo "停止命令：kill $PID"
echo "查看状态：./main.py --status"
