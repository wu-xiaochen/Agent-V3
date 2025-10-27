# GitHub 仓库设置指南

## 手动创建 GitHub 仓库

由于无法直接通过命令行创建仓库，请按照以下步骤手动创建 GitHub 仓库：

1. 访问 [GitHub](https://github.com) 并登录您的账户 (wu-xiaochen@hotmail.com)
2. 点击右上角的 "+" 号，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `Agent-V3`
   - Description: `Agent-V3: 智能体系统 - 基于大语言模型的智能体框架，提供统一的智能体架构和多种专用智能体`
   - 选择 Public 或 Private（根据您的需求）
   - 不要勾选 "Initialize this repository with a README"（因为我们已有本地仓库）
4. 点击 "Create repository"

## 推送代码到 GitHub

创建仓库后，GitHub 会显示设置说明。请按照以下步骤推送代码：

1. 在本地终端中执行（如果尚未执行）：
   ```bash
   cd /Users/xiaochenwu/Desktop/Agent-V3
   git remote add origin https://github.com/wu-xiaochen/Agent-V3.git
   ```

2. 推送代码到 GitHub：
   ```bash
   git push -u origin main
   ```

## 设置 GitHub Actions

代码推送成功后，GitHub Actions 将自动运行。您可能需要：

1. 在 GitHub 仓库中设置以下 Secrets（Settings > Secrets and variables > Actions）：
   - `DOCKER_USERNAME`: Docker Hub 用户名
   - `DOCKER_PASSWORD`: Docker Hub 密码或访问令牌
   - `OPENAI_API_KEY`: OpenAI API 密钥（可选）
   - `ANTHROPIC_API_KEY`: Anthropic API 密钥（可选）
   - `SILICONFLOW_API_KEY`: 硅基流动 API 密钥（可选）

2. 启用 GitHub Actions：
   - 进入仓库的 Actions 选项卡
   - 如果提示，点击 "I understand my workflows, go ahead and enable them"

## 后续步骤

1. 检查 GitHub Actions 运行状态
2. 根据需要调整 CI/CD 流程
3. 设置项目描述、标签和主题
4. 添加贡献者（如需要）

## 注意事项

- 确保 .gitignore 文件已正确配置，避免提交敏感信息
- 检查 README.md 中的链接是否正确指向您的仓库
- 考虑添加 LICENSE 文件（如果尚未添加）