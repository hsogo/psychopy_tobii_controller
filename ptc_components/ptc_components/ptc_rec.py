#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 
from psychopy.experiment.components import BaseComponent, Param
from os import path


class ptc_rec_component(BaseComponent):
    """Recording"""
    categories = ['tobii_controller']
    targets = ['PsychoPy']
    thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
    iconFile = path.join(thisFolder,'ptc_rec.png')
    tooltip = 'ptc_rec: tobii_controller calibration'

    def __init__(self, exp, parentName, name='ptc_rec', start_rec=True, start_msg='', stop_rec=True, stop_msg='', wait=True):
        super(ptc_rec_component, self).__init__(exp, parentName, name)
        self.type='ptc_rec'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'
        
        #params
        self.order = ['name', 'start_rec', 'start_msg', 'stop_rec', 'stop_msg', 'wait']
        self.params['start_rec']=Param(start_rec, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint="Start recording at the beginning of this routine.  Uncheck this if recording is continuing from the preceding routine.",
            label="Start Recording")
        self.params['start_msg'] = Param(start_msg, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='This text is inserted at the beginning of the recording.',
            label='Event (start)', categ='Advanced')
        self.params['stop_rec']=Param(stop_rec, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint="Stop recording at the end of this routine.  Uncheck this if you want to continue recording in the next routine.",
            label="Stop Recording")
        self.params['stop_msg'] = Param(stop_msg, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='This text is inserted at the end of the recording.',
            label='Event (stop)', categ='Advanced')
        self.params['wait'] = Param(wait, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If checked, experiment stops until data become available.',
            label='Wait for data', categ='Advanced')
            
        # these inherited params are harmless but might as well trim:
        for p in ('startType', 'startVal', 'startEstim', 'stopVal',
                  'stopType', 'durationEstim',
                  'saveStartStop', 'syncScreenRefresh'):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        if self.params['start_rec'].val:
            buff.writeIndented('ptc_controller_current_routineTimer_value = routineTimer.getTime()\n')
            buff.writeIndented('ptc_controller_tobii_controller.subscribe(wait=%(wait)s)\n' % (self.params))
            buff.writeIndented('routineTimer.reset(ptc_controller_current_routineTimer_value)\n')
            if self.params['start_msg'].val != '':
                buff.writeIndented('ptc_controller_tobii_controller.record_event(%(start_msg)s)\n' % (self.params))

    def writeFrameCode(self, buff):
        pass

    def writeRoutineEndCode(self,buff):
        if self.params['stop_rec'].val:
            if self.params['stop_msg'].val != '':
                buff.writeIndented('ptc_controller_tobii_controller.record_event(%(stop_msg)s)\n' % (self.params))
            buff.writeIndented('ptc_controller_tobii_controller.unsubscribe()\n')
