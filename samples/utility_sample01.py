import matplotlib.pyplot as plt
import numpy as np

# import utility
import psychopy_tobii_controller.utility as util
import psychopy_tobii_controller.constants as const

# Load data file using load_data().
# Return values are two list objects.
# The first one is gaze data, and the other is event data.
gaze_data, event_data = util.load_data('data.tsv')

# Use moving_average() to smooth gaze data if necessary.
# Note that the first argument of moving_average() is not
# gaze data list returned by load_data, but the ELEMENTS of 
# the gaze data.
# 
# If you want to apply moving average to N-th recording session
# of the gaze data, call moving_average()
# 
#     util.moving_average(gaze_data[N], n=3)
# 
smoothed_data = [util.moving_average(g, n=3) for g in gaze_data]


for trial in range(len(gaze_data)):

    # Getting list of fixations using detect_fixation_dt().
    # numpy.savetxt() would be convenient to output fixation data
    # to a text file.
    #
    #     numpy.savetxt('fix.txt',fixations, fmt='%.1f', delimiter=',')
    #
    fixations = util.detect_fixation_dt(smoothed_data[trial],
                                        max_dispersion = 50,
                                        min_duration = 100,
                                        eye = 'LR')
    
    # Prepare gaze data to plot.
    t = smoothed_data[trial][:,const.TimeStamp]
    x = smoothed_data[trial][:,const.GazePointX]
    y = smoothed_data[trial][:,const.GazePointY]
    
    # X-Y plot (smoothed data)
    plt.subplot(2,2,1)
    plt.plot(x, y)
    plt.xlim([-800,800])
    plt.ylim([-600,600])
    plt.xlabel('Horizontal gaze position (pix)')
    plt.ylabel('Vertical gaze position (pix)')
    
    # X-Y plot (detected fixations)
    plt.subplot(2,2,2)
    plt.plot(fixations[:,const.FixX], fixations[:,const.FixY], 'o-')
    plt.xlim([-800,800])
    plt.ylim([-600,600])
    plt.xlabel('Horizontal gaze position (pix)')
    plt.ylabel('Vertical gaze position (pix)')
    
    # X-T plot with event data
    plt.subplot(2,2,3)
    plt.plot(t, x, label='X')
    plt.plot(t, y, label='Y')
    
    for event in event_data[trial]:
        plt.plot([event[const.EventTime], event[const.EventTime]],
                 [-800, 800], 'k:')
        plt.text(event[const.EventTime], 400, event[const.EventText],
                 rotation=90)
    
    plt.ylim([-800,800])
    plt.xlabel('Time (ms)')
    plt.ylabel('Gaze position (pix)')
    plt.legend()
    
    plt.show()

