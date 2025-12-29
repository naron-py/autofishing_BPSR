# main.py
import threading
import time
import tkinter as tk
from vision import capture_screen, find_template, check_color_in_region
from controls import hold_left_click, release_left_click, hold_key, release_key, click, move_cursor
import cv2
import pyautogui
from win32api import SetCursorPos

# --- IMPORTANT: THESE VALUES ONLY WORK FOR 1920x1080 SCREEN ---
# Coordinates are (x, y, width, height)
FISHING_MONITOR_REGION = (640, 270, 700, 762)
# This point is RELATIVE to your entire screen, not the game window.
CAST_POINT = (960, 600) # Center of a 1920x1080 screen
TENSION_BAR_REGION = (120, 627, 4, 4)
TENSION_BAR_RED_BGR = (9, 11, 199)
TENSION_BAR_WHITE_BGR = (254, 254, 255)
ARROW_REGION = (100, 187, 440, 148)
FIGHT_GRACE_PERIOD = 2.0
EXIT_POINT = (1595, 982)
FISHING_ROD_REGION = (1000, 800, 1040, 1100-762)
FISHING_ROD_ICON_POS = (1674, 1016)
FISHING_ROD_BUY = (1711, 598)

# Tracks the last arrow showed (none=0, left=1, right=2)
last_arrow = 0
counter = 0
COOLDOWN_SECONDS = 1.5 # cooldown duration (1.5 seconds)
last_action_time = 0   # variable to track time

pyautogui.FAILSAFE = True

MODE_FISHING = "FISHING"
MODE_MINING = "MINING"

def _sleep_with_stop(seconds, stop_event):
    end_time = time.time() + seconds
    while time.time() < end_time:
        if stop_event.is_set():
            return False
        time.sleep(min(0.1, end_time - time.time()))
    return True

def run_mining(stop_event):
    print("Starting automine in 3 seconds... Switch to the game window!")
    if not _sleep_with_stop(3, stop_event):
        return
    print("Automine started. Press Ctrl+C to stop.")
    while not stop_event.is_set():
        pyautogui.press('f')
        if not _sleep_with_stop(0.2, stop_event):
            break
        pyautogui.scroll(-300)
        if not _sleep_with_stop(0.5, stop_event):
            break

def run_fishing(stop_event):
    global last_arrow
    global counter
    global last_action_time
    global COOLDOWN_SECONDS
    print("Starting fishing bot in 3 seconds... Switch to the game window!")
    if not _sleep_with_stop(3, stop_event):
        return
    print("Bot started. Press Ctrl+C to stop.")

    state = "CASTING"
    is_mouse_held_down = False
    last_release_time = 0
    last_cast_time = 0.0
    bite_timeout_seconds = 30.0

    try:
        while not stop_event.is_set():
            # === STATE: CASTING ===
            if state == "CASTING":

                print("Changing fishing rod")
                if not _sleep_with_stop(1.0, stop_event):
                    break
                hold_key('m')
                if not _sleep_with_stop(0.1, stop_event):
                    break
                release_key('m')
                if not _sleep_with_stop(0.5, stop_event):
                    break
                click(FISHING_ROD_BUY[0], FISHING_ROD_BUY[1])
                click(FISHING_ROD_BUY[0], FISHING_ROD_BUY[1])
                if not _sleep_with_stop(0.5, stop_event):
                    break
                # Wait for the game to return to the fishing state before casting again.
                print("Waiting for game to return to idle state...")
                if not _sleep_with_stop(1.0, stop_event):
                    break


                print("State: CASTING")
                release_left_click()
                release_key('a')
                release_key('d')

                move_cursor(CAST_POINT[0], CAST_POINT[1])
                if not _sleep_with_stop(0.1, stop_event):
                    break
                hold_left_click()
                if not _sleep_with_stop(0.1, stop_event):
                    break
                release_left_click()
                move_cursor(CAST_POINT[0], CAST_POINT[1])
                if not _sleep_with_stop(0.1, stop_event):
                    break
                hold_left_click()
                if not _sleep_with_stop(0.1, stop_event):
                    break
                release_left_click()

                print("Line cast. Waiting for a bite...")
                last_cast_time = time.time()
                state = "WAITING_FOR_BITE"
                if not _sleep_with_stop(1, stop_event):
                    break

            # === STATE: WAITING FOR BITE ===
            elif state == "WAITING_FOR_BITE":
                screen = capture_screen(FISHING_MONITOR_REGION)

                # --- DEBUG WINDOW ---

                # cv2.imshow('Bot Vision', screen) # This will open a window showing you exactly what the bot sees
                # cv2.waitKey(1)

                # --- END OF DEBUG CODE ---

                if find_template(screen, 'assets/exclamation_mark.png', threshold=0.5):
                    print("Bite detected! Hooking the fish.")
                    hold_left_click()
                    if not _sleep_with_stop(0.1, stop_event):
                        break
                    release_left_click()
                    state = "FIGHTING_FISH"
                    is_mouse_held_down = False
                    last_release_time = 0
                    if not _sleep_with_stop(1, stop_event):
                        break
                else:
                    # We print something here to know it's still looking
                    print("... a fish has yet to bite ...")
                    if time.time() - last_cast_time >= bite_timeout_seconds:
                        print("No bite detected. Recasting.")
                        state = "CASTING"
                    if not _sleep_with_stop(0.1, stop_event):
                        break

            # === STATE: FIGHTING THE FISH ===
            elif state == "FIGHTING_FISH":
                screen = capture_screen(FISHING_MONITOR_REGION)
                screen1 = capture_screen(FISHING_ROD_REGION)

                # --- DEBUG WINDOW ---

                #cv2.imshow('Bot Vision', screen) # This will open a window showing you exactly what the bot sees.
                #cv2.waitKey(1)

                # --- END OF DEBUG CODE ---

                is_bar_red = check_color_in_region(screen, TENSION_BAR_REGION, TENSION_BAR_RED_BGR)
                is_bar_white = check_color_in_region(screen, TENSION_BAR_REGION, TENSION_BAR_WHITE_BGR)
                if is_bar_red or is_bar_white:
                    if is_mouse_held_down:
                        print("Tension high! Releasing click.")
                        is_mouse_held_down = False
                        last_release_time = time.time()

                        release_left_click()
                else:
                    if not is_mouse_held_down and (time.time() - last_release_time > 2.0):
                        print("Tension low. Holding click.")
                        hold_left_click()
                        is_mouse_held_down = True

                arrow_screen_roi = screen[
                    ARROW_REGION[1]:ARROW_REGION[1] + ARROW_REGION[3], ARROW_REGION[0]:ARROW_REGION[0] + ARROW_REGION[2]]
                found_left = find_template(arrow_screen_roi, 'assets/arrow_left.png', threshold=0.4)
                found_right = find_template(arrow_screen_roi, 'assets/arrow_right.png', threshold=0.4)

                # --- ADD THIS DEBUG WINDOW ---

                #cv2.imshow('Bot Vision', arrow_screen_roi) # This will open a window showing you exactly what the bot sees.
                #cv2.waitKey(1)                             # ps. remember to destroy all windows

                # --- END OF DEBUG CODE ---

                current_time = time.time()

                if found_left:
                    if last_arrow == 2:
                        release_key('a')
                        release_key('d')
                        last_arrow = 0
                        last_action_time = time.time()

                    elif last_arrow == 0 and current_time - last_action_time > COOLDOWN_SECONDS:
                        # If left arrow is visible, hold 'a' and make sure 'd' is released.
                        print("Fish moving left. Holding 'a'.")
                        hold_key('a')
                        release_key('d')
                        last_arrow = 1
                        last_action_time = time.time()
                    else:
                        pass
                elif found_right:
                    if last_arrow == 1:
                        release_key('a')
                        release_key('d')
                        last_arrow = 0
                        last_action_time = time.time()
                    elif last_arrow == 0 and current_time - last_action_time > COOLDOWN_SECONDS:
                        # If right arrow is visible, hold 'd' and make sure 'a' is released.
                        print("Fish moving right. Holding 'd'.")
                        hold_key('d')
                        release_key('a')
                        last_arrow = 2
                        last_action_time = time.time()
                    else:
                        pass
                if find_template(screen1, 'assets/fishing_rod_empty.png', threshold=0.7):
                    state = "CASTING"
                    #cv2.destroyAllWindows()
                if find_template(screen, 'assets/end.png', threshold=0.4):
                    print("Minigame seems to be over. Fish caught!")
                    # CRITICAL: Wait for the UI to become interactive.
                    if not _sleep_with_stop(1.0, stop_event):
                        break

                    # Use our new, more reliable click function.
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])

                    # Wait for the game to return to the fishing state before casting again.
                    print("Waiting for game to return to idle state...")
                    if not _sleep_with_stop(3.0, stop_event):
                        break

                    # Reset the state for the next cast.
                    state = "CASTING"
                    last_arrow = 0
                    cv2.destroyAllWindows()


                if not _sleep_with_stop(0.1, stop_event):
                    break

    except KeyboardInterrupt:
        print("\nBot stopped by user. Releasing all controls.")
    finally:
        release_left_click()
        release_key('a')
        release_key('d')

def main():
    stop_event = threading.Event()
    worker = {"thread": None}

    def set_status(text):
        status_label.config(text=text)

    def start_mode(mode):
        if worker["thread"] and worker["thread"].is_alive():
            return
        stop_event.clear()
        if mode == MODE_MINING:
            target = run_mining
            set_status("Running: Mining")
        else:
            target = run_fishing
            set_status("Running: Fishing")
        thread = threading.Thread(target=target, args=(stop_event,), daemon=True)
        worker["thread"] = thread
        thread.start()

    def stop_mode():
        stop_event.set()
        set_status("Stopped")

    def on_close():
        stop_event.set()
        root.destroy()

    root = tk.Tk()
    root.title("Bot Control")
    root.geometry("280x180")
    root.resizable(False, False)

    status_label = tk.Label(root, text="Idle", pady=10)
    status_label.pack()

    btn_fish = tk.Button(root, text="Start Fishing", width=22, command=lambda: start_mode(MODE_FISHING))
    btn_fish.pack(pady=4)

    btn_mine = tk.Button(root, text="Start Mining", width=22, command=lambda: start_mode(MODE_MINING))
    btn_mine.pack(pady=4)

    btn_stop = tk.Button(root, text="Stop", width=22, command=stop_mode)
    btn_stop.pack(pady=6)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
