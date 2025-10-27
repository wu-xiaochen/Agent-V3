# 单元测试目录

此目录包含所有单元测试代码，按照模块进行组织。

## 目录结构

- `agents/`: 智能体单元测试
- `core/`: 核心业务逻辑单元测试
- `infrastructure/`: 基础设施层单元测试
- `interfaces/`: 接口层单元测试
- `shared/`: 共享组件单元测试

## 测试命名规范

- 测试文件名: `{module_name}_test.py`
- 测试类名: `Test{ClassName}`
- 测试方法名: `test_{scenario}_{expected_result}`