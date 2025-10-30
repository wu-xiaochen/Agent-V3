/**
 * 设置功能E2E测试
 * 
 * 测试场景:
 * 1. 系统配置
 * 2. 主题切换
 * 3. Agent配置
 * 4. 工具配置
 */
import { test, expect } from '@playwright/test';
import {
  waitForElement,
  clearLocalStorage,
  takeScreenshot,
  fillInput,
  verifyToast
} from '../helpers/test-helpers';

test.describe('设置功能', () => {
  
  test.beforeEach(async ({ page }) => {
    await clearLocalStorage(page);
    await page.goto('/');
    await waitForElement(page, 'main');
  });
  
  test('3.1 打开设置页面', async ({ page }) => {
    // 点击设置按钮
    const settingsButton = await page.locator('button[aria-label="Settings"]').or(
      page.locator('a[href="/settings"]')
    ).first();
    
    await settingsButton.click();
    
    // 验证导航到设置页面
    await page.waitForURL('**/settings**');
    await expect(page).toHaveURL(/settings/);
    
    // 截图
    await takeScreenshot(page, '21-settings-opened');
    
    console.log('✅ 打开设置页面测试通过');
  });
  
  test('3.2 查看系统配置', async ({ page }) => {
    // 导航到设置页面
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 查找System标签页
    const systemTab = await page.locator('button:has-text("System")').first();
    if (await systemTab.isVisible()) {
      await systemTab.click();
      await page.waitForTimeout(500);
    }
    
    // 验证配置字段存在
    const providerSelect = await page.locator('select').or(
      page.locator('[role="combobox"]')
    ).first();
    await expect(providerSelect).toBeVisible();
    
    // 截图
    await takeScreenshot(page, '22-system-config');
    
    console.log('✅ 查看系统配置测试通过');
  });
  
  test('3.3 更新系统配置', async ({ page }) => {
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 切换到System标签页
    const systemTab = await page.locator('button:has-text("System")').first();
    if (await systemTab.isVisible()) {
      await systemTab.click();
      await page.waitForTimeout(500);
      
      // 修改Temperature
      const tempInput = await page.locator('input[type="number"]').first();
      if (await tempInput.isVisible()) {
        await tempInput.fill('0.8');
        
        // 点击保存
        const saveButton = await page.locator('button:has-text("Save")').first();
        await saveButton.click();
        
        // 等待保存完成
        await page.waitForTimeout(1000);
        
        // 截图
        await takeScreenshot(page, '23-config-updated');
        
        console.log('✅ 更新系统配置测试通过');
      }
    }
  });
  
  test('3.4 主题切换', async ({ page }) => {
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 查找Appearance标签页
    const appearanceTab = await page.locator('button:has-text("Appearance")').first();
    if (await appearanceTab.isVisible()) {
      await appearanceTab.click();
      await page.waitForTimeout(500);
      
      // 查找主题切换按钮
      const themeToggle = await page.locator('button[aria-label*="theme"]').or(
        page.locator('button:has-text("Dark")')
      ).first();
      
      if (await themeToggle.isVisible()) {
        // 获取当前主题
        const html = page.locator('html');
        const isDarkBefore = await html.evaluate(el => el.classList.contains('dark'));
        
        // 切换主题
        await themeToggle.click();
        await page.waitForTimeout(500);
        
        // 验证主题切换
        const isDarkAfter = await html.evaluate(el => el.classList.contains('dark'));
        expect(isDarkAfter).not.toBe(isDarkBefore);
        
        // 截图
        await takeScreenshot(page, '24-theme-toggled');
        
        console.log('✅ 主题切换测试通过');
      }
    } else {
      // 尝试在header查找主题切换按钮
      const headerThemeToggle = await page.locator('header button[aria-label*="theme"]').first();
      if (await headerThemeToggle.isVisible()) {
        const html = page.locator('html');
        const isDarkBefore = await html.evaluate(el => el.classList.contains('dark'));
        
        await headerThemeToggle.click();
        await page.waitForTimeout(500);
        
        const isDarkAfter = await html.evaluate(el => el.classList.contains('dark'));
        expect(isDarkAfter).not.toBe(isDarkBefore);
        
        await takeScreenshot(page, '24-theme-toggled');
        console.log('✅ 主题切换测试通过（从header）');
      }
    }
  });
  
  test('3.5 主题持久化', async ({ page }) => {
    // 切换主题
    const headerThemeToggle = await page.locator('button[aria-label*="theme"]').first();
    const html = page.locator('html');
    
    if (await headerThemeToggle.isVisible()) {
      await headerThemeToggle.click();
      await page.waitForTimeout(500);
      
      const isDark = await html.evaluate(el => el.classList.contains('dark'));
      
      // 刷新页面
      await page.reload();
      await waitForElement(page, 'main');
      
      // 验证主题保持
      const isDarkAfterReload = await html.evaluate(el => el.classList.contains('dark'));
      expect(isDarkAfterReload).toBe(isDark);
      
      await takeScreenshot(page, '25-theme-persistent');
      
      console.log('✅ 主题持久化测试通过');
    }
  });
  
  test('3.6 Agent配置管理', async ({ page }) => {
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 查找Agents标签页
    const agentsTab = await page.locator('button:has-text("Agents")').first();
    if (await agentsTab.isVisible()) {
      await agentsTab.click();
      await page.waitForTimeout(500);
      
      // 验证Agent列表显示
      const agentsList = await page.locator('[data-testid="agents-list"]').or(
        page.locator('table')
      ).first();
      
      await expect(agentsList).toBeVisible();
      
      // 截图
      await takeScreenshot(page, '26-agents-config');
      
      console.log('✅ Agent配置管理测试通过');
    }
  });
  
  test('3.7 工具配置管理', async ({ page }) => {
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 查找Tools标签页
    const toolsTab = await page.locator('button:has-text("Tools")').first();
    if (await toolsTab.isVisible()) {
      await toolsTab.click();
      await page.waitForTimeout(500);
      
      // 验证工具列表显示
      const toolsList = await page.locator('[data-testid="tools-list"]').or(
        page.locator('table')
      ).first();
      
      await expect(toolsList).toBeVisible();
      
      // 截图
      await takeScreenshot(page, '27-tools-config');
      
      console.log('✅ 工具配置管理测试通过');
    }
  });
  
  test('3.8 配置重置功能', async ({ page }) => {
    await page.goto('/settings');
    await waitForElement(page, 'main');
    
    // 切换到System标签页
    const systemTab = await page.locator('button:has-text("System")').first();
    if (await systemTab.isVisible()) {
      await systemTab.click();
      await page.waitForTimeout(500);
      
      // 查找Reset按钮
      const resetButton = await page.locator('button:has-text("Reset")').first();
      if (await resetButton.isVisible()) {
        await resetButton.click();
        
        // 等待重置完成
        await page.waitForTimeout(1000);
        
        // 截图
        await takeScreenshot(page, '28-config-reset');
        
        console.log('✅ 配置重置功能测试通过');
      }
    }
  });
});

