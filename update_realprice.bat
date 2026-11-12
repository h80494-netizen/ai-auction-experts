@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ===================================================
echo 국토부 실거래가 격자 오버레이 업데이트 도구
echo ===================================================
echo.
if not exist "data\실거래가" if not exist "realprice" (
    echo [ERROR] 'data\실거래가' 또는 'realprice' 폴더를 찾을 수 없습니다.
    pause
    exit /b 1
)

echo 최신 실거래가 CSV 집계 및 DB 반영을 시작합니다...
python backend/load_realprice_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 실거래가 데이터 적재 중 오류가 발생했습니다.
    pause
    exit /b 1
)

echo.
echo ===================================================
echo 실거래가 격자 오버레이 업데이트가 완료되었습니다!
echo ===================================================
pause
