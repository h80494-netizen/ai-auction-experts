@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo =========================================================
echo AI Auction / Stock Terminal - Cloudflare Tunnel
echo =========================================================
echo.
echo Starting tunnel to allow internet access...
echo Please do not close this window! (You can minimize it)
echo.
cloudflared.exe tunnel run ai-auction-tunnel
pause
