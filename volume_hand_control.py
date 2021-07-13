import cv2
import mediapipe
import numpy as np
import time

import HandTrackingModule as htm  # import created hand tracking module


CAP_WIDTH, CAP_HEIGHT = 1000, 750

cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)  # id 3 => capture window width
cap.set(4, CAP_HEIGHT)  # id 4 => capture window height

detector = htm.HandDetector()

prev_time = 0  # set initial time for fps tracking

while True:
    success, img = cap.read()
    img = detector.find_hands(img)


    # Tracking fps
    cur_time = time.time()
    fps = 1/(cur_time - prev_time)
    prev_time = cur_time
    # Displaying FPS
    cv2.putText(img, f"FPS: {int(fps)}", (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # Displaying video frame
    cv2.imshow("Volume Hand Control", img)
    cv2.waitKey(1)
