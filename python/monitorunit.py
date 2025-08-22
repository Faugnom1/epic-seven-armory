import pyautogui
import cv2
import numpy as np
import time
import os
import json
import sys
from pathlib import Path
import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Projects\EpicSevenArmory\backend\Pytesseract\tesseract.exe'

# Define regions for character portraits (x, y, width, height)
LEFT_UNITS = [
    (50, 200, 100, 100),
    (30, 320, 100, 100),
    (20, 440, 100, 100),
    (10, 560, 100, 100),
    (10, 680, 100, 100)
]

RIGHT_UNITS = [
    (850, 200, 100, 100),
    (870, 320, 100, 100),
    (880, 440, 100, 100),
    (890, 560, 100, 100),
    (890, 680, 100, 100)
]

def get_bluestacks_window():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and 'BlueStacks' in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def capture_bluestacks_window():
    hwnd = get_bluestacks_window()
    if not hwnd:
        print("BlueStacks window not found", file=sys.stderr)
        return None

    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)

    saveDC.SelectObject(saveBitMap)

    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    else:
        print("Failed to capture BlueStacks window", file=sys.stderr)
        return None

def is_pvp_screen(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Define the text to search for
    text = "Choose your team's formation"
    
    # Use pytesseract to do OCR on the image
    import pytesseract
    detected_text = pytesseract.image_to_string(gray)
    
    # Check if the text is in the detected text
    return text.lower() in detected_text.lower()

def extract_unit_images(image):
    left_units = [image[y:y+h, x:x+w] for x, y, w, h in LEFT_UNITS]
    right_units = [image[y:y+h, x:x+w] for x, y, w, h in RIGHT_UNITS]
    return left_units, right_units

def write_status(status_file, status):
    try:
        with open(status_file, 'w') as f:
            json.dump(status, f)
        print(f"Status written to {status_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing status file: {e}", file=sys.stderr)

def main():
    project_dir = Path('C:/Projects/EpicSevenArmory')
    screenshot_dir = project_dir / 'screenshots'
    unit_dir = project_dir / 'unit_portraits'
    status_file = project_dir / 'monitor_status.json'

    print(f"Python script started. Project dir: {project_dir}", file=sys.stderr)
    print(f"Status file location: {status_file}", file=sys.stderr)
    print(f"Screenshot directory: {screenshot_dir}", file=sys.stderr)
    print(f"Unit portraits directory: {unit_dir}", file=sys.stderr)

    try:
        screenshot_dir.mkdir(exist_ok=True)
        unit_dir.mkdir(exist_ok=True)
        print(f"Directories created/verified: {screenshot_dir}, {unit_dir}", file=sys.stderr)
    except Exception as e:
        print(f"Error creating directories: {e}", file=sys.stderr)

    while True:
        try:
            write_status(status_file, {"status": "running", "timestamp": time.time()})
            
            screenshot = capture_bluestacks_window()
            if screenshot is not None:
                print("Checking if it's a PvP screen...", file=sys.stderr)
                if is_pvp_screen(screenshot):
                    timestamp = int(time.time())
                    filename = screenshot_dir / f'pvp_screen_{timestamp}.png'
                    cv2.imwrite(str(filename), screenshot)
                    print(f"PvP screen detected and saved: {filename}", file=sys.stderr)
                    
                    left_units, right_units = extract_unit_images(screenshot)
                    for i, unit in enumerate(left_units):
                        unit_filename = unit_dir / f'left_unit_{i}_{timestamp}.png'
                        cv2.imwrite(str(unit_filename), unit)
                        print(f"Left unit {i} saved: {unit_filename}", file=sys.stderr)
                    for i, unit in enumerate(right_units):
                        unit_filename = unit_dir / f'right_unit_{i}_{timestamp}.png'
                        cv2.imwrite(str(unit_filename), unit)
                        print(f"Right unit {i} saved: {unit_filename}", file=sys.stderr)
                    print(f"Unit portraits extracted and saved", file=sys.stderr)
                else:
                    print("Not a PvP screen, continuing to monitor", file=sys.stderr)
            time.sleep(1)  # Check every second
        except Exception as e:
            print(f"An error occurred in main loop: {e}", file=sys.stderr)
            write_status(status_file, {"status": "error", "message": str(e), "timestamp": time.time()})
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error in main: {e}", file=sys.stderr)