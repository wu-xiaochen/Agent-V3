#!/bin/bash

# Agent-V3 用户体验测试执行脚本

echo "🚀 开始执行用户体验测试..."
echo "=================================="

# 确保前端和后端服务运行
echo "📋 检查服务状态..."

# 检查后端是否运行
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  后端服务未运行，正在启动..."
    cd /Users/xiaochenwu/Desktop/Agent-V3
    python api_server.py --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
    sleep 3
fi

# 检查前端是否运行
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  前端服务未运行，正在启动..."
    cd /Users/xiaochenwu/Desktop/Agent-V3/frontend
    npm run dev > ../frontend.log  bem>&1 &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
    sleep 5
fi

echo "✅ 服务检查完成"
echo ""

# 进入测试目录
cd /Users/xiaochenwu/Desktop/Agent-V3/tests/e2e

# 执行用户体验测试
echo "🧪 执行用户体验测试..."
npx playwright test playwright/04-user-experience.spec.ts --headed --project=chromium

echo ""
echo "📊 测试执行完成"
echo "=================================="

