#
# Tobii controller for PsychoPy
# 
# author: Hiroyuki Sogo
# Distributed under the terms of the GNU General Public License v3 (GPLv3).
# 
from psychopy.experiment.components import BaseComponent, Param
from os import path


class ptc_init_component(BaseComponent):
    """Initialize ptc_component"""
    categories = ['tobii_controller']
    targets = ['PsychoPy']
    thisFolder = path.abspath(path.dirname(__file__))#the absolute path to the folder containing this path
    iconFile = path.join(thisFolder,'ptc_init.png')
    tooltip = 'ptc_init: initialize tobii_controller'

    def __init__(self, exp, parentName, name='ptc_init', id=0, datafile="$'data/'+expInfo[\'participant\']+'.tsv'", embed=False, overwrite=False):
        super(ptc_init_component, self).__init__(exp, parentName, name)
        self.type='ptc_init'
        self.url='https://github.com/hsogo/psychopy_tobii_controller/'

        #params
        self.order = ['name', 'id', 'datafile', 'overwrite', 'embed']
        self.params['id'] = Param(id, valType='code', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='ID of Tobii eyetracker (0, 1, 2, ...)',
            label='Tobii eyetracker ID')
        self.params['datafile'] = Param(datafile, valType='str', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='Name of tobii_controller data file.',
            label='Tobii_controller Data File')
        self.params['overwrite'] = Param(overwrite, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If checked, existing datafile with the same name will be overwritten.',
            label='Overwrite datafile')
        self.params['embed'] = Param(embed, valType='bool', allowedTypes=[],
            updates='constant', allowedUpdates=[],
            hint='If checked, event data is embeded into gaze data.',
            label='Embed event', categ='Advanced')
        
        # these inherited params are harmless but might as well trim:
        for p in ('startType', 'startVal', 'startEstim', 'stopVal',
                  'stopType', 'durationEstim',
                  'saveStartStop', 'syncScreenRefresh'):
            if p in self.params:
                del self.params[p]
    
    def writeInitCode(self,buff):
        buff.writeIndented('from psychopy_tobii_controller import tobii_controller\n')
        buff.writeIndented('ptc_controller_tobii_controller = tobii_controller(win, id=%(id)s)\n' % (self.params))
        if self.params['datafile'].val != '':
            if not self.params['overwrite'].val:
                buff.writeIndented('ptc_controller_datafilename = %(datafile)s\n' % (self.params))
                buff.writeIndented('if os.path.exists(ptc_controller_datafilename):\n')
                buff.setIndentLevel(+1, relative=True)
                buff.writeIndented('raise FileExistsError(\'File exists: %s\' % ptc_controller_datafilename)\n')
                buff.setIndentLevel(-1, relative=True)
            buff.writeIndented('ptc_controller_tobii_controller.open_datafile(%(datafile)s, embed_events=%(embed)s)\n' % (self.params))
    
    def writeFrameCode(self, buff):
        pass
    
    def writeExperimentEndCode(self, buff):
        if self.params['datafile'].val != '':
            buff.writeIndented('ptc_controller_tobii_controller.close_datafile()\n')

