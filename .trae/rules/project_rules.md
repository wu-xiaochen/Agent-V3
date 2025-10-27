1. 目录结构规范
1.1 目录结构
<TEXT>
trae-project/
├── config/                           # 配置文件目录
│   ├── base/                         # 基础配置
│   │   ├── agents.yaml              # Agent基础配置
│   │   ├── database.yaml            # 数据库配置
│   │   ├── logging.yaml             # 日志配置
│   │   └── services.yaml            # 服务配置
│   ├── environments/                # 环境配置
│   │   ├── development.yaml         # 开发环境
│   │   ├── staging.yaml             # 预发环境
│   │   └── production.yaml          # 生产环境
│   └── schemas/                     # 配置Schema
├── src/
│   ├── agents/                       # Agent实现层
│   │   ├── {agent_name}/            # 每个Agent独立目录
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # Agent主逻辑
│   │   ├── contracts/               # Agent契约定义
│   │   └── factories/               # Agent工厂
│   ├── core/                        # 核心业务逻辑
│   │   ├── domain/                  # 领域模型
│   │   └── services/                # 核心服务
│   ├── infrastructure/              # 基础设施层
│   │   ├── database/
│   │   ├── cache/
│   │   └── external/
│   ├── interfaces/                  # 接口适配层
│   │   ├── api/                     # API接口
│   │   └── events/                  # 事件处理
│   └── shared/                      # 共享组件
│       ├── utils/
│       ├── exceptions/
│       └── types/
├── tests/
│   ├── unit/                        # 单元测试
│   │   ├── agents/
│   │   ├── core/
│   │   └── infrastructure/
│   ├── integration/                 # 集成测试
│   ├── e2e/                         # 端到端测试
│   └── fixtures/                    # 测试数据
├── docs/                            # 项目文档
│   ├── api/                         # API文档
│   ├── deployment/                  # 部署文档
│   └── development/                 # 开发文档
├── scripts/                         # 运维脚本
│   ├── deployment/
│   ├── monitoring/
│   └── maintenance/
├── .github/                         # CI/CD配置
│   └── workflows/
└── requirements/                    # 依赖管理
    ├── base.yaml
    ├── development.yaml
    └── production.yaml
1.2 目录命名规则
主目录: 小写蛇形命名，如 infrastructure
子目录: 小写蛇形命名，如 database_clients
资源目录: 使用复数形式，如 fixtures, scripts
Agent目录: 使用蛇形命名，反映功能领域
1.3 文件组织原则
按领域驱动设计划分目录结构
高内聚：相关文件放在同一目录
低耦合：跨目录依赖通过接口进行
2. 配置文件管理规范
2.1 配置分层架构
<TEXT>
配置加载优先级（从低到高）：
1. config/base/*.yaml              # 基础默认配置
2. config/environments/{env}.yaml  # 环境特定配置
3. 环境变量覆盖                    # 最高优先级
2.2 配置文件规则
<YAML>
# 基础配置模板
version: "1.0"                    # 配置版本
description: "Agent基础配置"
database:
  main:
    host: "localhost"
    port: 5432
    database: "trae_agents"
    username: "${DB_USERNAME}"     # 环境变量引用
    password: "${DB_PASSWORD}"     # 敏感信息必须使用环境变量
agents:
  summarizer:
    enabled: true
    model: "gpt-4"
    parameters:
      temperature: 0.7
      max_tokens: 1000
logging:
  level: "INFO"
  format: "json"
2.3 配置安全规范
敏感数据禁止硬编码，必须使用环境变量
配置文件必须包含版本控制和变更说明
生产环境配置必须加密存储和传输
2.4 环境配置管理
开发环境：允许调试信息，放宽超时限制
测试环境：使用模拟服务，隔离外部依赖
生产环境：严格的安全策略，监控配置
3. 代码命名规范
3.1 文件命名规则
Python文件: 小写蛇形命名，如 text_processor.py
配置文件: 小写蛇形命名，如 database_config.yaml
测试文件: {module_name}_test.py
配置文件: 明确描述配置内容，如 llm_services.yaml
3.2 类命名规范
Agent类: {Domain}Agent，如 SummarizerAgent
服务类: {Domain}Service，如 EmbeddingService
模型类: {Domain}Model，如 UserModel
接口类: {Behavior}Interface，如 StorageInterface
3.3 变量和函数命名
变量名: 小写蛇形命名，如 input_text
函数名: 小写蛇形命名，动词开头，如 process_document
常量名: 大写蛇形命名，如 MAX_RETRY_COUNT
3.4 模块导入规范
<PYTHON>
# 标准导入顺序
1. 标准库导入
2. 第三方库导入  
3. 项目内部导入
# 禁止循环导入
# 限制跨层直接导入
4. 低耦合设计规范
4.1 依赖注入原则
所有外部依赖必须通过构造函数注入
禁止在类内部直接实例化外部服务
使用接口隔离具体实现
4.2 接口隔离规则
每个接口只定义一个明确的职责
Agent间通信必须通过定义良好的接口
数据传递使用DTO（Data Transfer Object）
4.3 事件驱动架构
跨Agent通信优先使用事件机制
事件定义必须包含完整的上下文信息
事件处理必须是幂等的
4.4 契约设计规范
接口契约必须明确输入输出格式
错误处理契约必须包含所有可能的错误情况
版本化契约，向后兼容变更
5. 测试脚本规范
5.1 测试目录结构
<TEXT>
tests/
├── unit/                           # 单元测试
│   ├── agents/                     # Agent单元测试
│   │   ├── summarizer_test.py
│   │   └── classifier_test.py
├── integration/                    # 集成测试
│   ├── api_tests/
│   └── database_tests/
├── e2e/                           # 端到端测试
│   ├── workflow_tests/            # 工作流测试
│   └── performance_tests/         # 性能测试
└── fixtures/                       # 测试数据
    ├── sample_documents/
    └── test_configs/
5.2 测试用例命名规范
测试方法名：test_{scenario}_{expected_result}
夹具命名：{data_type}_fixture，如 user_fixture
5.3 测试数据管理
测试数据与代码分离管理
关键测试数据需要版本控制
性能测试数据单独维护
5.4 测试执行规范
单元测试：快速执行，隔离外部依赖
集成测试：验证组件间协作
E2E测试：完整的业务流程验证
6. 质量门禁规范
6.1 代码提交前检查
静态代码分析通过
单元测试覆盖率 >85%
代码规范检查通过
6.2 集成测试要求
所有Agent组合场景必须有集成测试
关键业务路径必须有E2E测试覆盖
7. 依赖管理规范
7.1 外部依赖管理
明确声明所有依赖版本
定期更新依赖安全检查
禁止使用已弃用的依赖版本
8. 文档维护规范
8.1 文档同步机制
代码变更必须更新对应文档
API变更必须更新接口文档
配置变更必须更新配置说明