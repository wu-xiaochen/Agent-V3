# 环境配置目录

此目录包含特定环境的配置文件，这些配置会覆盖基础配置。

## 环境说明

- `development.yaml`: 开发环境配置
- `staging.yaml`: 预发环境配置
- `production.yaml`: 生产环境配置

## 配置加载优先级

1. 基础配置 (config/base/*.yaml)
2. 环境特定配置 (config/environments/{env}.yaml)
3. 环境变量 (最高优先级)