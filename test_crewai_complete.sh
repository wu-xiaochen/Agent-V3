#!/bin/bash
# CrewAI完整功能测试脚本

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 CrewAI完整功能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")"

# 停止旧服务
echo "🛑 停止旧服务..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null
sleep 2

# 启动后端
echo "🚀 启动后端..."
python api_server.py > backend.log 2>&1 &
BACKEND_PID=$!
sleep 5

# 检查后端是否启动
if ! lsof -i:8000 > /dev/null; then
    echo "❌ 后端启动失败！"
    tail -20 backend.log
    exit 1
fi

echo "✅ 后端启动成功 (PID: $BACKEND_PID)"

# 启动前端
echo "🚀 启动前端..."
cd frontend && npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 8
cd ..

# 检查前端是否启动
if ! lsof -i:3000 > /dev/null; then
    echo "❌ 前端启动失败！"
    tail -20 frontend.log
    exit 1
fi

echo "✅ 前端启动成功 (PID: $FRONTEND_PID)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 测试清单"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "阶段 1: UI布局测试"
echo "1. ✓ 打开 http://localhost:3000"
echo "2. ✓ 检查右上角CrewAI按钮是否可见"
echo "3. ✓ 检查左下角是否有Tools按钮"
echo "4. ✓ 点击Tools按钮，侧边栏应该滑出"
echo "5. ✓ 侧边栏应该有4个标签：N8N, Knowledge, Tools, Settings"
echo "6. ✓ 没有CrewAI标签（已移除）"
echo ""

echo "阶段 2: CrewAI基础功能测试"
echo "7. ✓ 点击右上角CrewAI按钮"
echo "8. ✓ 抽屉从右侧滑出，显示CrewAI Teams"
echo "9. ✓ 点击'Create New Crew'按钮"
echo "10. ✓ 显示空白画布"
echo "11. ✓ 点击'Add Agent'按钮添加Agent节点"
echo "12. ✓ 点击Agent节点，配置面板在右侧弹出"
echo "13. ✓ 编辑Agent属性（名称、角色、目标）"
echo "14. ✓ 关闭配置面板，验证节点标签更新"
echo "15. ✓ 点击'Add Task'按钮添加Task节点"
echo "16. ✓ 点击Task节点，配置面板弹出"
echo "17. ✓ 在Task配置中选择Agent"
echo "18. ✓ 从Agent拖线连接到Task"
echo ""

echo "阶段 3: 保存和加载测试"
echo "19. ✓ 点击'Save'按钮保存Crew"
echo "20. ✓ 应该显示\"保存成功\"提示"
echo "21. ✓ 关闭CrewAI抽屉"
echo "22. ✓ 重新打开CrewAI抽屉"
echo "23. ✓ 左侧列表应该显示刚保存的Crew"
echo "24. ✓ 点击Crew项，画布加载配置"
echo "25. ✓ 验证节点和连线正确显示"
echo ""

echo "阶段 4: AI自动生成测试（核心功能）"
echo "26. ✓ 在主聊天界面输入："帮我创建一个数据分析团队""
echo "27. ✓ 发送消息"
echo "28. ✓ 观察思维链状态（应显示工具调用）"
echo "29. ✓ AI应该调用crewai_generator工具"
echo "30. ✓ AI回复应包含Crew生成成功消息"
echo "31. ✓ 1.5秒后，CrewAI画布应该自动打开"
echo "32. ✓ 画布应该加载生成的Crew配置"
echo "33. ✓ 验证有Agent和Task节点"
echo "34. ✓ 可以编辑生成的配置"
echo ""

echo "阶段 5: 执行流程测试（待实现）"
echo "35. ⏳ 点击'Run Crew'按钮"
echo "36. ⏳ 显示执行状态"
echo "37. ⏳ 显示执行结果"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 服务已启动，开始测试！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 前端: http://localhost:3000"
echo "🔌 后端: http://localhost:8000"
echo ""
echo "📊 服务状态:"
lsof -nP -iTCP:8000,3000 -sTCP:LISTEN
echo ""
echo "📝 日志文件:"
echo "  - backend.log"
echo "  - frontend.log"
echo ""
echo "⚠️  测试完成后，按Ctrl+C停止服务"
echo ""

# 等待用户中断
wait

