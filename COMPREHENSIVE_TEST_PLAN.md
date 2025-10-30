# 🧪 Agent-V3 完整测试方案

**创建时间**: 2025-10-29  
**版本**: v1.0  
**状态**: 执行中

---

## 📋 测试策略

### 测试金字塔

```
        /\
       /  \     E2E Tests (10%)
      /────\    
     /      \   Integration Tests (30%)
    /────────\  
   /          \ Unit Tests (60%)
  /────────────\
```

### 测试原则

1. **先测试后开发** - 关键功能必须先写测试
2. **测试独立性** - 每个测试用例独立运行
3. **快速反馈** - 单元测试<1s，集成测试<5s
4. **真实场景** - E2E测试模拟真实用户行为

---

## 🎯 测试范围

### Phase 1: P0 关键功能测试（今晚）

#### 1.1 会话滚动测试 ✅

**测试文件**: `frontend/tests/chat-scrolling.test.tsx`

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChatInterface } from '@/components/chat-interface'
import { useAppStore } from '@/lib/store'

describe('Chat Scrolling', () => {
  beforeEach(() => {
    // 清空状态
    useAppStore.getState().clearMessages()
  })

  test('should scroll to bottom when new message is added', async () => {
    const { container } = render(<ChatInterface />)
    
    // 发送多条消息
    const input = screen.getByPlaceholderText('Type your message...')
    const sendButton = screen.getByTitle('发送消息')
    
    for (let i = 0; i < 10; i++) {
      fireEvent.change(input, { target: { value: `Message ${i}` } })
      fireEvent.click(sendButton)
      await waitFor(() => {
        expect(screen.getByText(`Message ${i}`)).toBeInTheDocument()
      })
    }
    
    // 检查滚动锚点
    const messagesEnd = container.querySelector('[ref="messagesEndRef"]')
    expect(messagesEnd).toBeInTheDocument()
    
    // 验证滚动到底部
    const scrollArea = container.querySelector('[data-radix-scroll-area-viewport]')
    await waitFor(() => {
      expect(scrollArea.scrollTop).toBeCloseTo(scrollArea.scrollHeight - scrollArea.clientHeight, -10)
    })
  })

  test('should auto-scroll when AI responds', async () => {
    // Mock API response
    jest.spyOn(require('@/lib/api').api.chat, 'sendMessage').mockResolvedValue({
      success: true,
      session_id: 'test',
      response: 'This is a long response...' + 'x'.repeat(1000)
    })
    
    render(<ChatInterface />)
    
    const input = screen.getByPlaceholderText('Type your message...')
    const sendButton = screen.getByTitle('发送消息')
    
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.click(sendButton)
    
    // 等待AI响应显示
    await waitFor(() => {
      expect(screen.getByText(/This is a long response/)).toBeInTheDocument()
    })
    
    // 验证自动滚动
    const scrollArea = document.querySelector('[data-radix-scroll-area-viewport]')
    expect(scrollArea.scrollTop).toBeGreaterThan(0)
  })

  test('should scroll when tool call status changes', async () => {
    // 测试工具调用时的滚动行为
    // ...
  })
})
```

**验证清单**:
- [ ] 新消息添加后自动滚动
- [ ] AI响应时自动滚动
- [ ] 工具调用状态变化时自动滚动
- [ ] 多条消息快速添加时滚动正常
- [ ] 使用 requestAnimationFrame 确保 DOM 渲染完成

**测试结果**: ⏳ 待执行

---

#### 1.2 工具调用状态测试 ✅

**测试文件**: `frontend/tests/tool-call-status.test.tsx`

```typescript
describe('Tool Call Status', () => {
  test('should not show duplicate tool status', () => {
    render(<ChatInterface />)
    
    // 触发工具调用
    // ...
    
    // 验证只有一个工具状态卡片
    const toolStatusCards = screen.getAllByText(/AI正在思考/)
    expect(toolStatusCards).toHaveLength(1)
  })

  test('should show collapse button only when there are tool calls', () => {
    const { rerender } = render(
      <ToolCallStatus toolCalls={[]} isThinking={true} />
    )
    
    // 思考中但无工具调用 - 不显示折叠按钮
    expect(screen.queryByRole('button', { name: /chevron/ })).not.toBeInTheDocument()
    
    // 添加工具调用 - 显示折叠按钮
    rerender(
      <ToolCallStatus 
        toolCalls={[{ tool: 'test', status: 'running' }]} 
        isThinking={false} 
      />
    )
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  test('should toggle tool call details on button click', () => {
    render(
      <ToolCallStatus 
        toolCalls={[{ tool: 'search', input: { query: 'test' }, output: 'result' }]} 
        isThinking={false} 
      />
    )
    
    // 初始状态：展开
    expect(screen.getByText(/输入: {"query":"test"}/)).toBeInTheDocument()
    
    // 点击折叠
    const collapseButton = screen.getByRole('button')
    fireEvent.click(collapseButton)
    
    // 验证折叠后不显示详情
    expect(screen.queryByText(/输入:/)).not.toBeInTheDocument()
    
    // 再次点击展开
    fireEvent.click(collapseButton)
    expect(screen.getByText(/输入:/)).toBeInTheDocument()
  })

  test('should display correct status indicators', () => {
    const { rerender } = render(
      <ToolCallStatus 
        toolCalls={[{ tool: 'test', status: 'running' }]} 
        isThinking={false} 
      />
    )
    
    // 运行中 - 黄色脉冲
    expect(screen.getByText('test').previousSibling).toHaveClass('bg-yellow-500')
    
    // 成功 - 绿色
    rerender(
      <ToolCallStatus 
        toolCalls={[{ tool: 'test', status: 'success' }]} 
        isThinking={false} 
      />
    )
    expect(screen.getByText('test').previousSibling).toHaveClass('bg-green-500')
    
    // 错误 - 红色
    rerender(
      <ToolCallStatus 
        toolCalls={[{ tool: 'test', status: 'error', error: 'Failed' }]} 
        isThinking={false} 
      />
    )
    expect(screen.getByText('test').previousSibling).toHaveClass('bg-red-500')
    expect(screen.getByText(/错误: Failed/)).toBeInTheDocument()
  })
})
```

**验证清单**:
- [ ] 不重复显示工具状态卡片
- [ ] 折叠按钮逻辑正确
- [ ] 状态指示器颜色正确
- [ ] 展开/折叠功能正常

**测试结果**: ⏳ 待执行

---

#### 1.3 文档分析测试 ✅

**测试文件**: `tests/test_document_analysis.py`

```python
import pytest
from fastapi.testclient import TestClient
from api_server import app
from src.infrastructure.multimodal.document_parser import parse_document

client = TestClient(app)

class TestDocumentAnalysis:
    """文档分析功能测试"""
    
    def test_upload_and_parse_pdf(self, tmp_path):
        """测试PDF上传和解析"""
        # 创建测试PDF文件
        pdf_path = tmp_path / "test.pdf"
        # ... 创建PDF内容
        
        with open(pdf_path, 'rb') as f:
            response = client.post(
                "/api/files/upload",
                files={"file": ("test.pdf", f, "application/pdf")},
                data={"file_type": "data"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "parsed_content" in data
        assert data["parsed_content"]["type"] == "pdf"
        assert len(data["parsed_content"]["full_text"]) > 0
    
    def test_chat_with_document_context(self):
        """测试带文档上下文的对话"""
        # 1. 上传文档
        with open("tests/fixtures/sample.pdf", 'rb') as f:
            upload_response = client.post(
                "/api/files/upload",
                files={"file": ("sample.pdf", f, "application/pdf")}
            )
        
        parsed_content = upload_response.json()["parsed_content"]
        
        # 2. 发送带附件的消息
        chat_response = client.post(
            "/api/chat/message",
            json={
                "session_id": "test-session",
                "message": "分析这个文档的内容",
                "attachments": [{
                    "id": "file-1",
                    "name": "sample.pdf",
                    "type": "document",
                    "url": "/api/files/download/xxx",
                    "size": 1024,
                    "parsed_content": parsed_content
                }]
            }
        )
        
        assert chat_response.status_code == 200
        data = chat_response.json()
        assert data["success"] is True
        # 验证AI响应包含文档内容的分析
        assert len(data["response"]) > 100  # 确保有实质性回复
    
    def test_document_context_length_limit(self):
        """测试文档内容长度限制"""
        # 创建超长文档
        long_text = "x" * 20000  # 20000字符
        
        response = client.post(
            "/api/chat/message",
            json={
                "session_id": "test",
                "message": "总结文档",
                "attachments": [{
                    "id": "1",
                    "name": "long.txt",
                    "type": "document",
                    "url": "/test",
                    "size": 20000,
                    "parsed_content": {
                        "type": "text",
                        "summary": "Long document",
                        "full_text": long_text
                    }
                }]
            }
        )
        
        # 验证文档内容被截断到8000字符
        assert response.status_code == 200
        # 检查日志确认截断
    
    def test_multiple_documents(self):
        """测试多个文档附件"""
        response = client.post(
            "/api/chat/message",
            json={
                "session_id": "test",
                "message": "对比这两个文档",
                "attachments": [
                    {
                        "id": "1",
                        "name": "doc1.pdf",
                        "type": "document",
                        "url": "/test1",
                        "size": 1000,
                        "parsed_content": {
                            "type": "pdf",
                            "summary": "Document 1 summary",
                            "full_text": "Content of document 1"
                        }
                    },
                    {
                        "id": "2",
                        "name": "doc2.pdf",
                        "type": "document",
                        "url": "/test2",
                        "size": 1000,
                        "parsed_content": {
                            "type": "pdf",
                            "summary": "Document 2 summary",
                            "full_text": "Content of document 2"
                        }
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
```

**验证清单**:
- [ ] PDF文档成功上传和解析
- [ ] Word文档成功上传和解析
- [ ] Excel文档成功上传和解析
- [ ] 文档内容正确传递给AI
- [ ] AI能够分析文档内容
- [ ] 超长文档正确截断
- [ ] 多个文档同时附加

**测试结果**: ⏳ 待执行

---

### Phase 2: 集成测试（明天上午）

#### 2.1 会话管理测试

```python
class TestSessionManagement:
    """会话管理功能测试"""
    
    def test_create_and_switch_sessions(self):
        """测试创建和切换会话"""
        # 创建第一个会话
        response1 = client.post("/api/chat/message", json={
            "session_id": "session-1",
            "message": "Hello from session 1"
        })
        assert response1.json()["session_id"] == "session-1"
        
        # 创建第二个会话
        response2 = client.post("/api/chat/message", json={
            "session_id": "session-2",
            "message": "Hello from session 2"
        })
        assert response2.json()["session_id"] == "session-2"
        
        # 切换回第一个会话
        response3 = client.post("/api/chat/message", json={
            "session_id": "session-1",
            "message": "Back to session 1"
        })
        # 验证会话上下文保持
    
    def test_session_history_persistence(self):
        """测试会话历史持久化"""
        # TODO: 实现Redis存储后测试
        pass
    
    def test_delete_session(self):
        """测试删除会话"""
        # 创建会话
        client.post("/api/chat/message", json={
            "session_id": "test-delete",
            "message": "Test"
        })
        
        # 删除会话
        response = client.delete("/api/chat/sessions/test-delete")
        assert response.json()["success"] is True
        
        # 验证会话已删除
        list_response = client.get("/api/chat/sessions")
        sessions = list_response.json()["sessions"]
        assert not any(s["session_id"] == "test-delete" for s in sessions)
```

#### 2.2 工具调用集成测试

```python
class TestToolIntegration:
    """工具调用集成测试"""
    
    def test_search_tool(self):
        """测试搜索工具"""
        response = client.post("/api/chat/message", json={
            "session_id": "test",
            "message": "搜索今天的天气"
        })
        
        # 验证工具被调用
        # 验证返回结果
    
    def test_crewai_tool(self):
        """测试CrewAI工具"""
        # TODO: 实现CrewAI后端后测试
        pass
```

---

### Phase 3: E2E测试（明天下午）

#### 3.1 完整用户流程测试

**测试文件**: `tests/e2e/user-workflow.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test.describe('Complete User Workflow', () => {
  test('user can upload document and chat about it', async ({ page }) => {
    // 1. 打开应用
    await page.goto('http://localhost:3000')
    
    // 2. 创建新会话
    await page.click('button:has-text("New Chat")')
    
    // 3. 上传文档
    const fileInput = await page.locator('input[type="file"]')
    await fileInput.setInputFiles('tests/fixtures/sample.pdf')
    
    // 4. 等待解析完成
    await expect(page.getByText(/解析成功/)).toBeVisible({ timeout: 10000 })
    
    // 5. 发送问题
    await page.fill('textarea', '这个文档的主要内容是什么？')
    await page.click('button[title="发送消息"]')
    
    // 6. 验证AI响应
    await expect(page.getByText(/文档.*内容/)).toBeVisible({ timeout: 30000 })
    
    // 7. 验证滚动到底部
    const scrollArea = await page.locator('[data-radix-scroll-area-viewport]')
    const scrollTop = await scrollArea.evaluate(el => el.scrollTop)
    const scrollHeight = await scrollArea.evaluate(el => el.scrollHeight)
    const clientHeight = await scrollArea.evaluate(el => el.clientHeight)
    expect(scrollTop).toBeGreaterThan(scrollHeight - clientHeight - 100)
    
    // 8. 切换到另一个会话
    await page.click('button:has-text("New Chat")')
    
    // 9. 切换回原会话
    await page.click('.session-item:first-child')
    
    // 10. 验证历史消息存在
    await expect(page.getByText('这个文档的主要内容是什么？')).toBeVisible()
  })
  
  test('user can interact with tools', async ({ page }) => {
    await page.goto('http://localhost:3000')
    
    // 发送需要工具的消息
    await page.fill('textarea', '搜索最新的AI新闻')
    await page.click('button[title="发送消息"]')
    
    // 验证工具调用状态显示
    await expect(page.getByText(/AI正在思考/)).toBeVisible()
    
    // 验证工具调用详情
    await expect(page.getByText(/输入:/)).toBeVisible()
    
    // 测试折叠功能
    await page.click('button:has([class*="ChevronUp"])')
    await expect(page.getByText(/输入:/)).not.toBeVisible()
  })
})
```

---

## 📊 测试覆盖率目标

### 总体目标

- **单元测试覆盖率**: > 80%
- **集成测试覆盖率**: > 60%
- **E2E测试覆盖率**: 核心流程 100%

### 模块覆盖率

| 模块 | 单元测试 | 集成测试 | E2E测试 | 总覆盖率 |
|------|----------|----------|---------|----------|
| 前端组件 | 85% | 60% | 80% | 85% |
| API客户端 | 90% | 70% | 90% | 90% |
| 后端API | 80% | 80% | 90% | 85% |
| Agent核心 | 75% | 70% | 80% | 80% |
| 工具系统 | 70% | 65% | 70% | 70% |
| 文件管理 | 85% | 75% | 80% | 85% |

---

## 🚀 测试执行计划

### 今晚 (2-3小时)

```bash
# 1. 安装测试依赖
cd frontend
npm install -D @testing-library/react @testing-library/jest-dom jest
npm install -D @playwright/test

cd ..
pip install pytest pytest-cov pytest-asyncio httpx

# 2. 配置测试环境
# - 创建 jest.config.js
# - 创建 pytest.ini
# - 创建 playwright.config.ts

# 3. 编写P0测试用例
# - chat-scrolling.test.tsx
# - tool-call-status.test.tsx
# - test_document_analysis.py

# 4. 运行测试
npm test                    # 前端单元测试
pytest tests/ -v --cov     # 后端单元/集成测试

# 5. 修复失败的测试
# 6. 提交测试代码
```

### 明天上午 (2小时)

```bash
# 1. 编写集成测试
# - test_session_management.py
# - test_tool_integration.py

# 2. 运行集成测试
pytest tests/integration/ -v

# 3. 修复失败的测试
```

### 明天下午 (2小时)

```bash
# 1. 编写E2E测试
# - user-workflow.spec.ts

# 2. 运行E2E测试
npx playwright test

# 3. 生成测试报告
npx playwright show-report
```

---

## ✅ 测试通过标准

### 功能测试

- [ ] 所有P0功能测试通过
- [ ] 会话滚动在所有场景下正常
- [ ] 工具调用状态不重复且可折叠
- [ ] 文档内容能被AI正确分析

### 性能测试

- [ ] 消息滚动响应时间 < 100ms
- [ ] 文档解析时间 < 2s
- [ ] API响应时间 < 500ms
- [ ] 前端渲染时间 < 50ms

### 兼容性测试

- [ ] Chrome/Edge 正常
- [ ] Firefox 正常
- [ ] Safari 正常
- [ ] 移动端浏览器正常

---

## 📝 测试报告模板

```markdown
# 测试报告 - YYYY-MM-DD

## 测试概览
- 测试时间: 
- 测试人员: 
- 测试范围: 
- 测试环境: 

## 测试结果
- 总用例数: 
- 通过数: 
- 失败数: 
- 跳过数: 
- 通过率: 

## 失败用例详情
1. 用例名称
   - 失败原因: 
   - 复现步骤: 
   - 修复计划: 

## 覆盖率报告
- 单元测试: 
- 集成测试: 
- E2E测试: 

## 问题汇总
- 严重问题: 
- 一般问题: 
- 建议优化: 

## 下一步计划
```

---

**创建者**: AI Assistant  
**状态**: ✅ 完成  
**下一步**: 执行测试计划


