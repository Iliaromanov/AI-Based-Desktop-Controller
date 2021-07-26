import cv2
import pyautogui
import autopy
import numpy as np
import time
import warnings

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm  # import created hand tracking module
from helpers import check_webcam_resolution


# Setting Constants
###################################################################
WEBCAM = 0  # Change this variable to change which webcam is used; 0=default webcam, 1=second webcam, etc.
RESOLUTION_W, RESOLUTION_H = pyautogui.size()
print(f"Detected screen resolution: {RESOLUTION_W}x{RESOLUTION_H}")

CAP_WIDTH, CAP_HEIGHT = RESOLUTION_W // 2, RESOLUTION_H // 2  # 960, 540  # 1000, 750
# Make sure CAP_WIDTH and CAP_HEIGHT constants are supported by webcam driver, if not update them
CAP_WIDTH, CAP_HEIGHT = check_webcam_resolution(CAP_WIDTH, CAP_HEIGHT, WEBCAM)

# Set other coordinate constants based on CAP_WIDTH and CAP_HEIGHT
VOL_BAR_X1, VOL_BAR_X2 = round(CAP_WIDTH / 64), round(CAP_WIDTH * 5/64)  # 250, 650
VOL_BAR_Y1, VOL_BAR_Y2 = round(CAP_HEIGHT * 5/18), round(CAP_HEIGHT * 13/18)  # 25, 65
MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2 = round(CAP_WIDTH * 5/32), round(CAP_WIDTH * 175/192)
MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2 = round(CAP_HEIGHT * 7/108), VOL_BAR_Y2
POWER_BUTTON_X1, POWER_BUTTON_X2 = 0, round(CAP_WIDTH * 5/48)
POWER_BUTTON_Y1, POWER_BUTTON_Y2 = 0, round(CAP_HEIGHT * 5/27)
SMOOTHING = 5  # Determines mouse movement sensitivity
BASE_COLOR = (250, 0, 0)

# Retrieving computer audio setup information
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
###################################################################

# When true the program is "on", when False program is off
power_button_state = False


def main():
    global power_button_state

    # Set up for video capture window
    cap = cv2.VideoCapture(WEBCAM, cv2.CAP_DSHOW)
    cap.set(3, CAP_WIDTH)  # id 3 => capture window width
    cap.set(4, CAP_HEIGHT)  # id 4 => capture window height
    detector = htm.HandDetector(max_num_hands=2, min_detection_confidence=0.8)

    prev_time = 0  # set initial time for fps tracking

    power_button_img = cv2.imread(r'images\power-button.png')
    power_button_img = cv2.resize(power_button_img, dsize=(POWER_BUTTON_X2-3, POWER_BUTTON_Y2-3))

    mouse_down = False  # When True, left mouse button is held down
    prev_mouse_x, prev_mouse_y = 0, 0  # pyautogui.position()

    bottom_text = None  # Text at bottom of capture img to describe current action (eg. 'Using mouse')

    while True:
        success, img = cap.read()

        if power_button_state:
            cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_X2), (0, 255, 0), 3)
            img = detector.find_hands(img)
            landmark_list = detector.find_positions(img)

            vol_percent = volume.GetMasterVolumeLevelScalar()

            #volume_bar_x = VOL_BAR_X1 + round((VOL_BAR_X2 - VOL_BAR_X1) * vol_percent)
            volume_bar_y = VOL_BAR_Y2 - round((VOL_BAR_Y2 - VOL_BAR_Y1) * vol_percent)

            if landmark_list:
                index_x, index_y = landmark_list[8][1], landmark_list[8][2]

                fingers_up = htm.HandDetector.fingers_up(landmark_list)

                # Stop holding down left mouse when condition not met
                if not (fingers_up[1] and fingers_up[4]) and mouse_down:
                    mouse_down = not mouse_down
                    autopy.mouse.toggle(down=mouse_down)

                # Mouse control
                if index_x in range(MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2) and \
                   index_y in range(MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2):
                    cv2.rectangle(img, (MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_Y1),
                                  (MOUSE_CTRL_WINDOW_X2, MOUSE_CTRL_WINDOW_Y2), (0, 255, 0), 3)

                    # Left click
                    if fingers_up[1] and fingers_up[2]:
                        dist, img, click = htm.HandDetector.find_distance(img, landmark_list, radius=8)
                        if click:
                            autopy.mouse.click()
                    # Right click
                    elif fingers_up[1] and fingers_up[0]:
                        dist, img, click = htm.HandDetector.find_distance(img, landmark_list, finger_2=0, radius=8)
                        if click:
                            # pyautogui.click(button="right")
                            autopy.mouse.click(autopy.mouse.Button.RIGHT)
                    # Mouse motion
                    elif fingers_up[1]:
                        new_mouse_x = np.interp(index_x, [MOUSE_CTRL_WINDOW_X1,
                                                          MOUSE_CTRL_WINDOW_X2], [-45, RESOLUTION_W + 45])
                        new_mouse_y = np.interp(index_y, [MOUSE_CTRL_WINDOW_Y1,
                                                          MOUSE_CTRL_WINDOW_Y2], [-45, RESOLUTION_H + 45])

                        new_mouse_x = RESOLUTION_W if new_mouse_x > RESOLUTION_W else new_mouse_x
                        new_mouse_y = RESOLUTION_H if new_mouse_y > RESOLUTION_H else new_mouse_y
                        new_mouse_x = 0 if new_mouse_x < 0 else new_mouse_x
                        new_mouse_y = 0 if new_mouse_y < 0 else new_mouse_y

                        mouse_x = prev_mouse_x + (new_mouse_x - prev_mouse_x) / SMOOTHING
                        mouse_y = prev_mouse_y + (new_mouse_y - prev_mouse_y) / SMOOTHING
                        autopy.mouse.move(mouse_x, mouse_y)

                        prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

                        # Holding down left click
                        if fingers_up[4] and not mouse_down:
                            mouse_down = not mouse_down
                            autopy.mouse.toggle(down=mouse_down)

                if index_x in range(VOL_BAR_X1, VOL_BAR_X2) and \
                   index_y in range(VOL_BAR_Y1, VOL_BAR_Y2) and fingers_up[1]:
                    cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (0, 255, 0), 3)
                    # volume_bar_x = index_x
                    # vol_percent = (volume_bar_x - VOL_BAR_X1) / (VOL_BAR_X2 - VOL_BAR_X1)
                    # Vertical volume bar
                    volume_bar_y = index_y
                    vol_percent = (VOL_BAR_Y2 - volume_bar_y) / (VOL_BAR_Y2 - VOL_BAR_Y1)
                    volume.SetMasterVolumeLevelScalar(vol_percent, None)

            # # Drawing Horizontal volume control bar
            # cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), BASE_COLOR, 1)
            # cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (volume_bar_x, VOL_BAR_Y2), BASE_COLOR, cv2.FILLED)
            # cv2.line(img, (volume_bar_x, VOL_BAR_Y1 - 5), (volume_bar_x, VOL_BAR_Y2 + 5), (255, 0, 25), 5)

            # Vertical volume bar
            cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), BASE_COLOR, 1)
            cv2.rectangle(img, (VOL_BAR_X1, volume_bar_y), (VOL_BAR_X2, VOL_BAR_Y2), BASE_COLOR, cv2.FILLED)
            cv2.line(img, (VOL_BAR_X1 - 5, volume_bar_y), (VOL_BAR_X2 + 5, volume_bar_y), BASE_COLOR, 5)

            # Displaying Volume Level Percentage
            cv2.putText(img, f"{round(vol_percent * 100)}%", (VOL_BAR_X1, VOL_BAR_Y1 - 10),
                        cv2.FONT_HERSHEY_COMPLEX, 1, BASE_COLOR, 2)

            # Drawing mouse controller box
            cv2.rectangle(img, (MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_Y1),
                          (MOUSE_CTRL_WINDOW_X2, MOUSE_CTRL_WINDOW_Y2), BASE_COLOR, 1)

            # Tracking fps
            cur_time = time.time()
            fps = 1 / (cur_time - prev_time)
            prev_time = cur_time
            # Displaying FPS
            cv2.putText(img, f"FPS: {int(fps)}", (VOL_BAR_X1, 495),
                        cv2.FONT_HERSHEY_COMPLEX, 1, BASE_COLOR, 2)
        else:
            cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_X2), (0, 0, 255), 3)

            detector.find_hands(img, draw=False)
            landmark_list = detector.find_positions(img)
            if landmark_list:
                index_x, index_y = landmark_list[8][1], landmark_list[8][2]
                if index_x in range(POWER_BUTTON_X1, POWER_BUTTON_X2) and \
                   index_y in range(POWER_BUTTON_Y1, POWER_BUTTON_Y2):
                    print("toggle power button")
                    power_button_state = not power_button_state

        # Overlay power button image at top left corner of capture img
        img[POWER_BUTTON_X1+3:POWER_BUTTON_X2, POWER_BUTTON_Y1+3:POWER_BUTTON_Y2] = power_button_img

        # Displaying video frame
        cv2.imshow("Hand Gesture Controller", img)
        cv2.waitKey(1)

        # Detect mouse clicks
        cv2.setMouseCallback('Hand Gesture Controller', power_button_toggle)


def power_button_toggle(event, x, y, flags, params):
    """
    Returns the x and y coordinates of the mouse when left clicked
      within the cv2 capture img window.
    """
    global power_button_state

    if event == cv2.EVENT_LBUTTONDOWN:
        if x in range(POWER_BUTTON_X1, POWER_BUTTON_X2) and y in range(POWER_BUTTON_Y1, POWER_BUTTON_Y2):
            power_button_state = not power_button_state


if __name__ == "__main__":
    main()
