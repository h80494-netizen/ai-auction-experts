@echo off
chcp 65001 > nul
echo ===================================================
echo [경공매 데이터 및 공시지가 자동 업데이트 시스템]
echo ===================================================
echo.
echo 1. 최신 경공매 엑셀 파일 탐색 및 데이터베이스 임포트 중...
python backend/scripts/import_auction_data.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 경공매 데이터 임포트 중 오류가 발생했습니다.
    pause
    exit /b %errorlevel%
)
echo.
echo 2. 공시지가 공간 연동 및 업데이트 중...
python backend/scripts/update_land_price.py
if %errorlevel% neq 0 (
    echo.
    echo [오류] 공시지가 업데이트 중 오류가 발생했습니다.
    pause
    exit /b %errorlevel%
)
echo.
echo ===================================================
echo [성공] 모든 업데이트가 성공적으로 완료되었습니다!
echo ===================================================
echo.
pause
