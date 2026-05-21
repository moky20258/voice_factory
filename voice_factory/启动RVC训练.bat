@echo off
chcp 65001 >nul
echo ========================================
echo   声模工厂 - RVC 训练启动器
echo ========================================
echo.

echo 音频数据已准备好:
echo   - 20 个 Speaker
echo   - 3,250 个音频文件
echo   - 平均时长 3.55 秒
echo.

echo 正在启动 RVC WebUI...
echo.

cd /d W:\rvc

echo 提示:
echo 1. 等待看到 "Running on local URL: http://127.0.0.1:7897"
echo 2. 在浏览器打开该地址
echo 3. 切换到"训练"标签页
echo 4. 输入实验名称: speaker_0001
echo 5. 点击"一键训练"
echo.
echo 训练完成后模型保存在:
echo   W:\rvc\logs\speaker_0001\G_200.pth
echo   W:\rvc\logs\speaker_0001\added_200.index
echo.
echo ========================================
echo.

go-web.bat

pause
