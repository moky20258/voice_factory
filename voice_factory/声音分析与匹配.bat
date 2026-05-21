@echo off
chcp 65001 >nul
echo ========================================
echo   声音分析与声模匹配建议系统
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe
set SCRIPT=voice_analysis_and_recommendation.py

if "%1"=="" (
    echo 用法: 声音分析与匹配.bat ^<音频文件或目录^> [选项]
    echo.
    echo 示例:
    echo   声音分析与匹配.bat audio.wav
    echo   声音分析与匹配.bat .\audio_folder
    echo   声音分析与匹配.bat audio.wav -o report.json
    echo.
    echo 选项:
    echo   -o ^<file^>     输出报告文件 (JSON)
    echo   --top-n ^<N^>   返回前 N 个匹配结果 (默认: 3)
    echo   --no-pretrained 跳过预训练声模匹配
    echo   --no-trained    跳过已训练声模匹配
    echo.
    pause
    exit /b
)

echo 🚀 开始分析...
echo.

%PYTHON% %SCRIPT% %*

echo.
echo ========================================
echo   分析完成！
echo ========================================
pause
