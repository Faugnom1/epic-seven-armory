# python/window_finder.py
# Robust Epic Seven standalone PC client window finder.
# - Matches only the REAL game window.
# - Ignores your Electron app ("Epic Seven Armory"), STOVE/launcher, overlays, and minimized/tiny windows.
# - Returns (left, top, right, bottom) or None.

from typing import Optional, Tuple, List
import platform

Rect = Tuple[int, int, int, int]

# Minimum usable size so we don't match tool/hidden windows
MIN_W = 640
MIN_H = 480

# Titles we will EXCLUDE even if they contain "Epic Seven"
EXCLUDE_TITLE_SUBSTRINGS = [
    "armory",           # your app: "Epic Seven Armory"
    "launcher",         # launchers
    "stove",
    "smilegate",
    "overlay",
    "devtools",
    "electron",
    "localhost",
    "chrome",
]

# Electron/Chromium window classes to ignore
EXCLUDE_WIN_CLASSES = {
    "Chrome_WidgetWin_0",
    "Chrome_WidgetWin_1",
}

# Expected game executables (best-effort)
ACCEPTED_EXE_NAMES = {
    "EpicSeven.exe",
    "EpicSeven",                     # some systems report without extension
    "EpicSevenClient.exe",
    "EpicSeven-Win64-Shipping.exe",  # common Unreal naming
}

def _title_is_game(title: str) -> bool:
    if not title:
        return False
    t = title.strip().lower()
    if "epic seven" not in t:
        return False
    for bad in EXCLUDE_TITLE_SUBSTRINGS:
        if bad in t:
            return False
    return True

def _rect_ok(l: int, t: int, r: int, b: int) -> bool:
    w = max(0, r - l)
    h = max(0, b - t)
    return w >= MIN_W and h >= MIN_H and r > l and b > t

def _process_name_from_hwnd(hwnd) -> Optional[str]:
    try:
        import win32process, psutil
        _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        name = psutil.Process(pid).name()
        return name
    except Exception:
        return None

def _class_name_from_hwnd(hwnd) -> Optional[str]:
    try:
        import win32gui
        return win32gui.GetClassName(hwnd)
    except Exception:
        return None

def _is_minimized(hwnd) -> bool:
    try:
        import win32gui
        return bool(win32gui.IsIconic(hwnd))
    except Exception:
        return False

def _is_real_game_window(hwnd, title: str, rect: Rect) -> bool:
    # Title must be Epic Seven and not excluded
    if not _title_is_game(title):
        return False

    # Reject minimized or tiny hidden windows
    if _is_minimized(hwnd):
        return False
    if not _rect_ok(*rect):
        return False

    # Reject known Electron/Chromium classes
    cls = _class_name_from_hwnd(hwnd) or ""
    if cls in EXCLUDE_WIN_CLASSES:
        return False

    # Prefer matching on process name if we can
    pname = _process_name_from_hwnd(hwnd)
    if pname:
        # If it's your Electron app (or anything not in accepted set), reject
        if pname not in ACCEPTED_EXE_NAMES:
            return False

    return True

def _pygetwindow_find() -> Optional[Rect]:
    # Use pygetwindow first (easy enumerate), then verify with Win32 where possible
    try:
        import pygetwindow as gw
        wins = gw.getAllWindows()
        for w in wins:
            title = (w.title or "").strip()
            # On Windows, pygetwindow exposes _hWnd we can validate with
            hwnd = getattr(w, "_hWnd", None)

            # Get bounds
            left = int(getattr(w, "left", 0) or 0)
            top = int(getattr(w, "top", 0) or 0)
            right = int(getattr(w, "right", left) or left)
            bottom = int(getattr(w, "bottom", top) or top)
            rect = (left, top, right, bottom)

            if hwnd is None:
                # If we can't validate via hwnd, fall back to title/rect only (strict title check)
                if _title_is_game(title) and _rect_ok(*rect):
                    return rect
                continue

            if _is_real_game_window(hwnd, title, rect):
                return rect
    except Exception:
        pass
    return None

def _win32_enum_find() -> Optional[Rect]:
    try:
        import win32gui

        found: List[Rect] = []

        def _enum_handler(hwnd, _result):
            if not win32gui.IsWindowVisible(hwnd):
                return

            title = (win32gui.GetWindowText(hwnd) or "").strip()
            try:
                l, t, r, b = win32gui.GetWindowRect(hwnd)
            except Exception:
                return

            rect = (l, t, r, b)
            if _is_real_game_window(hwnd, title, rect):
                _result.append(rect)

        win32gui.EnumWindows(_enum_handler, found)
        return found[0] if found else None
    except Exception:
        return None

def find_epic_seven_window() -> Optional[Rect]:
    # 1) Try pygetwindow
    rect = _pygetwindow_find()
    if rect:
        return rect

    # 2) Fallback to raw Win32 on Windows
    if platform.system().lower() == "windows":
        rect = _win32_enum_find()
        if rect:
            return rect

    return None
