@echo off
chcp 65001 >nul
echo ========================================
echo Fish Speech 声模工厂 - 启动脚本
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
set PYTHON_PATH=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON_PATH%" (
    echo ❌ 未找到 Python 3.12
    echo 请安装 Python 3.12: winget install Python.Python.3.12
    pause
    exit /b 1
)

echo ✅ Python 3.12 已找到
echo.

echo [2/3] 启动 Fish Speech WebUI...
echo 💡 请等待 WebUI 启动完成（约 30 秒）
echo 💡 看到 "Running on local URL: http://127.0.0.1:7860" 后继续
echo.

start "Fish Speech WebUI" "%PYTHON_PATH%" tools/run_webui.py

timeout /t 35 /nobreak >nul

echo.
echo [3/3] 启动声模工厂...
echo.

cd voice_factory
"%PYTHON_PATH%" run_factory.py

pause
