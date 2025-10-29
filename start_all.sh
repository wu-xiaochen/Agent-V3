#!/bin/bash

# Agent-V3 完整项目启动脚本
# 启动后端 API 服务和前端 Next.js 应用

set -e

echo "🚀 启动 Agent-V3 完整项目..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 环境
echo -e "${BLUE}📦 检查 Python 环境...${NC}"
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}⚠️  Python 未安装${NC}"
    exit 1
fi

PYTHON_CMD=$(command -v python3 || command -v python)
echo -e "${GREEN}✅ Python: $($PYTHON_CMD --version)${NC}"

# 检查 Node.js 环境
echo -e "${BLUE}📦 检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️  Node.js 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"

# 检查 pnpm
echo -e "${BLUE}📦 检查 pnpm...${NC}"
if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}⚠️  pnpm 未安装，正在安装...${NC}"
    npm install -g pnpm
fi
echo -e "${GREEN}✅ pnpm: $(pnpm --version)${NC}"

echo ""

# 检查后端依赖
echo -e "${BLUE}📦 检查后端依赖...${NC}"
if [ ! -d ".venv" ] && [ ! -f ".venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠️  虚拟环境不存在，正在创建...${NC}"
    $PYTHON_CMD -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate 2>/dev/null || . .venv/bin/activate

# 安装依赖
echo -e "${BLUE}📦 安装后端依赖...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✅ 后端依赖已安装${NC}"

# 检查前端依赖
echo -e "${BLUE}📦 检查前端依赖...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  前端依赖未安装，正在安装...${NC}"
    pnpm install
else
    echo -e "${GREEN}✅ 前端依赖已安装${NC}"
fi
cd ..

echo ""

# 创建日志目录
mkdir -p logs

# 启动后端 API
echo -e "${GREEN}🚀 启动后端 API 服务 (端口 8000)...${NC}"
$PYTHON_CMD api_server.py --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
BACKEND_PID=$!
echo "   后端 PID: $BACKEND_PID"

# 等待后端启动
echo -e "${BLUE}⏳ 等待后端服务启动...${NC}"
sleep 3

# 检查后端是否启动成功
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务已启动${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务可能未成功启动，请检查 logs/api.log${NC}"
fi

# 启动前端
echo -e "${GREEN}🚀 启动前端 Next.js 应用 (端口 3000)...${NC}"
cd frontend
pnpm dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   前端 PID: $FRONTEND_PID"
cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Agent-V3 项目已启动！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 服务信息:${NC}"
echo -e "   🔹 后端 API:  http://localhost:8000"
echo -e "   🔹 API 文档:  http://localhost:8000/docs"
echo -e "   🔹 前端界面:  http://localhost:3000"
echo ""
echo -e "${BLUE}📋 进程 ID:${NC}"
echo -e "   🔹 后端 PID: $BACKEND_PID"
echo -e "   🔹 前端 PID: $FRONTEND_PID"
echo ""
echo -e "${BLUE}📝 日志文件:${NC}"
echo -e "   🔹 后端日志: logs/api.log"
echo -e "   🔹 前端日志: logs/frontend.log"
echo ""
echo -e "${YELLOW}💡 提示:${NC}"
echo -e "   • 使用 Ctrl+C 或运行 ./stop_all.sh 停止所有服务"
echo -e "   • 查看日志: tail -f logs/api.log"
echo ""

# 保存 PID 到文件
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# 等待用户中断
echo -e "${GREEN}按 Ctrl+C 停止所有服务...${NC}"
wait

