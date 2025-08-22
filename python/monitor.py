# python/monitor.py
# Monitors the Epic Seven standalone PC client window and writes status to monitor_status.json
# on every loop, so movement is tracked continuously. Console messages are clean "[Monitor] …".

import json
import os
import sys
import time
from datetime import datetime
from typing import Optional, Tuple

try:
    from window_finder import find_epic_seven_window
except Exception as e:
    print(f"[Monitor] failed to import window finder: {e}", flush=True)
    sys.exit(1)

# Where we write the status (repo root, next to package.json/electron files)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATUS_PATH = os.path.join(REPO_ROOT, "monitor_status.json")

# Loop frequency (seconds). 0.2 = 5 updates/sec (smooth enough to catch drags, light CPU)
LOOP_DELAY = 0.2

def write_status(enabled: bool, found: bool, bbox: Optional[Tuple[int,int,int,int]]) -> None:
    data = {
        "enabled": enabled,
        "found": found,
        "bbox": list(bbox) if bbox else None,
        "ts": datetime.utcnow().isoformat() + "Z"
    }
    try:
        with open(STATUS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[Monitor] failed to write status: {e}", flush=True)

def main():
    print("[Monitor] Epic Seven monitor starting…", flush=True)

    last_found: Optional[bool] = None
    last_bbox: Optional[Tuple[int,int,int,int]] = None

    while True:
        bbox = find_epic_seven_window()
        found = bbox is not None

        # Always write current status so consumers see live bbox updates
        write_status(enabled=True, found=found, bbox=bbox)

        # Print only when state changes or bbox moves (reduces console spam)
        if found:
            if last_found is not True:
                print(f"[Monitor] Epic Seven window found at bbox: {bbox}", flush=True)
            elif last_bbox != bbox:
                print(f"[Monitor] Epic Seven window moved to bbox: {bbox}", flush=True)
        else:
            if last_found is not False:
                print("[Monitor] Epic Seven window not found", flush=True)

        last_found = found
        last_bbox = bbox

        time.sleep(LOOP_DELAY)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[Monitor] stopped by user", flush=True)
    except Exception as e:
        print(f"[Monitor] unexpected error: {e}", flush=True)
