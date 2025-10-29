#!/bin/bash

# Agent-V3 停止所有服务

echo "🛑 停止 Agent-V3 所有服务..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 停止后端
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}🛑 停止后端服务 (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID
    fi
    rm .backend.pid
fi

# 停止前端
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${GREEN}🛑 停止前端服务 (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID
    fi
    rm .frontend.pid
fi

# 额外检查并停止可能的残留进程
pkill -f "api_server.py" 2>/dev/null
pkill -f "next dev" 2>/dev/null

echo -e "${GREEN}✅ 所有服务已停止${NC}"

