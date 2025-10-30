#!/bin/bash

# 测试时间工具的完整流程

echo "🧪 测试时间工具 - 完整思维链展示"
echo "=================================="
echo ""

# 清空思维链
echo "1️⃣ 清空旧的思维链..."
curl -s -X DELETE http://localhost:8000/api/thinking/history/test-session > /dev/null
echo "✅ 已清空"
echo ""

# 发送测试消息
echo "2️⃣ 发送测试消息: '现在几点了'"
response=$(curl -s -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "现在几点了",
    "provider": "siliconflow",
    "memory": true
  }')

echo "✅ AI回复:"
echo "$response" | python3 -m json.tool | grep -A 2 '"response"'
echo ""

# 等待思维链完成
echo "3️⃣ 等待思维链完成..."
sleep 2
echo ""

# 获取思维链
echo "4️⃣ 获取思维链数据:"
curl -s http://localhost:8000/api/thinking/history/test-session | python3 -m json.tool
echo ""

echo "=================================="
echo "✅ 测试完成！"
echo ""
echo "📊 检查要点:"
echo "  1. 思维链应该包含 4 个步骤"
echo "  2. 应该有 chain_start"
echo "  3. 应该有 action (tool: time)"
echo "  4. 应该有 observation (工具结果)"
echo "  5. 应该有 chain_end"
echo ""
echo "🌐 前端测试:"
echo "  1. 打开 http://localhost:3000"
echo "  2. 选择 test-session 会话（或新建会话）"
echo "  3. 发送: 现在几点了"
echo "  4. 应该看到思维链展示（带AI头像）"

