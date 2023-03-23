#!/usr/bin/env python
from setuptools import setup
import sys
import os

version = '1.2.0'

setup(name = 'psychopy_tobii_controller',
      version = version,
      description = 'Tobii Controller for PsychoPy',
      long_description = """
psychopy_tobii_controller is a helper module to use tobii_research package from PsychoPy.

Disclaimer: psychopy_tobii_controller is unofficial. It is NOT affiliated with Tobii.
""",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering',
      ],
      keywords = 'Tobii, PsychoPy, Eye tracking',
      author = 'Hiroyuki Sogo',
      author_email = 'hsogo12600@gmail.com',
      url = 'https://github.com/hsogo/psychopy_tobii_controller/',
      licence = 'GNU GPL',
      packages = ['psychopy_tobii_controller',
                  'psychopy_tobii_controller.ptc_init',
                  'psychopy_tobii_controller.ptc_rec',
                  'psychopy_tobii_controller.ptc_message',
                  'psychopy_tobii_controller.ptc_getpos',
                  'psychopy_tobii_controller.ptc_cal'],
      package_data={'psychopy_tobii_controller':['ptc*/*/*.png']},
      entry_points={
            'psychopy.experiment.components':['ptc_init_component=psychopy_tobii_controller.ptc_init:ptc_init_component',
                                              'ptc_rec_component=psychopy_tobii_controller.ptc_rec:ptc_rec_component',
                                              'ptc_message_component=psychopy_tobii_controller.ptc_message:ptc_message_component',
                                              'ptc_getpos_component=psychopy_tobii_controller.ptc_getpos:ptc_getpos_component',
                                              'ptc_cal_component=psychopy_tobii_controller.ptc_cal:ptc_cal_component']}
      )