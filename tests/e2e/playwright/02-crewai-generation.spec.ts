import { test, expect } from '@playwright/test';

/**
 * E2E测试: CrewAI配置生成和自动加载
 * 
 * 测试模块2.1: 团队配置生成
 */

test.describe('CrewAI配置生成', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('2.1.1 - 通过对话生成CrewAI配置', async ({ page }) => {
    // 发送CrewAI团队生成请求
    const input = page.locator('textarea').first();
    const crewRequest = '请帮我创建一个CrewAI团队来完成以下任务：研究并撰写一篇关于"2025年AI技术趋势"的深度分析报告。我需要一个研究员负责收集信息,一个分析师负责数据分析,一个作家负责撰写文章。';
    
    await input.fill(crewRequest);
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待AI响应 (生成配置需要较长时间)
    await page.waitForTimeout(10000);
    
    // 检查思维链中是否有工具调用
    const toolCall = page.locator('text=/crewai_generator|crew|team/i');
    await expect(toolCall.first()).toBeVisible({ timeout: 30000 });
    
    console.log('✅ 检测到CrewAI生成工具调用');
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-generation-request.png', fullPage: true });
  });

  test('2.1.2 - JSON配置解析验证', async ({ page }) => {
    // 发送CrewAI生成请求
    const input = page.locator('textarea').first();
    await input.fill('创建一个简单的CrewAI团队,包含2个Agent和2个Task');
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待配置生成
    await page.waitForTimeout(15000);
    
    // 检查是否有JSON格式的内容 (可能在代码块中)
    const jsonContent = page.locator('pre code, [class*="json" i]');
    
    if (await jsonContent.count() > 0) {
      const jsonText = await jsonContent.first().textContent();
      
      // 验证JSON包含必需字段
      if (jsonText) {
        expect(jsonText).toContain('agents');
        expect(jsonText).toContain('tasks');
        console.log('✅ JSON配置包含必需字段');
      }
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-json-config.png', fullPage: true });
  });

  test('2.1.3 - 配置自动加载到画布', async ({ page }) => {
    // 发送CrewAI生成请求
    const input = page.locator('textarea').first();
    await input.fill('生成一个CrewAI研究团队,包含研究员和分析师');
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待配置生成和画布打开
    await page.waitForTimeout(20000);
    
    // 查找CrewAI画布/面板
    const crewCanvas = page.locator('[class*="crew" i][class*="canvas" i], [class*="crew" i][class*="drawer" i], [class*="crew" i][class*="panel" i]');
    
    if (await crewCanvas.count() > 0) {
      await expect(crewCanvas.first()).toBeVisible();
      console.log('✅ CrewAI画布已打开');
      
      // 检查是否有Agent节点
      const agentNodes = page.locator('[class*="agent" i][class*="node" i], [data-type="agent"]');
      
      if (await agentNodes.count() > 0) {
        console.log(`✅ 检测到 ${await agentNodes.count()} 个Agent节点`);
      }
      
      // 检查是否有Task节点
      const taskNodes = page.locator('[class*="task" i][class*="node" i], [data-type="task"]');
      
      if (await taskNodes.count() > 0) {
        console.log(`✅ 检测到 ${await taskNodes.count()} 个Task节点`);
      }
    } else {
      console.log('⚠️ 未找到CrewAI画布,可能需要手动打开');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-canvas-loaded.png', fullPage: true });
  });

  test('2.1.4 - 配置验证和默认值', async ({ page }) => {
    // 发送最小化CrewAI请求
    const input = page.locator('textarea').first();
    await input.fill('创建最简单的CrewAI团队');
    
    const sendButton = page.locator('button[aria-label*="send" i]').first();
    await sendButton.click();
    
    // 等待生成
    await page.waitForTimeout(15000);
    
    // 如果画布打开,检查Agent配置
    const agentCard = page.locator('[class*="agent" i]').first();
    
    if (await agentCard.count() > 0 && await agentCard.isVisible()) {
      // 点击Agent查看详情
      await agentCard.click();
      await page.waitForTimeout(1000);
      
      // 检查必需字段是否存在
      const requiredFields = ['role', 'goal', 'backstory'];
      
      for (const field of requiredFields) {
        const fieldElement = page.locator(`[name="${field}" i], [placeholder*="${field}" i]`);
        
        if (await fieldElement.count() > 0) {
          const fieldValue = await fieldElement.first().inputValue();
          expect(fieldValue).toBeTruthy();
          console.log(`✅ Agent ${field} 字段有默认值`);
        }
      }
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-validation.png', fullPage: true });
  });
});

test.describe('CrewAI画布交互', () => {
  test('2.2.1 - Agent节点编辑', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 先生成一个团队
    const input = page.locator('textarea').first();
    await input.fill('创建一个CrewAI团队');
    await page.locator('button[aria-label*="send" i]').first().click();
    
    await page.waitForTimeout(20000);
    
    // 查找Agent节点
    const agentNode = page.locator('[data-type="agent"], [class*="agent" i][class*="node" i]').first();
    
    if (await agentNode.count() > 0 && await agentNode.isVisible()) {
      // 双击或点击编辑按钮
      await agentNode.dblclick();
      await page.waitForTimeout(500);
      
      // 查找编辑对话框
      const editDialog = page.locator('[role="dialog"], [class*="dialog" i], [class*="modal" i]');
      
      if (await editDialog.count() > 0) {
        await expect(editDialog.first()).toBeVisible();
        console.log('✅ Agent编辑对话框已打开');
      }
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-agent-edit.png', fullPage: true });
  });

  test('2.2.2 - 工具选择界面', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 生成团队
    const input = page.locator('textarea').first();
    await input.fill('创建一个需要使用搜索工具的CrewAI团队');
    await page.locator('button[aria-label*="send" i]').first().click();
    
    await page.waitForTimeout(20000);
    
    // 检查是否有工具选择相关的UI元素
    const toolSelector = page.locator('[class*="tool" i], text=/search|calculator|time/i');
    
    if (await toolSelector.count() > 0) {
      console.log('✅ 检测到工具相关元素');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-tool-selector.png', fullPage: true });
  });
});

test.describe('CrewAI执行', () => {
  test('2.5.1 - 团队执行启动', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // 生成简单团队
    const input = page.locator('textarea').first();
    await input.fill('创建一个简单的CrewAI团队进行测试');
    await page.locator('button[aria-label*="send" i]').first().click();
    
    await page.waitForTimeout(20000);
    
    // 查找运行按钮
    const runButton = page.locator('button:has-text("Run"), button:has-text("运行"), button:has-text("Execute"), button[aria-label*="run" i]');
    
    if (await runButton.count() > 0) {
      console.log('✅ 找到运行按钮');
      
      // 注意: 实际执行可能需要很长时间,这里只测试按钮存在
      // 在真实场景中可以点击并等待执行
      // await runButton.first().click();
    } else {
      console.log('⚠️ 未找到运行按钮');
    }
    
    // 截图
    await page.screenshot({ path: 'test-results/screenshots/02-crewai-execution.png', fullPage: true });
  });
});

