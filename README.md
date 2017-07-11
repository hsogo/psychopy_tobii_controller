psychopy_tobii_controller
============================

psychopy_tobii_controller is a helper module to use tobii_research package with PsychoPy.

Disclaimer: psychopy_tobii_controller is unofficial. It is NOT affiliated with Tobii.


## Licence

GPLv3 (https://github.com/hsogo/psychopy_tobii_controller/blob/master/LICENCE)

## Author

Hiroyuki Sogo (https://github.com/hsogo)

## Requirements

PsychoPy (http://www.psychopy.org/)
tobii_research (https://pypi.python.org/pypi/tobii-research)

## Sample codes

### sample01.py

Basic usage of tobii_controller is demonstrated in this sample.

- Initializing tobii_controller object
- Open/close data file
- Showing Tobii status display
- Performing calibration
- Start/Stop recording
- Getting the latest gaze position
- Recording event data

### sample02.py

- Customizing calibation target color and size.
- Customizing the key to start calibration procedure.
- Controlling the order of calibration target position.

### sample03.py

- Customizing calibration procedure.

### sample04.py

- Customizing text color in the status display and calibration.
- Using mouse in the status display and calibration.

### sample05.py

- Customizing key mapping for selecting calibration points.

### builder_sample01.psyexp

Basic usage of Builder components of tobii_controller is demonstrated in this sample.

- ptc_init: Initialize tobii_controller. This component works in any routine.
- ptc_cal: Run calibration. Calibration is performed at the beginning of the routine where this component is placed.  More preceisely, this component is equivalent to add calibration codes to "begin routine" of the Code component.
- ptc_rec: Record gaze data in the routine where this component is placed.
- ptc_message: Insert event during recording. ptc_rec component should be placed in the same routine.
- ptc_getpos: Get the latest gaze position. Gaze position is stored in a variable with the same name as the 'Name' property of this component.  ptc_rec component should be placed in the same routine.

Builder components are in **ptc_components** directory.  Copy this directory to your component directory.  For example, 'C:/Users/foo/Documents/my_components' is in your component directory, contents of ptc_component directory (i.e, \_\_init\_\_.py, ptc_init.py and so on) should be placed in C:/Users/foo/Documents/my_components/ptc_components'.
