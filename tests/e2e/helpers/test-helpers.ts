/**
 * E2E测试辅助函数
 */
import { Page, expect } from '@playwright/test';

/**
 * 等待元素可见并返回
 */
export async function waitForElement(page: Page, selector: string, timeout = 10000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
  return page.locator(selector);
}

/**
 * 等待API响应
 */
export async function waitForAPIResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout = 30000
) {
  return await page.waitForResponse(
    response => {
      const url = response.url();
      const matches = typeof urlPattern === 'string' 
        ? url.includes(urlPattern)
        : urlPattern.test(url);
      return matches && response.status() === 200;
    },
    { timeout }
  );
}

/**
 * 填写输入框
 */
export async function fillInput(page: Page, selector: string, value: string) {
  const input = await waitForElement(page, selector);
  await input.clear();
  await input.fill(value);
}

/**
 * 点击按钮并等待响应
 */
export async function clickAndWait(
  page: Page,
  buttonSelector: string,
  waitSelector?: string,
  timeout = 10000
) {
  await page.click(buttonSelector);
  if (waitSelector) {
    await waitForElement(page, waitSelector, timeout);
  }
}

/**
 * 截图
 */
export async function takeScreenshot(page: Page, name: string) {
  await page.screenshot({
    path: `test-results/screenshots/${name}.png`,
    fullPage: true
  });
}

/**
 * 等待加载完成
 */
export async function waitForLoadingComplete(page: Page) {
  // 等待所有loading指示器消失
  await page.waitForSelector('[data-loading="true"]', { 
    state: 'hidden', 
    timeout: 30000 
  }).catch(() => {
    // 如果没有loading元素，忽略错误
  });
}

/**
 * 验证Toast消息
 */
export async function verifyToast(page: Page, expectedMessage: string) {
  const toast = await waitForElement(page, '[role="status"]');
  const text = await toast.textContent();
  expect(text).toContain(expectedMessage);
}

/**
 * 清空本地存储
 * 安全处理：在某些环境下（如跨域、file://协议）可能无法访问localStorage
 */
export async function clearLocalStorage(page: Page) {
  try {
    // 使用字符串形式避免TypeScript类型检查
    // evaluate中的代码在浏览器环境执行，有window对象
    const canAccessStorage = await page.evaluate(() => {
      // @ts-ignore - 浏览器环境有window对象
      try {
        const testKey = '__test__';
        // @ts-ignore
        window.localStorage.setItem(testKey, 'test');
        // @ts-ignore
        window.localStorage.removeItem(testKey);
        return true;
      } catch {
        return false;
      }
    });
    
    if (canAccessStorage) {
      await page.evaluate(() => {
        // @ts-ignore - 浏览器环境有window对象
        try {
          // @ts-ignore
          window.localStorage.clear();
          // @ts-ignore
          window.sessionStorage.clear();
        } catch (e) {
          // 静默失败
        }
      });
    } else {
      console.log('⚠️ 无法访问localStorage，跳过清空操作');
    }
  } catch (error: any) {
    // 完全忽略安全错误，不让它影响测试
    if (error.message && error.message.includes('SecurityError')) {
      console.log('⚠️ localStorage访问被浏览器安全策略阻止，跳过清空操作');
      return; // 直接返回，不抛出错误
    }
    // 其他错误才抛出
    throw error;
  }
}

/**
 * 等待思维链完成
 */
export async function waitForThinkingComplete(page: Page, timeout = 60000) {
  // 等待"Thinking..."消失
  await page.waitForSelector('text=Thinking', { 
    state: 'hidden', 
    timeout 
  }).catch(() => {
    // 可能思维链很快完成
  });
}

/**
 * 获取会话列表
 */
export async function getSessionList(page: Page) {
  const sessions = await page.locator('[data-testid="session-item"]').all();
  return sessions;
}

/**
 * 创建新会话
 */
export async function createNewSession(page: Page) {
  await clickAndWait(
    page,
    '[data-testid="new-session-button"]',
    '[data-testid="session-item"]'
  );
}

/**
 * 发送聊天消息
 */
export async function sendChatMessage(page: Page, message: string) {
  // 使用更灵活的选择器查找输入框
  const input = page.locator('textarea').first();
  await input.waitFor({ state: 'visible', timeout: 10000 });
  await input.fill(message);
  
  // 查找并点击发送按钮
  const sendButton = page.locator('button[type="submit"], button:has-text("Send"), button:has-text("发送")').first();
  await sendButton.waitFor({ state: 'visible', timeout: 5000 });
  await sendButton.click();
}

/**
 * 等待AI响应
 */
export async function waitForAIResponse(page: Page, timeout = 60000) {
  // 等待思维链完成
  await waitForThinkingComplete(page, timeout);
  
  // 等待响应消息出现 - 使用更灵活的选择器
  const responseSelectors = [
    '[data-role="assistant"]',
    '[class*="bot" i]',
    '[class*="assistant" i]',
    '.bg-card', // 消息气泡的通用类
  ];
  
  // 尝试等待任一选择器匹配的元素出现
  let found = false;
  for (const selector of responseSelectors) {
    try {
      await page.waitForSelector(selector, { state: 'visible', timeout: 5000 });
      found = true;
      break;
    } catch {
      // 继续尝试下一个选择器
    }
  }
  
  if (!found) {
    // 如果所有选择器都失败，至少等待一段时间让响应加载
    await page.waitForTimeout(2000);
  }
}

/**
 * 验证消息存在
 */
export async function verifyMessageExists(page: Page, content: string) {
  const message = await page.locator(`text=${content}`).first();
  await expect(message).toBeVisible();
}

