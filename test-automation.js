/**
 * 自动化测试脚本
 * 在浏览器Console中执行，验证所有关键功能
 */

const AutoTest = {
  results: [],
  
  log(emoji, title, status, detail = '') {
    const result = { title, status, detail, timestamp: new Date().toISOString() }
    this.results.push(result)
    console.log(`${emoji} [${status}] ${title}${detail ? ': ' + detail : ''}`)
    return status === 'PASS'
  },
  
  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  },
  
  // 测试1: 检查侧边栏布局
  async testSidebarLayout() {
    console.log('\n━━━ 测试1: 侧边栏按钮布局 ━━━')
    
    // 检查会话列表项是否存在
    const sessionItems = document.querySelectorAll('[class*="group"][class*="flex"][class*="items-center"]')
    
    if (sessionItems.length === 0) {
      return this.log('❌', '侧边栏布局', 'FAIL', '找不到会话列表项')
    }
    
    const firstItem = sessionItems[0]
    
    // 检查内容区域
    const contentDiv = firstItem.querySelector('.pr-14')
    if (!contentDiv) {
      return this.log('❌', '侧边栏布局', 'FAIL', '找不到pr-14内容区域')
    }
    
    // 检查按钮组
    const buttonGroup = firstItem.querySelector('.absolute.right-1')
    if (!buttonGroup) {
      return this.log('❌', '侧边栏布局', 'FAIL', '找不到按钮组')
    }
    
    // 检查按钮数量
    const buttons = buttonGroup.querySelectorAll('button')
    if (buttons.length !== 2) {
      return this.log('❌', '侧边栏布局', 'FAIL', `按钮数量错误: ${buttons.length}/2`)
    }
    
    // 检查truncate类
    const titleElement = contentDiv.querySelector('.truncate')
    if (!titleElement) {
      return this.log('❌', '侧边栏布局', 'FAIL', '标题没有truncate类')
    }
    
    return this.log('✅', '侧边栏布局', 'PASS', `会话项: ${sessionItems.length}, 按钮: ${buttons.length}`)
  },
  
  // 测试2: 检查思维链持久化
  async testThinkingChainPersistence() {
    console.log('\n━━━ 测试2: 思维链持久化 ━━━')
    
    // 检查localStorage
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]')
    if (sessions.length === 0) {
      return this.log('⚠️', '思维链持久化', 'SKIP', '没有会话数据')
    }
    
    const currentSession = sessions[0].session_id
    const thinkingChains = localStorage.getItem(`thinking_chains_${currentSession}`)
    
    if (!thinkingChains) {
      return this.log('⚠️', '思维链持久化', 'SKIP', '当前会话没有思维链数据')
    }
    
    const chains = JSON.parse(thinkingChains)
    const chainCount = Object.keys(chains).length
    
    if (chainCount === 0) {
      return this.log('⚠️', '思维链持久化', 'SKIP', '思维链数据为空')
    }
    
    // 检查UI是否渲染
    const thinkingComponents = document.querySelectorAll('[class*="thinking"]')
    
    return this.log('✅', '思维链持久化', 'PASS', 
      `localStorage: ${chainCount}条, UI组件: ${thinkingComponents.length}`)
  },
  
  // 测试3: 检查会话管理
  async testSessionManagement() {
    console.log('\n━━━ 测试3: 会话管理 ━━━')
    
    const sessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]')
    
    if (sessions.length === 0) {
      return this.log('❌', '会话管理', 'FAIL', '没有会话数据')
    }
    
    // 检查会话结构
    const firstSession = sessions[0]
    const requiredFields = ['session_id', 'messages', 'last_message', 'message_count']
    const missingFields = requiredFields.filter(field => !(field in firstSession))
    
    if (missingFields.length > 0) {
      return this.log('❌', '会话管理', 'FAIL', `缺少字段: ${missingFields.join(', ')}`)
    }
    
    // 检查消息持久化
    const totalMessages = sessions.reduce((sum, s) => sum + s.message_count, 0)
    
    return this.log('✅', '会话管理', 'PASS', 
      `会话数: ${sessions.length}, 总消息数: ${totalMessages}`)
  },
  
  // 测试4: 检查API可用性
  async testAPIAvailability() {
    console.log('\n━━━ 测试4: API可用性 ━━━')
    
    try {
      // 测试后端API
      const response = await fetch('http://localhost:8000/api/health', { 
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        return this.log('✅', 'API可用性', 'PASS', '后端服务正常')
      } else {
        return this.log('❌', 'API可用性', 'FAIL', `HTTP ${response.status}`)
      }
    } catch (error) {
      return this.log('❌', 'API可用性', 'FAIL', error.message)
    }
  },
  
  // 测试5: 检查CrewAI配置
  async testCrewAIConfig() {
    console.log('\n━━━ 测试5: CrewAI配置 ━━━')
    
    try {
      const response = await fetch('http://localhost:8000/api/crewai/crews', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) {
        return this.log('❌', 'CrewAI配置', 'FAIL', `HTTP ${response.status}`)
      }
      
      const data = await response.json()
      const crewCount = data.crews ? data.crews.length : 0
      
      return this.log('✅', 'CrewAI配置', 'PASS', `已保存crew: ${crewCount}个`)
    } catch (error) {
      return this.log('❌', 'CrewAI配置', 'FAIL', error.message)
    }
  },
  
  // 运行所有测试
  async runAll() {
    console.clear()
    console.log('🚀 开始自动化测试...\n')
    console.log('═'.repeat(50))
    
    this.results = []
    
    await this.testSidebarLayout()
    await this.sleep(500)
    
    await this.testThinkingChainPersistence()
    await this.sleep(500)
    
    await this.testSessionManagement()
    await this.sleep(500)
    
    await this.testAPIAvailability()
    await this.sleep(500)
    
    await this.testCrewAIConfig()
    await this.sleep(500)
    
    // 汇总报告
    console.log('\n' + '═'.repeat(50))
    console.log('📊 测试汇总报告\n')
    
    const passed = this.results.filter(r => r.status === 'PASS').length
    const failed = this.results.filter(r => r.status === 'FAIL').length
    const skipped = this.results.filter(r => r.status === 'SKIP').length
    
    console.log(`✅ 通过: ${passed}`)
    console.log(`❌ 失败: ${failed}`)
    console.log(`⚠️ 跳过: ${skipped}`)
    console.log(`📝 总计: ${this.results.length}`)
    
    const successRate = ((passed / (passed + failed)) * 100).toFixed(1)
    console.log(`\n成功率: ${successRate}%`)
    
    console.log('\n' + '═'.repeat(50))
    
    // 返回详细结果
    return {
      summary: { passed, failed, skipped, total: this.results.length, successRate },
      details: this.results
    }
  }
}

// 导出到全局
window.AutoTest = AutoTest

console.log(`
🧪 自动化测试工具已加载！

使用方法：
1. 运行所有测试：
   AutoTest.runAll()

2. 运行单个测试：
   AutoTest.testSidebarLayout()
   AutoTest.testThinkingChainPersistence()
   AutoTest.testSessionManagement()
   AutoTest.testAPIAvailability()
   AutoTest.testCrewAIConfig()

3. 查看结果：
   AutoTest.results
`)

