# 完整功能测试清单

## ⚠️ 测试前准备

### 1. 确认服务状态
```bash
# 检查服务
lsof -nP -iTCP:8000,3000 -sTCP:LISTEN

# 应该看到:
# python3.1 51163 ... *:8000 (新后端进程)
# node      52294 ... *:3000 (新前端进程)
```

### 2. 清除浏览器缓存
1. **打开浏览器**: http://localhost:3000
2. **打开控制台**: `Cmd+Option+J` (Mac) 或 `F12`
3. **清除localStorage**:
   ```javascript
   localStorage.clear()
   console.log("✅ localStorage已清除")
   ```
4. **强制刷新**: `Cmd+Shift+R`

---

## 测试1: 会话立即保存

### 目标
用户输入后立即保存，即使AI还在思考时切换会话也不丢失。

### 步骤
1. ✅ 新建会话 (点击"New Chat")
2. ✅ 输入消息: "你好"
3. ✅ **立即点击其他会话** (不等AI回复)
4. ✅ 切换回刚才的会话
5. ✅ **验证**: "你好"消息应该存在

### 预期结果
- ✅ 消息不丢失
- ✅ AI的回复出现在正确的会话中
- ✅ 切换回来后历史完整

### 调试
在控制台应该看到:
```
💾 用户输入后立即保存会话: session-xxxxx
```

---

## 测试2: 思维链实时显示

### 目标
思维链逐步显示，不是一次性输出。

### 步骤
1. ✅ 输入: "**用crew分析2025年AI发展趋势**"
2. ✅ 观察思维链区域（AI头像下方）
3. ✅ 应该看到**逐步出现**:
   - 第1步: "AI is thinking" (思考中)
   - 第2步: "Checked current time" (时间工具)
   - 第3步: "Built intelligent agent team" (crewai_generator)
   - 第4步: "Worked for Xs" (完成)

### 预期结果
- ✅ 每个步骤间隔200ms逐步出现
- ✅ 不是一次性显示所有步骤
- ✅ 显示工具调用状态

### 调试
在控制台应该看到:
```
🔄 轮询思维链 #1: session-xxxxx
📦 思维链数据: {...}
🔧 转换后的工具步骤: [...]
```

---

## 测试3: CrewAI画布自动弹出

### 目标
AI生成Crew后，1.5秒自动打开画布。

### 步骤
1. ✅ 输入: "用crew分析2025年AI发展趋势"
2. ✅ 等待AI回复
3. ✅ **查看控制台日志**

### 预期日志输出
```
🔍 检查metadata: {
  hasMetadata: true,
  action: "open_canvas",
  fullMetadata: { ... }
}
🎨 检测到CrewAI生成，准备自动打开画布
📦 Crew配置: { id: "...", agents: [...], tasks: [...] }
✅ pendingCrewConfig已设置
🚀 延迟执行：打开CrewAI画布
🎨 加载AI生成的Crew配置: {...}
```

### 预期结果
- ✅ 1.5秒后，右侧CrewAI画布自动滑出
- ✅ 画布显示生成的Agent和Task节点
- ✅ 节点可点击查看配置

### 如果没有弹出
查看控制台日志，找到问题：
- 如果显示 "⚠️ 未检测到open_canvas action"
  → 后端metadata没有传递action
- 如果没有任何日志
  → 前端代码没有加载

### 后端调试
```bash
tail -50 backend.log | grep "特殊action"
```
应该看到:
```
🎨 检测到特殊action: open_canvas, crew_id=...
✅ 特殊action已添加到metadata
```

---

## 测试4: Crew画布功能

### 4.1 测试Delete（删除）
1. ✅ CrewAI画布打开后
2. ✅ 左侧Crew列表应该显示生成的Crew
3. ✅ **hover列表项**
4. ✅ 应该看到右上角出现 **X 按钮**
5. ✅ 点击X → 弹出确认对话框
6. ✅ 点击确认 → 显示"删除成功"
7. ✅ 列表刷新，Crew消失

### 4.2 测试Save（保存）
1. ✅ 在画布中添加或修改节点
2. ✅ 点击画布上方的 **"Save"** 按钮
3. ✅ 应该显示 "保存成功" 提示
4. ✅ 验证: `data/crews/{crew_id}.json` 文件更新

### 4.3 测试Run（执行）
1. ✅ 点击画布上方的 **"Run Crew"** 按钮
2. ✅ 应该显示 "执行成功" 或执行状态
3. ✅ 查看后端日志验证执行

---

## 🐛 如果测试失败

### 问题1: 会话仍然丢失
**检查点**:
1. localStorage是否清除？
2. 控制台是否看到保存日志？
3. 查看 `frontend/components/chat-interface.tsx:262-269`

### 问题2: 思维链一次性显示
**检查点**:
1. 轮询间隔是否200ms？
2. 查看 `frontend/components/chat-interface.tsx:358`
3. 控制台是否有轮询日志？

### 问题3: 画布不弹出
**检查点**:
1. 后端日志: `tail -50 backend.log | grep "特殊action"`
2. 前端控制台: 查找 "🔍 检查metadata"
3. metadata.action 是否为 "open_canvas"？

**如果后端没有"特殊action"日志**:
```bash
# 验证文件是否修改
grep -n "特殊action" src/agents/unified/unified_agent.py

# 应该看到多行输出
# 如果没有，说明文件修改丢失，需要重新修改
```

### 问题4: Save/Run按钮不工作
**检查点**:
1. 点击按钮有反应吗？
2. 控制台是否有错误？
3. 查看 `frontend/components/crewai/crew-drawer.tsx:217-223`

---

## ✅ 全部通过的标志

- ✅ 测试1: 会话切换后消息完整
- ✅ 测试2: 思维链逐步显示（200ms间隔）
- ✅ 测试3: CrewAI画布自动弹出（1.5s延迟）
- ✅ 测试4: Delete/Save/Run按钮全部可用

---

## 🚀 下一步

全部测试通过后，我们可以继续：
1. 实现Crew执行状态实时显示
2. 优化思维链UI（更详细的状态）
3. 添加更多Crew管理功能

**现在请按照此清单测试，并告诉我哪些通过，哪些失败！** 📋

