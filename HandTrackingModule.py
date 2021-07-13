import cv2
import mediapipe as mp
import time


class HandDetector:
    def __init__(self, mode=False, max_num_hands=2,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        '''
        Initializing attributes
        '''
        self.mode = mode
        self.max_num_hands = max_num_hands
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.max_num_hands,
                                        self.min_detection_confidence, self.min_tracking_confidence)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, img, draw=True):
        '''
        Detects hands in given img and optionally highlights the detected landmarks
        '''
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert frame img to RGB
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_landmarks, self.mpHands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_num=0):
        '''
        Returns an array of hand landmark positions
        '''
        height, width, channels = img.shape  # get frames dimensions and channels

        landmark_positions = []

        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[hand_num]  # Get landmarks for specified hand

            for id, lm in enumerate(hand.landmark):
                x_pos, y_pos = int(lm.x * width), int(lm.y * height)
                landmark_positions.append((id, x_pos, y_pos))
                # if draw and id == 4:
                #     cv2.circle(img, (x_pos, y_pos), 15, (255, 255, 0), cv2.FILLED)

        return landmark_positions


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
