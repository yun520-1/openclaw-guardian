#!/bin/bash
# macOS launchd 服务配置

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDIAN_DIR="$SCRIPT_DIR"
PYTHON="$GUARDIAN_DIR/venv/bin/python3"
MAIN_PY="$GUARDIAN_DIR/main.py"
LOG_DIR="$GUARDIAN_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 创建 launchd plist 文件
PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.guardian.plist"

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.guardian</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON</string>
        <string>$MAIN_PY</string>
        <string>--daemon</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$GUARDIAN_DIR</string>
    
    <key>StandardOutPath</key>
    <string>$LOG_DIR/guardian.log</string>
    
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/guardian-error.log</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StartInterval</key>
    <integer>1800</integer>
</dict>
</plist>
EOF

# 加载服务
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo "✅ launchd 服务已配置"
echo "   服务名：com.openclaw.guardian"
echo "   日志：$LOG_DIR/guardian.log"
echo ""
echo "管理命令:"
echo "  launchctl unload $PLIST_FILE  # 停止服务"
echo "  launchctl load $PLIST_FILE    # 启动服务"
echo "  launchctl print gui/\$(id -u)/com.openclaw.guardian  # 查看状态"
