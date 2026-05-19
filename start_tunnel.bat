@echo off
cd /d "%~dp0"
echo =========================================================
echo AI 경매 사이트 - 도메인(인터넷) 연결 실행기
echo =========================================================
echo.
echo 터널을 실행하여 인터넷 접속을 허용합니다...
echo 이 창을 절대 끄지 마세요! (최소화 해두세요)
echo.
backend\cloudflared.exe tunnel run ai-auction-tunnel
pause
