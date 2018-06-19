import psychopy.visual
import psychopy.event
import sys
import numpy as np

from psychopy_tobii_controller import tobii_controller

# PsychoPy window must be created before initializing tobii_controller.
# Monitor profile must be specified if you want to use cm, deg, degFlat, degFlatPos units.
# See PsychoPy document for monitor profile.
win = psychopy.visual.Window(units='norm', monitor='default')

# Initialize tobii_controller.
controller = tobii_controller(win)

# Open data file if you want to save gaze data.
controller.open_datafile('test.tsv', embed_events=False)

# Show Tobii status display.
# Press space to exit status display.
controller.show_status()

# Run calibration.
ret = controller.run_calibration([(-0.4, 0.4), (0.4, 0.4), (0.0, 0.0),
                                  (-0.4, -0.4), (0.4, -0.4)], )
# If calibration is aborted by pressing ESC key, return value of run_calibration()
# is 'abort'.
if ret == 'abort':
    win.close()
    sys.exit()

# Run validation.
# if validation points are not specified, calibration points will be used.
# if get_output is True, return the result as strings
ret, result = controller.run_validation(get_output=True)

if ret == 'abort':
    win.close()
    sys.exit()
else:
    # save the validation result
    with open('validation.tsv', 'w') as out:
        out.write(result)

marker = psychopy.visual.Rect(win, width=0.01, height=0.01)

# Start recording.
controller.subscribe()

waitkey = True
while waitkey:
    # Get the latest gaze position data.
    currentGazePosition = controller.get_current_gaze_position()

    # Gaze position is a tuple of four values (lx, ly, rx, ry).
    # The value is numpy.nan if Tobii failed to detect gaze position.
    if not np.nan in currentGazePosition:
        marker.setPos(currentGazePosition[0:2])
        marker.setLineColor('white')
    else:
        marker.setLineColor('red')
    keys = psychopy.event.getKeys()
    if 'space' in keys:
        waitkey = False
    elif len(keys) >= 1:
        # Record the first key name to the data file.
        controller.record_event(keys[0])

    marker.draw()
    win.flip()

# Stop recording.
controller.unsubscribe()

# Close the data file.
controller.close_datafile()

win.close()
