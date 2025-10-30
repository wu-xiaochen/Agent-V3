# 🧪 完整测试套件

## 📋 测试范围

本测试套件覆盖Agent-V3项目的所有核心功能，包括：
1. 会话管理
2. 思维链系统
3. CrewAI画布
4. 文件上传
5. 工具调用
6. UI/UX交互

---

## 🎯 测试分类

###  1. 单元测试 (Unit Tests)

#### 1.1 思维链处理器
```python
# tests/unit/test_thinking_chain_handler.py
def test_thinking_chain_capture():
    """测试思维链捕获"""
    handler = ThinkingChainHandler()
    
    # 测试thought记录
    handler.record_thought("分析问题")
    assert len(handler.thinking_chain) == 1
    
    # 测试action记录
    handler.record_action("time", {"query": "now"})
    assert len(handler.thinking_chain) == 2
    
    # 测试observation记录
    handler.record_observation("2025-10-30")
    assert len(handler.thinking_chain) == 3

def test_thinking_chain_persistence():
    """测试思维链持久化"""
    session_id = "test-session"
    # 实现持久化测试
```

#### 1.2 CrewAI配置转换
```typescript
// tests/unit/crewai-converter.test.ts
describe('CrewAI Config Conversion', () => {
  test('should convert canvas to crew config', () => {
    const nodes = [/* test nodes */]
    const edges = [/* test edges */]
    const config = convertCanvasToCrewConfig(nodes, edges)
    
    expect(config.agents).toHaveLength(2)
    expect(config.tasks).toHaveLength(2)
  })
  
  test('should convert crew config to canvas', () => {
    const crewConfig = {/* test config */}
    const { nodes, edges } = convertCrewConfigToCanvas(crewConfig)
    
    expect(nodes).toHaveLength(4)  // 2 agents + 2 tasks
  })
})
```

---

### 2. 集成测试 (Integration Tests)

#### 2.1 完整对话流程
```python
# tests/integration/test_chat_flow.py
async def test_complete_chat_workflow():
    """测试完整的对话工作流"""
    # 1. 创建会话
    response = await client.post("/api/chat/session")
    session_id = response.json()["session_id"]
    
    # 2. 发送消息
    response = await client.post(f"/api/chat/message", json={
        "session_id": session_id,
        "content": "现在几点？"
    })
    assert response.status_code == 200
    
    # 3. 验证思维链
    thinking_response = await client.get(f"/api/thinking-chain/{session_id}")
    assert len(thinking_response.json()["thinking_chain"]) > 0
    
    # 4. 验证工具调用
    assert any(step["type"] == "action" for step in thinking_response.json()["thinking_chain"])
```

#### 2.2 CrewAI完整流程
```python
async def test_crewai_end_to_end():
    """测试CrewAI端到端流程"""
    # 1. 生成Crew
    response = await client.post("/api/chat/message", json={
        "session_id": "test",
        "content": "创建一个数据分析团队"
    })
    
    # 2. 验证Crew配置生成
    # 3. 保存Crew
    # 4. 加载Crew
    # 5. 执行Crew
    # 6. 验证结果
```

---

### 3. E2E测试 (End-to-End Tests)

#### 3.1 用户场景测试
```typescript
// tests/e2e/user-scenarios.spec.ts
describe('User Scenarios', () => {
  test('Scenario 1: New User First Chat', async ({ page }) => {
    // 1. 打开应用
    await page.goto('http://localhost:3000')
    
    // 2. 输入第一条消息
    await page.fill('textarea', '你好')
    await page.click('button:has-text("Send")')
    
    // 3. 验证AI回复
    await page.waitForSelector('text=你好')
    
    // 4. 验证保存状态提示
    await page.waitForSelector('text=Saved')
  })
  
  test('Scenario 2: Create and Run Crew', async ({ page }) => {
    // 完整的Crew创建和执行流程
  })
})
```

---

### 4. 性能测试 (Performance Tests)

#### 4.1 API响应时间
```python
def test_api_performance():
    """测试API响应时间"""
    import time
    
    start = time.time()
    response = client.get("/api/health")
    duration = time.time() - start
    
    assert duration < 0.1  # < 100ms
    assert response.status_code == 200
```

#### 4.2 前端性能
```typescript
test('Frontend Load Time', async ({ page }) => {
  const start = Date.now()
  await page.goto('http://localhost:3000')
  await page.waitForLoadState('networkidle')
  const duration = Date.now() - start
  
  expect(duration).toBeLessThan(2000)  // < 2秒
})
```

---

## 🔧 自动化测试脚本

### 后端测试脚本
```bash
# run-backend-tests.sh
#!/bin/bash

echo "🧪 运行后端测试..."

# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 覆盖率报告
pytest --cov=src tests/

echo "✅ 后端测试完成"
```

### 前端测试脚本
```bash
# run-frontend-tests.sh
#!/bin/bash

echo "🧪 运行前端测试..."

cd frontend

# 单元测试
npm run test

# E2E测试
npx playwright test

echo "✅ 前端测试完成"
```

---

## 📊 测试清单

### 功能测试清单

#### 会话管理
- [ ] 创建新会话
- [ ] 切换会话
- [ ] 删除会话
- [ ] 编辑会话名称
- [ ] 会话持久化（localStorage）
- [ ] 会话列表显示
- [ ] 默认会话初始化

#### 思维链系统
- [ ] 捕获Thought步骤
- [ ] 捕获Action步骤
- [ ] 捕获Observation步骤
- [ ] 实时显示思维链
- [ ] 逐条显示（不是一次性）
- [ ] 折叠/展开功能
- [ ] 持久化到localStorage
- [ ] 刷新后恢复
- [ ] 按会话存储

#### CrewAI功能
- [ ] 打开CrewAI画布
- [ ] 添加Agent节点
- [ ] 点击Agent打开配置面板
- [ ] 编辑Agent属性（role, goal, backstory）
- [ ] 添加Task节点
- [ ] 点击Task打开配置面板
- [ ] 编辑Task属性（description, expected_output）
- [ ] 分配Agent到Task
- [ ] 连接节点（dependencies）
- [ ] 保存Crew配置
- [ ] 加载已保存的Crew
- [ ] 删除Crew
- [ ] 运行Crew
- [ ] 显示执行日志
- [ ] 显示执行结果
- [ ] 导出结果

#### 文件上传
- [ ] 选择文件
- [ ] 上传图片
- [ ] 上传文档
- [ ] 预览上传的文件
- [ ] 删除已上传的文件
- [ ] 多文件上传

#### 工具调用
- [ ] Time工具调用
- [ ] Calculator工具调用
- [ ] Search工具调用（如配置）
- [ ] CrewAI Generator工具
- [ ] 工具调用状态显示
- [ ] 工具错误处理

#### UI/UX
- [ ] 侧边栏展开/收缩
- [ ] Hover显示编辑/删除按钮
- [ ] 长标题自动截断
- [ ] 保存状态提示（Saving/Saved）
- [ ] 画布打开时布局调整
- [ ] 深色/浅色主题切换

---

## 🎯 测试执行计划

### Phase 1: 核心功能验证 (30分钟)
1. 手动测试会话管理
2. 手动测试思维链显示
3. 手动测试CrewAI基础功能

### Phase 2: 自动化测试 (1小时)
1. 运行后端自动化测试
2. 运行前端自动化测试
3. 性能测试

### Phase 3: 回归测试 (30分钟)
1. 所有已修复的bug
2. 所有新增的功能
3. 边界情况测试

---

## 📝 测试报告模板

```markdown
# 测试报告

## 执行信息
- 测试日期: {{DATE}}
- 测试人员: {{NAME}}
- 测试环境: {{ENV}}
- 版本: {{VERSION}}

## 测试结果
- 通过: X/Y
- 失败: X/Y
- 跳过: X/Y

## 详细结果

### 会话管理 ✅
- 创建会话: PASS
- 切换会话: PASS
- ...

### 思维链系统 ⚠️
- 实时显示: PASS
- 持久化: FAIL - 原因: ...
- ...

### CrewAI功能 ✅
- 节点配置: PASS
- 保存加载: PASS
- ...

## 问题列表
1. [P0] 思维链持久化失败 - Session ID不匹配
2. [P1] CrewAI画布性能 - 节点>20时卡顿

## 建议
1. 优化思维链存储机制
2. 添加CrewAI虚拟滚动
```

---

## 🚀 快速测试指南

### 5分钟快速测试
```bash
# 1. 启动服务
python api_server.py &
cd frontend && npm run dev &

# 2. 运行自动化测试
python backend_test.py

# 3. 浏览器手动测试
# - 打开 http://localhost:3000
# - 输入消息验证思维链
# - 创建Crew验证配置面板
```

---

**创建时间**: {{NOW}}
**状态**: 📋 待执行
**预计时间**: 2小时

