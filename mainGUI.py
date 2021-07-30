import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import cv2
import pyautogui
import autopy
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTrackingModule as htm  # import created hand tracking module
from utils import check_webcam_resolution, speech_to_text, play_power_toggle_sound


# Setting Constants
###################################################################
WEBCAM = 0  # Change this variable to change which webcam is used; 0=default webcam, 1=second webcam, etc.
RESOLUTION_W, RESOLUTION_H = pyautogui.size()
print(f"Detected screen resolution: {RESOLUTION_W}x{RESOLUTION_H}")

CAP_WIDTH, CAP_HEIGHT = 640, 360  # RESOLUTION_W // 2, RESOLUTION_H // 2
# Make sure CAP_WIDTH and CAP_HEIGHT constants are supported by webcam driver, if not update them
CAP_WIDTH, CAP_HEIGHT = check_webcam_resolution(CAP_WIDTH, CAP_HEIGHT, WEBCAM)

# Set other coordinate constants based on CAP_WIDTH and CAP_HEIGHT
VOL_BAR_X1, VOL_BAR_X2 = round(CAP_WIDTH / 64), round(CAP_WIDTH * 5 / 64)  # 250, 650
VOL_BAR_Y1, VOL_BAR_Y2 = round(CAP_HEIGHT * 5 / 18), round(CAP_HEIGHT * 13 / 18)  # 25, 65
MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2 = round(CAP_WIDTH * 5 / 32), round(CAP_WIDTH * 175 / 192)
MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2 = round(CAP_HEIGHT * 7 / 108), VOL_BAR_Y2
POWER_BUTTON_X1, POWER_BUTTON_X2 = 0, round(CAP_WIDTH * 5 / 48)
POWER_BUTTON_Y1, POWER_BUTTON_Y2 = 0, round(CAP_HEIGHT * 5 / 27)
MIC_BUTTON_X1, MIC_BUTTON_X2 = POWER_BUTTON_X2, POWER_BUTTON_X2 * 2
MIC_BUTTON_Y1, MIC_BUTTON_Y2 = POWER_BUTTON_Y1, POWER_BUTTON_Y2
SMOOTHING = 5  # Determines mouse movement sensitivity
BASE_COLOR = (250, 0, 0)

# Retrieving computer audio setup information
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
###################################################################

executor = ThreadPoolExecutor()


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.VBL = QVBoxLayout()

        self.FeedLabel = QLabel('Comp Vision Controller')
        self.VBL.addWidget(self.FeedLabel)

        self.video_feed = VideoFeedWindowWorker()

        self.video_feed.start()
        self.video_feed.ImageUpdate.connect(self.update_img_slot)
        self.setLayout(self.VBL)

    def update_img_slot(self, img):
        self.FeedLabel.setPixmap(QPixmap.fromImage(img))


class VideoFeedWindowWorker(QThread):
    ImageUpdate = pyqtSignal(QImage)

    def run(self):
        # When true the program is "on", when False program is off
        self.power_button_state = False

        # Set up for video capture window
        cap = cv2.VideoCapture(WEBCAM, cv2.CAP_DSHOW)
        cap.set(3, CAP_WIDTH)  # id 3 => capture window width
        cap.set(4, CAP_HEIGHT)  # id 4 => capture window height
        detector = htm.HandDetector(max_num_hands=2, min_detection_confidence=0.8)

        prev_time = 0  # set initial time for fps tracking
        prev_power_toggle_time = 0
        prev_mic_toggle_time = 0

        power_button_img = cv2.imread(r'images\power-button.png')
        power_button_img = cv2.resize(power_button_img, dsize=(POWER_BUTTON_X2 - 3, POWER_BUTTON_Y2 - 3))

        mouse_down = False  # When True, left mouse button is held down
        prev_mouse_x, prev_mouse_y = 0, 0  # pyautogui.position()

        while True:
            success, img = cap.read()
            img = cv2.flip(img, 1)

            if self.power_button_state:
                cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_X2),
                              (0, 255, 0), 3)
                detector.find_hands(img)
                hand1_landmarks, hand1_type = detector.find_positions(img, hand_num=0)
                hand2_landmarks, hand2_type = detector.find_positions(img, hand_num=1)

                # Force the mouse controlling hand to be the right hand when possible
                if hand1_type and hand2_type:
                    print("Two hands")
                    if hand1_type == "Left":
                        hand1_landmarks, hand2_landmarks = hand2_landmarks, hand1_landmarks
                        hand1_type, hand2_type = hand2_type, hand1_type

                vol_percent = volume.GetMasterVolumeLevelScalar()

                volume_bar_y = VOL_BAR_Y2 - round((VOL_BAR_Y2 - VOL_BAR_Y1) * vol_percent)

                if hand1_landmarks:
                    index_x, index_y = hand1_landmarks[8][1], hand1_landmarks[8][2]

                    fingers_up = htm.HandDetector.fingers_up(hand1_landmarks, hand1_type)

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
                            dist, img, click = htm.HandDetector.find_distance(img, hand1_landmarks, radius=8)
                            if click:
                                autopy.mouse.click()
                        # Right click
                        elif fingers_up[1] and fingers_up[0]:
                            dist, img, click = htm.HandDetector.find_distance(img, hand1_landmarks, finger_2=0,
                                                                              radius=8)
                            if click:
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
                        # Activating speech to text
                        if fingers_up == [1, 0, 0, 0, 1] and (time.time() - prev_mic_toggle_time) >= 1:
                            print("toggle mic button")
                            text = speech_to_text()
                            autopy.key.type_string(text)
                            prev_mic_toggle_time = time.time()

                    if index_x in range(VOL_BAR_X1, VOL_BAR_X2) and \
                            index_y in range(VOL_BAR_Y1, VOL_BAR_Y2) and fingers_up[1]:
                        self.change_volume(img, index_y)

                    if index_x in range(POWER_BUTTON_X1, POWER_BUTTON_X2) and \
                            index_y in range(POWER_BUTTON_Y1, POWER_BUTTON_Y2) and \
                            (time.time() - prev_power_toggle_time) >= 1:
                        print("toggle power button")
                        executor.submit(play_power_toggle_sound)
                        prev_power_toggle_time = time.time()
                        self.power_button_state = not self.power_button_state

                # Vertical volume bar
                cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), BASE_COLOR, 1)
                cv2.rectangle(img, (VOL_BAR_X1, volume_bar_y), (VOL_BAR_X2, VOL_BAR_Y2), BASE_COLOR, cv2.FILLED)
                cv2.line(img, (VOL_BAR_X1 - 5, volume_bar_y), (VOL_BAR_X2 + 5, volume_bar_y), BASE_COLOR, 5)

                # Displaying Volume Level Percentage
                cv2.putText(img, f"{round(vol_percent * 100)}%", (VOL_BAR_X1, VOL_BAR_Y1 - 10),
                            cv2.FONT_HERSHEY_COMPLEX, CAP_HEIGHT / 540, BASE_COLOR, 2)

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
                cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_X2),
                              (0, 0, 255), 3)

                detector.find_hands(img, draw=False)
                hand1_landmarks, _ = detector.find_positions(img)
                if hand1_landmarks:
                    index_x, index_y = hand1_landmarks[8][1], hand1_landmarks[8][2]
                    if index_x in range(POWER_BUTTON_X1, POWER_BUTTON_X2) and \
                            index_y in range(POWER_BUTTON_Y1, POWER_BUTTON_Y2) and \
                            (time.time() - prev_power_toggle_time) >= 1:
                        print("toggle power button")
                        self.power_button_state = not self.power_button_state

                        executor.submit(play_power_toggle_sound)
                        prev_power_toggle_time = time.time()

            # Display power button
            img[POWER_BUTTON_Y1 + 3:POWER_BUTTON_Y2, POWER_BUTTON_X1 + 3:POWER_BUTTON_X2] = power_button_img

            # Preprocess and submit image to be displayed in GUI window
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_qt_format = QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], QImage.Format_RGB888)
            img_qt_format = img_qt_format.scaled(CAP_WIDTH, CAP_HEIGHT, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(img_qt_format)

    @staticmethod
    def change_volume(img, volume_bar_y):
        cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (0, 255, 0), 3)

        vol_percent = (VOL_BAR_Y2 - volume_bar_y) / (VOL_BAR_Y2 - VOL_BAR_Y1)
        volume.SetMasterVolumeLevelScalar(vol_percent, None)

    def stop(self):
        self.quit()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(App.exec())
