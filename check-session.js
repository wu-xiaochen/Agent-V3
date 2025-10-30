// 快速检查localStorage中的session
// 在浏览器Console中运行此脚本

console.log("🔍 检查Session保存状态...\n");

const sessionKey = 'session_session-1';
const sessionData = localStorage.getItem(sessionKey);

if (!sessionData) {
  console.error("❌ 没有找到session_session-1");
  console.log("💡 请确保:");
  console.log("  1. 已经打开了应用");
  console.log("  2. 在正确的域名 (localhost:3000)");
  console.log("  3. 已经刷新过页面");
} else {
  console.log("✅ 找到session_session-1\n");
  
  try {
    const parsed = JSON.parse(sessionData);
    console.log("📦 Session内容:");
    console.log("  - Session ID:", parsed.sessionId);
    console.log("  - 消息数量:", parsed.messages?.length || 0);
    console.log("  - 最后更新:", parsed.timestamp);
    
    if (parsed.messages && parsed.messages.length > 0) {
      console.log("\n💬 消息列表:");
      parsed.messages.forEach((msg, index) => {
        console.log(`  ${index + 1}. [${msg.role}]: ${msg.content.substring(0, 50)}...`);
      });
    } else {
      console.log("\n⚠️  消息列表为空");
    }
    
    console.log("\n✅ Session保存正常工作！");
  } catch (e) {
    console.error("❌ 解析session数据失败:", e);
    console.log("原始数据:", sessionData);
  }
}

console.log("\n" + "=".repeat(60));
console.log("要查看完整数据，执行:");
console.log("JSON.parse(localStorage.getItem('session_session-1'))");
