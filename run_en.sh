#!/bin/bash
# SuperWhisper Stats — English dashboard launcher (macOS / Linux)
# Usage: ./run_en.sh

cd "$(dirname "$0")"

echo "Syncing SuperWhisper recordings..."
python3 sync_history.py || { echo "ERROR: sync failed."; exit 1; }

echo ""
echo "Generating dashboard (EN)..."
python3 generate_dashboard.py --lang en
