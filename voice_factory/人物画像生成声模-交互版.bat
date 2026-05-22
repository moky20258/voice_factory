@echo off
chcp 65001 >nul
echo ========================================
echo   人物画像声模生成系统（交互版）
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe

echo 🚀 启动交互式声模生成系统...
echo.

%PYTHON% portrait_voice_model_interactive.py

echo.
pause
