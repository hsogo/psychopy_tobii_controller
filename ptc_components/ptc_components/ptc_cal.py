#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 

from psychopy.experiment.components import BaseComponent, Param
from os import path


class ptc_cal_component(BaseComponent):
    """Run calibration"""
    categories = ['tobii_controller']
    targets = ['PsychoPy']
    thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
    iconFile = path.join(thisFolder,'ptc_cal.png')
    tooltip = 'ptc_cal: tobii_controller calibration'

    def __init__(self, exp, parentName, name='ptc_cal', show_status=True,
        calibration_points = [[-0.4,-0.4],[0.4,-0.4],[0,0],[-0.4,0.4],[0.4,0.4]],
        shuffle=True, enable_mouse=False, start_key='space', decision_key='space',
        text_color='white', move_duration=1.5):
        super(ptc_cal_component, self).__init__(exp, parentName, name)
        self.type='ptc_cal'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'
        
        #params
        self.order = ['name', 'show_status', 'calibration_points', 'shuffle', 
            'enable_mouse', 'start_key', 'decision_key', 'text_color', 'move_duration']
            
        self.params['show_status'] = Param(show_status, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Show Tobii status before calibration',
            label='Show status')
        self.params['calibration_points'] = Param(calibration_points, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='List of calibration points',
            label='Calibration points')
        self.params['shuffle'] = Param(shuffle, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If checked, order of calibration points is randomized.',
            label='Shuffle')
        self.params['enable_mouse'] = Param(enable_mouse, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If checked, mouse operation is enabled.',
            label='Enable mouse operation', categ='Advanced')
        self.params['start_key'] = Param(start_key, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Name of the key that is used to start calibration procedure.',
            label='Start key', categ='Advanced')
        self.params['decision_key'] = Param(decision_key, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Name of the key that is used to decide accept/retry calibration.',
            label='Decision key', categ='Advanced')
        self.params['text_color'] = Param(text_color, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Text color',
            label='Text color', categ='Advanced')
        self.params['move_duration'] = Param(move_duration, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Motion duration',
            label='Motion duration', categ='Advanced')
            
        # these inherited params are harmless but might as well trim:
        for p in ('startType', 'startVal', 'startEstim', 'stopVal',
                  'stopType', 'durationEstim',
                  'saveStartStop', 'syncScreenRefresh'):
            if p in self.params:
                del self.params[p]    


    def writeRoutineStartCode(self, buff):
        if self.params['show_status'].val:
            buff.writeIndented('ptc_controller_tobii_controller.show_status(text_color=%(text_color)s, enable_mouse=%(enable_mouse)s)\n' % (self.params))
    
        buff.writeIndented('ptc_controller_tobii_controller.run_calibration(\n')
        buff.setIndentLevel(+1, relative=True)
        buff.writeIndented('calibration_points=%(calibration_points)s,\n' % (self.params))
        buff.writeIndented('shuffle=%(shuffle)s, start_key=%(start_key)s, decision_key=%(decision_key)s,\n' % (self.params))
        buff.writeIndented('text_color=%(text_color)s, enable_mouse=%(enable_mouse)s, move_duration=%(move_duration)s)\n' % (self.params))
        buff.setIndentLevel(-1, relative=True)

