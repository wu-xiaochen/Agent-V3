#!/bin/bash

# Agent-V3 启动脚本
# 使用方法: ./scripts/start.sh [选项]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
Agent-V3 启动脚本

使用方法:
    $0 [选项] [参数]

选项:
    -h, --help              显示此帮助信息
    -p, --provider PROVIDER 指定LLM提供商 (openai, anthropic, huggingface, siliconflow)
    -m, --model MODEL        指定模型名称
    -i, --interactive       启动交互模式
    -q, --query QUERY       执行单次查询
    -c, --config CONFIG      指定配置文件路径
    -e, --env ENV            指定环境 (development, staging, production)
    -d, --debug             启用调试模式
    --stream                启用流式输出
    --streaming-style STYLE 流式输出样式 (simple, detailed, none)
    -r, --reload            启用自动重载 (仅开发环境)
    -w, --workers WORKERS   指定工作进程数 (仅服务器模式)
    -s, --server            启动服务器模式
    -t, --test              运行测试
    --install               安装依赖
    --setup                 初始化项目设置
    --docker                使用Docker运行

示例:
    $0 --interactive --provider openai --stream
    $0 --query "你好" --provider anthropic --stream --streaming-style simple
    $0 --interactive --stream --streaming-style detailed
    $0 --server --workers 4
    $0 --test
    $0 --install
    $0 --setup

EOF
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_info "检测到Python版本: $PYTHON_VERSION"
    
    if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
        print_warning "建议使用Python 3.8或更高版本"
    fi
}

# 检查虚拟环境
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_info "检测到虚拟环境: $VIRTUAL_ENV"
    else
        print_warning "未检测到虚拟环境，建议使用虚拟环境"
        read -p "是否创建虚拟环境? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 -m venv venv
            source venv/bin/activate
            print_success "虚拟环境已创建并激活"
        fi
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
}

# 初始化项目设置
setup_project() {
    print_info "初始化项目设置..."
    
    # 创建必要的目录
    mkdir -p data logs temp
    
    # 复制环境变量文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            print_success "已创建 .env 文件，请根据需要修改配置"
        else
            print_warning ".env.example 文件不存在"
        fi
    else
        print_info ".env 文件已存在"
    fi
    
    # 复制配置文件
    if [[ ! -f "config.yaml" ]]; then
        if [[ -f "config.example.yaml" ]]; then
            cp config.example.yaml config.yaml
            print_success "已创建 config.yaml 文件，请根据需要修改配置"
        else
            print_warning "config.example.yaml 文件不存在"
        fi
    else
        print_info "config.yaml 文件已存在"
    fi
    
    print_success "项目设置初始化完成"
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    
    if command -v pytest &> /dev/null; then
        pytest
        print_success "测试完成"
    else
        print_error "pytest 未安装，请先安装依赖"
        exit 1
    fi
}

# 使用Docker运行
run_with_docker() {
    print_info "使用Docker运行..."
    
    if command -v docker &> /dev/null; then
        if [[ -f "Dockerfile" ]]; then
            docker build -t agent-v3 .
            docker run -p 8000:8000 --env-file .env agent-v3
        else
            print_error "Dockerfile 不存在"
            exit 1
        fi
    else
        print_error "Docker 未安装"
        exit 1
    fi
}

# 默认参数
PROVIDER=""
MODEL=""
INTERACTIVE=false
QUERY=""
CONFIG=""
ENV="development"
DEBUG=false
STREAM=false
STREAMING_STYLE="simple"
RELOAD=false
WORKERS=1
SERVER=false
TEST=false
INSTALL=false
SETUP=false
DOCKER=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--provider)
            PROVIDER="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -q|--query)
            QUERY="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        --stream)
            STREAM=true
            shift
            ;;
        --streaming-style)
            STREAMING_STYLE="$2"
            shift 2
            ;;
        -r|--reload)
            RELOAD=true
            shift
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        -s|--server)
            SERVER=true
            shift
            ;;
        -t|--test)
            TEST=true
            shift
            ;;
        --install)
            INSTALL=true
            shift
            ;;
        --setup)
            SETUP=true
            shift
            ;;
        --docker)
            DOCKER=true
            shift
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 检查Python环境
check_python

# 检查虚拟环境
check_venv

# 安装依赖
if [[ "$INSTALL" == true ]]; then
    install_dependencies
    exit 0
fi

# 初始化项目设置
if [[ "$SETUP" == true ]]; then
    setup_project
    exit 0
fi

# 运行测试
if [[ "$TEST" == true ]]; then
    run_tests
    exit 0
fi

# 使用Docker运行
if [[ "$DOCKER" == true ]]; then
    run_with_docker
    exit 0
fi

# 构建命令
CMD="python main.py"

# 添加环境变量
export APP_ENV="$ENV"

if [[ "$DEBUG" == true ]]; then
    export LOG_LEVEL="DEBUG"
    CMD="$CMD --debug"
fi

# 添加提供商
if [[ -n "$PROVIDER" ]]; then
    CMD="$CMD --provider $PROVIDER"
fi

# 添加模型
if [[ -n "$MODEL" ]]; then
    CMD="$CMD --model $MODEL"
fi

# 添加配置文件
if [[ -n "$CONFIG" ]]; then
    CMD="$CMD --config $CONFIG"
fi

# 添加交互模式
if [[ "$INTERACTIVE" == true ]]; then
    CMD="$CMD --interactive"
fi

# 添加查询
if [[ -n "$QUERY" ]]; then
    CMD="$CMD --query \"$QUERY\""
fi

# 添加流式输出
if [[ "$STREAM" == true ]]; then
    CMD="$CMD --stream"
fi

# 添加流式输出样式
if [[ -n "$STREAMING_STYLE" ]]; then
    CMD="$CMD --streaming-style $STREAMING_STYLE"
fi

# 添加服务器模式
if [[ "$SERVER" == true ]]; then
    CMD="$CMD --server"
    if [[ "$ENV" == "development" && "$RELOAD" == true ]]; then
        CMD="$CMD --reload"
    fi
    CMD="$CMD --workers $WORKERS"
fi

# 运行命令
print_info "运行命令: $CMD"
eval $CMD