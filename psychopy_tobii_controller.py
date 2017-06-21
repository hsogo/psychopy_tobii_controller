#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 

from __future__ import division

import os
import types
import datetime
import numpy as np
import time

import tobii_research

try:
    import Image
    import ImageDraw
except:
    from PIL import Image
    from PIL import ImageDraw

import psychopy.visual
import psychopy.event
import psychopy.core

from psychopy import monitors
from psychopy.tools.monitorunittools import deg2cm, deg2pix, pix2cm, cm2pix

default_calibration_target_dot_size = {
        'pix': 2.0, 'norm':0.004, 'height':0.002, 'cm':0.05,
        'deg':0.05, 'degFlat':0.05, 'degFlatPos':0.05
    }
default_calibration_target_disc_size = {
        'pix': 2.0*20, 'norm':0.004*20, 'height':0.002*20, 'cm':0.05*20,
        'deg':0.05*20, 'degFlat':0.05*20, 'degFlatPos':0.05*20
    }

key_index_dict = {
        '1':0, 'num_1':0, '2':1, 'num_2':1, '3':2, 'num_3':2,
        '4':3, 'num_4':3, '5':4, 'num_5':4, '6':5, 'num_6':5,
        '7':6, 'num_7':6, '8':7, 'num_8':7, '9':8, 'num_9':8
    }

def cm2deg(cm, monitor, correctFlat=False):
    """
    Bug-fixed version of psychopy.tools.monitorunittools.cm2deg
    (PsychoPy version<=1.85.1).
    """
    
    if not isinstance(monitor, monitors.Monitor):
        msg = ("cm2deg requires a monitors.Monitor object as the second "
               "argument but received %s")
        raise ValueError(msg % str(type(monitor)))
    dist = monitor.getDistance()
    if dist is None:
        msg = "Monitor %s has no known distance (SEE MONITOR CENTER)"
        raise ValueError(msg % monitor.name)
    if correctFlat:
        return np.degrees(np.arctan(cm / dist))
    else:
        return cm / (dist * 0.017455)


def pix2deg(pixels, monitor, correctFlat=False):
    """
    Bug-fixed version of psychopy.tools.monitorunittools.pix2deg
    (PsychoPy version<=1.85.1).
    """
    
    scrWidthCm = monitor.getWidth()
    scrSizePix = monitor.getSizePix()
    if scrSizePix is None:
        msg = "Monitor %s has no known size in pixels (SEE MONITOR CENTER)"
        raise ValueError(msg % monitor.name)
    if scrWidthCm is None:
        msg = "Monitor %s has no known width in cm (SEE MONITOR CENTER)"
        raise ValueError(msg % monitor.name)
    cmSize = pixels * float(scrWidthCm) / scrSizePix[0]
    return cm2deg(cmSize, monitor, correctFlat)


class tobii_controller:
    """
    Tobii controller for PsychoPy
    tobii_research package is required to use this class.
    """
    
    eyetracker = None
    calibration = None
    eyetracker_id = None
    win = None
    gaze_data = []
    event_data = []
    retry_points = []
    datafile = None
    embed_events = False


    def __init__(self, win, id=0):
        """
        Initialize tobii_controller object.
        
        :param win: PsychoPy Window object.
        :param int id: ID of Tobii unit to connect with.
            Default value is 0.
        """
        
        self.eyetracker_id = id
        self.win = win
        
        self.calibration_target_dot_size = default_calibration_target_dot_size[self.win.units]
        self.calibration_target_disc_size = default_calibration_target_disc_size[self.win.units]
        self.calibration_target_dot = psychopy.visual.Circle(self.win, 
            radius=self.calibration_target_dot_size, fillColor='white',
            lineColor=None,lineWidth=1, autoLog=False)
        self.calibration_target_disc = psychopy.visual.Circle(self.win,
            radius=self.calibration_target_disc_size, fillColor='lime',
            lineColor='white', lineWidth=1, autoLog=False)
        self.update_calibration = self.update_calibration_default
        if self.win.units == 'norm': # fix oval
            self.calibration_target_dot.setSize([float(self.win.size[1])/self.win.size[0], 1.0])
            self.calibration_target_disc.setSize([float(self.win.size[1])/self.win.size[0], 1.0])
        
        eyetrackers = tobii_research.find_all_eyetrackers()

        if len(eyetrackers)==0:
            raise RuntimeError('No Tobii eyetrackers')
        
        try:
            self.eyetracker = eyetrackers[self.eyetracker_id]
        except:
            raise ValueError(
                'Invalid eyetracker ID {}\n({} eyetrackers found)'.format(
                    self.eyetracker_id, len(eyetrackers)))
        
        self.calibration = tobii_research.ScreenBasedCalibration(self.eyetracker)


    def show_status(self, text_color='white', enable_mouse=False):
        """
        Draw eyetracker status on the screen.
        
        :param text_color: Color of message text. Default value is 'white'
        :param bool enable_mouse: If True, mouse operation is enabled.
            Default value is False.
        """
        
        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')
        
        original_mouseVisible = self.win.mouseVisible
        self.win.mouseVisible = False
        
        if enable_mouse:
            mouse = psychopy.event.Mouse(visible=False, win=self.win)
        
        self.gaze_data_status = None
        self.eyetracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA,
                                     self.on_gaze_data_status)
        
        msg = psychopy.visual.TextStim(self.win, color=text_color,
            height=0.02, pos=(0,-0.35), units='height', autoLog=False)
        bgrect = psychopy.visual.Rect(self.win,
            width=0.6, height=0.6, lineColor='white', fillColor='black',
            units='height', autoLog=False)
        leye = psychopy.visual.Circle(self.win,
            size=0.05, units='height', lineColor=None, fillColor='green',
            autoLog=False)
        reye = psychopy.visual.Circle(self.win, size=0.05, units='height',
            lineColor=None, fillColor='red', autoLog=False)
        
        b_show_status = True
        while b_show_status:
            bgrect.draw()
            if self.gaze_data_status is not None:
                lp, lv, rp, rv = self.gaze_data_status
                msgst = 'Left: {:.3f},{:.3f},{:.3f}\n'.format(*lp)
                msgst += 'Right: {:.3f},{:.3f},{:.3f}\n'.format(*rp)
                msg.setText(msgst)
                if lv:
                    leye.setPos(((lp[0]-0.5)/2,(lp[1]-0.5)/2))
                    leye.setRadius((1-lp[2])/2)
                    leye.draw()
                if rv:
                    reye.setPos(((rp[0]-0.5)/2,(rp[1]-0.5)/2))
                    reye.setRadius((1-rp[2])/2)
                    reye.draw()
            
            for key in psychopy.event.getKeys():
                if key == 'escape' or key == 'space':
                    b_show_status = False
            
            msg.draw()
            self.win.flip()
        
        self.eyetracker.unsubscribe_from(tobii_research.EYETRACKER_GAZE_DATA)

        self.win.mouseVisible = original_mouseVisible


    def on_gaze_data_status(self, gaze_data):
        """
        Callback function used by
        :func:`~psychopy_tobii_controller.tobii_controller.show_status`
        
        Usually, users don't have to call this method.
        """
        
        lp = gaze_data.left_eye.gaze_origin.position_in_track_box_coordinates
        lv = gaze_data.left_eye.gaze_origin.validity
        rp = gaze_data.right_eye.gaze_origin.position_in_track_box_coordinates
        rv = gaze_data.right_eye.gaze_origin.validity
        self.gaze_data_status = (lp, lv, rp, rv)


    def run_calibration(self, calibration_points, move_duration=1.5,
            shuffle=True, start_key='space', decision_key='space',
            text_color='white', enable_mouse=False):
        """
        Run calibration.
        
        :param calibration_points: List of position of calibration points.
        :param float move_duration: Duration of animation of calibration target.
            Unit is second.  Default value is 1.5.
        :param bool shuffle: If True, order of calibration point is shuffled.
            Otherwise, calibration target moves in the order of calibration_points.
            Default value is True.
        :param str start_key: Name of key to start calibration procedure.
            If None, calibration starts immediately afte this method is called.
            Default value is 'space'.
        :param str decision_key: Name of key to accept/retry calibration.
            Default value is 'space'.
        :param text_color: Color of message text. Default value is 'white'
        :param bool enable_mouse: If True, mouse operation is enabled.
            Default value is False.
        """
        
        if self.eyetracker is None:
            raise RuntimeError('Eyetracker is not found.')
        
        if not (2 <= len(calibration_points) <= 9):
            raise ValueError('Calibration points must be 2~9')
        
        original_mouseVisible = self.win.mouseVisible
        self.win.mouseVisible = False

        if enable_mouse:
            mouse = psychopy.event.Mouse(visible=False, win=self.win)
        
        img = Image.new('RGB',tuple(self.win.size))
        img_draw = ImageDraw.Draw(img)
        
        result_img = psychopy.visual.SimpleImageStim(self.win, img, autoLog=False)
        result_msg = psychopy.visual.TextStim(self.win, pos=(0,-self.win.size[1]/4),
            color=text_color, units='pix', autoLog=False)
        remove_marker = psychopy.visual.Circle(
            self.win, radius=self.calibration_target_dot.radius*5,
            fillColor='black', lineColor='white', lineWidth=1, autoLog=False)
        if self.win.units == 'norm': # fix oval
            remove_marker.setSize([float(self.win.size[1])/self.win.size[0], 1.0])
            remove_marker.setSize([float(self.win.size[1])/self.win.size[0], 1.0])

        self.calibration.enter_calibration_mode()

        self.move_duration = move_duration
        self.original_calibration_points = calibration_points[:]
        self.retry_points = list(range(len(self.original_calibration_points))) # set all points
        
        in_calibration_loop = True
        while in_calibration_loop:
            self.calibration_points = []
            for i in range(len(self.original_calibration_points)):
                if i in self.retry_points:
                    self.calibration_points.append(self.original_calibration_points[i])
            
            if shuffle:
                np.random.shuffle(self.calibration_points)
            
            if start_key is not None or enable_mouse:
                waitkey = True
                if start_key is not None:
                    if enable_mouse:
                        result_msg.setText('Press {} or click left button to start calibration'.format(start_key))
                    else:
                        result_msg.setText('Press {} to start calibration'.format(start_key))
                else: # enable_mouse==True
                    result_msg.setText('Click left button to start calibration')
                while waitkey:
                    for key in psychopy.event.getKeys():
                        if key==start_key:
                           waitkey = False
                    
                    if enable_mouse and mouse.getPressed()[0]:
                        waitkey = False
                    
                    result_msg.draw()
                    self.win.flip()
            else:
                self.win.flip()
            
            self.update_calibration()
            
            calibration_result = self.calibration.compute_and_apply()
            
            self.win.flip()
            
            img_draw.rectangle(((0,0),tuple(self.win.size)),fill=(128,128,128))
            if calibration_result.status == tobii_research.CALIBRATION_STATUS_FAILURE:
                #computeCalibration failed.
                pass
            else:
                if len(calibration_result.calibration_points) == 0:
                    pass
                else:
                    for calibration_point in calibration_result.calibration_points:
                        p = calibration_point.position_on_display_area
                        for calibration_sample in calibration_point.calibration_samples:
                            lp = calibration_sample.left_eye.position_on_display_area
                            rp = calibration_sample.right_eye.position_on_display_area
                            if calibration_sample.left_eye.validity == tobii_research.VALIDITY_VALID_AND_USED:
                                img_draw.line(((p[0]*self.win.size[0], p[1]*self.win.size[1]),
                                              (lp[0]*self.win.size[0], lp[1]*self.win.size[1])), fill=(0,255,0))
                            if calibration_sample.right_eye.validity == tobii_research.VALIDITY_VALID_AND_USED:
                                img_draw.line(((p[0]*self.win.size[0], p[1]*self.win.size[1]),
                                              (rp[0]*self.win.size[0], rp[1]*self.win.size[1])), fill=(255,0,0))
                        img_draw.ellipse(((p[0]*self.win.size[0]-3, p[1]*self.win.size[1]-3),
                                         (p[0]*self.win.size[0]+3, p[1]*self.win.size[1]+3)), outline=(0,0,0))

            if enable_mouse:
                result_msg.setText('Accept/Retry: {} or right-click\nSelect recalibration points: 0-9 key or left-click\nAbort: esc'.format(decision_key))
            else:
                result_msg.setText('Accept/Retry: {}\nSelect recalibration points: 0-9 key\nAbort: esc'.format(decision_key))
            result_img.setImage(img)
            
            waitkey = True
            self.retry_points = []
            if enable_mouse:
                mouse.setVisible(True)
            while waitkey:
                for key in psychopy.event.getKeys():
                    if key in [decision_key, 'escape']:
                        waitkey = False
                    elif key in ['0', 'num_0']:
                        if len(self.retry_points) == 0:
                            self.retry_points = list(range(len(self.original_calibration_points)))
                        else:
                            self.retry_points = []
                    elif key in key_index_dict:
                        key_index = key_index_dict[key]
                        if key_index<len(self.original_calibration_points):
                            if key_index in self.retry_points:
                                self.retry_points.remove(key_index)
                            else:
                                self.retry_points.append(key_index)
                if enable_mouse:
                    pressed = mouse.getPressed()
                    if pressed[2]: # right click
                        key = decision_key
                        waitkey = False
                    elif pressed[0]: # left click
                        mouse_pos = mouse.getPos()
                        for key_index in range(len(self.original_calibration_points)):
                            p = self.original_calibration_points[key_index]
                            if np.linalg.norm([mouse_pos[0]-p[0], mouse_pos[1]-p[1]]) < 0.1:
                                if key_index in self.retry_points:
                                    self.retry_points.remove(key_index)
                                else:
                                    self.retry_points.append(key_index)
                                time.sleep(0.2)
                                break
                result_img.draw()
                if len(self.retry_points)>0:
                    for index in self.retry_points:
                        if index > len(self.original_calibration_points):
                            self.retry_points.remove(index)
                        remove_marker.setPos(self.original_calibration_points[index])
                        remove_marker.draw()
                result_msg.draw()
                self.win.flip()
        
            if key == decision_key:
                if len(self.retry_points) == 0:
                    retval = 'accept'
                    in_calibration_loop = False
                else: #retry
                    for point_index in self.retry_points:
                        x, y = self.getTobiiPos(self.original_calibration_points[point_index])
                        self.calibration.discard_data(x, y)
            elif key == 'escape':
                retval = 'abort'
                in_calibration_loop = False
            else:
                raise RuntimeError('Calibration: Invalid key')
                
            if enable_mouse:
                mouse.setVisible(False)


        self.calibration.leave_calibration_mode()

        self.win.mouseVisible = original_mouseVisible

        return retval


    def collect_calibration_data(self, p, cood='PsychoPy'):
        """
        Callback function used by
        :func:`~psychopy_tobii_controller.tobii_controller.run_calibration`
        
        Usually, users don't have to call this method.
        """
        
        if cood=='PsychoPy':
            self.calibration.collect_data(*self.getTobiiPos(p))
        elif cood =='Tobii':
            self.calibration.collect_data(*p)
        else:
            raise ValueError('cood must be \'PsychoPy\' or \'Tobii\'')


    def update_calibration_default(self):
        """
        Updating calibration target and correcting calibration data.
        This method is called by
        :func:`~psychopy_tobii_controller.tobii_controller.run_calibration`
        
        Usually, users don't have to call this method.
        """
        
        clock = psychopy.core.Clock()
        for point_index in range(len(self.calibration_points)):
            x, y = self.getTobiiPos(self.calibration_points[point_index])
            self.calibration_target_dot.setPos(self.calibration_points[point_index])
            self.calibration_target_disc.setPos(self.calibration_points[point_index])
            
            clock.reset()
            current_time = clock.getTime()
            while current_time < self.move_duration:
                self.calibration_target_disc.setRadius(
                    (self.calibration_target_dot_size*2.0-self.calibration_target_disc_size)/ \
                     self.move_duration*current_time+self.calibration_target_disc_size
                    )
                psychopy.event.getKeys()
                self.calibration_target_disc.draw()
                self.calibration_target_dot.draw()
                self.win.flip()
                current_time = clock.getTime()
            self.calibration.collect_data(x, y)


    def set_custom_calibration(self, func):
        """
        Set custom calibration function.
        
        :param func: custom calibration function.
        """
        
        self.update_calibration = types.MethodType(func, self, tobii_controller)


    def use_default_calibration(self):
        """
        Revert calibration function to default one.
        """
        
        self.update_calibration = self.update_calibration_default


    def set_calibration_param(self, param_dict):
        """
        Set calibration parameters.
        
        :param dict param_dict: Dict object that holds calibration parameters.
            Use :func:`~psychopy_tobii_controller.tobii_controller.get_calibration_param`
            to get dict object.
        """
        self.calibration_target_dot_size = param_dict['dot_size']
        self.calibration_target_dot.lineColor = param_dict['dot_line_color']
        self.calibration_target_dot.fillColor = param_dict['dot_fill_color']
        self.calibration_target_dot.lineWidth = param_dict['dot_line_width']
        self.calibration_target_disc_size = param_dict['disc_size']
        self.calibration_target_disc.lineColor = param_dict['disc_line_color']
        self.calibration_target_disc.fillColor = param_dict['disc_fill_color']
        self.calibration_target_disc.lineWidth = param_dict['disc_line_width']


    def get_calibration_param(self):
        """
        Set calibration parameters as a dict object.
        The dict object has following keys.

        - 'dot_size': size of the center dot of calibration target.
        - 'dot_line_color': line color of the center dot of calibration target.
        - 'dot_fill_color': fill color of the center dot of calibration target.
        - 'dot_line_width': line width of the center dot of calibration target.
        - 'disc_size': size of the surrounding disc of calibration target.
        - 'disc_line_color': line color of the surrounding disc of calibration target
        - 'disc_fill_color': fill color of the surrounding disc of calibration target
        - 'disc_line_width': line width of the surrounding disc of calibration target
        - 'text_color': color of text
        """
        
        param_dict = {'dot_size':self.calibration_target_dot_size,
                      'dot_line_color':self.calibration_target_dot.lineColor,
                      'dot_fill_color':self.calibration_target_dot.fillColor,
                      'dot_line_width':self.calibration_target_dot.lineWidth,
                      'disc_size':self.calibration_target_disc_size,
                      'disc_line_color':self.calibration_target_disc.lineColor,
                      'disc_fill_color':self.calibration_target_disc.fillColor,
                      'disc_line_width':self.calibration_target_disc.lineWidth}
        return param_dict


    def subscribe(self):
        """
        Start recording.
        """
        
        self.gaze_data = []
        self.event_data = []
        self.eyetracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA, self.on_gaze_data)


    def unsubscribe(self):
        """
        Stop recording.
        """
        
        self.eyetracker.unsubscribe_from(tobii_research.EYETRACKER_GAZE_DATA)


    def on_gaze_data(self, gaze_data):
        """
        Callback function used by
        :func:`~psychopy_tobii_controller.tobii_controller.subscribe`
        
        Usually, users don't have to call this method.
        """
        
        t = gaze_data.system_time_stamp
        lx = gaze_data.left_eye.gaze_point.position_on_display_area[0]
        ly = gaze_data.left_eye.gaze_point.position_on_display_area[1]
        lp = gaze_data.left_eye.pupil.diameter
        lv = gaze_data.left_eye.gaze_point.validity
        rx = gaze_data.right_eye.gaze_point.position_on_display_area[0]
        ry = gaze_data.right_eye.gaze_point.position_on_display_area[1]
        rp = gaze_data.right_eye.pupil.diameter
        rv = gaze_data.right_eye.gaze_point.validity
        self.gaze_data.append((t,lx,ly,lp,lv,rx,ry,rp,rv))


    def get_current_gaze_position(self):
        """
        Get current (i.e. the latest) gaze position as a tuple of
        (left_x, left_y, right_x, right_y).
        Values are numpy.nan if Tobii fails to get gaze position.
        """
        
        if len(self.gaze_data)==0:
            return (np.nan, np.nan, np.nan, np.nan)
        else:
            lxy = self.getPsychoPyPos(self.gaze_data[-1][1:3])
            rxy = self.getPsychoPyPos(self.gaze_data[-1][5:7])
            return (lxy[0],lxy[1],rxy[0],rxy[1])


    def get_current_pupil_size(self):
        """
        Get current (i.e. the latest) pupil size as a tuple of
        (left, right).
        Values are numpy.nan if Tobii fails to get pupil size.
        """
        
        if len(self.gaze_data)==0:
            return (None,None)
        else:
            return (self.gaze_data[-1][3], #lp
                    self.gaze_data[-1][7]) #rp


    def open_datafile(self, filename, embed_events=False):
        """
        Open data file.
        
        :param str filename: Name of data file to be opened.
        :param bool embed_events: If True, event data is 
            embeded in gaze data.  Otherwise, event data is 
            separately output after gaze data.
        """
        
        if self.datafile is not None:
            self.close_datafile()
        
        self.embed_events = embed_events
        self.datafile = open(filename,'w')
        self.datafile.write('Recording date:\t'+datetime.datetime.now().strftime('%Y/%m/%d')+'\n')
        self.datafile.write('Recording time:\t'+datetime.datetime.now().strftime('%H:%M:%S')+'\n')
        self.datafile.write('Recording resolution\t%d x %d\n\n' % tuple(self.win.size))


    def close_datafile(self):
        """
        Write data to the data file and close the data file.
        """
        
        if self.datafile != None:
            self.flush_data()
            self.datafile.close()
        
        self.datafile = None


    def record_event(self,event):
        """
        Record events with timestamp.
        
        :param str event: Any string.
        """
        
        self.event_data.append((tobii_research.get_system_time_stamp(), event))


    def flush_data(self):
        """
        Write data to the data file.
        """
        
        if self.datafile == None:
            print('data file is not set.')
            return
        
        if len(self.gaze_data)==0:
            return
        
        if self.embed_events:
            self.datafile.write('\t'.join(['TimeStamp',
                                           'GazePointXLeft',
                                           'GazePointYLeft',
                                           'PupilLeft',
                                           'ValidityLeft',
                                           'GazePointXRight',
                                           'GazePointYRight',
                                           'PupilRight',
                                           'ValidityRight',
                                           'GazePointX',
                                           'GazePointY',
                                           'Event'])+'\n')
        else:
            self.datafile.write('\t'.join(['TimeStamp',
                                           'GazePointXLeft',
                                           'GazePointYLeft',
                                           'PupilLeft',
                                           'ValidityLeft',
                                           'GazePointXRight',
                                           'GazePointYRight',
                                           'PupilRight',
                                           'ValidityRight',
                                           'GazePointX',
                                           'GazePointY'])+'\n')
        timestamp_start = self.gaze_data[0][0]
        num_output_events = 0
        
        for g in self.gaze_data:
            if self.embed_events:
                if num_output_events < len(self.event_data) and self.event_data[num_output_events][0] < g[0]:
                    self.datafile.write(('%.1f'+'\t'*11+'%s\n') % (
                        (self.event_data[num_output_events][0]-timestamp_start)/1000.0,
                        self.event_data[num_output_events][1])
                         )
                    num_output_events += 1

            lxy = self.getPsychoPyPos(g[1:3])
            rxy = self.getPsychoPyPos(g[5:7])
            self.datafile.write('%.1f\t%.4f\t%.4f\t%.4f\t%d\t%.4f\t%.4f\t%.4f\t%d'%(
                                (g[0]-timestamp_start)/1000.0,
                                lxy[0], lxy[1],
                                g[3], g[4],
                                rxy[0], rxy[1],
                                g[7], g[8]))
            if g[4] == 0 and g[8] == 0: #not detected
                ave = (np.nan, np.nan)
            elif g[4] == 0:
                ave = rxy
            elif g[8] == 0:
                ave = lxy
            else:
                ave = ((lxy[0]+rxy[0])/2.0,(lxy[1]+rxy[1])/2.0)
                
            if self.embed_events:
                self.datafile.write('\t%.4f\t%.4f\t\n' % ave)
            else:
                self.datafile.write('\t%.4f\t%.4f\n' % ave)
        
        if not self.embed_events:
            self.datafile.write('TimeStamp\tEvent\n')
            for e in self.event_data:
                self.datafile.write('%.1f\t%s\n' % ((e[0]-timestamp_start)/1000.0, e[1]))
        
        self.datafile.write('\n')
        self.datafile.flush()


    def getPsychoPyPos(self, p):
        """
        Convert PsychoPy position to Tobii coordinate system.
        
        :param p: Position (x, y)
        """
        
        p = (p[0], 1-p[1]) #flip vert
        if self.win.units == 'norm':
            return (2*p[0]-1, 2*p[1]-1)
        elif self.win.units == 'height':
            return ((p[0]-0.5)*self.win.size[0]/self.win.size[1], p[1]-0.5)
        
        p_pix = ((p[0]-0.5)*self.win.size[0], (p[1]-0.5)*self.win.size[1])
        if self.win.units == 'pix':
            return p_pix
        elif self.win.units == 'cm':
            return (pix2cm(p_pix[0], self.win.monitor), pix2cm(p_pix[1], self.win.monitor))
        elif self.win.units == 'deg':
            return (pix2deg(p_pix[0], self.win.monitor), pix2deg(p_pix[1], self.win.monitor))
        elif self.win.units in ['degFlat', 'degFlatPos']:
            return (pix2deg(np.array(p_pix), self.win.monitor, correctFlat=True))
        else:
            #show warning
            print('unit ({}) is not supported.'.format(self.win.units))
            return p


    def getTobiiPos(self, p):
        """
        Convert Tobii position to PsychoPy coordinate system.
        
        :param p: Position (x, y)
        """
        
        if self.win.units == 'norm':
            gp = ((p[0]+1)/2, (p[1]+1)/2)
        elif self.win.units == 'height':
            gp = (p[0]*self.win.size[1]/self.win.size[0]+0.5, p[1]+0.5)
        elif self.win.units == 'pix':
            gp = (p[0]/self.win.size[0]+0.5, p[1]/self.win.size[1]+0.5)
        elif self.win.units == 'cm':
            p_pix = (cm2pix(p[0], self.win.monitor), cm2pix(p[1], self.win.monitor))
            gp = (p_pix[0]/self.win.size[0]+0.5, p_pix[1]/self.win.size[1]+0.5)
        elif self.win.units == 'deg':
            p_pix = (deg2pix(p[0], self.win.monitor), deg2pix(p[1], self.win.monitor))
            gp = (p_pix[0]/self.win.size[0]+0.5, p_pix[1]/self.win.size[1]+0.5)
        elif self.win.units in ['degFlat', 'degFlatPos']:
            p_pix = (deg2pix(np.array(p), self.win.monitor, correctFlat=True))
            gp = (p_pix[0]/self.win.size[0]+0.5, p_pix[1]/self.win.size[1]+0.5)
        else:
            #show warning
            print('unit ({}) is not supported'.format(self.win.units))
            return p

        return (gp[0], 1-gp[1]) # flip vert

