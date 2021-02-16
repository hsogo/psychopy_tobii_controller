import psychopy.visual
import psychopy.event
import sys
import numpy as np

from psychopy_tobii_controller import tobii_controller

win = psychopy.visual.Window(units='height', monitor='default', fullscr=True)
controller = tobii_controller(win)
controller.open_datafile('test.tsv', embed_events=False)

# Color and size of calibration target can be customized.
# get_calibration_param() returns current parameters as a dict object.
# The dict object has following keys.
#
# 'dot_size': size of the center dot of calibration target.
# 'dot_line_color': line color of the center dot of calibration target.
# 'dot_fill_color': fill color of the center dot of calibration target.
# 'dot_line_width': line width of the center dot of calibration target.
# 'disc_size': size of the surrounding disc of calibration target.
# 'disc_line_color': line color of the surrounding disc of calibration target
# 'disc_fill_color': fill color of the surrounding disc of calibration target
# 'disc_line_width': line width of the surrounding disc of calibration target
# 'text_color': color of text
#
# Edit these values and call set_calibration_param() with the edited dict
# object to update parameters.
param = controller.get_calibration_param()
param['disc_fill_color'] = 'red'
param['disc_line_width'] = 2
param['disc_size'] *= 2
controller.set_calibration_param(param)

controller.show_status()

# Speed of calibration target shrinking can be changed by move_duration paramter.
# If shuffle is False, order of the calibration target poisitons is not shuffled.
# Set start_key if you want to change the key to start calibration procedure.
# If start_key is None, calibration procedure starts immediately.
ret = controller.run_calibration(
        [(-0.4,0.4), (0.4,0.4) , (0.0,0.0), (-0.4,-0.4), (0.4,-0.4)],
        move_duration=0.5,
        shuffle=False,
        start_key='return'
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
        marker.setLineColor('white')
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
