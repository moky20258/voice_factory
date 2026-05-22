@echo off
chcp 65001 >nul
echo ========================================
echo   声模人物画像查询工具
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe
set SCRIPT=query_voice_portraits.py

echo 🚀 启动查询工具...
echo.

%PYTHON% %SCRIPT%

echo.
pause
