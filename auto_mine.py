# auto_mine.py
import time
import pyautogui

def sleep_with_stop(delay_seconds, stop_event):
    if stop_event is None:
        time.sleep(delay_seconds)
        return False

    end_time = time.time() + delay_seconds
    while time.time() < end_time:
        if stop_event.is_set():
            return True
        time.sleep(0.05)
    return False

def run_auto_mine(stop_event=None, startup_delay=3):
    # Safety: move mouse to top-left corner to STOP script instantly
    pyautogui.FAILSAFE = True

    if sleep_with_stop(startup_delay, stop_event):
        return

    while True:
        if stop_event is not None and stop_event.is_set():
            break

        # Press F key
        pyautogui.press('f')

        # Small delay
        if sleep_with_stop(0.2, stop_event):
            break

        # Scroll down (negative = down, positive = up)
        pyautogui.scroll(-300)

        # Delay before next loop
        if sleep_with_stop(0.5, stop_event):
            break
