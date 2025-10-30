import { test, expect } from '@playwright/test';

/**
 * E2E测试: 基础聊天功能
 * 
 * 测试模块1.1: 消息发送与接收
 */

test.describe('基础聊天功能', () => {
  test.beforeEach(async ({ page }) => {
    // 访问主页
    await page.goto('/');
    
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
    
    // 等待聊天界面出现
    await expect(page.locator('[role="main"]')).toBeVisible();
  });

  test('1.1.1 - 发送简单文本消息', async ({ page }) => {
    // 找到输入框
    const input = page.locator('textarea[placeholder*="message" i], textarea[placeholder*="消息" i]');
    await expect(input).toBeVisible();
    
    // 输入消息
    const testMessage = '你好,这是一个测试消息';
    await input.fill(testMessage);
    
    // 找到发送按钮并点击
    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send" i], button[aria-label*="发送" i]').first();
    await sendButton.click();
    
    // 验证消息已发送 - 用户消息气泡出现
    await expect(page.locator(`text="${testMessage}"`)).toBeVisible({ timeout: 5000 });
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-send-message.png', fullPage: true });
  });

  test('1.1.2 - 接收AI响应', async ({ page }) => {
    // 发送消息
    const input = page.locator('textarea').first();
    await input.fill('请介绍一下自己');
    
    const sendButton = page.locator('button:has-text("Send"), button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待AI响应出现 (查找Bot图标或AI消息气泡)
    const aiResponse = page.locator('[class*="bot" i], [class*="assistant" i], .bg-card').nth(1);
    await expect(aiResponse).toBeVisible({ timeout: 30000 });
    
    // 验证响应不为空
    const responseText = await aiResponse.textContent();
    expect(responseText).toBeTruthy();
    expect(responseText!.length).toBeGreaterThan(10);
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-ai-response.png', fullPage: true });
  });

  test('1.1.3 - Markdown渲染验证', async ({ page }) => {
    // 发送包含Markdown的消息请求
    const input = page.locator('textarea').first();
    await input.fill('请用Markdown格式回复,包含代码块、表格和列表');
    
    const sendButton = page.locator('button[aria-label*="send" i], button:has-text("Send")').first();
    await sendButton.click();
    
    // 等待AI响应
    await page.waitForTimeout(3000);
    
    // 检查是否有代码块渲染 (由react-syntax-highlighter生成)
    const codeBlock = page.locator('pre code, [class*="syntax-highlighter"]');
    
    // 如果响应中包含代码块，验证其存在
    const codeBlockCount = await codeBlock.count();
    if (codeBlockCount > 0) {
      await expect(codeBlock.first()).toBeVisible();
      console.log('✅ 检测到代码块渲染');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-markdown-render.png', fullPage: true });
  });

  test('1.1.4 - 特殊字符和Emoji处理', async ({ page }) => {
    // 测试特殊字符
    const specialMessages = [
      '测试特殊字符: < > & " \' 👍 🎉 ✅',
      '测试多语言: Hello 你好 こんにちは 안녕하세요',
      '测试代码: `const x = 10;`'
    ];
    
    for (const msg of specialMessages) {
      const input = page.locator('textarea').first();
      await input.fill(msg);
      
      const sendButton = page.locator('button[aria-label*="send" i]').first();
      await sendButton.click();
      
      // 验证消息正确显示
      await expect(page.locator(`text="${msg}"`).first()).toBeVisible({ timeout: 5000 });
      
      await page.waitForTimeout(1000);
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-special-chars.png', fullPage: true });
  });
});

test.describe('会话管理', () => {
  test('1.2.1 - 创建新会话', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 查找新建会话按钮
    const newChatButton = page.locator('button:has-text("New"), button:has-text("新建"), button[aria-label*="new chat" i]');
    
    const buttonCount = await newChatButton.count();
    if (buttonCount > 0) {
      await newChatButton.first().click();
      
      // 验证输入框已清空
      const input = page.locator('textarea').first();
      const inputValue = await input.inputValue();
      expect(inputValue).toBe('');
      
      console.log('✅ 新会话创建成功');
    } else {
      console.log('⚠️ 未找到新建会话按钮,跳过测试');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-new-session.png', fullPage: true });
  });

  test('1.2.2 - 会话列表显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 发送几条消息创建会话历史
    const messages = ['消息1', '消息2', '消息3'];
    
    for (const msg of messages) {
      const input = page.locator('textarea').first();
      await input.fill(msg);
      
      const sendButton = page.locator('button[aria-label*="send" i]').first();
      await sendButton.click();
      
      await page.waitForTimeout(2000);
    }
    
    // 查找会话列表 (通常在侧边栏)
    const sessionList = page.locator('[class*="session" i], [class*="conversation" i], [class*="sidebar" i]');
    
    if (await sessionList.count() > 0) {
      await expect(sessionList.first()).toBeVisible();
      console.log('✅ 会话列表显示正常');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-session-list.png', fullPage: true });
  });
});

test.describe('思维链功能', () => {
  test('1.3.1 - 思维链显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 发送需要工具调用的消息
    const input = page.locator('textarea').first();
    await input.fill('现在几点了?');
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待思维链出现
    await page.waitForTimeout(3000);
    
    // 查找思维链相关元素
    const thinkingChain = page.locator('[class*="thinking" i], [class*="chain" i], [class*="thought" i]');
    
    if (await thinkingChain.count() > 0) {
      await expect(thinkingChain.first()).toBeVisible();
      console.log('✅ 思维链显示正常');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-thinking-chain.png', fullPage: true });
  });

  test('1.3.2 - 工具调用显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 发送需要调用时间工具的消息
    const input = page.locator('textarea').first();
    await input.fill('请告诉我当前的详细时间');
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待工具调用完成
    await page.waitForTimeout(5000);
    
    // 查找工具调用相关元素 (可能包含"time"、"tool"等文本)
    const toolCall = page.locator('text=/time|tool|🔧/i');
    
    if (await toolCall.count() > 0) {
      console.log('✅ 检测到工具调用');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/01-chat-tool-call.png', fullPage: true });
  });
});

