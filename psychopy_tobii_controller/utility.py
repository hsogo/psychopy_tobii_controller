#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 

from __future__ import division
from __future__ import absolute_import

import numpy as np
import sys

from psychopy_tobii_controller.constants import *

def load_data(filename):
    """
    Load psychopy_tobii_controller's data file.
    This function returns two lists. The first list contains
    Tobii's gaze data, and the second list contains events recorded by
    :func:`~psychopy_tobii_controller.tobii_controller.record_event`.
    Length of these lists correspond to sessions included in the 
    data file.
    
    Gaze data of each session is sotred as a numpy.ndarray object with
    following 11 columns. 
    
    0. TimeStamp
    1. GazePointXLeft
    2. GazePointYLeft
    3. PupilLeft
    4. ValidityLeft
    5. GazePointXRight
    6. GazePointYRight
    7. PupilRight
    8. ValidityRight
    9. GazePointX
    10. GazePointY
    
    Event data of each session is stored as a list.
    
    [[timestamp1, event_string_1],
     [timestamp2, event_string_2],
     ...]
    
    *Example* ::
    
        gaze_data, event_data = load_data('datafile.txt')
    
    :param str filename:
        name of data file.
    :
    """

    status = 'none'
    event_mode = ''
    data = []
    event = []
    trial_data = []
    trial_event = []

    processed_lines = 0

    fp = open(filename, 'r')

    for line in fp:
        processed_lines += 1
        items = line.rstrip().split('\t')
        
        if len(items)==1 and items[0] == '':
            pass

        elif items[0][:9] == 'Recording':
            pass

        elif items[0] == 'Event recording mode:':
            event_mode = items[1]

        elif items[0] == 'Session Start':
            trial_data = []
            trial_event = []

        elif items[0] == 'Session End':
            if len(trial_data) > 0:
                data.append(np.array(trial_data))
                event.append(trial_event)
            
            status = 'none'
        
        elif len(items) == 2 and items[0] == 'TimeStamp' and items[1] == 'Event':
            if status != 'event': status = 'event' 

        elif items[0] == 'TimeStamp':
            if status != data: status = 'data'

        else: # data
            if status=='data':
                if event_mode == 'Separated':
                    trial_data.append(list(map(float, items)))
                    
                elif event_mode == 'Embedded':
                    if len(items)==11:
                        trial_data.append(list(map(float, items)))
                    elif len(items)==12:
                        trial_event.append([float(items[0]), items[-1]])
                    else:
                        raise VauleError('Invalid data format in line {}'.format(processed_line))
                else:
                    raise ValueError('Invalid event mode')
            elif status=='event':  # Separated mode only
                trial_event.append([float(items[0]), items[-1]])

    return data, event


def moving_average(data, n=3):
    """
    Apply moving averaget to gaze data.
    Format of the returned value is the same as that of input data.
    
    *Example* ::
    
        gaze_data, event_data = load_data('datafile.txt')
        
        # apply to the first session of the gaze data.
        smoothed_data = moving_average(gaze_data[0], n=3)
    
    :param numpy.ndarry data:
        Gaze data (single session).
    :param in n:
        Size of moving average.
    """
    
    new_data = np.zeros(data.shape)
    for col in range(data.shape[1]):
        if col in [GazePointXLeft, GazePointYLeft, PupilLeft,
                   GazePointXRight, GazePointYRight, PupilRight,
                   GazePointX, GazePointY]:
            new_data[:,col] = nan_moving_average_1d(data[:,col], n)
        else:
            new_data[:,col] = np.copy(data[:,col])
    
    return new_data


def nan_moving_average_1d(data, n=3):
    v = np.ones(n)/n
    
    if n%2==0:
        offset = int(n/2)
        f = [np.nanmean(data[max(idx-offset,0):idx+offset]) for idx in range(len(data))]
    else:
        offset = int((n-1)/2)
        f = [np.nanmean(data[max(idx-offset,0):idx+offset+1]) for idx in range(len(data))]
    
    return np.array(f)


def interpolate_gaze_data(data, t):
    """
    Calculate interploated gaze data at the time specified by t.
    
    :param numpy.ndarray data:
        Gaze data (single session).
    :param float t:
        Time to calculate interpolated value. Unit is milliseconds.
    :param str eye:
        Specify which eye is used.  Allowed value is 'L', 'R', or 'LR'.
        Each corresponds to left eye, right eye and avrage of eyes.
    """
    
    time_diff = np.abs(data[:,0]-t)
    idx = np.argmin(time_diff)
    
    if data[idx,0] == t:
        return data[idx,:]
    
    elif t < data[idx,0]:
        if idx == 0:
            return data[0,:]
        else:
            t1 = idx-1
            t2 = idx
    
    else: # data[idx,0] < t
        if t == len(data)-1:
            return data[idx,:]
        else:
            t1 = idx
            t2 = idx+1
            
    
    w1 = (data[t2,0]-t)/(data[t2,0]-data[t1,0])
    w2 = (t-data[t1,0])/(data[t2,0]-data[t1,0])
    
    # left eye
    if data[t1,ValidityLeft] == 0 and data[t2,ValidityLeft] == 0:
         left_data  = [np.nan, np.nan, np.nan]
         left_val = 0
    elif data[t2,ValidityLeft] == 0:
         left_data  = data[t1, GazePointXLeft:PupilLeft+1]
         left_val = 1
    elif data[t1,ValidityRight] == 0:
         left_data  = data[t2, GazePointXLeft:PupilLeft+1]
         left_val = 1
    else:
         left_data  = w1* data[t1, GazePointXLeft:PupilLeft+1] + w2* data[t2, GazePointXLeft:PupilLeft+1]
         left_val = 1
    
    # right eye
    if data[t1,ValidityRight] == 0 and data[t2,ValidityRight] == 0:
         right_data  = [np.nan, np.nan, np.nan]
         right_val = 0
    elif data[t2,ValidityRight] == 0:
         right_data  = data[t1, GazePointXRight:PupilRight+1]
         right_val = 1
    elif data[t1,ValidityRight] == 0:
         right_data  = data[t2, GazePointXRight:PupilRight+1]
         right_val = 1
    else:
         right_data  = w1* data[t1, GazePointXRight:PupilRight+1] + w2* data[t2, GazePointXRight:PupilRight+1]
         right_val = 1
    
    # gaze
    if left_val == 0 and right_val == 0:
        gaze_data = [np.nan, np.nan, np.nan]
    elif left_val == 0:
        gaze_data = right_data[:]
    elif right_val == 0:
        gaze_data = left_data[:]
    else:
        gaze_data = (left_data + right_data)/2.0
    
    result = []
    for s in [[t,], left_data, [left_val,], right_data, [right_val,], gaze_data]:
        result.extend(s)
    
    return np.array(result)


def detect_fixation_vt(data, max_velocity=100, min_duration=100, eye='LR'):
    """
    Detect fixations using velocity-threshold method.
    Returned value is a numpy.ndarray with following 4 columns.
    
    0. Onset time
    1. Duration
    2. Mean of X values within the fixation.
    3. Mean of Y values within the fixation.
    
    :param numpy.ndarray data:
        Gaze data (single session).
    :param float max_velocity:
        Fixation is considered to be terminated if velocity exceeds
        this value. Unit is pixel/sample.
    :param float min_duration:
        Fixation shorter than this value is rejected. Unit is milliseconds.
    :param str eye:
        Specify which eye is used.  Allowed value is 'L', 'R', or 'LR'.
        Each corresponds to left eye, right eye and avrage of eyes.
    """
    if eye=='L':
        x = data[:,GazePointXLeft]
        y = data[:,GazePointYLeft]
    elif eye=='R':
        x = data[:,GazePointXRight]
        y = data[:,GazePointYRight]
    elif eye=='LR':
        x = data[:,GazePointX]
        y = data[:,GazePointY]
    else:
        raise ValueError('eye must be L, R, or LR')
    
    vg = np.sqrt(np.diff(x)**2+np.diff(y)**2)
    vt = np.diff(data[:,0])
    
    on_fix = False
    candidates = []

    for idx in range(len(vg)):
        if vg[idx] < max_velocity:
            if not on_fix:
                on_fix = True
                start = idx
        else:
            if on_fix:
                dur = data[idx,0]-data[start,0]
                if dur >= min_duration:
                    on_fix = False
                    candidates.append([start, idx])
    
    fixations = []
    for idx in range(len(candidates)):
        start = candidates[idx][0]
        end = candidates[idx][1]
        x_ave = np.nanmean(x[start:end])
        y_ave = np.nanmean(y[start:end])
        fixations.append([data[start,0], data[end,0]-data[start,0], x_ave, y_ave])
    
    return np.array(fixations)


def detect_fixation_dt(data, max_dispersion=50, min_duration=100, eye='LR'):
    """
    Detect fixations using dispersion-threshold method.
    
    :param numpy.ndarray data:
        Gaze data (single session).
    :param float max_dispersion:
        Fixation is considered to be terminated if gaze points protrudes
        from an imaginary square with a side of this value.  Unit is pixel.
    :param float min_duration:
        Fixation shorter than this value is rejected. Unit is milliseconds.
    """
    if eye=='L':
        x = data[:,GazePointXLeft]
        y = data[:,GazePointYLeft]
    elif eye=='R':
        x = data[:,GazePointXRight]
        y = data[:,GazePointYRight]
    elif eye=='LR':
        x = data[:,GazePointX]
        y = data[:,GazePointY]
    else:
        raise ValueError('eye must be L, R, or LR')

    current_candidate = np.empty((0,2))
    candidates = []
    start = 0
    
    for idx in range(len(x)):
        if np.isnan(x[idx]):
            if idx==start:
                start += 1
                continue
        else:
            current_candidate = np.vstack([current_candidate, [x[idx],y[idx]]])
        if current_candidate.shape[0] > 0:
            disp = max(np.nanmax(current_candidate[:,0])-np.nanmin(current_candidate[:,0]),
                       np.nanmax(current_candidate[:,1])-np.nanmin(current_candidate[:,1]))
            if disp >= max_dispersion:
                dur = data[idx-1,0] - data[start,0]
                if dur >= min_duration:
                    candidates.append([start, idx-1])
                current_candidate = np.empty((0,2))
                start = idx

    fixations = []
    for idx in range(len(candidates)):
        start = candidates[idx][0]
        end = candidates[idx][1]
        x_ave = np.nanmean(x[start:end])
        y_ave = np.nanmean(y[start:end])
        fixations.append([data[start,0], data[end,0]-data[start,0], x_ave, y_ave])
    
    return np.array(fixations)

