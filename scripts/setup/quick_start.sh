#!/bin/bash

# Agent-V3 快速启动脚本
# 用于最常见的使用场景

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

# 显示菜单
show_menu() {
    echo "==================================="
    echo "    Agent-V3 快速启动菜单"
    echo "==================================="
    echo "1. 使用OpenAI启动交互模式"
    echo "2. 使用Anthropic启动交互模式"
    echo "3. 使用硅基流动启动交互模式"
    echo "4. 使用OpenAI执行单次查询"
    echo "5. 使用Anthropic执行单次查询"
    echo "6. 使用硅基流动执行单次查询"
    echo "7. 启动服务器模式"
    echo "8. 运行测试"
    echo "9. 安装依赖"
    echo "10. 初始化项目设置"
    echo "0. 退出"
    echo "==================================="
}

# 检查环境
check_environment() {
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_warning "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查虚拟环境
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_info "检测到虚拟环境: $VIRTUAL_ENV"
    else
        print_warning "未检测到虚拟环境，建议使用虚拟环境"
    fi
    
    # 检查配置文件
    if [[ ! -f "config.yaml" ]]; then
        print_warning "config.yaml 文件不存在，请先运行初始化项目设置"
        return 1
    fi
    
    # 检查环境变量文件
    if [[ ! -f ".env" ]]; then
        print_warning ".env 文件不存在，请先运行初始化项目设置"
        return 1
    fi
    
    return 0
}

# 交互模式
start_interactive() {
    local provider=$1
    print_info "启动 $provider 交互模式..."
    
    if ! check_environment; then
        return 1
    fi
    
    python main.py --provider "$provider" --interactive
}

# 单次查询
single_query() {
    local provider=$1
    read -p "请输入您的问题: " query
    
    if [[ -z "$query" ]]; then
        print_warning "问题不能为空"
        return 1
    fi
    
    print_info "使用 $provider 执行查询: $query"
    
    if ! check_environment; then
        return 1
    fi
    
    python main.py --provider "$provider" --query "$query"
}

# 服务器模式
start_server() {
    print_info "启动服务器模式..."
    
    if ! check_environment; then
        return 1
    fi
    
    read -p "请输入工作进程数 (默认1): " workers
    if [[ -z "$workers" ]]; then
        workers=1
    fi
    
    python main.py --server --workers "$workers"
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    
    if ! command -v pytest &> /dev/null; then
        print_warning "pytest 未安装，请先安装依赖"
        return 1
    fi
    
    pytest
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_warning "requirements.txt 文件不存在"
        return 1
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

# 主循环
while true; do
    show_menu
    read -p "请选择操作 (0-10): " choice
    
    case $choice in
        1)
            start_interactive "openai"
            ;;
        2)
            start_interactive "anthropic"
            ;;
        3)
            start_interactive "siliconflow"
            ;;
        4)
            single_query "openai"
            ;;
        5)
            single_query "anthropic"
            ;;
        6)
            single_query "siliconflow"
            ;;
        7)
            start_server
            ;;
        8)
            run_tests
            ;;
        9)
            install_dependencies
            ;;
        10)
            setup_project
            ;;
        0)
            print_info "退出程序"
            exit 0
            ;;
        *)
            print_warning "无效选择，请重新输入"
            ;;
    esac
    
    echo
    read -p "按回车键继续..."
    echo
done