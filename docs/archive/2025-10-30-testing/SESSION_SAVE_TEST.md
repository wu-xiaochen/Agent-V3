# 🧪 Session保存验证测试

## 测试目的
验证默认session保存功能是否正常工作

---

## 🔧 测试步骤

### 步骤1: 清空localStorage

1. 打开浏览器开发者工具 (F12)
2. 进入 Application → Local Storage → `http://localhost:3000`
3. **右键 → Clear** (清空所有数据)
4. **刷新页面** (Cmd+R 或 F5)

---

### 步骤2: 检查初始化

**打开Console标签，查找日志**:

**预期看到**:
```
💾 [初始化] 创建默认session: session-1
```

**或者**:
```
✅ [初始化] session已存在: session-1
```

**验证localStorage**:
1. 回到 Application → Local Storage
2. 应该看到 key: `session_session-1`
3. 点击查看 value:
```json
{
  "sessionId": "session-1",
  "messages": [],
  "timestamp": "2025-10-30T..."
}
```

✅ **如果看到上述内容，初始化成功！**

---

### 步骤3: 测试用户输入保存

1. **在输入框输入**: "你好"
2. **按Enter发送**
3. **立即查看Console**

**预期日志**:
```
💾💾💾 [重要] 用户输入后立即保存会话到localStorage: {
  sessionId: "session-1",
  messagesCount: 1,
  lastMessage: "你好"
}
```

**验证localStorage**:
1. 回到 Application → Local Storage
2. 刷新 (点击刷新按钮)
3. 点击 `session_session-1`
4. 应该看到:
```json
{
  "sessionId": "session-1",
  "messages": [
    {
      "id": "msg-...",
      "role": "user",
      "content": "你好",
      "timestamp": "..."
    }
  ],
  "timestamp": "..."
}
```

✅ **如果messages数组包含"你好"，保存成功！**

---

### 步骤4: 测试会话切换

1. **不等AI回复，立即点击"New Chat"按钮**
2. **点击回到之前的session (session-1)**

**预期结果**:
- ✅ 应该看到"你好"消息还在
- ✅ 消息没有丢失

---

## 🐛 问题排查

### 问题1: 没有看到初始化日志

**检查**:
- Console是否过滤了日志？（确保"Default levels"全部勾选）
- 是否真的刷新了页面？（硬刷新：Cmd+Shift+R）

**解决**:
- 清空localStorage后硬刷新
- 检查frontend.log: `tail -f /Users/xiaochenwu/Desktop/Agent-V3/frontend.log`

---

### 问题2: localStorage中没有session_session-1

**检查**:
```javascript
// 在Console中执行
localStorage.getItem('session_session-1')
```

**应该返回**:
```json
"{\"sessionId\":\"session-1\",\"messages\":[],\"timestamp\":\"...\"}"
```

**如果返回null**:
1. 检查Console是否有JavaScript错误
2. 检查是否在正确的域名 (localhost:3000)
3. 尝试手动执行:
```javascript
localStorage.setItem('session_session-1', JSON.stringify({
  sessionId: 'session-1',
  messages: [],
  timestamp: new Date().toISOString()
}))
```

---

### 问题3: 用户输入后没有保存

**检查Console日志**:
- 是否有 `💾💾💾 [重要] 用户输入后立即保存会话` 日志？
  - **否**: handleSend没有执行到保存逻辑
  - **是**: 继续下一步

**检查localStorage**:
```javascript
// 在Console中执行
JSON.parse(localStorage.getItem('session_session-1'))
```

**应该看到messages数组不为空**

---

## ✅ 成功标准

全部通过才算成功：

- [ ] 初始化时创建session_session-1
- [ ] Console有初始化日志
- [ ] localStorage中有session数据
- [ ] 用户输入后立即保存
- [ ] Console有保存日志（💾💾💾）
- [ ] localStorage中messages更新
- [ ] 切换会话后消息不丢失

---

## 📊 测试结果模板

```markdown
**测试时间**: 2025-10-30 15:XX

**步骤1 (清空localStorage)**: ✅ 完成

**步骤2 (初始化检查)**:
- Console日志: ✅ 有 / ❌ 无
- localStorage: ✅ 有session_session-1 / ❌ 无
- 截图: [附上]

**步骤3 (输入保存)**:
- Console日志: ✅ 有💾💾💾 / ❌ 无
- localStorage更新: ✅ 是 / ❌ 否
- messages数组: [粘贴内容]

**步骤4 (切换会话)**:
- 消息保留: ✅ 是 / ❌ 否

**最终结果**: ✅ 全部通过 / ❌ 部分失败

**问题描述**: ...
```

---

**现在开始测试！** 🚀

请按照上述步骤操作，并提供测试结果。

