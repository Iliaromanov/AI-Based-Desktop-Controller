import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import cv2
import autopy
import numpy as np
import time

import HandTrackingModule as htm  # import created hand tracking module
from utils import speech_to_text, play_power_toggle_sound
from config import *


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Uncomment to display window on top of all other open apps

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
        # Set up for video capture window
        cap = cv2.VideoCapture(WEBCAM, cv2.CAP_DSHOW)
        cap.set(3, CAP_WIDTH)  # id 3 => capture window width
        cap.set(4, CAP_HEIGHT)  # id 4 => capture window height
        detector = htm.HandDetector(max_num_hands=2, min_detection_confidence=0.8)

        prev_time = 0  # set initial time for fps tracking
        prev_mic_toggle_time = 0

        power_button_img = cv2.imread(r'images\power-button.png')
        power_b_side_length = POWER_BUTTON_X2 - POWER_BUTTON_X1 - 3
        power_button_img = cv2.resize(power_button_img, dsize=(power_b_side_length, power_b_side_length))

        self.power_button_state = False  # When true the controls are "on", when False controls are "off"
        self.prev_power_toggle_time = 0
        self.mouse_down = False  # When True, left mouse button is held down
        self.prev_mouse_x, self.prev_mouse_y = 0, 0

        while True:
            success, img = cap.read()
            img = cv2.flip(img, 1)

            if self.power_button_state:
                cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_Y2),
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

                    if index_x in range(MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2) and \
                            index_y in range(MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2):
                        cv2.rectangle(img, (MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_Y1),
                                      (MOUSE_CTRL_WINDOW_X2, MOUSE_CTRL_WINDOW_Y2), (0, 255, 0), 3)
                        self.mouse_controls(img, fingers_up, index_x, index_y, hand1_landmarks)

                    # Activating speech to text
                    if fingers_up == [1, 0, 0, 0, 1] and (time.time() - prev_mic_toggle_time) >= 1:
                        print("toggle speech to text")
                        speech_to_text()
                        prev_mic_toggle_time = time.time()

                    if index_x in range(VOL_BAR_X1, VOL_BAR_X2) and \
                            index_y in range(VOL_BAR_Y1, VOL_BAR_Y2) and fingers_up[1]:
                        self.change_volume(img, index_y)

                    self.check_toggle_power_button(index_x, index_y)

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
                cv2.putText(img, f"FPS: {int(fps)}", (MOUSE_CTRL_WINDOW_X2, int(CAP_HEIGHT * 4/5)),
                            cv2.FONT_HERSHEY_COMPLEX, CAP_HEIGHT / 500, BASE_COLOR, 2)
            else:
                cv2.rectangle(img, (POWER_BUTTON_X1, POWER_BUTTON_Y1), (POWER_BUTTON_X2, POWER_BUTTON_Y2),
                              (0, 0, 255), 3)

                detector.find_hands(img, draw=False)
                hand1_landmarks, _ = detector.find_positions(img)
                if hand1_landmarks:
                    index_x, index_y = hand1_landmarks[8][1], hand1_landmarks[8][2]
                    self.check_toggle_power_button(index_x, index_y)

            # Display power button
            img[POWER_BUTTON_Y1 + 3:POWER_BUTTON_Y2, POWER_BUTTON_X1 + 3:POWER_BUTTON_X2] = power_button_img

            # Preprocess and submit image to be displayed in GUI window
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_qt_format = QImage(img_rgb.data, img_rgb.shape[1], img_rgb.shape[0], QImage.Format_RGB888)
            img_qt_format = img_qt_format.scaled(CAP_WIDTH, CAP_HEIGHT, Qt.KeepAspectRatio)
            self.ImageUpdate.emit(img_qt_format)

    def mouse_controls(self, img, fingers_up, index_x, index_y, hand1_landmarks):
        """
        Mouse motion and mouse press operations
        """
        # Stop holding down left mouse when condition not met
        if not (fingers_up[1] and fingers_up[4]) and self.mouse_down:
            self.mouse_down = not self.mouse_down
            autopy.mouse.toggle(down=self.mouse_down)

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
            cv2.circle(img, (index_x, index_y), 6, BASE_COLOR, cv2.FILLED)

            new_mouse_x = np.interp(index_x, [MOUSE_CTRL_WINDOW_X1,
                                              MOUSE_CTRL_WINDOW_X2], [-45, RESOLUTION_W + 45])
            new_mouse_y = np.interp(index_y, [MOUSE_CTRL_WINDOW_Y1,
                                              MOUSE_CTRL_WINDOW_Y2], [-45, RESOLUTION_H + 45])

            new_mouse_x = RESOLUTION_W if new_mouse_x > RESOLUTION_W else new_mouse_x
            new_mouse_y = RESOLUTION_H if new_mouse_y > RESOLUTION_H else new_mouse_y
            new_mouse_x = 0 if new_mouse_x < 0 else new_mouse_x
            new_mouse_y = 0 if new_mouse_y < 0 else new_mouse_y

            mouse_x = self.prev_mouse_x + (new_mouse_x - self.prev_mouse_x) / SMOOTHING
            mouse_y = self.prev_mouse_y + (new_mouse_y - self.prev_mouse_y) / SMOOTHING
            autopy.mouse.move(mouse_x, mouse_y)

            self.prev_mouse_x, self.prev_mouse_y = mouse_x, mouse_y

            # Holding down left click
            if fingers_up[4] and not self.mouse_down:
                self.mouse_down = not self.mouse_down
                autopy.mouse.toggle(down=self.mouse_down)

    def check_toggle_power_button(self, index_x, index_y):
        """
        Checks if power button toggle was activated based on finger location.
        If it was, then power button is toggled
        """
        if index_x in range(POWER_BUTTON_X1, POWER_BUTTON_X2) and \
           index_y in range(POWER_BUTTON_Y1, POWER_BUTTON_Y2) and \
           (time.time() - self.prev_power_toggle_time) >= 1:
            print("toggle power button")
            play_power_toggle_sound()
            self.prev_power_toggle_time = time.time()
            self.power_button_state = not self.power_button_state

    @staticmethod
    def change_volume(img, volume_bar_y):
        """
        Adjust global system volume based on volume_bar_y parameter
        """
        cv2.rectangle(img, (VOL_BAR_X1, VOL_BAR_Y1), (VOL_BAR_X2, VOL_BAR_Y2), (0, 255, 0), 3)

        vol_percent = (VOL_BAR_Y2 - volume_bar_y) / (VOL_BAR_Y2 - VOL_BAR_Y1)

        # Displaying Volume Level Percentage in Green
        cv2.putText(img, f"{round(vol_percent * 100)}%", (VOL_BAR_X1, VOL_BAR_Y1 - 10),
                    cv2.FONT_HERSHEY_COMPLEX, CAP_HEIGHT / 540, (0, 255, 0), 3)

        volume.SetMasterVolumeLevelScalar(vol_percent, None)

    def stop(self):
        self.quit()


if __name__ == "__main__":
    App = QApplication(sys.argv)
    root = MainWindow()
    root.show()
    sys.exit(App.exec())
