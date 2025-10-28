# Agent-V3 文档中心

<div align="center">

**📚 完整的企业级文档体系**

欢迎来到 Agent-V3 文档中心！这里提供了覆盖开发、部署、运维全生命周期的专业文档。

[![Documentation](https://img.shields.io/badge/docs-15%2B-blue.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg)]()
[![Version](https://img.shields.io/badge/version-v3.0-brightgreen.svg)]()

</div>

---

## 📚 文档导航

### 🎯 快速入门（必读）

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [快速开始](QUICKSTART.md) | 5分钟快速上手指南 | 所有用户 | ⭐⭐⭐⭐⭐ |
| [项目总结](../PROJECT_SUMMARY.md) | 完整功能总结和关键指标 | 所有用户 | ⭐⭐⭐⭐⭐ |
| [项目结构](PROJECT_STRUCTURE.md) | 目录结构和组织说明 | 开发者 | ⭐⭐⭐⭐ |

### 🏗️ 架构与设计

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [系统架构](ARCHITECTURE.md) | 完整的架构设计文档 | 架构师、开发者 | ⭐⭐⭐⭐⭐ |
| [架构分析报告](../ARCHITECTURE_ANALYSIS.md) | 优化建议和实施计划 | 架构师、技术主管 | ⭐⭐⭐⭐⭐ |
| [生产就绪报告](../PRODUCTION_READINESS_REPORT.md) | 生产环境评估 | 技术主管、运维 | ⭐⭐⭐⭐⭐ |

### 🚀 部署与运维（生产级）

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [生产部署指南](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) | 完整的生产环境部署步骤 | 运维、DevOps | ⭐⭐⭐⭐⭐ |
| [运维手册](deployment/OPERATIONS_MANUAL.md) | 日常运维、监控和维护 | 运维 | ⭐⭐⭐⭐⭐ |
| [故障排查](deployment/TROUBLESHOOTING.md) | 问题诊断和解决方案 | 运维、开发者 | ⭐⭐⭐⭐⭐ |

### 🔧 功能指南

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [流式输出](STREAMING_USAGE.md) | 实时输出功能使用指南 | 开发者、用户 | ⭐⭐⭐⭐ |
| [N8N 集成](N8N_API_SETUP.md) | N8N工作流完整集成 | 开发者、运维 | ⭐⭐⭐⭐ |
| [CrewAI 工具](CREWAI_TOOLS_GUIDE.md) | 多智能体协作配置 | 开发者 | ⭐⭐⭐⭐ |
| [记忆管理](MEMORY_AND_CONTEXT_GUIDE.md) | Redis记忆系统详解 | 开发者 | ⭐⭐⭐⭐ |

### 🧪 测试与质量

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [测试指南](TESTING.md) | 完整的测试说明和用例 | 测试、开发者 | ⭐⭐⭐⭐ |

### 🔌 API 与开发

| 文档 | 说明 | 适合人群 | 推荐指数 |
|------|------|---------|----------|
| [API 参考](api/api_reference.md) | API接口完整文档 | 开发者 | ⭐⭐⭐ |
| [开发规范](development/project_rules.md) | 代码规范和最佳实践 | 开发者 | ⭐⭐⭐⭐ |

## 🎯 按角色查找

### 👤 新用户 / 产品经理

**目标**: 快速了解系统能力和使用方法

1. 📖 [快速开始](QUICKSTART.md) - 5分钟上手
2. 📊 [项目总结](../PROJECT_SUMMARY.md) - 了解完整功能
3. 💡 [使用示例](../examples/) - 查看实际用例
4. 🎬 [流式输出](STREAMING_USAGE.md) - 体验交互效果

**预计时间**: 1-2 小时

---

### 👨‍💻 开发者

**目标**: 理解架构，开发新功能

1. 🏗️ [系统架构](ARCHITECTURE.md) - 理解整体设计
2. 📁 [项目结构](PROJECT_STRUCTURE.md) - 熟悉代码组织
3. 📐 [开发规范](development/project_rules.md) - 遵循规范
4. 🔌 [API 参考](api/api_reference.md) - API 接口
5. 🧪 [测试指南](TESTING.md) - 编写和运行测试
6. 🔧 功能扩展:
   - [N8N 集成](N8N_API_SETUP.md)
   - [CrewAI 工具](CREWAI_TOOLS_GUIDE.md)
   - [记忆管理](MEMORY_AND_CONTEXT_GUIDE.md)

**预计时间**: 1-2 天

---

### 🚀 运维 / DevOps

**目标**: 部署和维护生产系统

**阶段 1: 部署前准备**
1. 📋 [生产就绪报告](../PRODUCTION_READINESS_REPORT.md) - 评估系统状态
2. 📐 [架构分析报告](../ARCHITECTURE_ANALYSIS.md) - 了解优化建议
3. 🚀 [生产部署指南](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) - 准备部署

**阶段 2: 部署执行**
1. ⚙️ 环境配置和依赖安装
2. 🐳 Docker / Kubernetes 部署
3. 🔒 安全配置 (SSL/TLS, 防火墙)
4. 📈 监控和告警设置

**阶段 3: 日常运维**
1. 📖 [运维手册](deployment/OPERATIONS_MANUAL.md) - 日常操作
2. 🔍 [故障排查](deployment/TROUBLESHOOTING.md) - 问题诊断
3. 📊 性能监控和优化

**预计时间**: 2-3 天

---

### 🏛️ 架构师 / 技术主管

**目标**: 评估系统，规划优化

1. 📊 [生产就绪报告](../PRODUCTION_READINESS_REPORT.md) - 整体评估
2. 🏗️ [系统架构](ARCHITECTURE.md) - 深入理解设计
3. 🔍 [架构分析报告](../ARCHITECTURE_ANALYSIS.md) - 优化机会
4. 📐 设计审视:
   - 分层架构合理性
   - 扩展性和可维护性
   - 性能瓶颈和优化
5. 🛣️ 制定优化路线图

**预计时间**: 1-2 天

## 📖 文档结构

```
Agent-V3/
├── README.md                                    # 项目主文档 ⭐
├── PROJECT_SUMMARY.md                           # 项目总结 ⭐
├── ARCHITECTURE_ANALYSIS.md                     # 架构分析报告 ⭐
├── PRODUCTION_READINESS_REPORT.md               # 生产就绪报告 ⭐
│
└── docs/                                        # 文档目录
    ├── README.md (本文档)                       # 文档索引 ⭐
    │
    ├── QUICKSTART.md                            # 快速开始
    ├── ARCHITECTURE.md                          # 系统架构
    ├── PROJECT_STRUCTURE.md                     # 项目结构
    ├── TESTING.md                               # 测试指南
    ├── STREAMING_USAGE.md                       # 流式输出
    ├── N8N_API_SETUP.md                         # N8N 集成
    ├── CREWAI_TOOLS_GUIDE.md                    # CrewAI 工具
    ├── MEMORY_AND_CONTEXT_GUIDE.md              # 记忆管理
    │
    ├── api/                                     # API 文档
    │   ├── README.md
    │   └── api_reference.md
    │
    ├── deployment/                              # 部署文档 ⭐⭐⭐
    │   ├── README.md
    │   ├── PRODUCTION_DEPLOYMENT_GUIDE.md       # 生产部署指南
    │   ├── OPERATIONS_MANUAL.md                 # 运维手册
    │   └── TROUBLESHOOTING.md                   # 故障排查
    │
    └── development/                             # 开发文档
        ├── README.md
        └── project_rules.md

⭐ = 必读文档
```

## 🔍 快速查找

### 我想要...

| 需求 | 推荐文档 | 预计时间 |
|------|----------|----------|
| 快速上手 | [快速开始](QUICKSTART.md) | 5-10分钟 |
| 了解整体功能 | [项目总结](../PROJECT_SUMMARY.md) | 15-30分钟 |
| 理解架构设计 | [系统架构](ARCHITECTURE.md) | 1-2小时 |
| 评估生产就绪度 | [生产就绪报告](../PRODUCTION_READINESS_REPORT.md) | 30分钟 |
| 部署到生产环境 | [生产部署指南](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) | 2-3天 |
| 日常运维操作 | [运维手册](deployment/OPERATIONS_MANUAL.md) | 持续 |
| 排查系统故障 | [故障排查](deployment/TROUBLESHOOTING.md) | 按需 |
| 开发新功能 | [API参考](api/api_reference.md) + [开发规范](development/project_rules.md) | 按需 |
| 运行测试 | [测试指南](TESTING.md) | 10-30分钟 |
| 配置工具 | [N8N](N8N_API_SETUP.md) / [CrewAI](CREWAI_TOOLS_GUIDE.md) | 30分钟-1小时 |

---

## ❓ 常见问题

<details>
<summary><b>🔧 如何快速启动系统？</b></summary>

最快方式是使用 Docker Compose：
```bash
docker-compose up -d
```
详见：[快速开始](QUICKSTART.md)
</details>

<details>
<summary><b>💾 如何配置 Redis 持久化？</b></summary>

Redis 已集成，支持 AOF + RDB 双重持久化。
详见：[系统架构 - 存储层](ARCHITECTURE.md)
</details>

<details>
<summary><b>🔧 如何添加自定义工具？</b></summary>

1. 在 `src/agents/shared/` 创建工具类
2. 在 `config/tools/tools_config.json` 注册
3. 在智能体配置中启用

详见：[系统架构 - 自定义工具](ARCHITECTURE.md)
</details>

<details>
<summary><b>🚀 如何部署到生产环境？</b></summary>

完整步骤请参考：[生产部署指南](deployment/PRODUCTION_DEPLOYMENT_GUIDE.md)

关键步骤：
1. 环境准备和依赖安装
2. 配置环境变量
3. Docker/Kubernetes 部署
4. 配置监控和告警
5. 验证和测试
</details>

<details>
<summary><b>🧪 如何运行测试？</b></summary>

```bash
# 运行所有测试
python tests/test_all.py

# 运行核心功能测试
python tests/test_all.py core

# 运行系统集成测试
python tests/test_all.py system
```
详见：[测试指南](TESTING.md)
</details>

<details>
<summary><b>🔍 如何查看系统监控？</b></summary>

系统支持 Prometheus + Grafana 监控方案。
详见：[运维手册 - 监控和告警](deployment/OPERATIONS_MANUAL.md)
</details>

<details>
<summary><b>⚠️ 系统出现问题如何排查？</b></summary>

1. 查看日志：`logs/agent.log`
2. 检查服务状态：`docker-compose ps`
3. 运行健康检查：`python verify_project.py`
4. 参考：[故障排查指南](deployment/TROUBLESHOOTING.md)
</details>

<details>
<summary><b>📈 系统性能如何优化？</b></summary>

参考优化建议：
- [架构分析报告](../ARCHITECTURE_ANALYSIS.md)
- [运维手册 - 性能优化](deployment/OPERATIONS_MANUAL.md)
</details>

---

## 📝 文档贡献

发现文档问题或想要改进？欢迎贡献！

**贡献方式**:
1. 🐛 在 [GitHub Issues](https://github.com/wu-xiaochen/Agent-V3/issues) 提出问题
2. 📝 提交 Pull Request 修复文档
3. 💡 在 [讨论区](https://github.com/wu-xiaochen/Agent-V3/discussions) 分享想法

**文档规范**:
- 使用 Markdown 格式
- 保持结构清晰
- 添加代码示例
- 更新目录和索引

参考：[贡献指南](../CONTRIBUTING.md)

---

## 🆘 获取帮助

**遇到问题？**

1. 📚 先查阅相关文档
2. 🔍 搜索 [已有 Issues](https://github.com/wu-xiaochen/Agent-V3/issues)
3. ❓ 在 [讨论区](https://github.com/wu-xiaochen/Agent-V3/discussions) 提问
4. 🐛 提交新 [Issue](https://github.com/wu-xiaochen/Agent-V3/issues/new)

**紧急问题？**

参考：[故障排查指南](deployment/TROUBLESHOOTING.md)

---

## 📊 文档质量

| 指标 | 状态 | 说明 |
|------|------|------|
| 文档数量 | 15+ | 覆盖全生命周期 |
| 完整度 | 100% | 所有模块有文档 |
| 准确性 | ✅ | 与代码同步 |
| 可读性 | ⭐⭐⭐⭐⭐ | 结构清晰 |
| 示例代码 | ✅ | 所有功能有示例 |

---

<div align="center">

**📚 文档持续更新中**

**最后更新**: 2025-10-28 | **版本**: v3.0 | **状态**: 🟢 生产就绪

Made with ❤️ by Agent-V3 Team

</div>
