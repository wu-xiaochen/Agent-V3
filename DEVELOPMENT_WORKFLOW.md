# 🔧 开发工作流规范

**创建日期**: 2025-10-30  
**版本**: v1.0  
**状态**: 强制执行

---

## 🎯 核心原则

### 1. 不改变原有功能 ⚠️
**最高优先级原则**

- ✅ 所有新功能必须是**独立添加**
- ✅ 禁止修改已实现的功能逻辑
- ✅ 禁止删除现有代码（除非是死代码）
- ✅ 保持向后兼容

### 2. 开发流程顺序 📋
**强制执行顺序**

```
1. 后端服务开发
   ↓
2. 后端单元测试
   ↓
3. 后端集成测试
   ↓
4. 测试通过
   ↓
5. API接口文档
   ↓
6. 前端开发
   ↓
7. 前端集成测试
   ↓
8. 端到端测试
   ↓
9. 用户验收测试
```

---

## 📖 详细开发流程

### 第一阶段：后端开发 🔧

#### 1.1 需求分析
- [ ] 明确功能需求
- [ ] 设计数据模型
- [ ] 设计API接口
- [ ] 评估技术可行性

#### 1.2 后端实现
**位置**: `api_server.py` 或 `src/api/routers/`

```python
# 示例：工具配置管理
@app.post("/api/tools/config")
async def update_tool_config(config: ToolConfig):
    """
    更新工具配置
    
    Args:
        config: 工具配置对象
    
    Returns:
        更新后的配置
    """
    # 实现逻辑
    pass
```

**要求**:
- ✅ 完整的类型注解
- ✅ 详细的docstring
- ✅ 错误处理
- ✅ 日志记录

#### 1.3 后端单元测试
**位置**: `tests/unit/`

```python
# tests/unit/test_tool_config.py
def test_update_tool_config():
    """测试工具配置更新"""
    config = ToolConfig(...)
    result = update_tool_config(config)
    assert result.success == True
```

**要求**:
- ✅ 测试所有正常路径
- ✅ 测试所有异常情况
- ✅ 测试边界条件
- ✅ 覆盖率 >85%

#### 1.4 后端集成测试
**位置**: `tests/integration/`

```python
# tests/integration/test_tool_api.py
def test_tool_config_api():
    """测试工具配置API集成"""
    response = client.post("/api/tools/config", json={...})
    assert response.status_code == 200
```

**要求**:
- ✅ 测试API端点
- ✅ 测试数据库交互
- ✅ 测试外部服务调用
- ✅ 测试完整业务流程

---

### 第二阶段：测试验证 ✅

#### 2.1 运行测试
```bash
# 后端测试
pytest tests/unit/ -v
pytest tests/integration/ -v

# 查看覆盖率
pytest --cov=src --cov-report=html
```

#### 2.2 测试通过标准
- ✅ 所有单元测试通过
- ✅ 所有集成测试通过
- ✅ 代码覆盖率 >85%
- ✅ 无linter错误
- ✅ 无类型错误

---

### 第三阶段：API文档 📚

#### 3.1 创建API文档
**位置**: `docs/api/`

```markdown
# 工具配置API

## POST /api/tools/config

更新工具配置

### Request
\`\`\`json
{
  "tool_id": "calculator",
  "enabled": true,
  "config": {
    "timeout": 5000
  }
}
\`\`\`

### Response
\`\`\`json
{
  "success": true,
  "tool": {...}
}
\`\`\`
```

**要求**:
- ✅ 完整的请求示例
- ✅ 完整的响应示例
- ✅ 错误码说明
- ✅ 参数说明

---

### 第四阶段：前端开发 🎨

#### 4.1 API集成
**位置**: `frontend/lib/api.ts`

```typescript
// frontend/lib/api/tools.ts
export const toolsApi = {
  async updateConfig(config: ToolConfig) {
    const response = await apiClient.post('/api/tools/config', config)
    return response.data
  }
}
```

**要求**:
- ✅ 完整的类型定义
- ✅ 错误处理
- ✅ 加载状态管理

#### 4.2 前端组件
**位置**: `frontend/components/`

```typescript
export function ToolConfigForm() {
  const [config, setConfig] = useState<ToolConfig>()
  
  const handleSave = async () => {
    try {
      await toolsApi.updateConfig(config)
      toast({ title: "Saved" })
    } catch (error) {
      toast({ title: "Error", variant: "destructive" })
    }
  }
  
  return (...)
}
```

**要求**:
- ✅ 完整的状态管理
- ✅ 错误处理
- ✅ 加载状态
- ✅ 用户反馈

---

### 第五阶段：前端测试 🧪

#### 5.1 前端集成测试
**位置**: `tests/frontend/`

```typescript
// tests/frontend/tool-config.test.ts
describe('ToolConfig', () => {
  it('should save config', async () => {
    const { getByText } = render(<ToolConfigForm />)
    fireEvent.click(getByText('Save'))
    await waitFor(() => {
      expect(toast).toHaveBeenCalled()
    })
  })
})
```

---

### 第六阶段：端到端测试 🔄

#### 6.1 E2E测试
**位置**: `tests/e2e/`

```typescript
// tests/e2e/tool-workflow.test.ts
test('complete tool configuration workflow', async () => {
  // 1. 打开设置页面
  await page.goto('http://localhost:3000/settings')
  
  // 2. 切换到Tools标签
  await page.click('text=Tools')
  
  // 3. 启用工具
  await page.click('[data-testid="calculator-toggle"]')
  
  // 4. 验证保存成功
  await expect(page.locator('text=Saved')).toBeVisible()
})
```

---

## 📊 开发检查清单

### 后端开发 ✅
- [ ] 需求明确
- [ ] 数据模型设计
- [ ] API接口实现
- [ ] 单元测试编写
- [ ] 集成测试编写
- [ ] 所有测试通过
- [ ] 代码覆盖率 >85%
- [ ] API文档完成

### 前端开发 ✅
- [ ] API客户端实现
- [ ] 组件开发
- [ ] 状态管理
- [ ] 错误处理
- [ ] 加载状态
- [ ] 前端测试编写
- [ ] E2E测试编写
- [ ] 所有测试通过

### 质量保证 ✅
- [ ] 无linter错误
- [ ] 无类型错误
- [ ] 无console错误（除调试日志）
- [ ] 响应式设计
- [ ] 无障碍性检查
- [ ] 性能检查

---

## 🚫 禁止行为

### ❌ 绝对禁止
1. **修改已实现的功能逻辑**
2. **删除现有代码（除非明确是死代码）**
3. **跳过测试阶段**
4. **先写前端再写后端**
5. **未测试就提交**

### ⚠️ 需要特别注意
1. 新增功能必须独立
2. API变更需要版本控制
3. 数据库迁移需要回滚方案
4. 配置变更需要向后兼容

---

## 📝 代码审查标准

### 后端代码
```python
# ✅ 好的示例
@app.post("/api/tools/{tool_id}/config")
async def update_tool_config(
    tool_id: str,
    config: ToolConfig,
    db: Session = Depends(get_db)
) -> ToolConfigResponse:
    """
    更新工具配置
    
    Args:
        tool_id: 工具ID
        config: 配置对象
        db: 数据库会话
        
    Returns:
        ToolConfigResponse: 更新后的配置
        
    Raises:
        HTTPException: 工具不存在时抛出404
    """
    try:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        tool.config = config.dict()
        db.commit()
        
        logger.info(f"Updated config for tool {tool_id}")
        return ToolConfigResponse(success=True, tool=tool)
        
    except Exception as e:
        logger.error(f"Failed to update tool config: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
```

### 前端代码
```typescript
// ✅ 好的示例
export function useToolConfig(toolId: string) {
  const [config, setConfig] = useState<ToolConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)
  
  const updateConfig = async (newConfig: ToolConfig) => {
    setLoading(true)
    setError(null)
    
    try {
      const result = await toolsApi.updateConfig(toolId, newConfig)
      setConfig(result.tool)
      return result
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }
  
  return { config, loading, error, updateConfig }
}
```

---

## 🎯 示例：完整开发流程

### 场景：实现工具配置功能

#### 1. 后端开发（第1天）
```bash
# 1. 创建数据模型
touch src/models/tool_config.py

# 2. 创建API路由
touch src/api/routers/tools.py

# 3. 创建测试
touch tests/unit/test_tool_config.py
touch tests/integration/test_tool_api.py

# 4. 实现功能
# ... 编写代码 ...

# 5. 运行测试
pytest tests/unit/test_tool_config.py -v
pytest tests/integration/test_tool_api.py -v

# 6. 查看覆盖率
pytest --cov=src.models.tool_config --cov-report=html
```

#### 2. API文档（第1天）
```bash
# 创建API文档
touch docs/api/tools_api.md
# ... 编写文档 ...
```

#### 3. 前端开发（第2天）
```bash
# 1. 创建API客户端
touch frontend/lib/api/tools.ts

# 2. 创建组件
touch frontend/components/settings/tool-config-form.tsx

# 3. 创建测试
touch tests/frontend/tool-config.test.ts

# 4. 实现功能
# ... 编写代码 ...

# 5. 运行测试
npm run test
```

#### 4. E2E测试（第2天）
```bash
# 创建E2E测试
touch tests/e2e/tool-workflow.test.ts

# 运行E2E测试
npm run test:e2e
```

#### 5. 用户测试（第3天）
```bash
# 启动服务
python api_server.py &
cd frontend && npm run dev &

# 手动测试
# 1. 访问 /settings
# 2. 切换到Tools标签
# 3. 测试所有功能
```

---

## 📌 当前待实现功能

### 1. 工具配置持久化 ⏳
**状态**: 前端UI已完成，需要后端支持

**开发步骤**:
1. ✅ 前端UI（已完成）
2. ⏳ 后端API（待开发）
   - POST /api/tools/config
   - GET /api/tools/config
3. ⏳ 数据持久化
4. ⏳ 前后端集成
5. ⏳ 测试验证

### 2. 主题切换持久化 ⏳
**状态**: 功能已修复，需要持久化

**开发步骤**:
1. ✅ 前端功能（已完成）
2. ⏳ LocalStorage持久化（待实现）
3. ⏳ 测试验证

### 3. Agent配置持久化 ⏳
**状态**: 前端UI已完成，需要后端支持

**开发步骤**:
1. ✅ 前端UI（已完成）
2. ⏳ 后端API（待开发）
3. ⏳ 数据库设计
4. ⏳ 前后端集成
5. ⏳ 测试验证

---

## ✅ 总结

**核心要求**:
1. 后端优先开发
2. 测试驱动开发(TDD)
3. 不修改已有功能
4. 完整的测试覆盖
5. 详细的文档

**违反规范的后果**:
- ❌ 代码被拒绝
- ❌ 需要重新开发
- ❌ 可能破坏已有功能

**遵守规范的好处**:
- ✅ 代码质量高
- ✅ 易于维护
- ✅ 减少Bug
- ✅ 用户满意度高

---

**最后更新**: 2025-10-30  
**维护者**: AI Assistant  
**适用范围**: 所有新功能开发

