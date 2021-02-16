import psychopy.visual
import psychopy.event
import sys
import numpy as np

from psychopy_tobii_controller import tobii_controller

# Background color of PsychoPy window is set to be white.
win = psychopy.visual.Window(fullscr=True, units='height', monitor='default', color='white')
controller = tobii_controller(win)
controller.open_datafile('test.tsv', embed_events=False)

# Text color of Status display is set to black.
# Mouse can be used to exit the status display (left click).
controller.show_status(text_color='black', enable_mouse=True)

# Text color of calibration display is set to black.
# Mouse can be used to operate calibration.
ret = controller.run_calibration(
        [(-0.4,0.4), (0.4,0.4) , (0.0,0.0), (-0.4,-0.4), (0.4,-0.4)],
        text_color='black',
        enable_mouse=True,
        start_key=None
    )
if ret == 'abort':
    win.close()
    sys.exit()

marker = psychopy.visual.Rect(win, size=(0.01, 0.01))

controller.subscribe()

waitkey = True
while waitkey:
    currentGazePosition = controller.get_current_gaze_position()
    if not np.nan in currentGazePosition:
        marker.setPos(currentGazePosition[0:2])
        marker.setLineColor('black')
    else:
        marker.setLineColor('red')
    keys = psychopy.event.getKeys()
    if 'space' in keys:
        waitkey=False
    elif len(keys)>=1:
        controller.record_event(keys[0])
    
    marker.draw()
    win.flip()

controller.unsubscribe()

controller.close_datafile()
win.close()
