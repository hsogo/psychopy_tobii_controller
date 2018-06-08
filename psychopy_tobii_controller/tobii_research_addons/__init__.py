from .ScreenBasedCalibrationValidation import ScreenBasedCalibrationValidation
from .ScreenBasedCalibrationValidation import CalibrationValidationPoint
from .ScreenBasedCalibrationValidation import CalibrationValidationResult
from .vectormath import calculate_mean_point, calculate_normalized_point2_to_point3
from .vectormath import Point2, Point3, Vector3

__all__ = ("ScreenBasedCalibrationValidation", "CalibrationValidationPoint", "CalibrationValidationResult",
           "calculate_mean_point", "calculate_normalized_point2_to_point3", "Point2", "Point3", "Vector3")

__author__ = 'Tobii AB'
__licence__ = 'BSD'
__copyright__ = '''
Copyright 2018 Tobii AB

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
