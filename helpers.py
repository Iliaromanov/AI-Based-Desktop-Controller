import cv2
import warnings


def check_webcam_resolution(desired_width, desired_height, webcam=0):
    """
    Checks if desired_width and desired_height are supported by webcam driver,
    if not, prints warning msg and returns closest dimensions supported by webcam
    """
    cap = cv2.VideoCapture(webcam, cv2.CAP_DSHOW)

    # Update capture window resolution
    cap.set(3, desired_width)  # id 3 => capture window width
    cap.set(4, desired_height)  # id 4 => capture window height

    # Check resulting resolution
    result_w, result_h = cap.get(3), cap.get(4)

    if result_w != desired_width or result_h != desired_height:
        msg = f"\nDesired capture image resolution not supported by chosen webcam driver." \
              f"\nSetting capture resolution to {result_w} x {result_h}.\n"
        print(msg)

    return result_w, result_h
