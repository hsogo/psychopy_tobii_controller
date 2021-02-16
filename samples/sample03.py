import psychopy.visual
import psychopy.event
import sys
import numpy as np

from psychopy_tobii_controller import tobii_controller


# Calibration procedure can be modified by registering a function
# which defines calibration procedure.
#
# Following attibutes can be used in the function.
# self.win
#    PsychoPy Window object
# self.original_calibration_points
#    List of calibration points passed to run_calibration().
# self.retry_points
#    List of indices of calibration points to be sampled in the current
#    calibration session.  For example, if self.retry_points is [0,3],
#    The first and fourth calibration points are sampled in the current session.
# 
# The custom function has to do following tasks.
#
# 1) Drawing calibration targets on PsychoPy window (self.win).
#
# 2) Collecting calibration samples by calling self.collect_calibration_data(p)
#    during the participant is fixating a calibration point.  p is the position 
#    of the calibration point in the coordinates (i.e. PsychoPy coordinates).
# 
# In the following example, five-point calibration is performed.
# Experimenter presses keypad 1-5 to select calibration point on which 
# calibration target is presented.  Calibration target can be hidden by
# pressing keypad 0.  Experimenter observe participant carefully and press 
# space key when participant is surely fixating calibration point.
# Calibration can be finished by pressing Enter key.
# 
def custom_calibration(self):
    dot = psychopy.visual.Circle(self.win, radius=0.002, fillColor='white', lineColor=None)
    disc = psychopy.visual.Circle(self.win, fillColor=None, lineColor='white')
    
    # if current_point_index holds the index of calibration point
    # on which calibration target is presented.  If -1, calibation
    # target is not presented.
    current_point_index = -1
    in_calibration_loop = True
    
    clock = psychopy.core.Clock() # 
    
    # Mapping key name to target index
    numkey_dict = {
        'num_0': -1,
        'num_1':  0,
        'num_2':  1,
        'num_3':  2,
        'num_4':  3,
        'num_5':  4,
    }
    
    while in_calibration_loop:
        # Get current time and expand-and-contract calibration target disc.
        t = clock.getTime() 
        disc.radius = (np.sin(3*t)+2)/40.0
        # Get key press.
        keys = psychopy.event.getKeys()
        for key in keys:
            if key in numkey_dict:
                # get calibration point index.
                current_point_index = numkey_dict[key]
            elif key == 'space':
                # Collect calibration samples if space key is pressed.
                # In this sample, sample correction is performed 
                # only if the current calibration point is included 
                # in self.retry_points.
                if current_point_index in self.retry_points:
                    # Call collect_calibration_data() to do this task.
                    self.collect_calibration_data(self.calibration_points[current_point_index])
                    # Hide calibration target.
                    current_point_index = -1
            elif key == 'return':
                # Exit loop if return is pressed.
                in_calibration_loop = False
                break
        
        # Draw calibration target if 0<=current_point_index<=4.
        if 0 <= current_point_index <= 4:
            dot.setPos(self.original_calibration_points[current_point_index]) 
            disc.setPos(self.original_calibration_points[current_point_index])
            dot.draw()
            disc.draw()

        self.win.flip()


win = psychopy.visual.Window(units='height', monitor='default', fullscr=True)
controller = tobii_controller(win)
controller.open_datafile('test.tsv', embed_events=False)

# Register custom calibration procedure.
controller.set_custom_calibration(custom_calibration)

controller.show_status()

ret = controller.run_calibration(
        [(-0.4,0.4), (0.4,0.4) , (0.0,0.0), (-0.4,-0.4), (0.4,-0.4)],
        # Calibration points should not be shuffled in this example because
        # correspondence between points and keys should not be shuffled!
        shuffle=False,
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
