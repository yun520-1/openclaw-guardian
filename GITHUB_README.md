# 🛡️ OpenClaw Guardian

<div align="center">

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/openclaw/openclaw-guardian/releases)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](README.md)
[![CI/CD](https://github.com/openclaw/openclaw-guardian/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/openclaw/openclaw-guardian/actions/workflows/ci-cd.yml)

**OpenClaw 安全卫士 - 自动监控、检测和修复 OpenClaw 运行时的安全问题**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [配置说明](#-配置说明) • [API 文档](#-api-文档) • [贡献指南](CONTRIBUTING.md)

</div>

---

## 📖 目录

- [功能特性](#-功能特性)
- [系统要求](#-系统要求)
- [安装](#-安装)
- [使用](#-使用)
- [配置](#-配置说明)
- [API 文档](#-api-文档)
- [开发](#-开发)
- [故障排除](#-故障排除)
- [贡献](#-贡献)
- [许可证](#-许可证)

---

## ✨ 功能特性

### 🔍 实时监控
- **进程监控**: 检测 OpenClaw 进程状态，异常自动重启
- **资源监控**: CPU、内存、磁盘使用率监控（阈值 90% 警报）
- **日志监控**: 自动扫描错误日志，及时发现异常
- **文件监控**: 关键配置文件完整性检查

### 🛠️ 自动修复
- **配置备份**: 自动备份配置文件，支持恢复（保留 10 个）
- **语法修复**: 自动检测并尝试修复配置文件语法错误
- **日志清理**: 自动清理旧日志，释放磁盘空间
- **进程管理**: 进程异常时自动重启

### 🔎 安全扫描
- **技能扫描**: 检查技能文件完整性和语法
- **配置验证**: 验证配置文件格式和有效性
- **敏感数据检测**: 扫描 API key、密码等敏感信息泄露

### ⚡ Token 优化
- **心跳机制**: 使用心跳而非轮询，减少 API 调用
- **问题分级**: 紧急/普通/低优先级分级处理
- **批量处理**: 非紧急问题批量处理，节省 token
- **摘要报告**: 多次检查合并为一次汇报

**日均 Token 消耗**: <100 tokens（基础模式）

---

## 💻 系统要求

- **操作系统**: macOS 10.15+ 或 Linux (Ubuntu 18.04+)
- **Python**: 3.8 或更高版本
- **内存**: 最低 512MB，推荐 1GB
- **磁盘**: 最低 100MB 可用空间

---

## 📦 安装

### 方法 1: 从 ClawHub 安装（推荐）

```bash
# 安装 clawhub CLI（如果未安装）
npm install -g clawhub

# 安装 OpenClaw Guardian
clawhub install openclaw-guardian
```

### 方法 2: 从源码安装

```bash
# 克隆仓库
git clone https://github.com/openclaw/openclaw-guardian.git
cd openclaw-guardian

# 运行安装脚本
./install.sh
```

### 方法 3: 使用 pip

```bash
# 从 PyPI 安装（即将发布）
pip install openclaw-guardian
```

---

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

### 查看日志

```bash
# 查看实时日志
tail -f logs/guardian-$(date +%Y-%m-%d).log

# 查看今日错误日志
grep ERROR logs/guardian-$(date +%Y-%m-%d).log
```

---

## ⚙️ 配置说明

配置文件位于 `config/guardian.yaml`，首次运行时自动生成。

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

---

## 📊 API 文档

### 命令行接口

| 命令 | 描述 | 示例 |
|------|------|------|
| `--daemon` | 后台守护模式 | `./main.py --daemon` |
| `--check` | 执行一次检查 | `./main.py --check` |
| `--scan` | 执行深度扫描 | `./main.py --scan` |
| `--status` | 查看状态报告 | `./main.py --status` |
| `--help` | 显示帮助信息 | `./main.py --help` |
| `--version` | 显示版本号 | `./main.py --version` |

### Python API

```python
from core.monitor import Monitor
from core.scanner import Scanner
from core.healer import Healer
from utils.config import Config

# 加载配置
config = Config()

# 创建监控器
monitor = Monitor(config)
result = monitor.run_full_check()

# 创建扫描器
scanner = Scanner(config)
result = scanner.run_full_scan()

# 创建修复器
healer = Healer(config)
healer.create_backup(file_path, reason='manual')
```

---

## 🛠️ 开发

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/openclaw/openclaw-guardian.git
cd openclaw-guardian

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install pytest black flake8
```

### 运行测试

```bash
# 运行测试套件
pytest

# 代码格式化
black .

# 代码质量检查
flake8 .
```

### 构建发布

```bash
# 运行发布脚本
./release.sh
```

---

## 🔧 故障排除

### 常见问题

**Q: 守护进程无法启动？**
```bash
# 检查日志
tail -f logs/guardian.log

# 手动运行测试
./main.py --check
```

**Q: 内存使用率过高？**
```bash
# 检查资源监控
./main.py --status

# 清理日志
./main.py --clean-logs
```

**Q: 开机自启动不工作？**
```bash
# macOS: 检查 launchd 状态
launchctl print gui/$(id -u)/com.openclaw.guardian

# Linux: 检查 systemd 状态
systemctl status openclaw-guardian
```

---

## 🤝 贡献

我们欢迎各种形式的贡献！

- 🐛 [报告 Bug](https://github.com/openclaw/openclaw-guardian/issues/new?template=bug_report.md)
- 💡 [提出功能建议](https://github.com/openclaw/openclaw-guardian/issues/new?template=feature_request.md)
- 🔧 [提交 PR](https://github.com/openclaw/openclaw-guardian/pulls)

详见 [贡献指南](CONTRIBUTING.md)

---

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - OpenClaw 项目
- [psutil](https://github.com/giampaolo/psutil) - 系统和进程监控
- [PyYAML](https://pyyaml.org/) - YAML 配置处理

---

## 📞 联系方式

- **作者**: 1 号小虫子 · 严谨专业版
- **项目地址**: https://github.com/openclaw/openclaw-guardian
- **问题反馈**: https://github.com/openclaw/openclaw-guardian/issues

---

<div align="center">

**如果觉得有用，请给个 ⭐ Star 支持一下！**

[返回顶部](#-openclaw-guardian)

</div>
