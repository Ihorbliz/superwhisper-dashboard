#!/bin/bash
# Sync-only launcher — for use with cron (macOS/Linux)
# Syncs new recordings into history.json without opening the browser.
#
# To automate with cron (runs every Monday at 10:00):
#   crontab -e
#   0 10 * * 1 /full/path/to/sync_only.sh >> /full/path/to/sync_log.txt 2>&1

cd "$(dirname "$0")"
python3 sync_history.py
