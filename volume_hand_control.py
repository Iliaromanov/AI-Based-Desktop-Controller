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
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

MIN_VOLUME, MAX_VOLUME = volume.GetVolumeRange()[0], volume.GetVolumeRange()[1]

cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)  # id 3 => capture window width
cap.set(4, CAP_HEIGHT)  # id 4 => capture window height

detector = htm.HandDetector(max_num_hands=1, min_detection_confidence=0.8)


prev_time = 0  # set initial time for fps tracking




while True:
    success, img = cap.read()
    volume_bar_y = int(np.interp(volume.GetMasterVolumeLevel(), [MIN_VOLUME, MAX_VOLUME], [400, 100]))
    img = detector.find_hands(img)
    landmark_list = detector.find_positions(img)

    if landmark_list:
        thumb_x, thumb_y = landmark_list[4][1], landmark_list[4][2]
        index_x, index_y = landmark_list[8][1], landmark_list[8][2]
        center_x, center_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2

        # Draw circles over target finger tips
        # cv2.circle(img, (thumb_x, thumb_y), 12, (250, 0, 0), cv2.FILLED)
        # cv2.circle(img, (index_x, index_y), 12, (250, 0, 0), cv2.FILLED)
        # # Draw circle at center between finger tips
        # cv2.circle(img, (center_x, center_y), 9, (250, 0, 0), cv2.FILLED)

        # Draw line between target finger tips
        #cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (250, 0, 50), 3)

        # Calculate distance between the two finger tips
        # dist = math.hypot(thumb_x-index_x, thumb_y-index_y)
        # print(dist)
        # Assuming max dist between fingers is 425 and min is 15
        # Transform distance into range of volume
        # Set the volume to the calculated value


        if index_x in range(50, 95) and index_y in range(100, 400):
            volume_bar_y = index_y
            vol = np.interp(volume_bar_y, [100, 400], [MAX_VOLUME, MIN_VOLUME])
            print(volume_bar_y, vol)
            if MIN_VOLUME < vol < MAX_VOLUME:  # just to be sure

                volume.SetMasterVolumeLevel(vol, None)

            vol_percent = np.interp(vol, [MIN_VOLUME, MAX_VOLUME], [0, 100])
            cv2.putText(img, f"Vol: {int(vol_percent)}%", (40, 80), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    cv2.rectangle(img, (50, 100), (95, 400), (250, 0, 0), 3)
    cv2.rectangle(img, (50, volume_bar_y), (95, 400), (250, 0, 0), cv2.FILLED)
    cv2.line(img, (45, volume_bar_y), (100, volume_bar_y), (255, 0, 25), 5)

    # Tracking fps
    cur_time = time.time()
    fps = 1/(cur_time - prev_time)
    prev_time = cur_time
    # Displaying FPS
    cv2.putText(img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Displaying video frame
    cv2.imshow("Volume Hand Control", img)
    cv2.waitKey(5)
