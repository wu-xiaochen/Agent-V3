# Agent-V3 贡献指南

欢迎为 Agent-V3 项目做出贡献！本指南将帮助您了解如何参与项目开发。

## 目录
- [开发环境设置](#开发环境设置)
- [代码贡献流程](#代码贡献流程)
- [代码规范](#代码规范)
- [测试指南](#测试指南)
- [文档贡献](#文档贡献)
- [问题报告](#问题报告)
- [社区准则](#社区准则)

## 开发环境设置

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/Agent-V3.git
cd Agent-V3
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements/development.txt
```

### 4. 配置环境变量
复制 `.env.example` 到 `.env` 并根据需要修改：
```bash
cp .env.example .env
```

### 5. 运行测试
```bash
python -m pytest tests/
```

## 代码贡献流程

### 1. Fork 仓库
在 GitHub 上 Fork 项目仓库到您的账户。

### 2. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

### 3. 开发和测试
- 遵循项目的代码规范
- 为新功能添加测试
- 确保所有测试通过

### 4. 提交代码
```bash
git add .
git commit -m "feat: 添加新功能描述"
```

### 5. 推送分支
```bash
git push origin feature/your-feature-name
```

### 6. 创建 Pull Request
在 GitHub 上创建 Pull Request，详细描述您的更改。

## 代码规范

### Python 代码规范
- 遵循 PEP 8 风格指南
- 使用 Black 进行代码格式化
- 使用 isort 进行导入排序
- 使用 flake8 进行代码检查

### 提交信息规范
使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：
- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `style:` 代码格式化
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建过程或辅助工具的变动

示例：
```
feat(supply-chain): 添加库存管理功能

- 实现库存查询API
- 添加库存预警机制
- 更新相关文档
```

### 代码审查
- 所有代码必须经过代码审查
- 审查者应关注代码质量、设计和安全性
- 提交者应及时回应审查意见

## 测试指南

### 测试类型
1. **单元测试**：测试单个函数或方法
2. **集成测试**：测试多个组件的交互
3. **端到端测试**：测试完整的用户流程

### 测试编写
- 为新功能编写测试
- 确保测试覆盖率达到85%以上
- 使用描述性的测试名称

### 测试运行
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/unit/test_agent.py

# 运行特定测试函数
python -m pytest tests/unit/test_agent.py::TestAgent::test_init

# 生成覆盖率报告
python -m pytest --cov=src tests/
```

## 文档贡献

### 文档类型
1. **API文档**：描述API接口
2. **开发文档**：指导开发人员
3. **用户文档**：指导最终用户
4. **部署文档**：指导部署和运维

### 文档编写
- 使用 Markdown 格式
- 保持文档简洁明了
- 包含代码示例
- 及时更新文档

## 问题报告

### 报告Bug
使用 GitHub Issues 报告Bug，包含以下信息：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息
- 相关日志

### 功能请求
使用 GitHub Issues 提出功能请求，包含以下信息：
- 功能描述
- 使用场景
- 期望实现
- 可能的解决方案

## 社区准则

### 行为准则
- 尊重他人，保持礼貌
- 接受建设性反馈
- 专注于对社区最有利的事情
- 对其他社区成员表示同理心

### 沟通方式
- 使用中文进行交流
- 在讨论中保持专业和友好
- 避免使用攻击性语言

## 发布流程

### 版本号规范
使用 [语义化版本](https://semver.org/)：
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 发布步骤
1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 创建 GitHub Release

## 获取帮助

如果您有任何问题或需要帮助，可以通过以下方式获取帮助：
- 查看 [项目文档](docs/)
- 搜索 [已有Issues](https://github.com/your-username/Agent-V3/issues)
- 创建新的 Issue
- 联系项目维护者

感谢您的贡献！