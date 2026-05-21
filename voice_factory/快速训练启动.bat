@echo off
chcp 65001 >nul
echo ========================================
echo   RVC 全自动训练 - 测试模式
echo ========================================
echo.
echo 将训练: speaker_0001
echo 预计时间: 30-60 分钟
echo.
echo 开始训练...
echo.

cd /d W:\rvc

REM 使用 RVC 自带的 Python 环境
runtime\python.exe -c "import sys; sys.path.insert(0, '.'); from infer.lib.train.process_ckpt import *; from infer.modules.vc.modules import VC; from configs.config import Config; print('环境检查成功')"

if errorlevel 1 (
    echo.
    echo ❌ 环境检查失败
    pause
    exit /b 1
)

echo.
echo ✅ 环境就绪
echo.
echo 提示: 训练过程会显示在这里
echo 请耐心等待...
echo.
echo ========================================
echo.

REM 启动训练（需要进一步开发完整的命令行训练脚本）
echo 由于 RVC 的训练函数深度依赖 WebUI 框架，
echo 建议使用以下最简单的方法：
echo.
echo 1. 双击: go-web.bat
echo 2. 浏览器打开: http://localhost:7897  
echo 3. 点击"训练"标签
echo 4. 输入: speaker_0001
echo 5. 点击"一键训练"
echo.
echo 这是目前最稳定的方式！
echo.

pause
