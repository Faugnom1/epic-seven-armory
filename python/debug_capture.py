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
import re

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Projects\EpicSevenArmory\backend\Pytesseract\tesseract.exe'

def get_bluestacks_window():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and 'BlueStacks' in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    if hwnds:
        print(f"BlueStacks window found: {hwnds[0]}", file=sys.stderr)
        return hwnds[0]
    else:
        print("BlueStacks window not found", file=sys.stderr)
        return None

def capture_bluestacks_window():
    hwnd = get_bluestacks_window()
    if not hwnd:
        return None

    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bot - top

    print(f"Window dimensions: {width}x{height}", file=sys.stderr)

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
        print("Screenshot captured successfully", file=sys.stderr)
        return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    else:
        print("Failed to capture BlueStacks window", file=sys.stderr)
        return None

def is_pvp_screen(image):
    # Define the region of interest (ROI)
    height, width = image.shape[:2]
    roi_y = int(height * 0.8)  # Start at 80% of the height
    roi_height = int(height * 0.15)  # Examine 15% of the height
    roi_x = int(width * 0.2)  # Start at 20% of the width
    roi_width = int(width * 0.4)  # Examine 40% of the width
    
    # Extract the ROI
    roi = image[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    
    # Convert ROI to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Perform text detection on ROI
    text = pytesseract.image_to_string(gray)
    print(f"Detected text in ROI: {text}", file=sys.stderr)
    
    # Use a more flexible regular expression to search for the phrase
    pattern = r"Choose your team['’]?s formation"
    match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
    is_pvp = bool(match)
    
    print(f"Is PvP screen: {is_pvp}", file=sys.stderr)
    
    # For debugging, save the ROI image
    cv2.imwrite('roi_debug.png', roi)
    
    if is_pvp:
        print(f"Matched text: {match.group(0)}", file=sys.stderr)
    else:
        print("No match found.", file=sys.stderr)
    
    return is_pvp, image if is_pvp else None

def save_screenshot(image, screenshot_dir, prefix="screen"):
    if image is None:
        print(f"Cannot save {prefix}: Image is None", file=sys.stderr)
        return

    timestamp = int(time.time())
    filename = screenshot_dir / f'{prefix}_{timestamp}.png'
    try:
        cv2.imwrite(str(filename), image)
        print(f"{prefix.capitalize()} saved: {filename}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving {prefix}: {e}", file=sys.stderr)

def template_matching_on_pvp_screen(pvp_image, left_hero_images_dir, right_hero_images_dir, left_units, right_units):
    # Convert the PvP screen to grayscale
    gray_pvp = cv2.cvtColor(pvp_image, cv2.COLOR_BGR2GRAY)
    print("Running template matching...", file=sys.stderr)

    # List of methods to try
    methods = [cv2.TM_SQDIFF_NORMED]

    def match_units(unit_positions, hero_images_dir, side):
        print(f"Matching units in directory: {hero_images_dir} (Side: {side})", file=sys.stderr)
        matches_found = False  # Flag to track if any matches were found
        for filename in os.listdir(hero_images_dir):
            if filename.endswith(".png"):  # Check file extension
                print(f"Processing template: {filename}", file=sys.stderr)
                # Full path to hero image
                template_path = os.path.join(hero_images_dir, filename)

                # Extract the hero's name from the filename
                unit_name = os.path.splitext(os.path.basename(template_path))[0]

                # Load the template image in grayscale
                template_full = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template_full is None:
                    print(f"Failed to load template image: {template_path}", file=sys.stderr)
                    continue

                h_full, w_full = template_full.shape
                crop_size = 50  # Size of the crop, centered
                if h_full < crop_size or w_full < crop_size:
                    print(f"Template image {filename} is smaller than crop size {crop_size}. Skipping.", file=sys.stderr)
                    continue

                start_x = w_full // 2 - crop_size // 2
                start_y = h_full // 2 - crop_size // 2
                template = template_full[start_y:start_y + crop_size, start_x:start_x + crop_size]
                h, w = template.shape

                print(f"Template cropped to size: {template.shape}", file=sys.stderr)

                for method in methods:
                    for idx, (x, y, w_unit, h_unit) in enumerate(unit_positions):
                        unit_roi = gray_pvp[y:y + h_unit, x:x + w_unit]

                        # Verify that unit_roi and template have the same size
                        if unit_roi.shape[0] < h or unit_roi.shape[1] < w:
                            print(f"Unit ROI at position {idx} is smaller than template size. Skipping.", file=sys.stderr)
                            continue

                        # Perform template matching
                        result = cv2.matchTemplate(unit_roi, template, method)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                        # Determine the best match location
                        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                            match_value = min_val
                        else:
                            match_value = max_val

                        # Define threshold
                        threshold = 0.08  # Adjust as needed
                        print(f"Template: {unit_name}, Unit Position: {idx}, Method: {method}, Match Value: {match_value}, Threshold: {threshold}", file=sys.stderr)

                        # Check if the method is cv2.TM_SQDIFF_NORMED and if the match is below a certain threshold
                        if method == cv2.TM_SQDIFF_NORMED:
                            if match_value < threshold:
                                print(f"Matched unit: {unit_name} at position {idx} on {side} side with match value: {match_value}", file=sys.stderr)
                                matches_found = True  # Set flag to true when a match is found

        if not matches_found:
            print(f"No matches found on {side} side.", file=sys.stderr)

    # Match units on the left side
    match_units(left_units, left_hero_images_dir, "Left")

    # Match units on the right side
    match_units(right_units, right_hero_images_dir, "Right")

def main():
    project_dir = Path('C:/Projects/EpicSevenArmory')
    screenshot_dir = project_dir / 'screenshots'
    pvp_screenshot_dir = project_dir / 'pvp_screenshots'
    left_hero_images_dir = project_dir / 'hero_images_reversed'
    right_hero_images_dir = project_dir / 'hero_images'

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

    print(f"Python script started. Project dir: {project_dir}", file=sys.stderr)

    try:
        screenshot_dir.mkdir(exist_ok=True)
        pvp_screenshot_dir.mkdir(exist_ok=True)
        print(f"Directories created/verified: {screenshot_dir}, {pvp_screenshot_dir}", file=sys.stderr)
    except Exception as e:
        print(f"Error creating directories: {e}", file=sys.stderr)

    while True:
        try:
            screenshot = capture_bluestacks_window()
            if screenshot is not None:
                timestamp = int(time.time())
                debug_filename = screenshot_dir / f'debug_{timestamp}.png'
                cv2.imwrite(str(debug_filename), screenshot)
                print(f"Debug screenshot saved: {debug_filename}", file=sys.stderr)
                
                print("Checking if it's a PvP screen...", file=sys.stderr)
                is_pvp, pvp_image = is_pvp_screen(screenshot)
                if is_pvp:
                    pvp_filename = pvp_screenshot_dir / f'pvp_{timestamp}.png'
                    cv2.imwrite(str(pvp_filename), screenshot)
                    print(f"PvP screen detected and saved: {pvp_filename}", file=sys.stderr)

                    # Perform template matching on the PvP screen
                    template_matching_on_pvp_screen(pvp_image, left_hero_images_dir, right_hero_images_dir, LEFT_UNITS, RIGHT_UNITS)

                    # Pause screenshots for 2 minutes
                    print("Pausing screenshots for 2 minutes...", file=sys.stderr)
                    time.sleep(120)
                    
                else:
                    print("Not a PvP screen, deleting debug screenshot", file=sys.stderr)
                    os.remove(debug_filename)
            
            time.sleep(1)  # Wait 1 second before next capture
        except Exception as e:
            print(f"An error occurred: {e}", file=sys.stderr)
            time.sleep(5)  # Wait 5 seconds before retrying after an error

    print("Script finished", file=sys.stderr)

if __name__ == "__main__":
    main()
