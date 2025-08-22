# scripts/scan_manager.py
# Background scanner + Flask blueprint to control it and print console status.

from __future__ import annotations
from threading import Thread, Event
from typing import Optional, Tuple
import time

from flask import Blueprint, jsonify, request
from .window_finder import find_epic_seven_window

SCAN_BP = Blueprint("scan", __name__)
_SCAN_THREAD: Optional[Thread] = None
_SCAN_STOP = Event()
_SCAN_ENABLED = False

_WINDOW_PRESENT: Optional[bool] = None  # None=unknown, True=found, False=not found

def _grab_window_frame(bbox: Tuple[int, int, int, int]):
    # Prefer mss for speed; fallback to PIL if missing
    try:
        import mss
        with mss.mss() as sct:
            l, t, r, b = bbox
            mon = {"left": l, "top": t, "width": r - l, "height": b - t}
            img = sct.grab(mon)  # BGRA
            import numpy as _np
            frame = _np.array(img)[:, :, :3][:, :, ::-1]  # BGR
            return frame
    except Exception:
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(bbox=bbox)  # RGB
            import numpy as _np
            frame = _np.array(img)[:, :, ::-1]  # BGR
            return frame
        except Exception:
            return None

def _maybe_print_window_status(found: bool, bbox: Optional[Tuple[int,int,int,int]]):
    global _WINDOW_PRESENT
    if _WINDOW_PRESENT is None or _WINDOW_PRESENT != found:
        _WINDOW_PRESENT = found
        if found:
            l, t, r, b = bbox  # type: ignore
            print(f"[SCAN] Epic Seven window found at bbox: ({l},{t},{r},{b})")
        else:
            print("[SCAN] Epic Seven window not found. Waiting...")

def _scan_loop(stop_event: Event):
    # Hook your existing OCR/unit detection here where 'frame' is captured.
    # E.g., result = recognize_units(frame)
    last_log = 0.0
    while not stop_event.is_set():
        bbox = find_epic_seven_window()
        if not bbox:
            _maybe_print_window_status(False, None)
            time.sleep(1.0)
            continue

        _maybe_print_window_status(True, bbox)
        frame = _grab_window_frame(bbox)
        if frame is None:
            time.sleep(0.4)
            continue

        # TODO: call your existing OCR here with `frame`
        # recognize_units(frame)

        now = time.time()
        # Optional heartbeat every ~10s while scanning
        if now - last_log > 10:
            print("[SCAN] Scanning Epic Seven window...")
            last_log = now

        time.sleep(0.25)  # ~4 FPS (tune)

@SCAN_BP.route("/scan/status", methods=["GET"])
def scan_status():
    return jsonify({"enabled": _SCAN_ENABLED})

@SCAN_BP.route("/scan/toggle", methods=["POST"])
def scan_toggle():
    global _SCAN_THREAD, _SCAN_ENABLED
    payload = request.get_json(silent=True) or {}
    enable = bool(payload.get("enabled"))

    if enable and not _SCAN_ENABLED:
        print("[SCAN] Enabling scanning...")
        _SCAN_ENABLED = True
        _SCAN_STOP.clear()
        _SCAN_THREAD = Thread(target=_scan_loop, args=(_SCAN_STOP,), daemon=True)
        _SCAN_THREAD.start()
    elif not enable and _SCAN_ENABLED:
        print("[SCAN] Disabling scanning...")
        _SCAN_ENABLED = False
        _SCAN_STOP.set()
    return jsonify({"enabled": _SCAN_ENABLED})

def register_blueprint(app):
    app.register_blueprint(SCAN_BP)
