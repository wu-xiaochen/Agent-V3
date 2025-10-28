@echo off
REM Agent-V3 Windows启动脚本
REM 使用方法: scripts\start.bat [选项]

setlocal enabledelayedexpansion

REM 默认参数
set PROVIDER=
set MODEL=
set INTERACTIVE=false
set QUERY=
set CONFIG=
set ENV=development
set DEBUG=false
set STREAM=false
set STREAMING_STYLE=simple
set RELOAD=false
set WORKERS=1
set SERVER=false
set TEST=false
set INSTALL=false
set SETUP=false
set DOCKER=false

REM 解析命令行参数
:parse_args
if "%~1"=="" goto end_parse
if "%~1"=="-h" goto show_help
if "%~1"=="--help" goto show_help
if "%~1"=="-p" (
    set PROVIDER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--provider" (
    set PROVIDER=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-m" (
    set MODEL=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--model" (
    set MODEL=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-i" (
    set INTERACTIVE=true
    shift
    goto parse_args
)
if "%~1"=="--interactive" (
    set INTERACTIVE=true
    shift
    goto parse_args
)
if "%~1"=="-q" (
    set QUERY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--query" (
    set QUERY=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-c" (
    set CONFIG=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--config" (
    set CONFIG=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-e" (
    set ENV=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--env" (
    set ENV=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-d" (
    set DEBUG=true
    shift
    goto parse_args
)
if "%~1"=="--debug" (
    set DEBUG=true
    shift
    goto parse_args
)
if "%~1"=="--stream" (
    set STREAM=true
    shift
    goto parse_args
)
if "%~1"=="--streaming-style" (
    set STREAMING_STYLE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-r" (
    set RELOAD=true
    shift
    goto parse_args
)
if "%~1"=="--reload" (
    set RELOAD=true
    shift
    goto parse_args
)
if "%~1"=="-w" (
    set WORKERS=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--workers" (
    set WORKERS=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-s" (
    set SERVER=true
    shift
    goto parse_args
)
if "%~1"=="--server" (
    set SERVER=true
    shift
    goto parse_args
)
if "%~1"=="-t" (
    set TEST=true
    shift
    goto parse_args
)
if "%~1"=="--test" (
    set TEST=true
    shift
    goto parse_args
)
if "%~1"=="--install" (
    set INSTALL=true
    shift
    goto parse_args
)
if "%~1"=="--setup" (
    set SETUP=true
    shift
    goto parse_args
)
if "%~1"=="--docker" (
    set DOCKER=true
    shift
    goto parse_args
)
echo 未知选项: %~1
goto show_help

:end_parse

REM 显示帮助信息
:show_help
echo Agent-V3 启动脚本
echo.
echo 使用方法:
echo     %~nx0 [选项] [参数]
echo.
echo 选项:
echo     -h, --help              显示此帮助信息
echo     -p, --provider PROVIDER 指定LLM提供商 (openai, anthropic, huggingface, siliconflow)
echo     -m, --model MODEL        指定模型名称
echo     -i, --interactive       启动交互模式
echo     -q, --query QUERY       执行单次查询
echo     -c, --config CONFIG      指定配置文件路径
echo     -e, --env ENV            指定环境 (development, staging, production)
echo     -d, --debug             启用调试模式
echo     --stream                启用流式输出
echo     --streaming-style STYLE 流式输出样式 (simple, detailed, none)
echo     -r, --reload            启用自动重载 (仅开发环境)
echo     -w, --workers WORKERS   指定工作进程数 (仅服务器模式)
echo     -s, --server            启动服务器模式
echo     -t, --test              运行测试
echo     --install               安装依赖
echo     --setup                 初始化项目设置
echo     --docker                使用Docker运行
echo.
echo 示例:
echo     %~nx0 --interactive --provider openai --stream
echo     %~nx0 --query "你好" --provider anthropic --stream --streaming-style simple
echo     %~nx0 --server --workers 4
echo     %~nx0 --test
echo     %~nx0 --install
echo     %~nx0 --setup
echo.
exit /b 0

REM 检查Python环境
:check_python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 未安装，请先安装Python
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] 检测到Python版本: %PYTHON_VERSION%

goto :eof

REM 检查虚拟环境
:check_venv
if defined VIRTUAL_ENV (
    echo [INFO] 检测到虚拟环境: %VIRTUAL_ENV%
) else (
    echo [WARNING] 未检测到虚拟环境，建议使用虚拟环境
    set /p create_venv="是否创建虚拟环境? (y/n): "
    if /i "!create_venv!"=="y" (
        python -m venv venv
        call venv\Scripts\activate.bat
        echo [SUCCESS] 虚拟环境已创建并激活
    )
)

goto :eof

REM 安装依赖
:install_dependencies
echo [INFO] 安装项目依赖...

if exist requirements.txt (
    pip install -r requirements.txt
    echo [SUCCESS] 依赖安装完成
) else (
    echo [ERROR] requirements.txt 文件不存在
    exit /b 1
)

goto :eof

REM 初始化项目设置
:setup_project
echo [INFO] 初始化项目设置...

REM 创建必要的目录
if not exist data mkdir data
if not exist logs mkdir logs
if not exist temp mkdir temp

REM 复制环境变量文件
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo [SUCCESS] 已创建 .env 文件，请根据需要修改配置
    ) else (
        echo [WARNING] .env.example 文件不存在
    )
) else (
    echo [INFO] .env 文件已存在
)

REM 复制配置文件
if not exist config.yaml (
    if exist config.example.yaml (
        copy config.example.yaml config.yaml >nul
        echo [SUCCESS] 已创建 config.yaml 文件，请根据需要修改配置
    ) else (
        echo [WARNING] config.example.yaml 文件不存在
    )
) else (
    echo [INFO] config.yaml 文件已存在
)

echo [SUCCESS] 项目设置初始化完成
goto :eof

REM 运行测试
:run_tests
echo [INFO] 运行测试...

pytest --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pytest 未安装，请先安装依赖
    exit /b 1
)

pytest
echo [SUCCESS] 测试完成
goto :eof

REM 使用Docker运行
:run_with_docker
echo [INFO] 使用Docker运行...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker 未安装
    exit /b 1
)

if exist Dockerfile (
    docker build -t agent-v3 .
    docker run -p 8000:8000 --env-file .env agent-v3
) else (
    echo [ERROR] Dockerfile 不存在
    exit /b 1
)

goto :eof

REM 主程序
call :check_python
call :check_venv

REM 安装依赖
if "%INSTALL%"=="true" (
    call :install_dependencies
    exit /b 0
)

REM 初始化项目设置
if "%SETUP%"=="true" (
    call :setup_project
    exit /b 0
)

REM 运行测试
if "%TEST%"=="true" (
    call :run_tests
    exit /b 0
)

REM 使用Docker运行
if "%DOCKER%"=="true" (
    call :run_with_docker
    exit /b 0
)

REM 构建命令
set CMD=python main.py

REM 添加环境变量
set APP_ENV=%ENV%

if "%DEBUG%"=="true" (
    set LOG_LEVEL=DEBUG
    set CMD=%CMD% --debug
)

REM 添加提供商
if not "%PROVIDER%"=="" (
    set CMD=%CMD% --provider %PROVIDER%
)

REM 添加模型
if not "%MODEL%"=="" (
    set CMD=%CMD% --model %MODEL%
)

REM 添加配置文件
if not "%CONFIG%"=="" (
    set CMD=%CMD% --config %CONFIG%
)

REM 添加交互模式
if "%INTERACTIVE%"=="true" (
    set CMD=%CMD% --interactive
)

REM 添加查询
if not "%QUERY%"=="" (
    set CMD=%CMD% --query "%QUERY%"
)

REM 添加流式输出
if "%STREAM%"=="true" (
    set CMD=%CMD% --stream
)

REM 添加流式输出样式
if not "%STREAMING_STYLE%"=="" (
    set CMD=%CMD% --streaming-style %STREAMING_STYLE%
)

REM 添加服务器模式
if "%SERVER%"=="true" (
    set CMD=%CMD% --server
    if "%ENV%"=="development" if "%RELOAD%"=="true" (
        set CMD=%CMD% --reload
    )
    set CMD=%CMD% --workers %WORKERS%
)

REM 运行命令
echo [INFO] 运行命令: %CMD%
%CMD%