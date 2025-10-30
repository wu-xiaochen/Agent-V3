import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E测试配置
 * 
 * 测试目标:
 * - 基础聊天功能
 * - CrewAI完整流程
 * - 设置功能
 * - 知识库管理
 */
export default defineConfig({
  testDir: './tests',
  
  // 测试超时设置
  timeout: 60 * 1000, // 60秒
  expect: {
    timeout: 10 * 1000, // 10秒
  },
  
  // 失败时重试次数
  retries: process.env.CI ? 2 : 0,
  
  // 并行工作线程数
  workers: process.env.CI ? 1 : undefined,
  
  // 测试报告配置
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['list']
  ],
  
  // 全局测试配置
  use: {
    // 基础URL（前端服务）
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // 追踪配置（失败时）
    trace: 'on-first-retry',
    
    // 截图配置
    screenshot: 'only-on-failure',
    
    // 视频配置
    video: 'retain-on-failure',
    
    // 浏览器上下文配置
    viewport: { width: 1920, height: 1080 },
    
    // 操作超时
    actionTimeout: 15 * 1000,
    navigationTimeout: 30 * 1000,
  },
  
  // 测试项目配置（不同浏览器）
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    
    // 可选：其他浏览器
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
    
    // 移动端测试
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
  ],
  
  // Web服务器配置（自动启动）
  webServer: [
    {
      command: 'cd ../.. && python api_server.py',
      port: 8000,
      timeout: 30 * 1000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'cd ../../frontend && npm run dev',
      port: 3000,
      timeout: 60 * 1000,
      reuseExistingServer: !process.env.CI,
    },
  ],
});

