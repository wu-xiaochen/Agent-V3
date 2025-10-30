# Agent-V3 快速开始指南

## 🚀 5分钟快速上手

### 1. 启动后端服务

```bash
cd /Users/xiaochenwu/Desktop/Agent-V3

# 安装依赖（首次运行）
pip install -r requirements.txt

# 启动API服务器
python api_server.py
```

**验证**: 访问 http://localhost:8000 应该看到：
```json
{
  "name": "Agent-V3 API",
  "version": "3.1.0",
  "status": "running"
}
```

### 2. 启动前端服务

```bash
cd /Users/xiaochenwu/Desktop/Agent-V3/frontend

# 安装依赖（首次运行）
pnpm install

# 配置环境变量（首次运行）
cp .env.example .env.local

# 启动开发服务器
pnpm dev
```

**验证**: 访问 http://localhost:3000 应该看到聊天界面

### 3. 或者使用一键启动脚本

```bash
cd /Users/xiaochenwu/Desktop/Agent-V3

# 启动所有服务
./start_all.sh

# 停止所有服务
./stop_all.sh
```

---

## 🎯 核心功能测试

### 功能 1: 基础对话

1. 打开 http://localhost:3000
2. 点击 "New Chat" 创建新会话
3. 输入: "你好，介绍一下自己"
4. 观察:
   - ✅ 会话名称自动更新为 "你好，介绍一下自己"
   - ✅ AI回复显示在聊天区域
   - ✅ 消息气泡高度一致

### 功能 2: 会话名称编辑

1. hover任意会话项
2. 点击右侧的编辑图标（铅笔）
3. 修改标题，按 Enter 保存
4. 观察:
   - ✅ 标题立即更新
   - ✅ 会话列表刷新

### 功能 3: 工具调用状态

1. 输入: "用CrewAI分析手机市场趋势"
2. 观察聊天区域:
   - ✅ 显示 "AI正在思考..." 卡片
   - ✅ 显示工具调用详情
   - ✅ 可以折叠/展开

### 功能 4: 工具调用历史

1. 点击右上角菜单图标
2. 切换到 "Tools" 标签页
3. 滚动到底部
4. 观察:
   - ✅ "工具调用历史" 卡片
   - ✅ 点击展开查看详情

### 功能 5: 删除会话

1. hover任意会话
2. 点击右侧垃圾桶图标
3. 确认删除
4. 观察:
   - ✅ 会话从列表消失
   - ✅ 如果删除的是当前会话，自动创建新会话

---

## 📊 API端点速查

### V1 API（传统）

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/chat/message` | POST | 发送消息 |
| `/api/chat/sessions` | GET | 获取会话列表 |
| `/api/chat/sessions/{id}` | DELETE | 删除会话 |
| `/api/files/upload` | POST | 上传文件 |
| `/api/health` | GET | 健康检查 |

### V2 API（增强）

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/v2/chat/stream` | POST | 流式聊天 (SSE) |
| `/api/v2/chat/sessions/{id}/update` | POST | 更新会话 |
| `/api/v2/tools/stats` | GET | 工具统计 |

---

## 🐛 常见问题

### Q1: 前端无法连接后端

**症状**: "无法连接到服务器"

**解决**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/health

# 2. 检查前端环境变量
cat frontend/.env.local
# 确保 NEXT_PUBLIC_API_URL=http://localhost:8000

# 3. 重启前端
cd frontend
rm -rf .next
pnpm dev
```

### Q2: 工具调用不显示

**症状**: 发送消息后没有工具调用卡片

**解决**:
- 确保消息包含 "CREW" 或 "CrewAI" 关键词
- 查看浏览器控制台是否有错误
- 检查后端日志输出

### Q3: 会话标题编辑失败

**症状**: 点击保存后标题未更新

**解决**:
```bash
# 查看浏览器控制台
# 应该看到: "💾 Saving session title: ..."
# 和: "✅ Session title saved"

# 如果看到错误，检查API是否可用
curl -X POST http://localhost:8000/api/v2/chat/sessions/test/update \
  -H "Content-Type: application/json" \
  -d '{"title": "测试"}'
```

### Q4: 端口被占用

**症状**: "Address already in use"

**解决**:
```bash
# 查找占用端口的进程
lsof -ti:8000  # 后端
lsof -ti:3000  # 前端

# 杀死进程
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:3000)
```

---

## 🎨 UI组件位置

```
主界面
├── 侧边栏 (Sidebar)
│   ├── New Chat 按钮
│   ├── 会话列表
│   │   ├── 会话标题 (可编辑)
│   │   └── 删除按钮 (hover显示)
│   ├── Quick Access
│   │   ├── Knowledge Bases
│   │   └── CrewAI Teams
│   └── Settings
│
├── 聊天区域 (ChatInterface)
│   ├── 消息列表
│   ├── 工具调用状态卡片
│   └── 输入框
│
└── 工具面板 (ToolPanel) - 右侧滑出
    ├── CrewAI 标签
    ├── N8N 标签
    ├── Knowledge 标签
    ├── Tools 标签
    │   ├── 工具配置
    │   └── 工具调用历史 ⭐
    └── Settings 标签
```

---

## 📝 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Enter` | 发送消息（聊天输入框） |
| `Shift + Enter` | 换行 |
| `Enter` | 保存（编辑会话标题） |
| `Esc` | 取消（编辑会话标题） |
| `Cmd/Ctrl + R` | 刷新页面 |
| `F12` | 打开开发者工具 |

---

## 🔍 调试技巧

### 1. 查看控制台日志

打开浏览器开发者工具（F12），查看 Console 标签：

```javascript
// 应该看到详细日志
🔄 Sidebar Render - currentSession: session-xxx
✨ Creating new session: session-xxx
🚀 Sending message: {...}
📥 Response received: {...}
📝 Auto-generating session title: "..."
```

### 2. 检查网络请求

开发者工具 → Network 标签：

```
Name                    Status  Type        Size
api/chat/message        200     xhr         1.2kb
api/chat/sessions       200     xhr         0.5kb
```

### 3. 检查后端日志

```bash
# 后端终端应该显示
🚀 Agent-V3 API 服务启动中...
✅ 文件管理器已初始化
✅ 工具注册器已初始化
✅ Agent-V3 API 服务已启动
INFO:     Uvicorn running on http://0.0.0.0:8000

# 收到请求时
💬 处理消息: 你好...
⏱️  执行时间: 1.23s
```

---

## 📚 进一步学习

### 详细文档

- `README.md` - 项目总览
- `FINAL_UI_IMPROVEMENTS.md` - UI改进详情
- `COMPLETE_OPTIMIZATION_SUMMARY.md` - 优化总结
- `FRONTEND_TEST_GUIDE.md` - 完整测试指南

### API文档

访问 http://localhost:8000/docs 查看交互式API文档

### 示例代码

```python
# 后端示例: 使用 UnifiedAgent
from src.agents.unified.unified_agent import UnifiedAgent

agent = UnifiedAgent(
    provider="siliconflow",
    memory=True,
    session_id="test-session"
)

response = agent.run("你好")
print(response)
```

```typescript
// 前端示例: 调用聊天API
import { api } from '@/lib/api'

const response = await api.chat.sendMessage(
  "session-123",
  "你好",
  { provider: "siliconflow", memory: true }
)

console.log(response.response)
```

---

## ✅ 验收清单

使用本指南完成以下任务：

- [ ] 成功启动后端服务
- [ ] 成功启动前端服务
- [ ] 创建新会话
- [ ] 发送消息并收到回复
- [ ] 编辑会话标题
- [ ] 查看工具调用状态
- [ ] 查看工具调用历史
- [ ] 删除会话
- [ ] 查看API文档

**如果全部完成，恭喜！你已经掌握了 Agent-V3 的基本使用！** 🎉

---

## 🆘 获取帮助

如有问题：

1. 查看完整文档
2. 检查浏览器和后端日志
3. 查看 GitHub Issues
4. 参考测试指南

**快速开始指南更新时间**: 2025-10-29

