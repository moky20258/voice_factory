@echo off
chcp 65001 >nul
echo ========================================
echo   人物画像声模生成系统
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe
set SCRIPT=portrait_to_voice_model.py

if "%1"=="" (
    echo 用法: 人物画像生成声模.bat ^<人物画像^> [选项]
    echo.
    echo 示例:
    echo   人物画像生成声模.bat "中年男中音"
    echo   人物画像生成声模.bat "青年女高音，活泼可爱" --epochs 50
    echo.
    echo 选项:
    echo   --speaker-id ^<ID^>  指定 speaker 编号
    echo   --epochs ^<N^>       训练轮数 (默认: 50)
    echo   --sentences ^<N^>    生成句子数 (默认: 30)
    echo.
    echo 可用画像:
    echo   中年男中音、中年男低音、青年男高音、中年男高音
    echo   青年女高音、青年女中音、中年女低音
    echo.
    pause
    exit /b
)

echo 🚀 开始生成声模...
echo.

%PYTHON% %SCRIPT% %*

echo.
echo ========================================
echo   生成完成！
echo ========================================
pause
