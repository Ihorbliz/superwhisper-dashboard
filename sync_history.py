#!/usr/bin/env python3
"""
SuperWhisper History Sync
=========================
Reads recordings from your SuperWhisper folder and appends new entries
to history.json. Safe to run multiple times — already-saved recordings
are never duplicated (deduplication by folder ID).

Run this weekly to preserve data before SuperWhisper auto-deletes old recordings.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import config

HISTORY_FILE = Path(__file__).parent / "history.json"


def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"recordings": [], "last_sync": None}


def save_history(data):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def is_meeting(mode_name):
    """Return True if the mode name matches any configured meeting prefix."""
    prefixes = getattr(config, 'MEETING_PREFIXES', ['meeting'])
    return any(mode_name.lower().startswith(p.lower()) for p in prefixes)


def sync():
    recordings_path = config.get_recordings_path()
    if not recordings_path.exists():
        print(f"ERROR: Recordings path not found: {recordings_path}")
        print("Check RECORDINGS_PATH in config.py")
        return

    history = load_history()
    known_folders = {r['folder'] for r in history['recordings']}

    folders = [
        f for f in os.listdir(recordings_path)
        if os.path.isdir(recordings_path / f) and not f.startswith('.')
    ]

    new_count = 0
    for folder_name in folders:
        if folder_name in known_folders:
            continue

        meta_file = recordings_path / folder_name / 'meta.json'
        if not meta_file.exists():
            continue

        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            mode_name   = data.get('modeName', '')
            result_text = data.get('result', '') or data.get('rawResult', '') or ''
            duration_ms = data.get('duration', 0)

            history['recordings'].append({
                'folder':           folder_name,
                'datetime':         data.get('datetime', ''),
                'duration_ms':      duration_ms,
                'duration_minutes': duration_ms / 1000 / 60,
                'mode_name':        mode_name,
                'recording_type':   'meeting' if is_meeting(mode_name) else 'dictation',
                'word_count':       len(result_text.split()) if result_text else 0,
                'model_name':       data.get('modelName', ''),
                'app_version':      data.get('appVersion', ''),
            })
            new_count += 1

        except Exception as e:
            print(f"  Skipping {folder_name}: {e}")

    history['last_sync'] = datetime.now().isoformat()
    save_history(history)

    total = len(history['recordings'])
    print(f"Synced {new_count} new recordings. Total in history: {total}")
    print(f"Saved to: {HISTORY_FILE}")


if __name__ == "__main__":
    print("Syncing SuperWhisper history...")
    sync()
