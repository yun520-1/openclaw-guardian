# 贡献指南

感谢你考虑为 OpenClaw Guardian 做出贡献！

## 如何贡献

### 报告 Bug

1. 检查是否已有类似的 [Issue](https://github.com/openclaw/openclaw-guardian/issues)
2. 使用 Bug 报告模板创建新 Issue
3. 提供详细的复现步骤和环境信息

### 提出功能建议

1. 检查是否已有类似的建议
2. 使用功能建议模板创建新 Issue
3. 描述清楚使用场景和期望行为

### 提交代码

1. Fork 本项目
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/openclaw/openclaw-guardian.git
cd openclaw-guardian

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest black flake8
```

### 代码规范

- 遵循 PEP 8 代码规范
- 使用 Black 格式化代码
- 函数和类需要文档字符串
- 添加适当的类型注解

```bash
# 格式化代码
black .

# 检查代码质量
flake8 .
```

### 测试

```bash
# 运行测试
pytest

# 测试安装
pip install .
guardian --help
```

## 分支管理

- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `bugfix/*` - Bug 修复分支
- `release/*` - 发布分支

## 版本发布

1. 更新版本号（`setup.py`, `pyproject.toml`, `clawhub.json`）
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 发布到 ClawHub 和 GitHub

## 行为准则

- 保持友好和尊重
- 对事不对人
- 欢迎新贡献者
- 提供建设性反馈

## 许可证

通过贡献代码，你同意你的贡献遵循本项目的 [MIT 许可证](LICENSE)。

## 需要帮助？

- 查看 [README.md](README.md)
- 查看 [DELIVERY.md](DELIVERY.md)
- 创建 Issue 提问

感谢你的贡献！🎉
