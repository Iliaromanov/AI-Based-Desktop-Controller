# AI-Based-Desktop-Controller

Computer vision based alternative to a physical mouse and keyboard built using computer vision with Python, OpenCV and Mediapipe. Allows intuitive hand gesture based control of mouse motion and mouse buttons, a hand gesture based master volume slider for convenience, and speech-to-text typing functionality using google's web speech to text API also triggered by hand gesture.

<!--Collection of tools for Windows users built using computer vision with Python, OpenCV and Mediapipe-->

<img src="https://img.shields.io/badge/-Python-green" /> <img src="https://img.shields.io/badge/-OpenCV-blue" /> <img src="https://img.shields.io/badge/-Mediapipe-yellow" /> <img src="https://img.shields.io/badge/-Google_SpeechToText_API-red" /> 

<!-- Maybe add audio tool that runs specific program so the program isn't always on. e.g. for volume control, user would say "turn on volume control" to run the program
  Would be super sick if you used arduino for all this shit too.
--> 

## Demo

https://user-images.githubusercontent.com/47427592/127780214-e368f34d-b88f-4f36-aa8d-97af47eb4187.mp4

*Note that the GUI window in the top right is used mainly for demonstration purposes and can be minimized without any changes in functionality.*

## Usage

**Power Button**

To toggle the controller on and off users can hover their index finger over the power button in the top right corner of the capture video. The toggle makes a sound so it can be used even when the capture video window is minimized by just moving the hand in top right corner direction until the sound is played. This feature helps prevent users from unintentionally triggering actions with the controller.

<img src="images/power-button-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Mouse Pad and Volume Controller**

To use the mouse pad or volume controller the users hand must be in the dedicated area outlined in blue on the feedback window. When a hand is detected in a controller area, the area is outlined in green as can be seen in the demo below. There are also sound effects when a hand enters or leaves these areas that are useful when the feedback window is minimized. Both controllers operate based on the location of the index finger.

<img src="images/mouse_pad-volume_control-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Left and Right click**

To left click bring your middle finger up with your index and move them together. To right click bring out your thumb with your index finger and move them together. For both click types the mouse stops moving at the position where the secondary finger is lifted to make it easier for the user to accurately click. The clicks are activated when the distance between the index and secondary finger is less than a certain threshold and the middle circle turns green when a click occurs.

<img src="images/right_click-left_click-demo.gif" width="600" height="350" />

*Note that this version of the left click presses the left mouse key and immediately releases it. Thus, it is useful for double-clicks as demonstrated in the above demo gif when opening the images folder*

----------------------------------------------------------------

**Hold Down Left Click**

To hold down the left mouse key lift your pinky up with your index finger and to release it lower your pinky. The cursor does not stop moving when the left mouse key is pressed this way and will be positioned based on the location of the index finger as it is in default mouse motion mode. This method can be used for single clicks, but is more useful for dragging and dropping items since the mmouse key is not released immediately after it is pressed.

<img src="images/hold_down_left_click-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Speech to Text**

To trigger speech to text recognition lift your pinky and thumb. This hand position does not need to be held up the entire time you are talking, the voice recording will end when you stop talking and then you may make the gesture to trigger it again. Supported special characters are `'exclamation mark'` &rarr; `!`,  `'question mark'` &rarr; `?`, `'period'` &rarr; `.`, `'comma'` &rarr; `,`, `'space'`, &rarr; `' '`, and numeric characters.

<img src="images/speech_to_text-demo.gif" width="600" height="350" />

----------------------------------------------------------------

***More cool new features coming soon!***

----------------------------------------------------------------

## Installation

> `git clone https://github.com/Iliaromanov/Resume-Chat-Bot.git`

> `cd AI-Based-Desktop-Controller`

> `pip install -r requirements.txt`

> `python mainGUI.py`
