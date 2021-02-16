#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 
from psychopy.experiment.components import BaseComponent, Param
from os import path

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'ptc_rec.png')
tooltip = 'ptc_rec: tobii_controller calibration'

class ptc_rec_component(BaseComponent):
    """Recording"""
    categories = ['tobii_controller']
    def __init__(self, exp, parentName, name='ptc_rec', start_msg='', stop_msg=''):
        super(ptc_rec_component, self).__init__(exp, parentName, name)
        self.type='ptc_rec'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'
        
        #params
        self.order = ['name', 'start_msg', 'stop_msg']
        self.params['start_msg'] = Param(start_msg, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='This text is inserted at the beginning of the recording.',
            label='Event (start)', categ='Advanced')
        self.params['stop_msg'] = Param(stop_msg, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='This text is inserted at the end of the recording.',
            label='Event (stop)', categ='Advanced')
            
        # these inherited params are harmless but might as well trim:
        for p in ('startType', 'startVal', 'startEstim', 'stopVal',
                  'stopType', 'durationEstim',
                  'saveStartStop', 'syncScreenRefresh'):
            if p in self.params:
                del self.params[p]

    def writeRoutineStartCode(self, buff):
        buff.writeIndented('ptc_controller_tobii_controller.subscribe()\n')
        if self.params['start_msg'].val != '':
            buff.writeIndented('ptc_controller_tobii_controller.record_event(%(start_msg)s)\n' % (self.params))

    def writeFrameCode(self, buff):
        pass

    def writeRoutineEndCode(self,buff):
        if self.params['stop_msg'].val != '':
            buff.writeIndented('ptc_controller_tobii_controller.record_event(%(stop_msg)s)\n' % (self.params))
        buff.writeIndented('ptc_controller_tobii_controller.unsubscribe()\n')
