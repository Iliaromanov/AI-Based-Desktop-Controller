import cv2
import mediapipe as mp
import time

import numpy as np

class HandDetector:
    finger_tip_ids = [4, 8, 12, 16, 20]

    def __init__(self, mode=False, max_num_hands=2,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initializing attributes
        """
        self.mode = mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.max_num_hands,
                                        self.min_detection_confidence, self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        """
        Detects hands in given img and optionally highlights the detected landmarks
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert frame img to RGB
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_num=0):
        """
        Returns a list of hand landmark positions
        """
        height, width, channels = img.shape  # get frames dimensions and channels

        landmark_positions = []
        handedness = None

        if self.results.multi_hand_landmarks:
            # Ensure there are enough detected hands to retrieve specified lm positions
            if hand_num != 0 and len(self.results.multi_hand_landmarks) <= 1:
                return [], None

            handedness = self.results.multi_handedness[hand_num].classification[0].label
            hand = self.results.multi_hand_landmarks[hand_num]  # Get landmarks for specified hand

            for id, lm in enumerate(hand.landmark):
                x_pos, y_pos = int(lm.x * width), int(lm.y * height)
                landmark_positions.append((id, x_pos, y_pos))

        return landmark_positions, handedness

    @classmethod
    def fingers_up(cls, lm_positions, handedness):
        """
        Detects which fingers are up and returns a list of length 5,
        one value for each finger; 0 = finger down, 1 = finger up
        """
        result = []

        # Special case for thumb
        if handedness == "Left":
            result.append(1) if lm_positions[4][1] > lm_positions[3][1] else result.append(0)
        else:
            result.append(1) if lm_positions[4][1] < lm_positions[3][1] else result.append(0)

        # Check rest of the fingers
        for id in cls.finger_tip_ids[1:]:
            result.append(1) if lm_positions[id][2] < lm_positions[id - 2][2] else result.append(0)

        return result

    @classmethod
    def find_distance(cls, img, lm_positions, finger_1=1, finger_2=2, draw=True, radius=10, thickness=3, click_dist=20):
        """
        Finds the distance between two specified finger tips, and optionally draws a line between them

        Params:
            img:
            lm_positions:
            finger_1:
            finger_2:
            draw:
            radius:
            thickness:
        Returns:
            distance, img,
        """
        x1, y1 = lm_positions[cls.finger_tip_ids[finger_1]][1:]
        x2, y2 = lm_positions[cls.finger_tip_ids[finger_2]][1:]
        center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2

        dist = np.hypot((x1-x2), (y1-y2))

        if draw:
            cv2.circle(img, (x1, y1), radius, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), radius, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), thickness)

            if dist <= click_dist:
                cv2.circle(img, (center_x, center_y), radius, (0, 255, 0), cv2.FILLED)
                click = True
            else:
                cv2.circle(img, (center_x, center_y), radius, (255, 0, 0), cv2.FILLED)
                click = False

        return dist, img, click


def main():
    # Create video object
    capture = cv2.VideoCapture(0)  # using webcam number 0

    detector = HandDetector()

    p_time = 0
    c_time = 0

    while True:
        success, img = capture.read()  # Get img frame
        img = detector.find_hands(img)

        lm_list = detector.find_positions(img)
        if len(lm_list) > 0:
            print(lm_list[8])  # 8 = index finger tip

        # Calculate frame rate
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255),
                    3)  # Display text on frame

        cv2.imshow("Image", img)  # Display frame
        cv2.waitKey(1)  # Display each frame for 1ms


if __name__ == "__main__":
    main()
