#!/bin/bash
# OpenClaw Guardian - 发布脚本
# 用于打包并发布到 ClawHub 和 GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 OpenClaw Guardian 发布脚本"
echo "=============================="
echo ""

# 版本号
VERSION="1.0.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查必要工具
check_tools() {
    echo "📋 检查必要工具..."
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ 错误：需要 git${NC}"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 错误：需要 python3${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 工具检查通过${NC}"
    echo ""
}

# 清理构建文件
cleanup() {
    echo "🧹 清理构建文件..."
    rm -rf build/ dist/ *.egg-info __pycache__/
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "${GREEN}✅ 清理完成${NC}"
    echo ""
}

# 运行测试
run_tests() {
    echo "🧪 运行测试..."
    
    # 激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 运行基本测试
    python3 main.py --check > /dev/null 2>&1
    python3 main.py --scan > /dev/null 2>&1
    
    echo -e "${GREEN}✅ 测试通过${NC}"
    echo ""
}

# 代码质量检查
check_quality() {
    echo "🔍 代码质量检查..."
    
    # 如果安装了 flake8 和 black，运行检查
    if command -v flake8 &> /dev/null; then
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    fi
    
    if command -v black &> /dev/null; then
        black --check . || true
    fi
    
    echo -e "${GREEN}✅ 质量检查完成${NC}"
    echo ""
}

# 更新版本号
update_version() {
    echo "📝 更新版本号到 ${VERSION}..."
    
    # 更新 clawhub.json
    if [ -f "clawhub.json" ]; then
        sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$VERSION\"/" clawhub.json
        rm -f clawhub.json.bak
    fi
    
    # 更新 setup.py
    if [ -f "setup.py" ]; then
        sed -i.bak "s/version=\"[^\"]*\"/version=\"$VERSION\"/" setup.py
        rm -f setup.py.bak
    fi
    
    # 更新 pyproject.toml
    if [ -f "pyproject.toml" ]; then
        sed -i.bak "s/version = \"[^\"]*\"/version = \"$VERSION\"/" pyproject.toml
        rm -f pyproject.toml.bak
    fi
    
    echo -e "${GREEN}✅ 版本号已更新${NC}"
    echo ""
}

# 构建 Python 包
build_package() {
    echo "📦 构建 Python 包..."
    
    python3 -m build 2>/dev/null || python3 setup.py sdist bdist_wheel
    
    echo -e "${GREEN}✅ 包构建完成${NC}"
    echo "   位置：dist/"
    ls -la dist/ 2>/dev/null || true
    echo ""
}

# 创建 Git 标签
create_tag() {
    echo "🏷️  创建 Git 标签 v${VERSION}..."
    
    # 检查是否在 git 仓库中
    if [ -d ".git" ]; then
        git add -A
        git commit -m "release: v${VERSION}" || true
        git tag -a "v${VERSION}" -m "Release version ${VERSION}"
        echo -e "${GREEN}✅ Git 标签已创建${NC}"
    else
        echo -e "${YELLOW}⚠️  不是 git 仓库，跳过标签创建${NC}"
    fi
    echo ""
}

# 发布到 ClawHub
publish_clawhub() {
    echo "📤 发布到 ClawHub..."
    
    if command -v clawhub &> /dev/null; then
        clawhub publish . || echo -e "${YELLOW}⚠️  ClawHub 发布失败${NC}"
    else
        echo -e "${YELLOW}⚠️  未安装 clawhub CLI，跳过发布${NC}"
        echo "   安装：npm install -g clawhub"
    fi
    echo ""
}

# 推送到 GitHub
push_github() {
    echo "📤 推送到 GitHub..."
    
    if [ -d ".git" ]; then
        echo "   请手动运行以下命令推送:"
        echo "   git push origin main"
        echo "   git push origin v${VERSION}"
    else
        echo -e "${YELLOW}⚠️  不是 git 仓库，跳过推送${NC}"
    fi
    echo ""
}

# 显示发布说明
show_release_notes() {
    echo "📋 发布说明"
    echo "=============================="
    echo ""
    echo "✅ 完成事项:"
    echo "   - 代码质量检查"
    echo "   - 基本功能测试"
    echo "   - 版本号更新"
    echo "   - Python 包构建"
    echo "   - Git 标签创建"
    echo ""
    echo "📦 发布包位置:"
    echo "   - dist/openclaw_guardian-${VERSION}*.tar.gz"
    echo "   - dist/openclaw_guardian-${VERSION}*.whl"
    echo ""
    echo "🚀 下一步操作:"
    echo "   1. 推送到 GitHub:"
    echo "      git push origin main"
    echo "      git push origin v${VERSION}"
    echo ""
    echo "   2. 发布到 ClawHub:"
    echo "      clawhub publish ."
    echo ""
    echo "   3. 发布到 PyPI (可选):"
    echo "      twine upload dist/*"
    echo ""
}

# 主函数
main() {
    check_tools
    cleanup
    run_tests
    check_quality
    update_version
    build_package
    create_tag
    # publish_clawhub  # 需要 clawhub CLI
    # push_github     # 需要手动确认
    
    show_release_notes
    
    echo -e "${GREEN}🎉 发布准备完成！${NC}"
}

# 运行主函数
main
