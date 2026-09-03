@echo off
chcp 65001 > NUL
echo ==========================================================
echo 📦 AWS EC2 데이터베이스 및 대용량 파일 전송 도구
echo ==========================================================
echo.

set /p EC2_HOST="1. EC2 공인 IP 또는 퍼블릭 DNS를 입력하세요 (예: 13.125.xx.xx): "
set /p PEM_KEY="2. SSH 키(.pem) 파일의 전체 경로를 입력하세요: "
set /p EC2_USER="3. SSH 사용자명 [기본값: ubuntu]: "

if "%EC2_USER%"=="" set EC2_USER=ubuntu

echo.
echo [전송 시작] backend/data 디렉토리 데이터를 EC2 서버로 업로드합니다...
echo.

scp -i "%PEM_KEY%" -r backend\data\* %EC2_USER%@%EC2_HOST%:~/ai-auction-experts/backend/data/

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 데이터 전송이 성공적으로 완료되었습니다!
) else (
    echo.
    echo ❌ 전송 중 오류가 발생했습니다. IP와 키페어 경로를 확인해주세요.
)

pause
