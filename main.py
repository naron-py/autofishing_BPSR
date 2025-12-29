# main.py
import time
from vision import capture_screen, find_template, check_color_in_region
from controls import hold_left_click, release_left_click, hold_key, release_key, click
import cv2
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

def main():
    global last_arrow
    global counter
    global last_action_time
    global COOLDOWN_SECONDS
    print("Starting fishing bot in 3 seconds... Switch to the game window!")
    time.sleep(3)
    print("Bot started. Press Ctrl+C to stop.")

    state = "CASTING"
    is_mouse_held_down = False
    last_release_time = 0
    last_cast_time = 0.0
    bite_timeout_seconds = 12.0

    try:
        while True:
            # === STATE: CASTING ===
            if state == "CASTING":

                print("Changing fishing rod")
                time.sleep(1.0)
                hold_key('m')
                time.sleep(0.1)
                release_key('m')
                time.sleep(0.5)
                click(FISHING_ROD_BUY[0], FISHING_ROD_BUY[1])
                click(FISHING_ROD_BUY[0], FISHING_ROD_BUY[1])
                time.sleep(0.5)
                # Wait for the game to return to the fishing state before casting again.
                print("Waiting for game to return to idle state...")
                time.sleep(1.0)


                print("State: CASTING")
                release_left_click()
                release_key('a')
                release_key('d')

                SetCursorPos(CAST_POINT)
                time.sleep(0.1)
                hold_left_click()
                time.sleep(0.1)
                release_left_click()
                SetCursorPos(CAST_POINT)
                time.sleep(0.1)
                hold_left_click()
                time.sleep(0.1)
                release_left_click()

                print("Line cast. Waiting for a bite...")
                last_cast_time = time.time()
                state = "WAITING_FOR_BITE"
                time.sleep(1)

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
                    time.sleep(0.1)
                    release_left_click()
                    state = "FIGHTING_FISH"
                    is_mouse_held_down = False
                    last_release_time = 0
                    time.sleep(1)
                else:
                    # We print something here to know it's still looking
                    print("... a fish has yet to bite ...")
                    if time.time() - last_cast_time >= bite_timeout_seconds:
                        print("No bite detected. Recasting.")
                        state = "CASTING"
                    time.sleep(0.1)

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
                    time.sleep(1.0)

                    # Use our new, more reliable click function.
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])
                    click(EXIT_POINT[0], EXIT_POINT[1])

                    # Wait for the game to return to the fishing state before casting again.
                    print("Waiting for game to return to idle state...")
                    time.sleep(3.0)

                    # Reset the state for the next cast.
                    state = "CASTING"
                    last_arrow = 0
                    cv2.destroyAllWindows()


                time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nBot stopped by user. Releasing all controls.")
        release_left_click()
        release_key('a')
        release_key('d')

if __name__ == "__main__":
    main()
