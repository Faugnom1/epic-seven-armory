# Debug script to identify the correct Epic Seven window coordinates

import pygetwindow as gw
import win32gui
import win32process
import psutil
from typing import Optional, Tuple

def debug_all_epic_windows():
    """Find all windows that might be Epic Seven and show their coordinates"""
    print("=== DEBUGGING EPIC SEVEN WINDOW DETECTION ===\n")
    
    all_windows = gw.getAllWindows()
    epic_candidates = []
    
    for w in all_windows:
        title = (w.title or "").lower()
        
        # Look for any window with "epic" or "seven" in the title
        if "epic" in title or "seven" in title:
            print(f"FOUND CANDIDATE: '{w.title}'")
            print(f"  Coordinates: ({w.left}, {w.top}, {w.right}, {w.bottom})")
            print(f"  Size: {w.width} x {w.height}")
            print(f"  Visible: {w.visible}")
            
            # Get process info if available
            if hasattr(w, '_hWnd') and w._hWnd:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(w._hWnd)
                    process = psutil.Process(pid)
                    class_name = win32gui.GetClassName(w._hWnd)
                    print(f"  Process: {process.name()}")
                    print(f"  Window Class: {class_name}")
                    print(f"  HWND: {w._hWnd}")
                except Exception as e:
                    print(f"  Process info failed: {e}")
            
            epic_candidates.append(w)
            print()
    
    print(f"Total candidates found: {len(epic_candidates)}")
    return epic_candidates

def debug_window_positions():
    """Show positions of all visible windows to help identify the correct game window"""
    print("=== ALL VISIBLE WINDOWS (for reference) ===\n")
    
    windows = gw.getAllWindows()
    game_sized_windows = []
    
    for w in windows:
        if w.visible and w.width > 500 and w.height > 400:  # Reasonable game window size
            print(f"'{w.title}' -> ({w.left}, {w.top}, {w.right}, {w.bottom}) [{w.width}x{w.height}]")
            
            # Check if this could be a game window
            if w.width > 1000 and w.height > 600:
                game_sized_windows.append(w)
    
    print(f"\nLarge windows that could be games: {len(game_sized_windows)}")
    for w in game_sized_windows:
        print(f"  '{w.title}' -> ({w.left}, {w.top}, {w.right}, {w.bottom})")

def test_coordinates_on_screenshot():
    """
    Based on your screenshot, let's manually identify what the correct coordinates should be.
    Your current bbox [302, 103, 1813, 982] is clearly wrong.
    """
    print("=== COORDINATE ANALYSIS ===\n")
    
    current_bbox = [302, 103, 1813, 982]
    print(f"Current (incorrect) bbox: {current_bbox}")
    print(f"Current size: {current_bbox[2] - current_bbox[0]} x {current_bbox[3] - current_bbox[1]}")
    
    # From your screenshot, it looks like the Epic Seven window should be roughly:
    # - Starting more to the right (maybe around x=650-700 based on the visible content)
    # - The width looks reasonable but the left edge is wrong
    
    print("\nAnalyzing your screenshot:")
    print("- Current capture starts at x=302, but Epic Seven window appears to start around x=650+")
    print("- The height (982-103=879) might be correct")
    print("- The width (1813-302=1511) might be too wide")
    
    # Let's find windows that might match the actual game position
    windows = gw.getAllWindows()
    for w in windows:
        title = w.title or ""
        # Look for windows positioned more to the right where the game actually appears
        if w.left > 600 and w.left < 800 and w.width > 1000 and w.height > 600:
            print(f"\nPotential match: '{title}'")
            print(f"  Position: ({w.left}, {w.top}, {w.right}, {w.bottom})")
            print(f"  Size: {w.width} x {w.height}")

def get_window_at_cursor_position():
    """Get the window that's currently under the mouse cursor"""
    try:
        import win32gui
        from ctypes import windll, Structure, c_long, byref
        
        class POINT(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]
        
        # Get cursor position
        cursor_pos = POINT()
        windll.user32.GetCursorPos(byref(cursor_pos))
        
        # Get window at cursor position
        hwnd = win32gui.WindowFromPoint((cursor_pos.x, cursor_pos.y))
        
        if hwnd:
            title = win32gui.GetWindowText(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            print(f"Window under cursor: '{title}'")
            print(f"Position: {rect}")
            print(f"Size: {rect[2]-rect[0]} x {rect[3]-rect[1]}")
            
            return hwnd, rect
            
    except Exception as e:
        print(f"Error getting window at cursor: {e}")
    
    return None, None

def manual_coordinate_finder():
    """
    Interactive tool to help find the correct Epic Seven window coordinates
    """
    print("=== MANUAL COORDINATE FINDER ===")
    print("1. Position your mouse over the TOP-LEFT corner of the Epic Seven game window")
    print("2. Press Enter")
    input("Press Enter when mouse is at TOP-LEFT of game window...")
    
    try:
        from ctypes import windll, Structure, c_long, byref
        
        class POINT(Structure):
            _fields_ = [("x", c_long), ("y", c_long)]
        
        # Get top-left position
        tl_pos = POINT()
        windll.user32.GetCursorPos(byref(tl_pos))
        print(f"Top-left recorded: ({tl_pos.x}, {tl_pos.y})")
        
        print("\n3. Now position your mouse over the BOTTOM-RIGHT corner of the Epic Seven game window")
        print("4. Press Enter")
        input("Press Enter when mouse is at BOTTOM-RIGHT of game window...")
        
        # Get bottom-right position
        br_pos = POINT()
        windll.user32.GetCursorPos(byref(br_pos))
        print(f"Bottom-right recorded: ({br_pos.x}, {br_pos.y})")
        
        # Calculate correct bbox
        correct_bbox = [tl_pos.x, tl_pos.y, br_pos.x, br_pos.y]
        width = br_pos.x - tl_pos.x
        height = br_pos.y - tl_pos.y
        
        print(f"\n=== CORRECT COORDINATES ===")
        print(f"Bbox: {correct_bbox}")
        print(f"Size: {width} x {height}")
        
        # Compare with current wrong coordinates
        current_bbox = [302, 103, 1813, 982]
        print(f"\nComparison:")
        print(f"Current (wrong): {current_bbox}")
        print(f"Correct:         {correct_bbox}")
        print(f"Difference: left={correct_bbox[0]-current_bbox[0]}, top={correct_bbox[1]-current_bbox[1]}")
        
        return correct_bbox
        
    except Exception as e:
        print(f"Error in manual finder: {e}")
        return None

if __name__ == "__main__":
    print("Epic Seven Window Detection Debugger")
    print("=====================================\n")
    
    # Run all debug functions
    debug_all_epic_windows()
    print("\n" + "="*50 + "\n")
    debug_window_positions()
    print("\n" + "="*50 + "\n")
    test_coordinates_on_screenshot()
    print("\n" + "="*50 + "\n")
    
    # Interactive coordinate finder
    try:
        correct_coords = manual_coordinate_finder()
        if correct_coords:
            print(f"\nUse these coordinates in your window finder: {correct_coords}")
    except KeyboardInterrupt:
        print("\nManual finder skipped")