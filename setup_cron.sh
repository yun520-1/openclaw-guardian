#!/bin/bash
# 配置 Guardian 每小时优化 cron 任务

CURRENT_CRON=$(crontab -l 2>/dev/null)

# 检查是否已有 Guardian 任务
if echo "$CURRENT_CRON" | grep -q "hourly_optimize.sh"; then
    echo "✅ Guardian cron 任务已存在"
    crontab -l
else
    echo "⏳ 添加 Guardian cron 任务..."
    # 添加新任务
    (echo "$CURRENT_CRON"; echo "0 * * * * cd ~/.jvs/.openclaw/workspace/openclaw-guardian && ./hourly_optimize.sh >> logs/optimization.log 2>&1") | crontab -
    echo "✅ Cron 任务已添加"
    crontab -l
fi
