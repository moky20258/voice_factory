@echo off
chcp 65001 >nul
echo ========================================
echo   人物画像声模生成系统
echo ========================================
echo.

set PYTHON=C:\Users\moqi\AppData\Local\Programs\Python\Python312\python.exe

REM 检查是否有命令行参数
if not "%1"=="" (
    echo 🚀 开始生成声模...
    echo.
    %PYTHON% portrait_to_voice_model.py %*
    echo.
    echo ========================================
    echo   生成完成！
    echo ========================================
    pause
    exit /b
)

REM 交互式模式
echo 请选择输入方式:
echo 1. 选择预设画像
echo 2. 自定义画像描述
echo 3. 查看画像列表
echo 4. 退出
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="4" exit /b
if "%choice%=="3" (
    echo.
    echo ========================================
    echo   可用画像列表
    echo ========================================
    echo.
    echo 男声声模:
    echo   1. 中年男中音 - 温暖、稳重、成熟
    echo   2. 中年男低音 - 深沉、磁性、厚重
    echo   3. 青年男高音 - 明亮、阳光、活力
    echo   4. 中年男高音 - 激情、澎湃、有力
    echo.
    echo 女声声模:
    echo   5. 青年女高音 - 清亮、甜美、活泼
    echo   6. 青年女中音 - 温柔、知性、亲切
    echo   7. 中年女低音 - 温婉、成熟、沉稳
    echo.
    pause
    goto :main_menu
)

if "%choice%"=="2" (
    echo.
    set /p custom_portrait="请输入自定义画像描述 (例如: 青年女高音，活泼可爱): "
    if "!custom_portrait!"=="" (
        echo ❌ 输入不能为空
        pause
        goto :main_menu
    )
    set portrait=!custom_portrait!
    goto :set_params
)

if "%choice%"=="1" (
    echo.
    echo 请选择预设画像:
    echo 1. 中年男中音
    echo 2. 中年男低音
    echo 3. 青年男高音
    echo 4. 中年男高音
    echo 5. 青年女高音
    echo 6. 青年女中音
    echo 7. 中年女低音
    echo.
    
    set /p portrait_choice="请输入选项 (1-7): "
    
    if "!portrait_choice!"=="1" set portrait=中年男中音
    if "!portrait_choice!"=="2" set portrait=中年男低音
    if "!portrait_choice!"=="3" set portrait=青年男高音
    if "!portrait_choice!"=="4" set portrait=中年男高音
    if "!portrait_choice!"=="5" set portrait=青年女高音
    if "!portrait_choice!"=="6" set portrait=青年女中音
    if "!portrait_choice!"=="7" set portrait=中年女低音
    
    goto :set_params
)

echo ❌ 无效选项
pause
goto :main_menu

:set_params
echo.
echo 当前选择: %portrait%
echo.

set /p epochs="请输入训练轮数 (默认: 50): "
if "!epochs!"=="" set epochs=50

set /p sentences="请输入生成句子数 (默认: 30): "
if "!sentences!"=="" set sentences=30

echo.
echo ========================================
echo   开始生成声模
echo ========================================
echo 画像: %portrait%
echo 训练轮数: %epochs%
echo 生成句子: %sentences%
echo ========================================
echo.

%PYTHON% portrait_to_voice_model.py "!portrait!" --epochs !epochs! --sentences !sentences!

echo.
echo ========================================
echo   生成完成！
echo ========================================
pause
exit /b
