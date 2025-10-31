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
 */
export async function clearLocalStorage(page: Page) {
  try {
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  } catch (error) {
    // 忽略安全错误（在某些环境下可能被阻止）
    console.log('⚠️ 无法清空localStorage:', error);
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
  const input = await waitForElement(page, 'textarea[placeholder*="Message"]');
  await input.fill(message);
  await page.click('button[type="submit"]');
}

/**
 * 等待AI响应
 */
export async function waitForAIResponse(page: Page, timeout = 60000) {
  // 等待思维链完成
  await waitForThinkingComplete(page, timeout);
  
  // 等待响应消息出现
  await waitForElement(page, '[data-role="assistant"]', timeout);
}

/**
 * 验证消息存在
 */
export async function verifyMessageExists(page: Page, content: string) {
  const message = await page.locator(`text=${content}`).first();
  await expect(message).toBeVisible();
}

