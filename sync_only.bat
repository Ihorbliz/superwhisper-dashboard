@echo off
:: Sync-only launcher — for use with Windows Task Scheduler
:: Syncs new recordings into history.json without opening the browser.
::
:: Task Scheduler command:
::   Program: "%~dp0sync_only.bat"
::   (no need to hardcode the path — %~dp0 resolves to the script's own folder)

cd /d "%~dp0"
python sync_history.py >> sync_log.txt 2>&1
