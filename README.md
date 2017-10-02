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

Builder components are in **ptc_components** directory.
Copy this directory anywhere you have write permissions and add this directory to *component foloders* of PsychoPy Preferences.
For example, if you copy ptc_components directory to 'C:/Users/foo/Documents', add 'C:/Users/foo/Documents/ptc_components' to *components folder* and restart PsychoPy.  *components folder* is in 'Builder' tab of PsychoPy Preference dialog.

### utility_sample01.py

A sample of utility functions.

- Loading data recorded by psychopy_tobii_controller.
- Applying moving average to gaze data.
- Detecting fixations.
- Plotting gaze data.

