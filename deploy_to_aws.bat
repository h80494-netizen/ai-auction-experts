@echo off
chcp 65001 > NUL
cd /d "%~dp0"

echo ==========================================================
echo 🚀 AWS EC2 서버 원클릭 자동 배포 도구
echo ==========================================================
echo.
echo  [1] 코드 및 화면 변경사항 초고속 배포 (권장, 3초 소요)
echo  [2] 전체 동기화 배포 (대용량 DB map_data.db 포함)
echo.
set /p MODE="배포 옵션을 선택하세요 (1 또는 2, 기본값: 1): "

if "%MODE%"=="2" (
    echo.
    echo [전체 동기화 모드] 대용량 DB를 포함하여 배포를 시작합니다...
    python deploy_to_aws.py --with-db
) else (
    echo.
    echo [초고속 코드 모드] 코드 및 UI 변경사항을 배포합니다...
    python deploy_to_aws.py
)

echo.
pause
