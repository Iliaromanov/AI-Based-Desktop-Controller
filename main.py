import cv2
import mediapipe
import numpy as np
import time
import math

import HandTrackingModule as htm  # import created hand tracking module

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


CAP_WIDTH, CAP_HEIGHT = 1000, 750
VOL_BAR_Y1, VOL_BAR_Y2 = 150, 450
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)  # id 3 => capture window width
cap.set(4, CAP_HEIGHT)  # id 4 => capture window height

detector = htm.HandDetector(max_num_hands=1, min_detection_confidence=0.8)

prev_time = 0  # set initial time for fps tracking

while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    # img = cv2.flip(img, 1)
    landmark_list = detector.find_positions(img)

    vol_percent = volume.GetMasterVolumeLevelScalar()
    cv2.putText(img, f"Vol: {round(vol_percent * 100)}%", (40, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    volume_bar_y = VOL_BAR_Y2 - round((VOL_BAR_Y2 - VOL_BAR_Y1) * vol_percent)

    if landmark_list:
        thumb_x, thumb_y = landmark_list[4][1], landmark_list[4][2]
        index_x, index_y = landmark_list[8][1], landmark_list[8][2]
        center_x, center_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2

        fingers_up = htm.HandDetector.fingers_up(landmark_list)
        if fingers_up[1] and fingers_up[2]:
            dist, img = htm.HandDetector.find_distance(img, landmark_list)
            print(dist)

        # Draw circles over target finger tips
        # cv2.circle(img, (thumb_x, thumb_y), 12, (250, 0, 0), cv2.FILLED)
        # cv2.circle(img, (index_x, index_y), 12, (250, 0, 0), cv2.FILLED)
        # # Draw circle at center between finger tips
        # cv2.circle(img, (center_x, center_y), 9, (250, 0, 0), cv2.FILLED)

        if index_x in range(50, 95) and index_y in range(VOL_BAR_Y1, VOL_BAR_Y2):
            volume_bar_y = index_y
            vol_percent = (VOL_BAR_Y2 - volume_bar_y) / (VOL_BAR_Y2 - VOL_BAR_Y1)
            volume.SetMasterVolumeLevelScalar(vol_percent, None)


    # cv2.rectangle(img, (300, 55), (750, 20), (250, 0, 0), 3)


    cv2.rectangle(img, (45, VOL_BAR_Y1), (95, VOL_BAR_Y2), (250, 0, 0), 3)
    cv2.rectangle(img, (45, volume_bar_y), (95, VOL_BAR_Y2), (250, 0, 0), cv2.FILLED)
    cv2.line(img, (40, volume_bar_y), (100, volume_bar_y), (255, 0, 25), 5)

    # Tracking fps
    cur_time = time.time()
    fps = 1/(cur_time - prev_time)
    prev_time = cur_time
    # Displaying FPS
    cv2.putText(img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Displaying video frame
    cv2.imshow("Volume Hand Control", img)
    cv2.waitKey(5)
