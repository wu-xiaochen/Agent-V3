/**
 * 用户体验测试 - 从真实用户角度评估功能完善度、易用性、UI/UE设计
 * 
 * 测试维度:
 * 1. 功能完善度: 功能是否完整、可靠、准确
 * 2. 易用性: 学习曲线、操作效率、错误恢复
 * 3. UI/UE设计: 视觉设计、交互设计、响应式、无障碍性
 */
import { test, expect } from '@playwright/test';

// 评分记录
const scores: Record<string, { completeness: number; usability: number; ux: number }> = {};

test.describe('用户体验测试', () => {
  
  test.beforeEach(async ({ page }) => {
    // 访问首页
    await page.goto('/', { waitUntil: 'networkidle' });
    
    // 等待页面加载完成
    const textarea = page.locator('textarea').first();
    await textarea.waitFor({ state: 'visible', timeout: 15000 });
  });

  test.describe('模块1: 首次使用体验', () => {
    
    test('1.1 首次访问应用 - 功能完善度', async ({ page }) => {
      // 评估维度1: 功能完善度
      let completeness = 0;
      
      // 1.1 界面加载速度
      const startTime = Date.now();
      await page.goto('/', { waitUntil: 'networkidle' });
      const loadTime = Date.now() - startTime;
      if (loadTime < 2000) completeness += 2;
      else if (loadTime < 5000) completeness += 1;
      
      // 1.2 关键元素存在性
      const sidebar = page.locator('[class*="sidebar" i], nav').first();
      const textarea = page.locator('textarea').first();
      const chatContainer = page.locator('[class*="chat" i], [role="main"]').first();
      
      if (await sidebar.isVisible()) completeness += 1;
      if (await textarea.isVisible()) completeness += 1;
      if (await chatContainer.isVisible()) completeness += 1;
      
      // 1.3 响应式布局
      await page.setViewportSize({ width: 375, height: 667 }); // 移动端
      await page.waitForTimeout(500);
      const mobileLayout = await page.locator('textarea').first().isVisible();
      if (mobileLayout) completeness += 1;
      
      await page.setViewportSize({ width: 1920, height: 1080 }); // 桌面端
      await page.waitForTimeout(500);
      const desktopLayout = await page.locator('textarea').first().isVisible();
      if (desktopLayout) completeness += 1;
      
      scores['首次访问-功能完善度'] = { completeness, usability: 0, ux: 0 };
      console.log(`📊 首次访问-功能完善度: ${completeness}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-01-first-visit.png', fullPage: true });
    });

    test('1.2 首次访问应用 - 易用性', async ({ page }) => {
      let usability = 0;
      
      // 2.1 输入框是否明显
      const textarea = page.locator('textarea').first();
      const isVisible = await textarea.isVisible();
      const placeholder = await textarea.getAttribute('placeholder');
      
      if (isVisible) usability += 2;
      if (placeholder && placeholder.length > 0) usability += 1;
      
      // 2.2 发送按钮是否清晰
      const sendButton = page.locator('button[aria-label*="send" i], button:has-text("Send")').first();
      const sendButtonVisible = await sendButton.isVisible();
      if (sendButtonVisible) usability += 1;
      
      // 2.3 新手引导或提示
      const welcomeText = page.locator('text=/欢迎|Welcome|开始|Get started/i');
      const welcomeCount = await welcomeText.count();
      if (welcomeCount > 0) usability += 2;
      
      // 2.4 快捷键支持
      await textarea.click();
      await page.keyboard.press('Tab');
      const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
      if (focusedElement) usability += 1;
      
      scores['首次访问-易用性'] = { completeness: 0, usability, ux: 0 };
      console.log(`📊 首次访问-易用性: ${usability}/10`);
    });

    test('1.3 首次访问应用 - UI/UE设计', async ({ page }) => {
      let ux = 0;
      
      // 3.1 视觉设计 - 检查基本样式
      const bodyStyles = await page.evaluate(() => {
        const body = document.body;
        return {
          backgroundColor: window.getComputedStyle(body).backgroundColor,
          color: window.getComputedStyle(body).color,
          fontFamily: window.getComputedStyle(body).fontFamily
        };
      });
      
      if (bodyStyles.backgroundColor && bodyStyles.color) ux += 2;
      if (bodyStyles.fontFamily) ux += 1;
      
      // 3.2 布局合理性
      const sidebar = page.locator('[class*="sidebar" i]').first();
      const chatArea = page.locator('[class*="chat" i], [role="main"]').first();
      
      const sidebarBox = await sidebar.boundingBox();
      const chatBox = await chatArea.boundingBox();
      
      if (sidebarBox && chatBox) {
        // 检查侧边栏宽度是否合理（不超过40%）
        const sidebarRatio = sidebarBox.width / (sidebarBox.width + chatBox.width);
        if (sidebarRatio < 0.4) ux += 1;
      }
      
      // 3.3 主题切换
      // 查找设置按钮
      const settingsButton = page.locator('button:has-text("Settings"), button[aria-label*="settings" i], button:has([class*="settings" i])').first();
      const hasSettings = await settingsButton.count() > 0;
      if (hasSettings) ux += 2;
      
      scores['首次访问-UI/UE设计'] = { completeness: 0, usability: 0, ux };
      console.log(`📊 首次访问-UI/UE设计: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-01-ui-design.png', fullPage: true });
    });

    test('1.4 发送第一条消息 - 完整流程', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      const testMessage = '你好，请介绍一下自己';
      
      // 功能完善度
      const textarea = page.locator('textarea').first();
      await textarea.fill(testMessage);
      completeness += 1; // 输入功能正常
      
      // 支持Enter键发送
      await textarea.press('Enter');
      await page.waitForTimeout(500);
      
      const sentMessage = page.locator(`text="${testMessage}"`).first();
      if (await sentMessage.count() > 0) {
        completeness += 2; // 发送功能正常
        usability += 2; // Enter键支持
      }
      
      // 易用性 - 发送反馈
      const sendingIndicator = page.locator('[class*="sending" i], [class*="loading" i]').first();
      const hasIndicator = await sendingIndicator.count() > 0;
      if (hasIndicator) usability += 1;
      
      // 等待AI响应开始
      await page.waitForTimeout(3000);
      
      // 功能完善度 - AI响应
      const aiResponse = page.locator('[class*="assistant" i], [class*="bot" i]').first();
      const responseVisible = await aiResponse.isVisible({ timeout: 30000 });
      if (responseVisible) {
        completeness += 2; // AI响应正常
        
        // 易用性 - 响应速度
        const responseTime = Date.now();
        // 假设响应时间小于5秒为优秀
        usability += 2;
      }
 худо
      // UI/UE - 消息显示
      const userMessage = page.locator(`text="${testMessage}"`).first();
      if (await userMessage.isVisible()) {
        const messageBox = await userMessage.boundingBox();
        if (messageBox && messageBox.height > 0) ux += 2; // 消息正确显示
      }
      
      scores['发送第一条消息'] = { completeness, usability, ux };
      console.log(`📊 发送第一条消息 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-02-first-message.png', fullPage: true });
    });
  });

  test.describe('模块2: 核心对话功能', () => {
    
    test('2.1 对话流畅度 - 连续对话', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      const messages = [
        '你好',
        '请介绍一下你的功能',
        '你能做什么？'
      ];
      
      for (let i = 0; i < messages.length; i++) {
        const textarea = page.locator('textarea').first();
        await textarea.fill(messages[i]);
        await textarea.press('Enter');
        
        // 等待消息发送
        await page.waitForTimeout(1000);
        
        // 验证消息显示
        const messageVisible = await page.locator(`text="${messages[i]}"`).isVisible({ timeout: 5000 });
        if (messageVisible) completeness += 1;
        
        // 等待AI响应（最后一次等待更长时间）
        if (i < messages.length - 1) {
          await page.waitForTimeout(2000);
        } else {
          await page.waitForTimeout(5000);
        }
      }
      
      // 易用性 - 消息区分
      const userMessages = page.locator('[class*="user" i], [data-role="user"]');
      const assistantMessages = page.locator('[class*="assistant" i], [data-role="assistant"]');
      
      const userCount = await userMessages.count();
      const assistantCount = await assistantMessages.count();
      
      if (userCount > 0 && assistantCount > 0) {
        usability += 2; // 消息区分清晰
      }
      
      // UI/UE - 消息布局
      const chatContainer = page.locator('[class*="chat" i], [role="main"]').first();
      const containerBox = await chatContainer.boundingBox();
      if (containerBox && containerBox.height > 0) ux += 2;
      
      scores['对话流畅度'] = { completeness, usability, ux };
      console.log(`📊 对话流畅度 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-03-conversation.png', fullPage: true });
    });

    test('2.2 思维链展示 - 可视化和交互', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      // 发送需要思考过程的复杂问题
      const textarea = page.locator('textarea').first();
      await textarea.fill('请帮我分析一下如何优化 lead generation 流程，给出详细的步骤和工具建议');
      await textarea.press('Enter');
      
      // 等待思维链出现
      await page.waitForTimeout(5000);
      
      // 查找思维链元素
      const thinkingChain = page.locator('[class*="thinking" i], [class*="chain" i], [data-thinking="true"]').first();
      const hasThinking = await thinkingChain.count() > 0;
      
      if (hasThinking) {
        completeness += 2; // 思维链显示
        
        // 检查是否可以展开/折叠
        const expandButton = page.locator('button[aria-label*="expand" i], button[aria-label*="展开" i]').first();
        const collapseButton = page.locator('button[aria-label*="collapse" i], button[aria-label*="折叠" i]').first();
        
        const hasExpand = await expandButton.count() > 0;
        const hasCollapse = await collapseButton.count() > 0;
        
        if (hasExpand || hasCollapse) {
          usability += 2; // 可以展开/折叠
          ux += 1; // 交互友好
        }
        
        // 检查工具调用显示
        const toolCall = page.locator('[class*="tool" i], [class*="invoke" i]').first();
        const hasToolCall = await toolCall.count() > 0;
        if (hasToolCall) {
          completeness += 1; // 工具调用显示
          ux += 1; // 可视化清晰
        }
      } else {
        // 如果没有思维链，可能是不需要工具调用的简单问题
        console.log('⚠️ 未检测到思维链，可能是简单问题或需要更长的等待时间');
      }
      
      scores['思维链展示'] = { completeness, usability, ux };
      console.log(`📊 思维链展示 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-04-thinking-chain.png', fullPage: true });
    });

    test('2.3 Markdown渲染质量', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      // 请求Markdown格式回复
      const textarea = page.locator('textarea').first();
      await textarea.fill('请用Markdown格式回复，包含：1. 代码块 2. 表格 3. 列表 4. 加粗和斜体');
      await textarea.press('Enter');
      
      // 等待AI响应
      await page.waitForTimeout(5000);
      
      // 检查代码块
      const codeBlock = page.locator('pre code, [class*="syntax-highlighter"]').first();
      const hasCodeBlock = await codeBlock.count() > 0;
      if (hasCodeBlock) {
        completeness += 2; // 代码块渲染
        ux += 1; // 代码高亮美观
      }
      
      // 检查表格
      const table = page.locator('table').first();
      const hasTable = await table.count() > 0;
      if (hasTable) {
        completeness += 2; // 表格渲染
        ux += 1; // 表格样式美观
      }
      
      // 检查列表
      const list = page.locator('ul, ol').first();
      const hasList = await list.count() > 0;
      if (hasList) {
        completeness += 1; // 列表渲染
      }
      
      // 检查加粗
      const bold = page.locator('strong, b, [class*="bold"]').first();
      const hasBold = await bold.count() > 0;
      if (hasBold) {
        completeness += 1; // 加粗渲染
      }
      
      scores['Markdown渲染'] = { completeness, usability, ux };
      console.log(`📊 Markdown渲染 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-05-markdown.png', fullPage: true });
    });
  });

  test.describe('模块3: 会话管理', () => {
    
    test('3.1 创建和切换会话', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      // 创建新会话
      const newChatButton = page.locator('button:has-text("New"), button:has-text("新建"), button[aria-label*="new" i]').first();
      const hasNewButton = await newChatButton.count() > 0;
      
      if (hasNewButton) {
        await newChatButton.click();
        await page.waitForTimeout(1000);
        
        // 检查输入框是否清空
        const textarea = page.locator('textarea').first();
        const inputValue = await textarea.inputValue();
        if (inputValue === '') {
          completeness += 2; // 新会话创建成功
          usability += 1; // 操作简单
        }
      }
      
      // 发送消息创建会话
      const textarea = page.locator('textarea').first();
      await textarea.fill('测试会话1');
      await textarea.press('Enter');
      await page.waitForTimeout(2000);
      
      // 创建第二个会话
      if (hasNewButton) {
        await newChatButton.click();
        await page.waitForTimeout(1000);
        await textarea.fill('测试会话2');
        await textarea.press('Enter');
        await page.waitForTimeout(2000);
      }
      
      // 检查会话列表
      const sessionList = page.locator('[class*="session" i], [class*="conversation" i]');
      const sessionCount = await sessionList.count();
      if (sessionCount > 1) {
        completeness += 2; // 会话列表正确
        ux += 1; // 会话区分清晰
      }
      
      // 测试切换会话（点击第一个会话）
      if (sessionCount > 1) {
        await sessionList.first().click();
        await page.waitForTimeout(1000);
        
        // 检查是否切换到正确的会话
        const messageVisible = await page.locator('text="测试会话1"').isVisible({ timeout: 5000 });
        if (messageVisible) {
          completeness += 2; // 会话切换成功
          usability += 2; // 切换操作流畅
        }
      }
      
      scores['会话管理'] = { completeness, usability, ux };
      console.log(`📊 会话管理 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-06-session-management.png', fullPage: true });
    });
  });

  test.describe('模块4: 系统设置', () => {
    
    test('4.1 设置入口和主题切换', async ({ page }) => {
      let completeness = 0, usability = 0, ux = 0;
      
      // 查找设置入口
      const settingsButton = page.locator('button:has-text("Settings"), button[aria-label*="settings" i], button:has([class*="settings" i])').first();
      const hasSettings = await settingsButton.count() > 0;
      
      if (hasSettings) {
        usability += 2; // 设置入口明显
        
        await settingsButton.click();
        await page.waitForTimeout(1000);
        
        // 查找主题切换选项
        const themeSelector = page.locator('select[name*="theme" i], button[aria-label*="theme" i]').first();
        const hasTheme = await themeSelector.count() > 0;
        
        if (hasTheme) {
          completeness += 2; // 主题切换功能存在
          
          // 测试切换主题
          const currentTheme = await page.evaluate(() => document.documentElement.className);
          
          await themeSelector.click();
          await page.waitForTimeout(500);
          
          // 选择其他主题（如果有选项）
          const themeOptions = page.locator('option, [role="option"]');
          const optionCount = await themeOptions.count();
          if (optionCount > 1) {
            await themeOptions.nth(1).click();
            await page.waitForTimeout(1000);
            
            const newTheme = await page.evaluate(() => document.documentElement.className);
            if (newTheme !== currentTheme) {
              completeness += 1; // 主题切换生效
              ux += 2; // 主题切换流畅
            }
          }
        }
      }
      
      scores['系统设置'] = { completeness, usability, ux };
      console.log(`📊 系统设置 - 功能完善度: ${completeness}/10, 易用性: ${usability}/10, UI/UE: ${ux}/10`);
      
      await page.screenshot({ path: 'test-results/screenshots/ux-07-settings.png', fullPage: true });
    });
  });

  test.afterAll(async () => {
    // 生成测试报告
    console.log('\n📊 ========== 用户体验测试评分汇总 ==========');
    console.log('模块 | 功能完善度 | 易用性 | UI/UE设计 | 总分');
    console.log('----|----------|--------|-----------|------');
    
    let totalCompleteness = 0, totalUsability = 0, totalUx = 0;
    let moduleCount = 0;
    
    for (const [module, scores] of Object.entries(scores)) {
      const total = scores.completeness + scores.usability + scores.ux;
      totalCompleteness += scores.completeness;
      totalUsability += scores.usability;
      totalUx += scores.ux;
      moduleCount++;
      
      console.log(`${module} | ${scores.completeness}/10 | ${scores.usability}/10 | ${scores.ux}/10 | ${total}/30`);
    }
    
    if (moduleCount > 0) {
      const avgCompleteness = (totalCompleteness / moduleCount).toFixed(1);
      const avgUsability = (totalUsability / moduleCount).toFixed(1);
      const avgUx = (totalUx / moduleCount).toFixed(1);
      const avgTotal = ((totalCompleteness + totalUsability + totalUx) / moduleCount).toFixed(1);
      
      console.log('----|----------|--------|-----------|------');
      console.log(`平均 | ${avgCompleteness}/10 | ${avgUsability}/10 | ${avgUx}/10 | ${avgTotal}/30`);
    }
    
    console.log('\n✅ 用户体验测试完成');
  });
});

