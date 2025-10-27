@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM Agent-V3 快速启动脚本 (Windows版本)
REM 用于最常见的使用场景

:main_menu
cls
echo ===================================
echo     Agent-V3 快速启动菜单
echo ===================================
echo 1. 使用OpenAI启动交互模式
echo 2. 使用Anthropic启动交互模式
echo 3. 使用硅基流动启动交互模式
echo 4. 使用OpenAI执行单次查询
echo 5. 使用Anthropic执行单次查询
echo 6. 使用硅基流动执行单次查询
echo 7. 启动服务器模式
echo 8. 运行测试
echo 9. 安装依赖
echo 10. 初始化项目设置
echo 0. 退出
echo ===================================
set /p choice=请选择操作 (0-10): 

if "%choice%"=="1" goto openai_interactive
if "%choice%"=="2" goto anthropic_interactive
if "%choice%"=="3" goto siliconflow_interactive
if "%choice%"=="4" goto openai_query
if "%choice%"=="5" goto anthropic_query
if "%choice%"=="6" goto siliconflow_query
if "%choice%"=="7" goto server_mode
if "%choice%"=="8" goto run_tests
if "%choice%"=="9" goto install_dependencies
if "%choice%"=="10" goto setup_project
if "%choice%"=="0" goto exit_program

echo 无效选择，请重新输入
pause
goto main_menu

:openai_interactive
call :check_environment
if errorlevel 1 goto main_menu
echo 启动 OpenAI 交互模式...
python main.py --provider openai --interactive
pause
goto main_menu

:anthropic_interactive
call :check_environment
if errorlevel 1 goto main_menu
echo 启动 Anthropic 交互模式...
python main.py --provider anthropic --interactive
pause
goto main_menu

:siliconflow_interactive
call :check_environment
if errorlevel 1 goto main_menu
echo 启动 硅基流动 交互模式...
python main.py --provider siliconflow --interactive
pause
goto main_menu

:openai_query
call :check_environment
if errorlevel 1 goto main_menu
set /p query=请输入您的问题: 
if "%query%"=="" (
    echo 问题不能为空
    pause
    goto main_menu
)
echo 使用 OpenAI 执行查询: %query%
python main.py --provider openai --query "%query%"
pause
goto main_menu

:anthropic_query
call :check_environment
if errorlevel 1 goto main_menu
set /p query=请输入您的问题: 
if "%query%"=="" (
    echo 问题不能为空
    pause
    goto main_menu
)
echo 使用 Anthropic 执行查询: %query%
python main.py --provider anthropic --query "%query%"
pause
goto main_menu

:siliconflow_query
call :check_environment
if errorlevel 1 goto main_menu
set /p query=请输入您的问题: 
if "%query%"=="" (
    echo 问题不能为空
    pause
    goto main_menu
)
echo 使用 硅基流动 执行查询: %query%
python main.py --provider siliconflow --query "%query%"
pause
goto main_menu

:server_mode
call :check_environment
if errorlevel 1 goto main_menu
echo 启动服务器模式...
set /p workers=请输入工作进程数 (默认1): 
if "%workers%"=="" set workers=1
python main.py --server --workers %workers%
pause
goto main_menu

:run_tests
echo 运行测试...
where pytest >nul 2>&1
if errorlevel 1 (
    echo pytest 未安装，请先安装依赖
    pause
    goto main_menu
)
pytest
pause
goto main_menu

:install_dependencies
echo 安装项目依赖...
if exist requirements.txt (
    pip install -r requirements.txt
    echo 依赖安装完成
) else (
    echo requirements.txt 文件不存在
)
pause
goto main_menu

:setup_project
echo 初始化项目设置...

REM 创建必要的目录
if not exist data mkdir data
if not exist logs mkdir logs
if not exist temp mkdir temp

REM 复制环境变量文件
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo 已创建 .env 文件，请根据需要修改配置
    ) else (
        echo .env.example 文件不存在
    )
) else (
    echo .env 文件已存在
)

REM 复制配置文件
if not exist config.yaml (
    if exist config.example.yaml (
        copy config.example.yaml config.yaml >nul
        echo 已创建 config.yaml 文件，请根据需要修改配置
    ) else (
        echo config.example.yaml 文件不存在
    )
) else (
    echo config.yaml 文件已存在
)

echo 项目设置初始化完成
pause
goto main_menu

:check_environment
REM 检查Python
where python >nul 2>&1
if errorlevel 1 (
    echo Python 未安装，请先安装Python
    exit /b 1
)

REM 检查配置文件
if not exist config.yaml (
    echo config.yaml 文件不存在，请先运行初始化项目设置
    exit /b 1
)

REM 检查环境变量文件
if not exist .env (
    echo .env 文件不存在，请先运行初始化项目设置
    exit /b 1
)

exit /b 0

:exit_program
echo 退出程序
exit /b 0