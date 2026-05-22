@echo off
chcp 65001 >nul
echo ========================================
echo   Fish Speech API 服务器启动器
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe

echo 📍 工作目录: w:\fish-speech-1.5.1
echo 🌐 API 地址: http://127.0.0.1:8080
echo.
echo 📋 启动参数:
echo   --listen 127.0.0.1:8080
echo.
echo ========================================
echo.

cd /d w:\fish-speech-1.5.1

echo 🚀 正在启动 Fish Speech API 服务器...
echo.
echo 💡 提示:
echo   - 首次启动需要加载模型，可能需要1-2分钟
echo   - 看到 "Uvicorn running on http://127.0.0.1:8080" 表示启动成功
echo   - 保持此窗口打开以维持 API 服务运行
echo   - 按 Ctrl+C 可停止服务
echo.
echo ========================================
echo.

%PYTHON% tools/api_server.py --listen 127.0.0.1:8080

echo.
echo ========================================
echo   服务器已停止
echo ========================================
pause
