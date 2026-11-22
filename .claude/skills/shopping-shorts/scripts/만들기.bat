@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo 쇼핑 쇼츠 만드는 중... (1~2분)
call "%USERPROFILE%\.aside\runtime\bin\python.cmd" "%USERPROFILE%\.aside\u\0\skills\user\shopping-shorts\scripts\render_short.py" "%~dp0."
if errorlevel 1 (echo 실패했습니다. render_log.txt 를 Aside 에 보여주세요.) else (start "" "%~dp0out\final.mp4")
pause
