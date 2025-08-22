# backend/hero_scanner.py
import os, platform, json, time, threading, hashlib, re, traceback
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import cv2
from PIL import Image
import pytesseract
import imagehash
import requests
from mss import mss

# ========================= Config =========================
BACKEND_BASE = os.environ.get("E7_BACKEND_URL", "http://localhost:5000")
INGEST_URL   = f"{BACKEND_BASE}/ingest_unit_ocr"
EVENT_URL    = f"{BACKEND_BASE}/scan_event"

USERNAME_HEADER = "username"
USERNAME_VALUE  = ""   # set by /scanner route in app.py

DWELL_SECONDS = 2.0
FPS = 6

VERBOSE = True
PRINT_EVERY_SEC = 2.0

# ========================= Resolve status path =========================
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

def _default_data_dir() -> Path:
    sys = platform.system()
    if sys == "Windows":
        base = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        return Path(base) / "E7Armory"
    elif sys == "Darwin":
        return Path.home() / "Library" / "Application Support" / "E7Armory"
    else:
        base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(base) / "E7Armory"

def _resolve_status_path() -> Path:
    env_dir = os.environ.get("E7_STATUS_DIR")
    if env_dir:
        return Path(env_dir) / "monitor_status.json"
    # dev: project root or parent
    for c in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
        p = c / "monitor_status.json"
        if p.exists():
            return p
    return _default_data_dir() / "monitor_status.json"

STATUS_PATH = _resolve_status_path()
BASE_DIR    = STATUS_PATH.parent  # <<< all captures go next to monitor_status.json
STATUS_DIR  = BASE_DIR

# Always save raw window screenshots whenever found=True
WINDOW_STREAM_DIR = BASE_DIR / "captures_window"
WINDOW_STREAM_INTERVAL = 1.0   # seconds
MAX_WINDOW_SNAPSHOTS = 500

# Save annotated debug images for OCR ingest/errors
SNAPSHOT_DIR = BASE_DIR / "captures_debug"
MAX_SNAPSHOTS = 200

# ========================= ROIs (fractions of game window) =========================
ROI = {
    "name":        [0.078125, 0.157407, 0.442708, 0.212963],
    "cp":          [0.107813, 0.513889, 0.211979, 0.560185],
    "stat_labels": [0.050000, 0.570000, 0.180000, 0.820000],
    "attack":      [0.217708, 0.574074, 0.254167, 0.600926],
    "defense":     [0.217708, 0.600000, 0.254167, 0.631481],
    "health":      [0.205208, 0.632407, 0.257292, 0.663889],
    "speed":       [0.200521, 0.666667, 0.252604, 0.693519],
    "crit_chance": [0.200521, 0.694444, 0.252604, 0.721296],
    "crit_damage": [0.200521, 0.726852, 0.252604, 0.758333],
    "eff":         [0.200521, 0.759259, 0.252604, 0.790741],
    "eff_res":     [0.200521, 0.787037, 0.252604, 0.818519],
}

# ========================= Helpers =========================
RE_NUM = re.compile(r"[0-9][0-9,]*")
RE_PCT = re.compile(r"(\d{1,3})(?:\.\d+)?\s*%")
TESS_NUM = r'--oem 3 --psm 7 -l eng -c tessedit_char_whitelist=0123456789,%+'
TESS_TXT = r'--oem 3 --psm 7 -l eng'
# pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_CMD", pytesseract.pytesseract.tesseract_cmd)

_last_print = 0.0

def _log(msg: str):
    global _last_print
    now = time.time()
    if VERBOSE and (now - _last_print) >= PRINT_EVERY_SEC:
        print(f"[hero_scanner] {msg}")
        _last_print = now

def _read_monitor_status() -> dict:
    if STATUS_PATH.exists():
        try:
            return json.loads(STATUS_PATH.read_text(encoding="utf-8") or "{}")
        except Exception:
            return {}
    return {}

def _write_hero_scanner_flag(on: bool):
    try:
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        data = _read_monitor_status()
        data["hero_scanner_running"] = on
        STATUS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

def _ensure_dirs():
    try:
        WINDOW_STREAM_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"[hero_scanner] saving window caps to: {WINDOW_STREAM_DIR}")
        print(f"[hero_scanner] saving debug caps  to: {SNAPSHOT_DIR}")
    except Exception as e:
        print(f"[hero_scanner] could not create capture dirs: {e}")

def crop_frac(img: np.ndarray, box) -> np.ndarray:
    H, W = img.shape[:2]
    x0 = int(box[0] * W); y0 = int(box[1] * H)
    x1 = int(box[2] * W); y1 = int(box[3] * H)
    x0 = max(0, min(W-1, x0)); x1 = max(1, min(W, x1))
    y0 = max(0, min(H-1, y0)); y1 = max(1, min(H, y1))
    return img[y0:y1, x0:x1]

def _binarize(gray):
    gray = cv2.bilateralFilter(gray, 7, 35, 35)
    return cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 9)

def ocr_text(img: np.ndarray, numeric=False) -> str:
    th = _binarize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    return pytesseract.image_to_string(Image.fromarray(th),
                                       config=TESS_NUM if numeric else TESS_TXT).strip()

def clean_int(s: str) -> Optional[int]:
    if not s: return None
    s = s.replace("O","0")
    m = RE_NUM.search(s)
    return int(m.group(0).replace(",","")) if m else None

def clean_pct(s: str) -> Optional[float]:
    if not s: return None
    s = s.replace("O","0")
    m = RE_PCT.search(s)
    return float(m.group(1)) if m else None

def clean_stat(stat, keep_percentage=False):
    stat = re.sub(r'[*:©]', '', stat or "").strip()
    stat = re.split(r'[.|]', stat)[0].strip()
    if keep_percentage:
        if not stat.endswith('%'): stat += '%'
    else:
        stat = stat.rstrip('%')
    return stat

def clean_unit_name(name):
    cleaned_name = re.sub(r'\s*\d+$', '', name or "")
    return cleaned_name.rstrip()

try:
    from name_correction import correct_name, correct_unit_names
except Exception:
    def correct_name(unit_name: str, lst): return None
    correct_unit_names = []

def looks_like_hero_page(frame: np.ndarray) -> bool:
    text = ocr_text(crop_frac(frame, ROI["stat_labels"]), numeric=False).lower()
    return ("attack" in text and "defense" in text)

def read_name_cp(frame: np.ndarray):
    raw = ocr_text(crop_frac(frame, ROI["name"]), numeric=False)
    name = re.sub(r"[^A-Za-z '\-]", "", raw or "").strip()
    name = clean_unit_name(name).lower()
    corr = correct_name(name, correct_unit_names)
    if corr: name = corr
    name_title = " ".join([w.capitalize() for w in name.split()])
    cp = clean_int(ocr_text(crop_frac(frame, ROI["cp"]), numeric=True))
    return name_title, cp

def read_stats(frame: np.ndarray) -> Dict[str, float]:
    vals = {}
    vals["attack"] = clean_int(ocr_text(crop_frac(frame, ROI["attack"]), True))
    vals["defense"] = clean_int(ocr_text(crop_frac(frame, ROI["defense"]), True))
    vals["health"] = clean_int(ocr_text(crop_frac(frame, ROI["health"]), True))
    vals["speed"] = clean_int(ocr_text(crop_frac(frame, ROI["speed"]), True))
    vals["crit_chance"] = clean_pct(ocr_text(crop_frac(frame, ROI["crit_chance"]), False))
    vals["crit_damage"] = clean_pct(ocr_text(crop_frac(frame, ROI["crit_damage"]), False))
    vals["effectiveness"] = clean_pct(ocr_text(crop_frac(frame, ROI["eff"]), False))
    vals["effect_resistance"] = clean_pct(ocr_text(crop_frac(frame, ROI["eff_res"]), False))
    return {k: v for k, v in vals.items() if v is not None}

def phash(img: np.ndarray) -> str:
    return str(imagehash.phash(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))))

def make_sig(hero_name: str, cp: Optional[int], frame: np.ndarray) -> str:
    region = crop_frac(frame, ROI["name"])
    return hashlib.sha1(f"{hero_name}|{cp or 'NA'}|{phash(region)}".encode()).hexdigest()

def send_event(event_type: str, hero_name: str, cp: Optional[int], sig: str, msg: str = ""):
    try:
        headers = {"Content-Type":"application/json"}
        if USERNAME_VALUE: headers[USERNAME_HEADER] = USERNAME_VALUE
        payload = {"event_type": event_type, "hero_name": hero_name, "cp": cp, "sig": sig, "message": msg}
        requests.post(EVENT_URL, json=payload, headers=headers, timeout=3)
    except Exception:
        pass

def _grab_bbox_frame(bbox: Tuple[int,int,int,int]) -> Optional[np.ndarray]:
    try:
        l, t, r, b = bbox
        w, h = max(1, r - l), max(1, b - t)
        with mss() as sct:
            img = sct.grab({"left": int(l), "top": int(t), "width": int(w), "height": int(h)})
        arr = np.array(img)  # shape (h, w, 4) BGRA
        # Convert to BGR (3 channels) for OpenCV
        if arr.shape[2] == 4:
            arr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        print(f"[hero_scanner] frame shape={arr.shape} dtype={arr.dtype}")
        return arr
    except Exception as e:
        print("[hero_scanner] mss grab failed:", e)
        traceback.print_exc()
        return None

def _annotate(frame: np.ndarray, label: str) -> np.ndarray:
    out = frame.copy()
    H, W = out.shape[:2]
    for k, box in ROI.items():
        x0 = int(box[0] * W); y0 = int(box[1] * H)
        x1 = int(box[2] * W); y1 = int(box[3] * H)
        cv2.rectangle(out, (x0,y0), (x1,y1), (0,255,0), 2)
        cv2.putText(out, k, (x0, max(0,y0-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    cv2.putText(out, label, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2, cv2.LINE_AA)
    return out

def _save_png(img: np.ndarray, prefix: str, directory: Path, max_keep: int):
    try:
        directory.mkdir(parents=True, exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        path = directory / f"{prefix}_{ts}.png"

        ok_cv = False
        try:
            ok_cv = cv2.imwrite(str(path), img)
            print(f"[hero_scanner] cv2.imwrite -> {path} (ok={ok_cv})")
        except Exception as e:
            print(f"[hero_scanner] cv2.imwrite error: {e}")

        if not ok_cv:
            try:
                # Convert BGR->RGB for PIL if 3 channels
                if len(img.shape) == 3 and img.shape[2] == 3:
                    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                elif len(img.shape) == 2:
                    pil_img = Image.fromarray(img)
                else:
                    # try RGBA path if needed
                    pil_img = Image.fromarray(img)
                pil_img.save(str(path))
                print(f"[hero_scanner] PIL.save -> {path} (ok=True)")
            except Exception as e2:
                print(f"[hero_scanner] PIL.save error: {e2}")
        # prune
        files = sorted(directory.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
        for f in files[max_keep:]:
            try: f.unlink(missing_ok=True)
            except Exception: pass
    except Exception as e:
        print(f"[hero_scanner] save failed for {prefix}: {e}")
        traceback.print_exc()

# ========================= Thread =========================
class HeroScanner(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop_event = threading.Event()   # renamed to avoid shadowing Thread._stop()
        self._last_sig = None
        self._first_seen = 0.0
        self._recent = set()
        self._last_bbox = None            # tuple[int,int,int,int], for logging/changes only
        self._last_window_snap = 0.0

    def stop(self):
        self._stop_event.set()

    def run(self):
        print(f"[hero_scanner] monitor_status at {STATUS_PATH}")
        print(f"[hero_scanner] saving window caps to: {WINDOW_STREAM_DIR}")
        print(f"[hero_scanner] saving debug caps  to: {SNAPSHOT_DIR}")
        WINDOW_STREAM_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        _write_hero_scanner_flag(True)

        try:
            while not self._stop_event.is_set():
                # --- read status and normalize bbox every loop ---
                st = _read_monitor_status()
                found = bool(st.get("found"))
                bbox = st.get("bbox")
                bbox_norm = tuple(map(int, bbox)) if isinstance(bbox, (list, tuple)) and len(bbox) == 4 else None
                _log(f"found={found} bbox={bbox_norm}")

                if not found or not bbox_norm:
                    self._last_sig = None
                    self._last_bbox = None
                    time.sleep(1.0 / FPS)
                    continue

                if bbox_norm != self._last_bbox:
                    print(f"[hero_scanner] bbox changed: {self._last_bbox} -> {bbox_norm}")
                    self._last_bbox = bbox_norm

                # ---- ALWAYS use the CURRENT bbox (so it follows the window) ----
                frame = _grab_bbox_frame(bbox_norm)
                if frame is None or frame.size == 0:
                    time.sleep(1.0 / FPS)
                    continue

                # Save window snapshot (throttled) — include bbox in filename to verify
                now = time.time()
                if (now - self._last_window_snap) >= WINDOW_STREAM_INTERVAL:
                    prefix = f"window_{bbox_norm[0]}_{bbox_norm[1]}_{bbox_norm[2]}_{bbox_norm[3]}"
                    _save_png(frame, prefix, WINDOW_STREAM_DIR, MAX_WINDOW_SNAPSHOTS)
                    self._last_window_snap = now

                # ---- OCR path (unchanged) ----
                if not looks_like_hero_page(frame):
                    self._last_sig = None
                    self._first_seen = 0.0
                    time.sleep(1.0 / FPS)
                    continue

                name, cp = read_name_cp(frame)
                sig = make_sig(name, cp, frame)

                if sig != self._last_sig:
                    self._last_sig = sig
                    self._first_seen = now

                if now - self._first_seen >= DWELL_SECONDS and sig not in self._recent:
                    stats = read_stats(frame)
                    try:
                        headers = {"Content-Type": "application/json"}
                        if USERNAME_VALUE:
                            headers[USERNAME_HEADER] = USERNAME_VALUE
                        payload = {"hero_name": name, "cp": cp, "stats": stats, "sig": sig}
                        r = requests.post(INGEST_URL, json=payload, headers=headers, timeout=8)
                        r.raise_for_status()
                        event = r.json().get("event", "added")
                        _save_png(_annotate(frame, f"{event.upper()}: {name}"), "ingest", SNAPSHOT_DIR, MAX_SNAPSHOTS)
                        self._recent.add(sig)
                        time.sleep(1.0)  # cooldown
                    except Exception as e:
                        _save_png(_annotate(frame, f"ERROR: {e}"), "error", SNAPSHOT_DIR, MAX_SNAPSHOTS)

                time.sleep(1.0 / FPS)
        finally:
            _write_hero_scanner_flag(False)


_scanner: Optional[HeroScanner] = None

def start_scanner():
    global _scanner
    if _scanner and _scanner.is_alive(): return
    _write_hero_scanner_flag(True)
    _scanner = HeroScanner(); _scanner.start()

def stop_scanner():
    global _scanner
    if _scanner:
        _scanner.stop(); _scanner.join(timeout=2.0)
        _scanner = None
    _write_hero_scanner_flag(False)

if __name__ == "__main__":
    try:
        start_scanner()
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_scanner()
