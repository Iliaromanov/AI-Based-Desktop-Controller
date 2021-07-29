import cv2
import speech_recognition as sr
import warnings

from pydub import AudioSegment
from pydub.playback import play

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


def speech_to_text(start_listen_timeout=5, listen_time_limit=10):
    '''
    Listens to audio input from microphone and returns text string recognized
    by google speech recognition api
    '''
    r = sr.Recognizer()

    with sr.Microphone() as source:
        try:
            print("listening")
            audio_text = r.listen(source, timeout=start_listen_timeout, phrase_time_limit=listen_time_limit)
            print("finished listening")
            result = r.recognize_google(audio_text)
        except Exception as err:
            print(err)
            return ""

        return result


def play_power_toggle_sound():
    """
    Uses pydub to play power-toggle.wav sound (function defined for threading purposes)
    :return:
    """
    sound = AudioSegment.from_wav('sounds/power-toggle.wav')
    play(sound)
