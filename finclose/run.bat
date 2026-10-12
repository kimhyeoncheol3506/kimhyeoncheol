@echo off
REM FinClose AI 로컬 실행 (Windows)
REM   run.bat          설치(최초 1회) 후 서버 실행 -> http://127.0.0.1:8000
REM   run.bat test     테스트 실행
REM   run.bat demo     시연용 과거 이력 생성 후 실행
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist backend\.venv\Scripts\python.exe (
  echo [1/3] Python 가상환경 생성 및 패키지 설치
  py -3 -m venv backend\.venv 2>nul || python -m venv backend\.venv
  if errorlevel 1 ( echo Python 3.11 이상을 설치하세요. & exit /b 1 )
  backend\.venv\Scripts\python -m pip install -q --upgrade pip
  backend\.venv\Scripts\python -m pip install -q -r backend\requirements-dev.txt
)

where npm >nul 2>nul
if %errorlevel%==0 (
  if not exist frontend\node_modules (
    echo [2/3] 프런트엔드 패키지 설치
    pushd frontend & call npm install --no-audit --no-fund & popd
  )
  if /i not "%1"=="test" (
    echo [2/3] 프런트엔드 빌드
    pushd frontend & call npm run build >nul & popd
  )
) else (
  if not exist frontend\dist ( echo Node.js가 없고 빌드된 화면도 없습니다. Node.js 18+를 설치하세요. & exit /b 1 )
  echo [2/3] Node.js 없음 - 동봉된 빌드 화면 사용
)

pushd backend
if /i "%1"=="test" (
  .venv\Scripts\python -m pytest
  popd
  where npm >nul 2>nul && (pushd frontend & call npm test & popd)
  exit /b 0
)
if /i "%1"=="demo" .venv\Scripts\python -m finclose.seed_demo
echo [3/3] 서버 시작: http://127.0.0.1:8000  (종료: Ctrl+C)
.venv\Scripts\python -m finclose
popd
