@echo off
chcp 65001 >nul 2>&1
title 启动实时变声
echo ========================================
echo    声模工厂 - 启动实时变声
echo ========================================
echo.

cd /d W:\fish-speech-1.5.1
python voice_factory\run_factory.py --realtime-vc

pause
