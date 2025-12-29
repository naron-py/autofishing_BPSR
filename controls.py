# controls.py
import time
import win32api
import win32con
import pyautogui
from win32api import SetCursorPos

# --- Key Code Dictionary ---
KEY_MAP = {
    "a": 0x41, # used in left arrow
    "d": 0x44, # used in right arrow
    "m": 0x4D, # used to change fishing rod when its durability ends
}

# --- Mouse Functions ---
def hold_left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)

def release_left_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def _clamp_to_virtual_screen(x, y):
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    right = left + width - 1
    bottom = top + height - 1
    return (max(left, min(right, x)), max(top, min(bottom, y)))

def move_cursor(x, y):
    x, y = _clamp_to_virtual_screen(int(x), int(y))
    try:
        SetCursorPos((x, y))
    except win32api.error:
        # Fallback to PyAutoGUI if SetCursorPos fails.
        pyautogui.moveTo(x, y)
    return x, y

def click(x, y):
    """
    Moves the mouse to a coordinate and performs a realistic left click.
    """
    x, y = move_cursor(x, y)
    print(f"Moving to ({x}, {y}) and clicking.")
    # A short pause after moving the mouse can be crucial
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    # A short hold time
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# --- Keyboard Functions ---
def hold_key(key):
    """Holds down a key. Expects a single character like 'a'."""
    key_code = KEY_MAP.get(key.lower())
    if key_code:
        win32api.keybd_event(key_code, 0, 0, 0)

def release_key(key):
    """Releases a key. Expects a single character like 'a'."""
    key_code = KEY_MAP.get(key.lower())
    if key_code:
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
