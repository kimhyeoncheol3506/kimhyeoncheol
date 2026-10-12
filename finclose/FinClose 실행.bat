@echo off
REM 더블클릭으로 FinClose 데스크톱 앱 실행(소스 버전, Python 필요). 처음 한 번은 설치 때문에 몇 분 걸립니다.
REM 연습 모드: 이 파일을 "FinClose 실행.bat demo" 로 실행하거나 "FinClose 연습모드.bat" 사용
chcp 65001 >nul
cd /d "%~dp0"
if not exist backend\.venv\Scripts\pythonw.exe (
  echo 처음 실행 준비 중입니다. 잠시 기다려 주세요...
  py -3 -m venv backend\.venv 2>nul || python -m venv backend\.venv
  if errorlevel 1 ( echo Python 3.11 이상을 먼저 설치하세요: https://www.python.org/downloads/ & pause & exit /b 1 )
  backend\.venv\Scripts\python -m pip install -q --upgrade pip
  backend\.venv\Scripts\python -m pip install -q -r backend\requirements.txt
  if errorlevel 1 ( echo 설치 실패. 인터넷 연결을 확인하세요. & pause & exit /b 1 )
)
cd backend
if /i "%1"=="demo" ( start "" .venv\Scripts\pythonw.exe -m finclose.desktop --demo ) else ( start "" .venv\Scripts\pythonw.exe -m finclose.desktop )
