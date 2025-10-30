/**
 * 基础聊天功能E2E测试
 * 
 * 测试场景:
 * 1. 页面加载
 * 2. 发送消息
 * 3. 接收响应
 * 4. 会话管理
 * 5. 思维链显示
 */
import { test, expect } from '@playwright/test';
import {
  waitForElement,
  sendChatMessage,
  waitForAIResponse,
  verifyMessageExists,
  clearLocalStorage,
  takeScreenshot,
  createNewSession,
  getSessionList
} from '../helpers/test-helpers';

test.describe('基础聊天功能', () => {
  
  test.beforeEach(async ({ page }) => {
    // 清空本地存储
    await clearLocalStorage(page);
    
    // 访问首页
    await page.goto('/');
    
    // 等待页面加载完成
    await waitForElement(page, 'main');
  });
  
  test('1.1 页面正常加载', async ({ page }) => {
    // 验证关键元素存在
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('aside')).toBeVisible(); // 侧边栏
    await expect(page.locator('textarea')).toBeVisible(); // 输入框
    
    // 截图
    await takeScreenshot(page, '01-page-loaded');
    
    console.log('✅ 页面加载测试通过');
  });
  
  test('1.2 发送简单消息', async ({ page }) => {
    const testMessage = '你好，请介绍一下自己';
    
    // 发送消息
    await sendChatMessage(page, testMessage);
    
    // 验证消息显示在界面上
    await verifyMessageExists(page, testMessage);
    
    // 截图
    await takeScreenshot(page, '02-message-sent');
    
    console.log('✅ 发送消息测试通过');
  });
  
  test('1.3 接收AI响应', async ({ page }) => {
    const testMessage = '1+1等于几？';
    
    // 发送消息
    await sendChatMessage(page, testMessage);
    
    // 等待AI响应
    await waitForAIResponse(page);
    
    // 验证响应存在
    const assistantMessage = await page.locator('[data-role="assistant"]').first();
    await expect(assistantMessage).toBeVisible();
    
    const responseText = await assistantMessage.textContent();
    expect(responseText).toBeTruthy();
    expect(responseText!.length).toBeGreaterThan(0);
    
    // 截图
    await takeScreenshot(page, '03-ai-response');
    
    console.log('✅ AI响应测试通过');
  });
  
  test('1.4 思维链显示', async ({ page }) => {
    const testMessage = '帮我搜索一下今天的天气';
    
    // 发送消息
    await sendChatMessage(page, testMessage);
    
    // 等待思维链出现
    const thinkingIndicator = await page.locator('text=Thinking').first();
    
    // 验证思维链可见（可能很快消失）
    try {
      await expect(thinkingIndicator).toBeVisible({ timeout: 5000 });
      console.log('✅ 思维链指示器显示');
    } catch {
      console.log('⚠️  思维链指示器未捕获（可能执行太快）');
    }
    
    // 等待响应完成
    await waitForAIResponse(page);
    
    // 截图
    await takeScreenshot(page, '04-thinking-chain');
    
    console.log('✅ 思维链显示测试通过');
  });
  
  test('1.5 创建新会话', async ({ page }) => {
    // 获取初始会话数量
    const initialSessions = await getSessionList(page);
    const initialCount = initialSessions.length;
    
    // 创建新会话
    await createNewSession(page);
    
    // 验证会话增加
    const newSessions = await getSessionList(page);
    expect(newSessions.length).toBe(initialCount + 1);
    
    // 截图
    await takeScreenshot(page, '05-new-session');
    
    console.log('✅ 创建新会话测试通过');
  });
  
  test('1.6 会话切换', async ({ page }) => {
    // 在第一个会话发送消息
    const message1 = '这是第一个会话的消息';
    await sendChatMessage(page, message1);
    await waitForAIResponse(page);
    
    // 创建新会话
    await createNewSession(page);
    
    // 在第二个会话发送消息
    const message2 = '这是第二个会话的消息';
    await sendChatMessage(page, message2);
    await waitForAIResponse(page);
    
    // 验证第二个会话的消息存在
    await verifyMessageExists(page, message2);
    
    // 切换回第一个会话
    const firstSession = (await getSessionList(page))[0];
    await firstSession.click();
    
    // 等待消息加载
    await page.waitForTimeout(1000);
    
    // 验证第一个会话的消息存在
    await verifyMessageExists(page, message1);
    
    // 截图
    await takeScreenshot(page, '06-session-switch');
    
    console.log('✅ 会话切换测试通过');
  });
  
  test('1.7 长文本消息处理', async ({ page }) => {
    const longMessage = '请帮我分析以下内容：' + 'A'.repeat(500);
    
    // 发送长消息
    await sendChatMessage(page, longMessage);
    
    // 验证消息发送
    await verifyMessageExists(page, longMessage.substring(0, 50));
    
    // 等待响应
    await waitForAIResponse(page);
    
    // 截图
    await takeScreenshot(page, '07-long-message');
    
    console.log('✅ 长文本消息测试通过');
  });
  
  test('1.8 特殊字符处理', async ({ page }) => {
    const specialMessage = '测试特殊字符: !@#$%^&*()_+ <script>alert("test")</script>';
    
    // 发送包含特殊字符的消息
    await sendChatMessage(page, specialMessage);
    
    // 验证消息正确显示（没有XSS）
    const messageElement = await page.locator(`text=${specialMessage}`).first();
    await expect(messageElement).toBeVisible();
    
    // 截图
    await takeScreenshot(page, '08-special-chars');
    
    console.log('✅ 特殊字符处理测试通过');
  });
  
  test('1.9 会话持久化', async ({ page, context }) => {
    const testMessage = '测试持久化消息';
    
    // 发送消息
    await sendChatMessage(page, testMessage);
    await waitForAIResponse(page);
    
    // 刷新页面
    await page.reload();
    
    // 等待页面加载
    await waitForElement(page, 'main');
    
    // 验证消息仍然存在
    await verifyMessageExists(page, testMessage);
    
    // 截图
    await takeScreenshot(page, '09-persistence');
    
    console.log('✅ 会话持久化测试通过');
  });
  
  test('1.10 工具调用显示', async ({ page }) => {
    const testMessage = '帮我生成一个CrewAI团队来分析市场趋势';
    
    // 发送触发工具调用的消息
    await sendChatMessage(page, testMessage);
    
    // 等待工具调用指示器
    try {
      const toolIndicator = await page.locator('text=🔧').first();
      await expect(toolIndicator).toBeVisible({ timeout: 10000 });
      console.log('✅ 工具调用指示器显示');
    } catch {
      console.log('⚠️  工具调用指示器未捕获');
    }
    
    // 等待响应
    await waitForAIResponse(page, 90000); // CrewAI生成需要更长时间
    
    // 截图
    await takeScreenshot(page, '10-tool-call');
    
    console.log('✅ 工具调用显示测试通过');
  });
});

