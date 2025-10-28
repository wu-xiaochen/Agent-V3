# 流式输出使用指南

## 概述

智能体系统支持实时流式输出，让你能够实时看到智能体的思考过程、工具调用和执行结果。

## 快速开始

### 1. 启用流式输出

在运行智能体时添加 `--stream` 参数：

```bash
# Linux/Mac
./scripts/setup/start.sh --interactive --stream

# Windows
scripts\setup\start.bat --interactive --stream
```

或者直接使用 Python：

```bash
python main.py --interactive --stream
```

### 2. 选择输出样式

使用 `--streaming-style` 参数选择不同的输出样式：

#### Simple（简洁模式）- 默认推荐

```bash
python main.py --interactive --stream --streaming-style simple
```

**特点：**
- ✅ 显示工具调用和参数
- ✅ 显示执行结果摘要
- ✅ 清晰的分隔线
- ❌ 不显示步骤编号
- ❌ 不显示详细思考过程

**输出示例：**
```
════════════════════════════════════════════════════════════
🤖 智能体启动
════════════════════════════════════════════════════════════
📥 任务: 帮我分析一下供应链优化方案
════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────
🔧 工具: search
📝 参数: query=供应链优化最佳实践
⏳ 执行中...
✅ 完成
📊 结果:
   找到了相关的供应链优化策略...
   包括库存管理、物流优化等方面...
   
────────────────────────────────────────────────────────────
🔧 工具: calculator
📝 参数: expression=cost_reduction * efficiency
⏳ 执行中...
✅ 完成
📊 结果:
   计算结果: 85.6

════════════════════════════════════════════════════════════
✅ 任务完成
════════════════════════════════════════════════════════════
```

#### Detailed（详细模式）

```bash
python main.py --interactive --stream --streaming-style detailed
```

**特点：**
- ✅ 显示完整的思考过程
- ✅ 显示工具调用详情
- ✅ 显示详细的执行结果
- ✅ 丰富的颜色和图标
- ❌ 不显示步骤编号

**输出示例：**
```
════════════════════════════════════════════════════════════
  🤖 智能体启动
════════════════════════════════════════════════════════════
  任务: 帮我分析一下供应链优化方案
════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════
════════════════════════════════════════════════════════════

  🤔 思考过程
  我需要首先了解当前的供应链优化最佳实践，
  然后结合具体情况提供建议...

  🔧 工具调用: search
  参数: query=供应链优化最佳实践

  ⏳ 执行中

  👁️ 观察结果
  找到了丰富的供应链优化资料，包括：
  1. 库存管理优化
  2. 物流网络优化
  3. 供应商关系管理
  ...（详细内容）

════════════════════════════════════════════════════════════
  💡 结论
  基于研究和分析，我建议采用以下优化策略...
════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════
  ✅ 任务完成
════════════════════════════════════════════════════════════
```

#### None（静默模式）

```bash
python main.py --interactive --stream --streaming-style none
```

**特点：**
- ❌ 不显示中间过程
- ✅ 只显示最终结果
- 适合需要简洁输出的场景

**输出示例：**
```
基于供应链优化的最佳实践，我为您制定了以下方案：
1. 库存管理优化...
2. 物流网络优化...
...
```

## 使用场景建议

### 开发调试
```bash
python main.py --interactive --stream --streaming-style detailed --debug
```
- 使用 `detailed` 模式查看完整执行过程
- 启用 `--debug` 查看详细日志

### 日常使用
```bash
python main.py --interactive --stream
```
- 使用默认的 `simple` 模式
- 平衡了信息量和可读性

### 生产环境/API调用
```bash
python main.py --query "你的问题" --streaming-style none
```
- 使用 `none` 模式只获取结果
- 不需要 `--stream` 参数

## 命令行参数完整列表

```bash
python main.py [选项]

选项:
  --interactive              交互模式
  --query "问题"             单次查询模式
  --stream                   启用流式输出
  --streaming-style STYLE    输出样式 (simple|detailed|none)
  --provider PROVIDER        LLM提供商 (siliconflow|openai|anthropic|ollama)
  --debug                    启用调试模式
  --no-debug                 关闭调试模式
  --config PATH              指定配置文件
```

## 配置文件方式

你也可以在配置文件中设置默认的流式输出样式（未来功能）：

```yaml
# config/base/agents.yaml
unified_agent:
  streaming:
    enabled: true
    style: "simple"  # simple | detailed | none
```

## 编程方式使用

在代码中使用流式输出：

```python
from src.agents.unified.unified_agent import UnifiedAgent

# 创建智能体时指定流式输出样式
agent = UnifiedAgent(
    provider="siliconflow",
    streaming_style="simple"  # simple, detailed, none
)

# 使用流式输出
for chunk in agent.stream("你的问题"):
    if isinstance(chunk, dict) and "response" in chunk:
        print(chunk["response"], end="", flush=True)
    else:
        print(chunk, end="", flush=True)
```

## 常见问题

### Q: 为什么我看不到流式输出？

A: 请确保：
1. 使用了 `--stream` 参数
2. 选择了正确的 `--streaming-style`（默认是 `simple`）
3. 不要使用 `--streaming-style none`，那会隐藏中间过程

### Q: 如何关闭"步骤 X"这样的标识？

A: 最新版本已经移除了步骤编号显示，你只会看到工具调用和执行结果。

### Q: Simple 和 Detailed 模式的主要区别是什么？

A: 
- **Simple**: 显示工具调用和结果，不显示AI的内部思考过程
- **Detailed**: 显示完整的思考过程、工具调用和详细结果

### Q: 流式输出会影响性能吗？

A: 流式输出的性能影响很小：
- **Simple**: 几乎无影响
- **Detailed**: 轻微影响（增加了输出量）
- **None**: 无影响

## 快速示例

### 示例1：简洁模式问答
```bash
python main.py --query "今天天气怎么样？" --stream --streaming-style simple
```

### 示例2：详细模式交互
```bash
python main.py --interactive --stream --streaming-style detailed
```

### 示例3：使用启动脚本
```bash
# Linux/Mac
./scripts/setup/start.sh --interactive --stream

# Windows
scripts\setup\start.bat --interactive --stream
```

## 更新日志

### v3.0 (当前版本)
- ✅ 移除了"步骤 X"标识
- ✅ 优化了输出格式
- ✅ 添加了更丰富的图标
- ✅ 改进了错误处理显示

### v2.0
- ✅ 添加了 simple/detailed/none 三种输出模式
- ✅ 支持启动脚本传参

### v1.0
- ✅ 基础流式输出功能

---

**需要帮助？** 查看完整文档：[docs/README.md](./README.md)

