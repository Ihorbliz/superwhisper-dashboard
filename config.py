#!/usr/bin/env python3
"""
SuperWhisper Dashboard — Configuration
=======================================

Two things to configure before first run:

  1. RECORDINGS_PATH  — path to your SuperWhisper recordings folder
  2. TYPING_WPM       — your personal typing speed (WPM × accuracy)

Everything else has sensible defaults.
"""

import os
import sys
from pathlib import Path


# ==============================================================================
# 1. RECORDINGS PATH                                        ← CHANGE THIS
# ==============================================================================
#
# Where SuperWhisper stores its recordings on your computer.
#
# Leave as "AUTO" — the script will try to find it automatically.
# If auto-detection fails, set the path manually:
#
#   macOS:   "~/Library/Application Support/com.superwhisper.app/recordings"
#   Windows: "C:/Users/YOUR_USERNAME/AppData/Local/com.superwhisper.app/recordings"
#
# How to find it manually:
#   macOS:   Finder → Go → Go to Folder → paste the path above
#   Windows: Explorer address bar → paste %LOCALAPPDATA%\com.superwhisper.app\recordings

RECORDINGS_PATH = "AUTO"


# ==============================================================================
# 2. TYPING SPEED                                           ← CHANGE THIS
# ==============================================================================
#
# Your effective typing speed = raw WPM × accuracy.
#
# How to measure: go to monkeytype.com, run a 60-second test, then multiply.
# Example: 50 WPM × 0.89 accuracy = 44
#
# This value is used to calculate how much time you saved by speaking
# instead of typing. The higher your real speed, the smaller the savings.

TYPING_WPM = 44


# ==============================================================================
# 3. MEETING MODE NAMES                          ← CHANGE IF NEEDED
# ==============================================================================
#
# SuperWhisper mode names that count as MEETING recordings.
# Meetings are shown in a separate card and excluded from time-savings math.
#
# The check: does the mode name START WITH any of these strings?
# Case-insensitive. Default catches "Meeting OPUS", "Meeting Whisper", etc.
#
# To find your mode names: SuperWhisper → Settings → Modes
#
# Examples:
#   MEETING_PREFIXES = ['meeting']
#   MEETING_PREFIXES = ['meeting', 'нарада', 'call', 'zoom']

MEETING_PREFIXES = ['meeting']


# ==============================================================================
# Internal helpers — no need to edit below this line
# ==============================================================================

def _detect_recordings_path():
    """Try to find the SuperWhisper recordings folder automatically."""
    if sys.platform == 'darwin':
        candidates = [
            "~/Library/Application Support/com.superwhisper.app/recordings",
            "~/Library/Application Support/SuperWhisper/recordings",
        ]
    elif sys.platform == 'win32':
        local = os.environ.get('LOCALAPPDATA', '')
        candidates = [
            os.path.join(local, 'com.superwhisper.app', 'recordings') if local else '',
            "~/AppData/Local/com.superwhisper.app/recordings",
        ]
    else:
        candidates = [
            "~/.local/share/com.superwhisper.app/recordings",
        ]
    for p in candidates:
        if not p:
            continue
        expanded = Path(os.path.expanduser(p))
        if expanded.exists() and expanded.is_dir():
            return expanded
    return None


def get_recordings_path():
    """Return the recordings path as a Path object."""
    if RECORDINGS_PATH == "AUTO":
        detected = _detect_recordings_path()
        if detected:
            return detected
        raise FileNotFoundError(
            "Could not auto-detect SuperWhisper recordings path.\n"
            "Please set RECORDINGS_PATH in config.py manually."
        )
    return Path(os.path.expanduser(RECORDINGS_PATH))


if __name__ == "__main__":
    print("SuperWhisper Dashboard — config check")
    print("=" * 40)
    try:
        p = get_recordings_path()
        if p.exists():
            print(f"  Recordings path OK: {p}")
        else:
            print(f"  WARNING: path does not exist: {p}")
    except FileNotFoundError as e:
        print(f"  ERROR: {e}")
    print(f"  Typing speed: {TYPING_WPM} WPM")
    print(f"  Meeting prefixes: {MEETING_PREFIXES}")
