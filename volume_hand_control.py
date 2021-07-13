import cv2
import mediapipe
import numpy as np
import time

import HandTrackingModule as htm  # import created hand tracking module


CAP_WIDTH, CAP_HEIGHT = 1000, 750

cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)  # id 3 => capture window width
cap.set(4, CAP_HEIGHT)  # id 4 => capture window height

detector = htm.HandDetector(max_num_hands=1, min_detection_confidence=0.65)

prev_time = 0  # set initial time for fps tracking

while True:
    success, img = cap.read()
    img = detector.find_hands(img)
    landmark_list = detector.find_positions(img)

    if landmark_list:
        thumb_x, thumb_y = landmark_list[4][1], landmark_list[4][2]
        index_x, index_y = landmark_list[8][1], landmark_list[8][2]

        # Draw circles over target finger tips
        cv2.circle(img, (thumb_x, thumb_y), 15, (250, 0, 0), cv2.FILLED)
        cv2.circle(img, (index_x, index_y), 15, (250, 0, 0), cv2.FILLED)

    # Tracking fps
    cur_time = time.time()
    fps = 1/(cur_time - prev_time)
    prev_time = cur_time
    # Displaying FPS
    cv2.putText(img, f"FPS: {int(fps)}", (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)

    # Displaying video frame
    cv2.imshow("Volume Hand Control", img)
    cv2.waitKey(1)
