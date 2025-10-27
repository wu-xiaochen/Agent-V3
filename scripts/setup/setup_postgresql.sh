#!/bin/bash

# PostgreSQL 数据库初始化脚本
# 用于 Agent-V3 项目的 PostgreSQL 数据库设置

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 默认配置
DEFAULT_DB_NAME="trae_agents"
DEFAULT_DB_USER="agent_user"
DEFAULT_DB_HOST="localhost"
DEFAULT_DB_PORT="5432"

# 从环境变量或使用默认值
DB_NAME=${DB_NAME:-$DEFAULT_DB_NAME}
DB_USER=${DB_USER:-$DEFAULT_DB_USER}
DB_HOST=${DB_HOST:-$DEFAULT_DB_HOST}
DB_PORT=${DB_PORT:-$DEFAULT_DB_PORT}

# 函数：检查 PostgreSQL 是否安装
check_postgres_installation() {
    log_info "检查 PostgreSQL 安装状态..."
    
    if command -v psql &> /dev/null; then
        log_info "PostgreSQL 已安装"
        psql --version
    else
        log_error "PostgreSQL 未安装"
        log_info "请参考 docs/deployment/postgresql_setup.md 安装 PostgreSQL"
        exit 1
    fi
}

# 函数：检查 PostgreSQL 服务状态
check_postgres_service() {
    log_info "检查 PostgreSQL 服务状态..."
    
    # 尝试连接到 PostgreSQL
    if pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
        log_info "PostgreSQL 服务正在运行"
    else
        log_error "PostgreSQL 服务未运行"
        log_info "请启动 PostgreSQL 服务："
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            log_info "  brew services start postgresql@15"
        else
            # Linux
            log_info "  sudo systemctl start postgresql"
        fi
        
        exit 1
    fi
}

# 函数：提示输入密码
prompt_password() {
    while true; do
        read -s -p "请输入 PostgreSQL 用户 '$DB_USER' 的密码: " password
        echo
        read -s -p "请再次输入密码确认: " password_confirm
        echo
        
        if [ "$password" = "$password_confirm" ]; then
            if [ ${#password} -ge 8 ]; then
                echo $password
                return 0
            else
                log_error "密码长度至少需要 8 个字符"
            fi
        else
            log_error "两次输入的密码不匹配"
        fi
    done
}

# 函数：创建数据库和用户
setup_database() {
    log_info "设置数据库和用户..."
    
    # 提示输入密码
    DB_PASSWORD=$(prompt_password)
    
    # 创建 SQL 脚本
    SQL_SCRIPT="/tmp/setup_trae_agents_db.sql"
    cat > $SQL_SCRIPT << EOF
-- 创建数据库
CREATE DATABASE $DB_NAME;

-- 创建用户
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- 连接到新数据库并授予 schema 权限
\c $DB_NAME;

GRANT ALL ON SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- 显示创建的数据库和用户
\l
\du
EOF
    
    # 执行 SQL 脚本
    log_info "执行数据库初始化脚本..."
    if sudo -u postgres psql -f $SQL_SCRIPT; then
        log_info "数据库和用户创建成功"
    else
        log_error "数据库和用户创建失败"
        rm -f $SQL_SCRIPT
        exit 1
    fi
    
    # 清理临时文件
    rm -f $SQL_SCRIPT
}

# 函数：更新 .env 文件
update_env_file() {
    log_info "更新 .env 文件..."
    
    ENV_FILE=".env"
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warn ".env 文件不存在，将创建新文件"
        cp .env.example "$ENV_FILE"
    fi
    
    # 备份原始文件
    cp "$ENV_FILE" "$ENV_FILE.backup"
    
    # 更新数据库配置
    sed -i.bak "s/DB_NAME=.*/DB_NAME=$DB_NAME/" "$ENV_FILE"
    sed -i.bak "s/DB_USERNAME=.*/DB_USERNAME=$DB_USER/" "$ENV_FILE"
    sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" "$ENV_FILE"
    
    # 删除备份文件
    rm -f "$ENV_FILE.bak"
    
    log_info ".env 文件已更新"
}

# 函数：测试数据库连接
test_connection() {
    log_info "测试数据库连接..."
    
    # 从 .env 文件加载数据库配置
    if [ -f ".env" ]; then
        source .env
    else
        log_error ".env 文件不存在"
        exit 1
    fi
    
    # 尝试连接
    if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT version();" &> /dev/null; then
        log_info "数据库连接测试成功"
    else
        log_error "数据库连接测试失败"
        exit 1
    fi
}

# 函数：显示完成信息
show_completion_info() {
    log_info "PostgreSQL 数据库初始化完成!"
    echo
    log_info "数据库配置信息:"
    echo "  主机: $DB_HOST"
    echo "  端口: $DB_PORT"
    echo "  数据库名: $DB_NAME"
    echo "  用户名: $DB_USER"
    echo
    log_info "下一步:"
    echo "1. 运行项目: python main.py --interactive --stream"
    echo "2. 如果需要，请参考 docs/deployment/postgresql_setup.md 获取更多信息"
}

# 主函数
main() {
    log_info "开始 PostgreSQL 数据库初始化..."
    echo
    
    check_postgres_installation
    echo
    
    check_postgres_service
    echo
    
    setup_database
    echo
    
    update_env_file
    echo
    
    test_connection
    echo
    
    show_completion_info
}

# 运行主函数
main "$@"