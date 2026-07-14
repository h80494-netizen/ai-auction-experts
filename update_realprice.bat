@echo off
cd /d "%~dp0"
echo ===================================================
echo Real Price Data Update Tool (Monthly Update)
echo ===================================================
echo.
echo 1. Checking realprice directory...
if not exist "realprice" (
    echo [ERROR] 'realprice' directory not found in the root.
    echo Please create 'realprice' directory and put your CSV files there.
    pause
    exit /b
)

echo.
echo 2. Running database migration and grid aggregation...
echo (It will clear old indicators and aggregate from new CSV files...)
python backend/load_realprice_data.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Data migration failed! Please check python console log above.
    pause
    exit /b
)

echo.
echo ===================================================
echo Real price data update completed successfully!
echo The grid indicators on the map have been updated.
echo ===================================================
echo.
pause
