#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 
try:
    from psychopy.app.builder.components._base import BaseComponent, Param
except:
    from psychopy.experiment.components import BaseComponent, Param
from os import path

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'ptc_message.png')
tooltip = 'ptc_message: tobii_controller calibration'

paramNames = ['time','timeType','text']

class ptc_message_component(BaseComponent):
    """Recording"""
    categories = ['tobii_controller']
    def __init__(self, exp, parentName, name='ptc_message', time=0, timeType='time (s)', text='event'):
        super(ptc_message_component, self).__init__(exp, parentName, name)
        self.type='ptc_message'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'
        
        #params
        self.order = ['name'] + paramNames[:] # want a copy, else codeParamNames list gets mutated
        self.params['time']=Param(time, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='When this event should be recorded?',
            label='time')
        self.params['timeType']=Param(timeType, valType='str', allowedVals=['time (s)', 'frame N', 'condition'],
            updates='constant', allowedUpdates=[],
            hint='How do you want to define time?',
            label='time type')
        self.params['text']=Param(text, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Event text',
            label='Event')

            
        # these inherited params are harmless but might as well trim:
        for p in ['startType', 'startVal', 'startEstim', 'stopVal', 'stopType', 'durationEstim']:
            del self.params[p]


    def writeRoutineStartCode(self, buff):
        buff.writeIndented('%(name)s_sent=False\n' % (self.params))

    def writeFrameCode(self, buff):
        if self.params['timeType'].val=='time (s)':
            buff.writeIndented('if %(name)s_sent==False and %(time)s<=t:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('ptc_controller_tobii_controller.record_event(%(text)s)\n' % (self.params))
            buff.writeIndented('%(name)s_sent=True\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
        elif self.params['timeType'].val=='frame N':
            buff.writeIndented('if %(time)s==frameN:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('ptc_controller_tobii_controller.record_event(%(text)s)\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
        else: # condition
            buff.writeIndented('if %(time)s:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('ptc_controller_tobii_controller.record_event(%(text)s)\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)

