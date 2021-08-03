# Windows-CompVision-Controller

Windows computer vision assistant built using computer vision with Python, OpenCV and Mediapipe. Also, supports speech to text based typing triggered by hand gesture using google's web speech to text API. 

Can be used as a complete alternative to a physical mouse and keyboard!
<!--Collection of tools for Windows users built using computer vision with Python, OpenCV and Mediapipe-->

<img src="https://img.shields.io/badge/-Python-green" /> <img src="https://img.shields.io/badge/-OpenCV-blue" /> <img src="https://img.shields.io/badge/-Mediapipe-yellow" /> <img src="https://img.shields.io/badge/-Google_SpeechToText_API-red" /> 

<!-- Maybe add audio tool that runs specific program so the program isn't always on. e.g. for volume control, user would say "turn on volume control" to run the program
  Would be super sick if you used arduino for all this shit too.
--> 

## Demo

Note that the GUI window in the top right is used mainly for demonstration purposes and can be minimized without any changes in functionality.

https://user-images.githubusercontent.com/47427592/127780214-e368f34d-b88f-4f36-aa8d-97af47eb4187.mp4

## Usage

**Power Button**

To toggle the controller on and off users can hover their index finger over the power button in the top right corner of the capture video. The toggle makes a sound so it can be used even when the capture video window is minimized by just moving the hand in top right corner direction until the sound is played. This feature helps prevent users from unintentionally triggering actions with the controller.

<img src="images/power-button-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Mouse Pad and Volume Controller**

To use the mouse pad or volume controller the users hand must be in the dedicated area outlined in blue on the feedback window. When a hand is detected in a controller area, the area is outlined in green as can be seen in the demo below. There are also sound effects when a hand enters or leaves these areas that are useful when the feedback window is minimized.

<img src="images/mouse_pad-volume_control-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Left and Right click**

To left click bring your middle finger up with your index and move them together. To right click bring out your thumb with your index finger and move them together. For both click types the mouse stops moving at the position where the secondary finger is lifted to make it easier for the user to accurately click. The clicks are activated when the distance between the index and secondary finger is less than a certain threshold and the middle circle turns green when a click occurs.

<img src="images/right_click-left_click-demo.gif" width="600" height="350" />

----------------------------------------------------------------

**Hold Down Left Click**

----------------------------------------------------------------

**Speech to Text**

----------------------------------------------------------------
