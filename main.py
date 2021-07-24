import cv2
import pyautogui
import autopy
import numpy as np
import time
import os

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm  # import created hand tracking module


# Setting Constants
###################################################################
RESOLUTION_W, RESOLUTION_H = pyautogui.size()
print(f"Detected screen resolution: {RESOLUTION_W}x{RESOLUTION_H}")
CAP_WIDTH, CAP_HEIGHT = 1000, 750
VOL_BAR_X1, VOL_BAR_X2 = 15, 75  # 250, 650
VOL_BAR_Y1, VOL_BAR_Y2 = 150, CAP_HEIGHT-360  # 25, 65
MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2 = 150, CAP_WIDTH - 100
MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2 = 35, VOL_BAR_Y2
SMOOTHING = 5  # Determines mouse movement sensitivity
###################################################################

# Retrieving computer audio setup information
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Set up for video capture window
cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)  # id 3 => capture window width
cap.set(4, CAP_HEIGHT)  # id 4 => capture window height

detector = htm.HandDetector(max_num_hands=1, min_detection_confidence=0.8)

prev_mouse_x, prev_mouse_y = 0, 0  # pyautogui.position()

prev_time = 0  # set initial time for fps tracking

power_button_img = cv2.imread(r'images\power-button.png')
power_button_img = cv2.resize(power_button_img, dsize=(100, 100))

click_x, click_y = None, None

def detect_mouse_click(event, x, y, flags, params):
    """
    Returns the x and y coordinatesof the mouse when left clicked
      relative to the cv2 capture img.
    :param event:
    :param x:
    :param y:
    :param flags:
    :param params:
    :return:
    """
    global click_x, click_y

    if event == cv2.EVENT_LBUTTONDOWN:
        click_x, click_y = x, y


while True:
    success, img = cap.read()

    img[0:100, 0:100] = power_button_img

    img = detector.find_hands(img)
    landmark_list = detector.find_positions(img)

    vol_percent = volume.GetMasterVolumeLevelScalar()

    #volume_bar_x = VOL_BAR_X1 + round((VOL_BAR_X2 - VOL_BAR_X1) * vol_percent)
    volume_bar_y = VOL_BAR_Y2 - round((VOL_BAR_Y2 - VOL_BAR_Y1) * vol_percent)

    if landmark_list:
        thumb_x, thumb_y = landmark_list[4][1], landmark_list[4][2]
        index_x, index_y = landmark_list[8][1], landmark_list[8][2]
        center_x, center_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2

        fingers_up = htm.HandDetector.fingers_up(landmark_list)

        # Mouse control
        if index_x in range(MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2) and \
           index_y in range(MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2):
            cv2.rectangle(img, (MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_Y1),
                          (MOUSE_CTRL_WINDOW_X2, MOUSE_CTRL_WINDOW_Y2), (0, 255, 0), 3)
            # NOTE: when in click mode, set mouse location to center circle; NOT index tip
            # Left click
            if fingers_up[1] and fingers_up[2]:
                dist, img, click = htm.HandDetector.find_distance(img, landmark_list, radius=8)
                if click:
                    autopy.mouse.click()
            # Right click **thumb up/down only recognized for right hand; could add feature to choose, left or right
            elif fingers_up[1] and fingers_up[0]:
                dist, img, click = htm.HandDetector.find_distance(img, landmark_list, finger_2=0, radius=8)
                if click:
                    pyautogui.click(button="right")
            # Moving mode
            elif fingers_up[1]:
                new_mouse_x = np.interp(index_x, [MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2], [0, RESOLUTION_W])
                new_mouse_y = np.interp(index_y, [MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2], [0, RESOLUTION_H])

                mouse_x = prev_mouse_x + (new_mouse_x - prev_mouse_x) / SMOOTHING
                mouse_y = prev_mouse_y + (new_mouse_y - prev_mouse_y) / SMOOTHING
                autopy.mouse.move(mouse_x, mouse_y)

                prev_mouse_x, prev_mouse_y = mouse_x, mouse_y

        if index_x in range(VOL_BAR_X1, VOL_BAR_X2) and index_y in range(VOL_BAR_Y1, VOL_BAR_Y2) and fingers_up[1]:
            cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (0, 255, 0), 3)
            # volume_bar_x = index_x
            # vol_percent = (volume_bar_x - VOL_BAR_X1) / (VOL_BAR_X2 - VOL_BAR_X1)
            # Vertical volume bar
            volume_bar_y = index_y
            vol_percent = (VOL_BAR_Y2 - volume_bar_y) / (VOL_BAR_Y2 - VOL_BAR_Y1)
            volume.SetMasterVolumeLevelScalar(vol_percent, None)

    # # Drawing Horizontal volume control bar
    # cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (250, 0, 0), 1)
    # cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (volume_bar_x, VOL_BAR_Y2), (250, 0, 0), cv2.FILLED)
    # cv2.line(img, (volume_bar_x, VOL_BAR_Y1 - 5), (volume_bar_x, VOL_BAR_Y2 + 5), (255, 0, 25), 5)

    # Vertical volume bar
    cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (250, 0, 0), 1)
    cv2.rectangle(img, (VOL_BAR_X1, volume_bar_y), (VOL_BAR_X2, VOL_BAR_Y2), (250, 0, 0), cv2.FILLED)
    cv2.line(img, (VOL_BAR_X1 - 5, volume_bar_y), (VOL_BAR_X2 + 5, volume_bar_y), (255, 0, 25), 5)

    # Drawing mouse controller box
    cv2.rectangle(img, (MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_Y1),
                  (MOUSE_CTRL_WINDOW_X2, MOUSE_CTRL_WINDOW_Y2), (250, 0, 0), 1)

    # Displaying Volume Level Percentage
    cv2.putText(img, f"Vol: {round(vol_percent * 100)}%", (VOL_BAR_X1, CAP_HEIGHT-285), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Tracking fps
    cur_time = time.time()
    fps = 1/(cur_time - prev_time)
    prev_time = cur_time
    # Displaying FPS
    cv2.putText(img, f"FPS: {int(fps)}", (VOL_BAR_X1, CAP_HEIGHT-255), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Displaying video frame
    cv2.imshow("Hand Gesture Controller", img)
    cv2.waitKey(1)

    # Detect mouse clicks
    cv2.setMouseCallback('Hand Gesture Controller', detect_mouse_click)
    # click_x, click_y = click_coordinates
    if click_x and click_y:
        print((click_x, click_y))
