#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 
try:
    from psychopy.app.builder.components._base import BaseVisualComponent, Param
except:
    from psychopy.experiment.components import BaseVisualComponent, Param
from os import path

thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
iconFile = path.join(thisFolder,'ptc_getpos.png')
tooltip = 'ptc_getpos: tobii_controller calibration'

paramNames = ['start_msg', 'stop_msg']

class ptc_getpos_component(BaseVisualComponent):
    """Recording"""
    categories = ['tobii_controller']
    def __init__(self, exp, parentName, name='ptc_getpos', filler=-10000, binocular='Average'):
        super(ptc_getpos_component, self).__init__(exp, parentName, name)
        self.type='ptc_getpos'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'
        
        #params
        self.order = ['name'] + paramNames[:] # want a copy, else codeParamNames list gets mutated
        self.params['filler']=Param(filler, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If gaze position is not available, gaze position is filled by this value.',
            label='Filler')
        self.params['binocular']=Param(binocular, valType='str', allowedTypes=[], allowedVals=['Average','LR'],
            updates='constant', allowedUpdates=[],
            hint='Average: (average_x, average_y) LR: {\'left\':(left_x, left_y), \'right\':(right_x, right_y)}',
            label='Binocular Data')
            
        # these inherited params are harmless but might as well trim:
        for p in ['startType', 'startVal', 'startEstim', 'stopVal', 'stopType', 'durationEstim']:
            del self.params[p]
        for p in ['color','opacity','colorSpace','pos','size','ori','units']:
            del self.params[p]

    def writeRoutineStartCode(self, buff):
        buff.writeIndented('%(name)s = []\n\n' % self.params)

    def writeFrameCode(self, buff):
        buff.writeIndented('%(name)s = ptc_controller_tobii_controller.get_current_gaze_position()\n' % self.params)

        if self.params['binocular'] == 'LR':
            buff.writeIndented('if %(name)s[0] is np.nan:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s[0] = %(filler)s\n' % (self.params))
            buff.writeIndented('%(name)s[1] = %(filler)s\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
            buff.writeIndented('if %(name)s[2] is np.nan:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s[2] = %(filler)s\n' % (self.params))
            buff.writeIndented('%(name)s[3] = %(filler)s\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
        else: #average
            buff.writeIndented('if %(name)s[0] is np.nan and %(name)s[2] is np.nan:\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s = [%(filler)s, %(filler)s]\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
            buff.writeIndented('elif %(name)s[0] is np.nan: #left eye is not available\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s = %(name)s[2:4]\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
            buff.writeIndented('elif %(name)s[2] is np.nan: #right eye is not available\n' % (self.params))
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s = %(name)s[0:2]\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
            buff.writeIndented('else:\n')
            buff.setIndentLevel(+1, relative=True)
            buff.writeIndented('%(name)s = [(%(name)s[0]+%(name)s[2])/2.0,(%(name)s[1]+%(name)s[3])/2.0]\n' % (self.params))
            buff.setIndentLevel(-1, relative=True)
