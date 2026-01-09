@echo off
chcp 65001 >nul
echo ========================================
echo 北京退休金测算系统 - 启动脚本
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [√] Python已安装
echo.

REM 检查API Key
echo %ZHIPU_API_KEY% | findstr "." >nul
if errorlevel 1 (
    echo [警告] 未检测到ZHIPU_API_KEY环境变量
    echo.
    echo 请先设置API Key：
    echo   set ZHIPU_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

echo [√] API Key已配置
echo.

REM 检查必要的文件
if not exist "app.py" (
    echo [错误] 未找到app.py文件
    pause
    exit /b 1
)

if not exist "prompts\system_prompt.txt" (
    echo [错误] 未找到prompts\system_prompt.txt
    pause
    exit /b 1
)

echo [√] 必要文件检查通过
echo.

REM 检查Flask是否安装
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [提示] Flask未安装，正在安装...
    pip install flask requests
    echo.
)

echo [√] 依赖库检查完成
echo.
echo ========================================
echo 正在启动Web服务器...
echo ========================================
echo.

REM 启动应用
python app.py

pause
