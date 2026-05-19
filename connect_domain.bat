@echo off
cd /d "%~dp0"
echo =========================================================
echo Cloudflare Tunnel Setup Wizard (Auto-Cert Fix)
echo =========================================================
echo.
echo [Step 1] Logging into Cloudflare.
echo A browser window will open. Please login and click "Authorize".
echo.
echo **IMPORTANT**: Your browser might download a file named "cert.pem".
echo Please MAKE SURE the file is downloaded. (Check your browser's download history)
echo.
backend\cloudflared.exe tunnel login
echo.
echo Please check if "cert.pem" is downloaded. 
echo Once downloaded, press any key to continue. We will automatically move it for you!
pause
echo.
echo [Moving certificate from Downloads if it exists...]
if exist "%USERPROFILE%\Downloads\cert.pem" (
    move /Y "%USERPROFILE%\Downloads\cert.pem" "%USERPROFILE%\.cloudflared\cert.pem"
    echo Successfully moved cert.pem!
) else if exist "%USERPROFILE%\Downloads\cert (1).pem" (
    move /Y "%USERPROFILE%\Downloads\cert (1).pem" "%USERPROFILE%\.cloudflared\cert.pem"
    echo Successfully moved cert (1).pem!
) else (
    echo No cert.pem found in Downloads. (It might already be installed)
)
echo.
echo [Step 2] Creating tunnel: ai-auction-tunnel
backend\cloudflared.exe tunnel create ai-auction-tunnel
echo.
echo [Step 3] Routing domain to tunnel (ai-auction-experts.cloud)
backend\cloudflared.exe tunnel route dns ai-auction-tunnel ai-auction-experts.cloud
echo.
echo [Step 4] Starting the tunnel...
echo (Keep this window open to keep the site online)
echo.
backend\cloudflared.exe tunnel run ai-auction-tunnel
pause
