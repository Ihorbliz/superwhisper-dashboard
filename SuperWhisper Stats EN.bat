@echo off
:: SuperWhisper Stats — English dashboard launcher
:: Syncs new recordings and opens dashboard_en.html

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
echo Generating dashboard (EN)...
python generate_dashboard.py --lang en
echo.
pause
