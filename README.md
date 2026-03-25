# 🛡️ OpenClaw Guardian

OpenClaw 安全卫士 - 自动监控、检测和修复 OpenClaw 运行时的安全问题

## ✨ 功能特性

### 🔍 实时监控
- **进程监控**: 检测 OpenClaw 进程状态，异常自动重启
- **资源监控**: CPU、内存、磁盘使用率监控
- **日志监控**: 自动扫描错误日志，及时发现异常
- **文件监控**: 关键配置文件完整性检查

### 🛠️ 自动修复
- **配置备份**: 自动备份配置文件，支持恢复
- **语法修复**: 自动检测并尝试修复配置文件语法错误
- **日志清理**: 自动清理旧日志，释放磁盘空间
- **进程管理**: 进程异常时自动重启

### 🔎 安全扫描
- **技能扫描**: 检查技能文件完整性和语法
- **配置验证**: 验证配置文件格式和有效性
- **敏感数据检测**: 扫描 API key、密码等敏感信息泄露

### 🧠 智能协助
- **自动搜索**: 遇到未知问题自动全网搜索解决方案
- **缓存机制**: 缓存已解决的问题，减少重复搜索
- **批量处理**: 非紧急问题批量处理，节省 token

### ⚡ Token 优化
- **心跳机制**: 使用心跳而非轮询，减少 API 调用
- **问题分级**: 紧急/普通/低优先级分级处理
- **摘要报告**: 多次检查合并为一次汇报
- **本地优先**: 能本地解决的问题不搜索

## 📦 安装

### 快速安装

```bash
cd ~/.jvs/.openclaw/workspace/openclaw-guardian
./install.sh
```

### 手动安装

```bash
# 安装依赖
pip3 install -r requirements.txt

# 测试运行
python3 main.py --check
```

## 🚀 使用

### 基本命令

```bash
# 后台守护模式运行（推荐）
./main.py --daemon

# 执行一次检查
./main.py --check

# 执行深度扫描
./main.py --scan

# 查看状态报告
./main.py --status

# 查看帮助
./main.py --help
```

### 设置开机自启动

**macOS:**
```bash
./setup-launchd.sh
```

**Linux:**
```bash
./setup-systemd.sh
```

## 📋 配置

配置文件位于 `config/guardian.yaml`

### 主要配置项

```yaml
# 监控配置
monitoring:
  enabled: true
  interval_seconds: 1800  # 检查间隔（秒）
  check_processes: true
  check_resources: true
  check_logs: true
  check_files: true

# 扫描配置
scanning:
  enabled: true
  daily_deep_scan: true
  deep_scan_time: "03:00"  # 深度扫描时间

# 修复配置
healing:
  enabled: true
  auto_backup: true
  auto_restore: false  # 自动恢复需确认
  max_backups: 10
  auto_restart: true

# 搜索配置
search:
  enabled: true
  cache_solutions: true
  cache_ttl_hours: 168  # 缓存有效期（小时）

# 优化配置
optimization:
  batch_non_critical: true
  batch_interval_minutes: 60
  summary_reports: true
  min_token_mode: true
```

## 📊 输出示例

### 检查报告

```
🛡️  OpenClaw Guardian 状态报告

**运行时间**: 2026-03-25 10:37:00
**总检查次数**: 24
**上次检查**: 2026-03-25 10:30:00
**上次深度扫描**: 2026-03-25 03:00:00

✨ 最近没有发现问题
```

### 问题警报

```
🔴 OpenClaw 进程未运行
⚠️ 内存使用率过高：92%
⚠️ 发现 3 个错误日志
```

## 🔧 开发

### 项目结构

```
openclaw-guardian/
├── main.py              # 主入口
├── core/
│   ├── monitor.py      # 监控模块
│   ├── scanner.py      # 扫描模块
│   ├── healer.py       # 修复模块
│   └── optimizer.py    # 优化模块
├── utils/
│   ├── config.py       # 配置管理
│   ├── logger.py       # 日志工具
│   └── searcher.py     # 搜索模块
├── config/
│   └── guardian.yaml   # 配置文件
├── logs/               # 运行日志
├── cache/              # 缓存目录
└── backups/            # 备份目录
```

### 添加新功能

1. 在 `core/` 或 `utils/` 创建新模块
2. 在 `main.py` 中集成
3. 更新配置文件添加相关配置项

## 📝 日志

日志文件位于 `logs/guardian-YYYY-MM-DD.log`

查看最新日志：
```bash
tail -f logs/guardian-$(date +%Y-%m-%d).log
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- OpenClaw 团队
- 所有贡献者

---

**版本**: v1.0.0  
**作者**: 1 号小虫子 · 严谨专业版  
**创建时间**: 2026-03-25
