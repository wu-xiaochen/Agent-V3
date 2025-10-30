import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E测试配置
 * 
 * 用于Agent-V3项目的端到端测试
 */
export default defineConfig({
  // 测试目录
  testDir: '../tests/e2e/playwright',
  
  // 完整的测试报告
  fullyParallel: true,
  
  // 禁止在CI中运行重试
  forbidOnly: !!process.env.CI,
  
  // CI中失败重试一次
  retries: process.env.CI ? 1 : 0,
  
  // 并发worker数量
  workers: process.env.CI ? 1 : undefined,
  
  // 测试报告
  reporter: [
    ['html', { outputFolder: '../test-results/html' }],
    ['json', { outputFile: '../test-results/results.json' }],
    ['list']
  ],
  
  // 全局配置
  use: {
    // Base URL
    baseURL: 'http://localhost:3000',
    
    // 截图
    screenshot: 'only-on-failure',
    
    // 视频
    video: 'retain-on-failure',
    
    // 追踪
    trace: 'on-first-retry',
    
    // 浏览器上下文选项
    viewport: { width: 1920, height: 1080 },
    
    // 忽略HTTPS错误
    ignoreHTTPSErrors: true,
    
    // 等待导航完成
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  
  // 配置测试项目
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  
  // Web服务器配置(可选 - 自动启动开发服务器)
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    stdout: 'ignore',
    stderr: 'pipe',
  },
});

