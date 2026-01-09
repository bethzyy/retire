@echo off
chcp 65001 >nul
echo ========================================
echo 北京退休金测算系统 - 测试脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python
    pause
    exit /b 1
)

echo [√] Python已安装
echo.

REM 检查API Key
echo %ZHIPU_API_KEY% | findstr "." >nul
if errorlevel 1 (
    echo [错误] 未设置ZHIPU_API_KEY环境变量
    echo.
    echo 请先设置：
    echo   set ZHIPU_API_KEY=your_api_key_here
    echo.
    pause
    exit /b 1
)

echo [√] API Key已配置
echo.

REM 检查测试文件
if not exist "tests\test_api.py" (
    echo [错误] 未找到tests\test_api.py
    pause
    exit /b 1
)

echo [√] 测试文件检查通过
echo.
echo ========================================
echo 开始运行测试...
echo ========================================
echo.

REM 运行测试
cd /d "%~dp0" && python tests\test_api.py

echo.
echo ========================================
echo 测试完成
echo ========================================
pause
