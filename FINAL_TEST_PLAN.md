# 🧪 最终测试计划

**日期**: 2025-10-30  
**版本**: v3.1  
**目标**: 全面测试所有已实现功能

---

## ✅ 修复记录

### 1. apiClient导出错误 ✅
**问题**: `Export apiClient doesn't exist in target module`  
**修复**: 在`frontend/lib/api.ts`中添加`export`关键字  
**状态**: 已修复

### 2. 前端重启 ✅
**操作**: 重启前端服务  
**状态**: 运行正常

---

## 🧪 测试清单

### A. 主题切换测试
**位置**: 设置 → Appearance

- [ ] 切换到Light主题
- [ ] 刷新页面，主题保持Light
- [ ] 切换到Dark主题
- [ ] 刷新页面，主题保持Dark
- [ ] 检查localStorage存储

**预期**: 主题切换正常，刷新后保持

---

### B. 工具配置测试
**位置**: 设置 → Tools

#### B1. 基本功能
- [ ] 查看所有工具列表
- [ ] 查看工具状态（启用/禁用）
- [ ] 查看工具Mode（API/MCP）

#### B2. 启用/禁用测试
- [ ] 禁用"Calculator"工具
- [ ] 刷新页面验证保存
- [ ] 重新启用"Calculator"
- [ ] 刷新页面验证保存

#### B3. 配置编辑测试
- [ ] 点击"Time Tool"的设置图标
- [ ] 修改Timeout为10000
- [ ] 修改Retries为5
- [ ] 保存配置
- [ ] 刷新页面验证保存
- [ ] 重新打开配置验证修改

#### B4. 重置测试
- [ ] 修改多个工具配置
- [ ] 点击"Reset to Default"
- [ ] 验证所有工具恢复默认值

**预期**: 所有操作正常，数据持久化到后端

---

### C. Agent配置测试
**位置**: 设置 → Agents

#### C1. 查看功能
- [ ] 查看默认Agent列表
- [ ] 查看Agent详细信息
- [ ] 查看系统提示词预览

#### C2. 创建Agent
- [ ] 点击"New Agent"
- [ ] 填写名称: "Test Agent"
- [ ] 填写描述: "This is a test"
- [ ] 填写系统提示词: "You are a helpful test agent"
- [ ] 设置Temperature: 0.5
- [ ] 保存
- [ ] 验证新Agent出现在列表中
- [ ] 刷新页面验证保存

#### C3. 编辑Agent
- [ ] 点击"Test Agent"的编辑按钮
- [ ] 修改描述为"Updated description"
- [ ] 修改Temperature为0.8
- [ ] 保存
- [ ] 验证修改生效
- [ ] 刷新页面验证保存

#### C4. 删除Agent
- [ ] 点击"Test Agent"的删除按钮
- [ ] 验证Agent被删除
- [ ] 刷新页面验证删除持久化
- [ ] 尝试删除最后一个Agent（应该失败）

#### C5. 重置测试
- [ ] 创建多个测试Agent
- [ ] 点击"Reset to Default"
- [ ] 验证恢复到默认Agent

**预期**: 完整的CRUD操作，数据持久化到后端

---

### D. 系统配置测试
**位置**: 设置 → System

#### D1. LLM Provider切换
- [ ] 切换到OpenAI
- [ ] 验证Base URL自动更新
- [ ] 验证Model列表更新
- [ ] 保存配置
- [ ] 刷新页面验证保存

#### D2. API Key测试
- [ ] 输入测试API Key
- [ ] 切换显示/隐藏
- [ ] 保存
- [ ] 刷新验证（应该保存到localStorage）

#### D3. 参数配置
- [ ] 修改Temperature
- [ ] 修改Max Tokens
- [ ] 保存
- [ ] 刷新验证

#### D4. 重置测试
- [ ] 修改所有配置
- [ ] 点击Reset
- [ ] 验证恢复默认值

**预期**: 配置保存到localStorage，刷新后保持

---

### E. 知识库测试
**位置**: 设置 → Knowledge

- [ ] 查看占位符提示
- [ ] 验证"Create Knowledge Base"按钮禁用

**预期**: 显示"Coming soon"提示

---

## 🔍 后端API测试

### 工具配置API
```bash
# 获取所有工具
curl http://localhost:8000/api/tools/configs

# 更新工具
curl -X PUT http://localhost:8000/api/tools/time/config \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# 重置
curl -X POST http://localhost:8000/api/tools/configs/reset
```

### Agent配置API
```bash
# 获取所有Agent
curl http://localhost:8000/api/agents

# 创建Agent
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "API Test", "system_prompt": "test"}'

# 删除Agent
curl -X DELETE http://localhost:8000/api/agents/{agent_id}
```

---

## 🐛 已知问题追踪

### 高优先级
1. ✅ apiClient导出错误 - 已修复
2. ⏳ 工具开关保存 - 待验证
3. ⏳ 设置功能 - 待验证

### 中优先级
- ⏳ JSON解析错误警告（不影响功能）

---

## 📊 测试结果记录

### 主题切换
- [ ] 通过
- [ ] 失败
- 备注: ________________

### 工具配置
- [ ] 通过
- [ ] 失败
- 备注: ________________

### Agent配置
- [ ] 通过
- [ ] 失败
- 备注: ________________

### 系统配置
- [ ] 通过
- [ ] 失败
- 备注: ________________

---

## ✅ 测试通过标准

### 功能性
- ✅ 所有CRUD操作正常
- ✅ 数据持久化正常
- ✅ 刷新后数据保持
- ✅ 错误处理正确
- ✅ Toast提示正常

### 性能
- ✅ 加载速度<2秒
- ✅ 操作响应<500ms
- ✅ 无明显卡顿

### 用户体验
- ✅ UI响应及时
- ✅ 错误提示清晰
- ✅ 操作流程顺畅

---

## 🚀 下一步行动

### 如果测试通过
1. 标记P0任务完成
2. 更新项目文档
3. 开始P1任务

### 如果测试失败
1. 记录具体问题
2. 优先修复
3. 重新测试

---

**测试人员**: 用户  
**测试环境**: 
- 前端: http://localhost:3000
- 后端: http://localhost:8000
- 浏览器: ____________
- OS: macOS

**开始测试时间**: ____________  
**完成测试时间**: ____________

