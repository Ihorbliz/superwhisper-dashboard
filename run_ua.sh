#!/bin/bash
# SuperWhisper Stats — Ukrainian dashboard launcher (macOS / Linux)
# Usage: ./run_ua.sh

cd "$(dirname "$0")"

echo "Syncing SuperWhisper recordings..."
python3 sync_history.py || { echo "ERROR: sync failed."; exit 1; }

echo ""
echo "Generating dashboard (UA)..."
python3 generate_dashboard.py --lang ua
