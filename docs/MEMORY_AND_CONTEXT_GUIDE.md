# 记忆与上下文管理指南

## 概述

智能体系统现在具备了完善的记忆和上下文管理功能，包括：
- ✅ 多轮对话记忆
- ✅ 自动对话摘要
- ✅ 智能上下文压缩
- ✅ Token数量控制
- ✅ Redis持久化存储
- ✅ 会话管理

## 核心功能

### 1. 对话记忆（Memory）

智能体会记住整个会话过程中的所有对话，包括：
- 用户的问题和陈述
- 智能体的回答
- 工具调用结果

**特点：**
- 自动保存对话历史
- 支持跨会话检索（使用Redis时）
- 内存和Redis两种存储方式

### 2. 自动摘要（Summary）

当对话轮数超过阈值（默认10轮），系统会自动生成摘要：
- 📝 压缩旧对话，保留关键信息
- 🎯 保留最近4轮完整对话
- 💾 存储摘要历史供查询

**触发条件：**
- 对话轮数 > 10轮
- 预估Token数 > 最大值的80%

### 3. 上下文压缩（Compression）

智能地管理对话上下文，避免超出Token限制：
- 保留最重要的信息
- 删除冗余内容
- 优化Token使用

### 4. Token控制

自动估算和控制Token数量：
- 默认最大4000 tokens
- 超过80%自动触发压缩
- 粗略估算：2字符 ≈ 1 token

## 使用方法

### 基本使用

```bash
# 默认使用内存存储（带自动摘要）
python main.py --interactive

# 使用Redis持久化存储
# 需要先配置Redis连接（config/base/database.yaml）
python main.py --interactive
```

### 交互命令

在交互模式下，可以使用以下命令：

#### 1. 查看对话历史
```
您: memory
```
显示当前会话的所有对话记录。

#### 2. 查看记忆统计
```
您: stats
```
显示记忆系统的统计信息：
- 记忆状态（启用/未启用）
- 消息数量
- 对话轮数
- 摘要数量
- 存储类型
- 会话ID

**示例输出：**
```
=== 记忆统计 ===
记忆状态: 启用
消息数量: 24
对话轮数: 12
摘要数量: 1
存储类型: in_memory_with_summary
会话ID: default
========================================
```

#### 3. 查看对话摘要
```
您: summary
```
显示自动生成的对话摘要历史。

**示例输出：**
```
=== 对话摘要历史 ===

摘要 1:
用户咨询了供应链优化方案，我们讨论了库存管理、
物流优化、供应商关系管理等关键领域。用户特别
关注成本控制和效率提升...

========================================
```

#### 4. 清除对话历史
```
您: clear
```
清除当前会话的所有对话记录和摘要。

#### 5. 退出程序
```
您: quit
或
您: exit
```

## 配置选项

### 配置文件位置
`config/base/agents.yaml`

### 记忆配置示例

```yaml
unified_agent:
  enabled: true
  memory:
    enabled: true                    # 启用记忆功能
    max_conversation_length: 4000    # 最大对话长度（字符数）
    summary_interval: 10             # 每N轮对话触发摘要
```

### Redis配置（可选）
`config/base/database.yaml`

```yaml
redis:
  host: "localhost"
  port: 6379
  db: 0
  password: ""
  connection_pool:
    max_connections: 10
    timeout: 30
```

## 工作原理

### 对话流程

```
用户输入
    ↓
[检查对话轮数]
    ↓
≤ 10轮 ─→ 直接处理
    ↓
> 10轮
    ↓
[生成摘要]
    ↓
[保留最近4轮完整对话]
    ↓
[使用摘要 + 最近对话作为上下文]
    ↓
智能体处理
    ↓
保存新对话到记忆
```

### 摘要生成过程

1. **触发条件检查**
   - 对话轮数 > summary_threshold
   - 或 Token数 > max_tokens * 0.8

2. **提取对话**
   - 旧对话：前N-4轮
   - 最近对话：最后4轮

3. **生成摘要**
   - 使用LLM分析旧对话
   - 提取关键信息和上下文
   - 生成简洁摘要（≤200字）

4. **组合上下文**
   ```
   [摘要消息] + [最近4轮完整对话]
   ```

## 示例场景

### 场景1：短对话（无摘要）

```bash
$ python main.py --interactive

您: 帮我分析一下供应链优化方案
助手: 好的，我来帮您分析...

您: 重点关注成本控制
助手: 明白了，成本控制方面...

您: memory
=== 对话历史 ===
用户: 帮我分析一下供应链优化方案
助手: 好的，我来帮您分析...
用户: 重点关注成本控制
助手: 明白了，成本控制方面...
========================================
```

### 场景2：长对话（自动摘要）

```bash
# 经过12轮对话后...

您: stats
=== 记忆统计 ===
记忆状态: 启用
消息数量: 24
对话轮数: 12
摘要数量: 1
存储类型: in_memory_with_summary
会话ID: default
========================================

您: summary
=== 对话摘要历史 ===

摘要 1:
用户咨询供应链优化，讨论了库存管理策略、
物流路径优化、供应商评估标准。重点关注
成本控制和效率提升...

========================================
```

### 场景3：使用Redis持久化

```bash
# 配置Redis后，对话会持久化存储
$ python main.py --interactive

✅ 使用Redis存储对话历史 (会话ID: default)

您: 继续上次的讨论
助手: 我记得上次我们讨论了...（从Redis加载历史）
```

## 编程接口

### 在代码中使用

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体（自动启用记忆）
agent = UnifiedAgent(
    provider="siliconflow",
    memory=True,
    session_id="user_123"
)

# 使用智能体
response = agent.run("你好")

# 查看记忆统计
stats = agent.get_memory_stats()
print(f"对话轮数: {stats['conversation_rounds']}")
print(f"摘要数量: {stats['summary_count']}")

# 获取对话历史
memory = agent.get_memory()
for msg in memory:
    print(f"{msg.type}: {msg.content}")

# 获取摘要历史
summaries = agent.get_summary_history()
for i, summary in enumerate(summaries):
    print(f"摘要 {i+1}: {summary}")

# 清除记忆
agent.clear_memory()
```

## 高级配置

### 自定义摘要阈值

```python
agent = UnifiedAgent(
    provider="siliconflow",
    memory=True
)

# 修改配置文件
# config/base/agents.yaml
unified_agent:
  memory:
    summary_interval: 5  # 改为5轮就触发摘要
```

### 自定义Token限制

```python
# 修改配置文件
# config/base/agents.yaml
unified_agent:
  memory:
    max_conversation_length: 8000  # 增加到8000字符
```

### 关闭自动摘要

如果不想使用自动摘要功能，可以增大阈值：

```yaml
unified_agent:
  memory:
    summary_interval: 1000  # 设置很大的值，实际上不会触发
```

## 性能考虑

### 内存使用

- **无摘要**：线性增长，约50KB/100轮对话
- **有摘要**：稳定，约10KB（保留最近4轮+摘要）

### 响应时间

- **正常对话**：无额外延迟
- **触发摘要**：增加1-2秒（生成摘要）

### Redis vs 内存

| 特性 | 内存存储 | Redis存储 |
|------|---------|-----------|
| 速度 | 最快 | 快 |
| 持久化 | ❌ | ✅ |
| 跨进程 | ❌ | ✅ |
| 分布式 | ❌ | ✅ |
| 推荐场景 | 单机测试 | 生产环境 |

## 故障排查

### 问题1：记忆没有保存

**检查：**
```
您: stats
```

如果显示 `记忆状态: 未启用`，检查：
1. 配置文件中 `memory.enabled` 是否为 `true`
2. 是否正确创建了UnifiedAgent

**解决：**
```yaml
# config/base/agents.yaml
unified_agent:
  memory:
    enabled: true  # 确保为true
```

### 问题2：Redis连接失败

**错误信息：**
```
⚠️ Redis连接失败: ...，回退到内存存储
```

**解决：**
1. 检查Redis是否运行：`redis-cli ping`
2. 检查连接配置：`config/base/database.yaml`
3. 检查防火墙和端口

### 问题3：摘要未生成

**原因：**
- 对话轮数不足（默认需要>10轮）
- LLM调用失败

**检查：**
```
您: stats
```
查看 `对话轮数` 是否超过阈值

**解决：**
- 继续对话，达到阈值后自动生成
- 降低 `summary_interval` 配置

### 问题4：对话历史丢失

**可能原因：**
1. 使用内存存储，程序重启后丢失
2. Redis连接断开
3. 会话ID不匹配

**解决：**
- 使用Redis持久化存储
- 检查session_id是否一致
- 使用 `memory` 命令确认历史

## 最佳实践

### 1. 生产环境推荐配置

```yaml
unified_agent:
  memory:
    enabled: true
    max_conversation_length: 6000
    summary_interval: 15
```

**原因：**
- 6000字符可容纳较长对话
- 15轮触发摘要，平衡性能和完整性

### 2. 使用Redis存储

```yaml
redis:
  host: "your-redis-server"
  port: 6379
  password: "your-password"
```

**好处：**
- 对话持久化
- 支持分布式部署
- 多个智能体共享记忆

### 3. 定期清理

```python
# 长期运行的服务中，定期清理旧会话
if session_inactive_time > 24_hours:
    agent.clear_memory()
```

### 4. 监控记忆状态

```python
# 定期检查记忆使用情况
stats = agent.get_memory_stats()
if stats['message_count'] > 100:
    logger.warning("对话历史过长，考虑清理")
```

## 总结

记忆与上下文管理功能为智能体提供了：

✅ **智能的对话记忆** - 自动管理上下文  
✅ **高效的资源使用** - 自动压缩和摘要  
✅ **灵活的存储方案** - 内存或Redis  
✅ **完整的统计信息** - 实时监控状态  
✅ **简单的操作接口** - 易于使用和集成  

无需手动管理对话历史，系统会自动处理一切！

---

**需要帮助？** 查看其他文档：
- [流式输出使用指南](./STREAMING_USAGE.md)
- [快速开始](./QUICKSTART.md)
- [API文档](./api/README.md)

