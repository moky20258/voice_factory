@echo off
chcp 65001 >nul
echo ========================================
echo   声音分析与声模匹配（交互版）
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe
set SCRIPT=interactive_voice_matcher.py

echo 🚀 启动交互式分析系统...
echo.

%PYTHON% %SCRIPT%

echo.
pause
