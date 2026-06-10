@echo off
:: SuperWhisper Stats — Ukrainian dashboard launcher
:: Syncs new recordings and opens dashboard_ua.html

cd /d "%~dp0"

echo Syncing SuperWhisper recordings...
python sync_history.py
if errorlevel 1 (
    echo.
    echo ERROR: sync failed. Check that Python is installed and config.py is correct.
    pause
    exit /b 1
)

echo.
echo Generating dashboard (UA)...
python generate_dashboard.py --lang ua
echo.
pause
