# 🧪 Agent-V3 E2E测试文档

## 📋 概述

本目录包含使用Playwright编写的端到端(E2E)测试，覆盖Agent-V3的所有核心功能。

## 🎯 测试覆盖范围

### 1. 基础聊天功能 (`01-basic-chat.spec.ts`)
- ✅ 页面加载
- ✅ 发送消息
- ✅ 接收AI响应
- ✅ 思维链显示
- ✅ 会话创建和切换
- ✅ 长文本处理
- ✅ 特殊字符处理
- ✅ 会话持久化
- ✅ 工具调用显示

**测试数量**: 10个

### 2. CrewAI完整流程 (`02-crewai-flow.spec.ts`)
- ✅ AI生成配置
- ✅ 手动打开画布
- ✅ 创建新Crew
- ✅ 添加Agent/Task节点
- ✅ 配置Agent属性
- ✅ 保存Crew配置
- ✅ 执行Crew任务
- ✅ 查看执行结果
- ✅ 删除Crew

**测试数量**: 10个

### 3. 设置功能 (`03-settings.spec.ts`)
- ✅ 打开设置页面
- ✅ 查看系统配置
- ✅ 更新系统配置
- ✅ 主题切换
- ✅ 主题持久化
- ✅ Agent配置管理
- ✅ 工具配置管理
- ✅ 配置重置

**测试数量**: 8个

**总计**: 28个E2E测试用例

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Users/xiaochenwu/Desktop/Agent-V3/tests/e2e

# 安装Node依赖
npm install

# 安装Playwright浏览器
npm run install:browsers
```

### 2. 启动服务

测试会自动启动前后端服务，但也可以手动启动：

```bash
# 终端1: 启动后端
cd /Users/xiaochenwu/Desktop/Agent-V3
python api_server.py

# 终端2: 启动前端
cd /Users/xiaochenwu/Desktop/Agent-V3/frontend
npm run dev
```

### 3. 运行测试

```bash
# 运行所有测试（无头模式）
npm test

# 运行所有测试（有头模式，可见浏览器）
npm run test:headed

# 运行特定测试文件
npx playwright test tests/01-basic-chat.spec.ts

# 调试模式
npm run test:debug

# UI模式（推荐）
npm run test:ui
```

### 4. 查看报告

```bash
# 打开HTML测试报告
npm run report
```

---

## 📂 目录结构

```
tests/e2e/
├── playwright.config.ts      # Playwright配置
├── package.json               # 依赖配置
├── tsconfig.json              # TypeScript配置
├── helpers/                   # 测试辅助函数
│   └── test-helpers.ts
├── tests/                     # 测试用例
│   ├── 01-basic-chat.spec.ts
│   ├── 02-crewai-flow.spec.ts
│   └── 03-settings.spec.ts
├── test-results/              # 测试结果（自动生成）
│   ├── screenshots/
│   └── results.json
└── playwright-report/         # HTML报告（自动生成）
```

---

## 🔧 配置说明

### Playwright配置

```typescript
{
  timeout: 60000,              // 测试超时: 60秒
  expect: { timeout: 10000 },  // 断言超时: 10秒
  retries: 2,                  // CI环境重试2次
  workers: 1,                  // CI环境单线程执行
}
```

### 环境变量

- `BASE_URL`: 前端服务地址（默认: http://localhost:3000）
- `CI`: CI环境标识（影响重试和并行配置）

---

## 📸 截图和视频

测试执行时会自动生成：

- **截图**: 所有测试步骤截图保存在 `test-results/screenshots/`
- **失败截图**: 测试失败时自动截图
- **失败视频**: 测试失败时录制视频（保存在 `test-results/`）
- **追踪文件**: 失败时生成追踪文件，可用于调试

---

## 🎨 测试最佳实践

### 1. 使用辅助函数

```typescript
import { sendChatMessage, waitForAIResponse } from '../helpers/test-helpers';

// ✅ 推荐
await sendChatMessage(page, '你好');
await waitForAIResponse(page);

// ❌ 不推荐
await page.fill('textarea', '你好');
await page.click('button[type="submit"]');
// ... 手动等待逻辑
```

### 2. 合理设置超时

```typescript
// 对于AI响应等长时间操作，设置更长超时
await waitForAIResponse(page, 90000); // 90秒

// 对于CrewAI执行，设置测试级别超时
test.setTimeout(180000); // 3分钟
```

### 3. 使用data-testid

```typescript
// ✅ 推荐：使用data-testid
await page.locator('[data-testid="new-session-button"]').click();

// ⚠️  可用：使用文本（但可能受国际化影响）
await page.locator('button:has-text("New")').click();

// ❌ 避免：使用CSS类名（容易变化）
await page.locator('.btn-primary').click();
```

### 4. 截图调试

```typescript
// 测试中任意位置截图
await takeScreenshot(page, 'debug-step-1');
```

---

## 🐛 常见问题

### 1. 测试超时

**问题**: 测试执行超过60秒

**解决**:
```typescript
// 为特定测试设置更长超时
test('长时间任务', async ({ page }) => {
  test.setTimeout(120000); // 2分钟
  // ...
});
```

### 2. 元素未找到

**问题**: `Element not found: [selector]`

**解决**:
- 检查元素选择器是否正确
- 使用 `test:debug` 模式逐步调试
- 增加等待时间或使用 `waitForElement`

### 3. 服务未启动

**问题**: `connect ECONNREFUSED`

**解决**:
```bash
# 手动启动服务
python api_server.py  # 终端1
npm run dev           # 终端2（在frontend目录）

# 或修改playwright.config.ts中的reuseExistingServer
```

### 4. 浏览器安装问题

**问题**: `Executable doesn't exist`

**解决**:
```bash
# 重新安装浏览器
npx playwright install chromium --force
```

---

## 📊 测试报告

测试完成后会生成多种格式的报告：

### HTML报告
- 位置: `playwright-report/index.html`
- 查看: `npm run report`
- 包含: 所有测试结果、截图、视频、追踪文件

### JSON报告
- 位置: `test-results/results.json`
- 用途: CI/CD集成、自定义分析

### 控制台输出
- 实时显示测试进度
- 显示每个测试用例的执行时间
- 显示失败原因

---

## 🔄 CI/CD集成

### GitHub Actions示例

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          cd tests/e2e && npm install
      
      - name: Install Playwright browsers
        run: cd tests/e2e && npx playwright install chromium
      
      - name: Run E2E tests
        run: cd tests/e2e && npm test
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: tests/e2e/playwright-report/
```

---

## 📝 添加新测试

### 1. 创建测试文件

```bash
# 在tests目录创建新的.spec.ts文件
touch tests/04-new-feature.spec.ts
```

### 2. 编写测试

```typescript
import { test, expect } from '@playwright/test';
import { waitForElement, takeScreenshot } from '../helpers/test-helpers';

test.describe('新功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });
  
  test('测试用例', async ({ page }) => {
    // 测试逻辑
    await takeScreenshot(page, 'new-feature');
  });
});
```

### 3. 运行测试

```bash
npx playwright test tests/04-new-feature.spec.ts
```

---

## 🎯 测试目标

- ✅ **覆盖率**: 核心功能100%覆盖
- ✅ **稳定性**: 测试通过率 >95%
- ✅ **速度**: 所有测试 <5分钟
- ✅ **可维护性**: 使用Page Object模式
- ✅ **可读性**: 清晰的测试描述

---

## 📚 参考文档

- [Playwright官方文档](https://playwright.dev/)
- [Playwright最佳实践](https://playwright.dev/docs/best-practices)
- [测试选择器](https://playwright.dev/docs/selectors)
- [调试指南](https://playwright.dev/docs/debug)

---

**最后更新**: 2025-10-30  
**维护者**: AI Development Team  
**版本**: 1.0.0
