#!/bin/bash
# OpenClaw Guardian - 安装脚本

set -e

echo "🛡️  正在安装 OpenClaw Guardian..."

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：需要 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "📦 安装依赖包..."
pip install -r requirements.txt

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p logs cache backups config

# 创建配置文件（如果不存在）
if [ ! -f "config/guardian.yaml" ]; then
    echo "⚙️  创建默认配置文件..."
    # 配置文件会在首次运行时自动创建
fi

# 设置执行权限
chmod +x main.py
chmod +x install.sh

# 创建系统服务（可选）
echo ""
echo "🔧 是否要设置开机自启动？"
echo "   macOS: 运行 ./setup-launchd.sh"
echo "   Linux: 运行 ./setup-systemd.sh"
echo ""

echo "✅ 安装完成！"
echo ""
echo "使用方法:"
echo "  ./main.py --daemon     # 后台运行"
echo "  ./main.py --check      # 执行一次检查"
echo "  ./main.py --status     # 查看状态"
echo "  ./main.py --help       # 查看帮助"
echo ""
