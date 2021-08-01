from utils import check_webcam_resolution

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import pyautogui


WEBCAM = 0  # Change this variable to change which webcam is used; 0=default webcam, 1=second webcam, etc.
RESOLUTION_W, RESOLUTION_H = pyautogui.size()
print(f"Detected screen resolution: {RESOLUTION_W}x{RESOLUTION_H}")

CAP_WIDTH, CAP_HEIGHT = 640, 360  # RESOLUTION_W // 2, RESOLUTION_H // 2
# Make sure CAP_WIDTH and CAP_HEIGHT constants are supported by webcam driver, if not update them
CAP_WIDTH, CAP_HEIGHT = check_webcam_resolution(CAP_WIDTH, CAP_HEIGHT, WEBCAM)

# Set other coordinate constants based on CAP_WIDTH and CAP_HEIGHT
VOL_BAR_X1, VOL_BAR_X2 = int(CAP_WIDTH - round(CAP_WIDTH * 6 / 64)), int(
    CAP_WIDTH - round(CAP_WIDTH / 64))  # round(CAP_WIDTH / 64), round(CAP_WIDTH * 5 / 64)  # 250, 650
VOL_BAR_Y1, VOL_BAR_Y2 = round(CAP_HEIGHT * 5 / 18), round(CAP_HEIGHT * 13 / 18)  # 25, 65
MOUSE_CTRL_WINDOW_X1, MOUSE_CTRL_WINDOW_X2 = int(CAP_WIDTH - round(CAP_WIDTH * 175 / 192)), int(
    CAP_WIDTH - round(CAP_WIDTH * 5 / 32))  # round(CAP_WIDTH * 5 / 32), round(CAP_WIDTH * 175 / 192)
MOUSE_CTRL_WINDOW_Y1, MOUSE_CTRL_WINDOW_Y2 = round(CAP_HEIGHT * 7 / 108), VOL_BAR_Y2
POWER_BUTTON_X1, POWER_BUTTON_X2 = int(CAP_WIDTH - round(CAP_WIDTH * 5 / 48) - 3), int(
    CAP_WIDTH - 3)  # 0, round(CAP_WIDTH * 5 / 48)
POWER_BUTTON_Y1, POWER_BUTTON_Y2 = 0, round(CAP_HEIGHT * 5 / 27)

SMOOTHING = 5  # Determines mouse movement sensitivity
BASE_COLOR = (250, 0, 0)

# Retrieving computer audio information
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
