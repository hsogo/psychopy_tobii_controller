'''
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

import math
import threading
from collections import defaultdict

import tobii_research
from . import vectormath


class CalibrationValidationPoint(object):
    '''Represents a collected point that goes into the calibration validation. It contains calculated values for
    accuracy and precision as well as the original gaze samples collected for the point.
    '''

    def __init__(self,
                 accuracy_left_eye,
                 accuracy_right_eye,
                 precision_left_eye,
                 precision_right_eye,
                 precision_rms_left_eye,
                 precision_rms_right_eye,
                 timed_out,
                 screen_point,
                 gaze_data):
        self.__accuracy_left_eye = accuracy_left_eye
        self.__accuracy_right_eye = accuracy_right_eye
        self.__precision_left_eye = precision_left_eye
        self.__precision_right_eye = precision_right_eye
        self.__precision_rms_left_eye = precision_rms_left_eye
        self.__precision_rms_right_eye = precision_rms_right_eye
        self.__timed_out = timed_out
        self.__screen_point = screen_point
        self.__gaze_data = gaze_data

    @property
    def accuracy_left_eye(self):
        '''The accuracy in degrees for the left eye.
        '''
        return self.__accuracy_left_eye

    @property
    def accuracy_right_eye(self):
        '''The accuracy in degrees for the right eye.
        '''
        return self.__accuracy_right_eye

    @property
    def precision_left_eye(self):
        '''The precision (standard deviation) in degrees for the left eye.
        '''
        return self.__precision_left_eye

    @property
    def precision_right_eye(self):
        '''The precision (standard deviation) in degrees for the right eye.
        '''
        return self.__precision_right_eye

    @property
    def precision_rms_left_eye(self):
        '''The precision (root mean square of sample-to-sample error) in degrees for the left eye.
        '''
        return self.__precision_rms_left_eye

    @property
    def precision_rms_right_eye(self):
        '''The precision (root mean square of sample-to-sample error) in degrees for the right eye.
        '''
        return self.__precision_rms_right_eye

    @property
    def timed_out(self):
        '''A boolean indicating if there was a timeout while collecting data for this point.
        '''
        return self.__timed_out

    @property
    def screen_point(self):
        '''The 2D coordinates of this point (in Active Display Coordinate System).
        '''
        return self.__screen_point

    @property
    def gaze_data(self):
        '''The gaze data samples collected for this point. These samples are the base for the calculated accuracy
        and precision.
        '''
        return self.__gaze_data


class CalibrationValidationResult(object):
    '''Contains the result of the calibration validation.
    '''

    def __init__(self,
                 points,
                 average_accuracy_left,
                 average_accuracy_right,
                 average_precision_left,
                 average_precision_right,
                 average_precision_rms_left,
                 average_precision_rms_right):
        self.__points = points
        self.__average_accuracy_left = average_accuracy_left
        self.__average_accuracy_right = average_accuracy_right
        self.__average_precision_left = average_precision_left
        self.__average_precision_right = average_precision_right
        self.__average_precision_rms_left = average_precision_rms_left
        self.__average_precision_rms_right = average_precision_rms_right

    @property
    def points(self):
        '''The results of the calibration validation per point (same points as were collected).
        '''
        return self.__points

    @property
    def average_accuracy_left(self):
        '''The accuracy in degrees averaged over all collected points for the left eye.
        '''
        return self.__average_accuracy_left

    @property
    def average_accuracy_right(self):
        '''The accuracy in degrees averaged over all collected points for the right eye.
        '''
        return self.__average_accuracy_right

    @property
    def average_precision_left(self):
        '''The precision (standard deviation) in degrees averaged over all collected points for the left eye.
        '''
        return self.__average_precision_left

    @property
    def average_precision_right(self):
        '''The precision (standard deviation) in degrees averaged over all collected points for the right eye.
        '''
        return self.__average_precision_right

    @property
    def average_precision_rms_left(self):
        '''The precision (root mean square of sample-to-sample error) in degrees averaged over all collected points
        for the left eye.
        '''
        return self.__average_precision_rms_left

    @property
    def average_precision_rms_right(self):
        '''The precision (root mean square of sample-to-sample error) in degrees averaged over all collected points
        for the right eye.
        '''
        return self.__average_precision_rms_right


def _calculate_eye_accuracy(gaze_origin_mean, gaze_point_mean, stimuli_point):
    '''Calculate angle difference between actual gaze point and target point.
    '''
    direction_gaze_point = vectormath.Vector3.from_points(gaze_origin_mean, gaze_point_mean).normalize()
    direction_target = vectormath.Vector3.from_points(gaze_origin_mean, stimuli_point).normalize()
    return direction_target.angle(direction_gaze_point)


def _calculate_eye_precision(direction_gaze_point_list, direction_gaze_point_mean_list):
    '''Calculate standard deviation of gaze point angles.
    '''
    angles = []
    for dir_gaze_point, dir_gaze_point_mean in zip(direction_gaze_point_list, direction_gaze_point_mean_list):
        angles.append(dir_gaze_point.angle(dir_gaze_point_mean))
    variance = sum([x**2 for x in angles]) / len(angles)
    standard_deviation = math.sqrt(variance)
    return standard_deviation


def _calculate_eye_precision_rms(direction_gaze_point_list):
    '''Calculate root mean square (RMS) of gaze point angles.
    '''
    consecutive_angle_diffs = []
    last_gaze_point_vector = direction_gaze_point_list[0]
    for gaze_point_vector in direction_gaze_point_list[1:]:
        consecutive_angle_diffs.append(gaze_point_vector.angle(last_gaze_point_vector))
        last_gaze_point_vector = gaze_point_vector
    variance = sum([x**2 for x in consecutive_angle_diffs]) / len(consecutive_angle_diffs)
    rms = math.sqrt(variance)
    return rms


class ScreenBasedCalibrationValidation(object):
    '''Provides methods and properties for managing calibration validation for screen based eye trackers.
    '''
    SAMPLE_COUNT_MIN = 10
    SAMPLE_COUNT_MAX = 3000
    TIMEOUT_MIN = 100  # ms
    TIMEOUT_MAX = 3000  # ms

    def __init__(self,
                 eyetracker,
                 sample_count=30,
                 timeout_ms=1000):
        '''Create a calibration validation object for screen based eye trackers.

        Args:
        eyetracker: See @ref EyeTracker.
        sample_count: The number of samples to collect. Default 30, minimum 10, maximum 3000.
        timeout_ms: Timeout in milliseconds. Default 1000, minimum 100, maximum 3000.

        Raises:
        ValueError
        '''
        if not isinstance(eyetracker, tobii_research.EyeTracker):
            raise ValueError("Not a valid EyeTracker object")
        self.__eyetracker = eyetracker

        if not self.SAMPLE_COUNT_MIN <= sample_count <= self.SAMPLE_COUNT_MAX:
            raise ValueError("Samples must be between 10 and 3000")
        self.__sample_count = sample_count

        if not self.TIMEOUT_MIN <= timeout_ms <= self.TIMEOUT_MAX:
            raise ValueError("Timeout must be between 100 and 3000")
        self.__timeout_ms = timeout_ms

        self.__current_point = None
        self.__current_gaze_data = []
        self.__collected_points = defaultdict(list)

        self.__is_collecting_data = False
        self.__validation_mode = False

        self.__timeout = False
        self.__timeout_thread = None
        self.__lock = threading.RLock()  # synchronization between timer and gaze data subscription callback

    def _calibration_timeout_handler(self):
        self.__lock.acquire()
        if self.__is_collecting_data:
            self.__timeout = True
            self.__is_collecting_data = False
        self.__lock.release()

    def _gaze_data_received(self, gaze_data):
        self.__lock.acquire()
        if self.__is_collecting_data:
            if len(self.__current_gaze_data) < self.__sample_count:
                if gaze_data.left_eye.gaze_point.validity and gaze_data.right_eye.gaze_point.validity:
                    self.__current_gaze_data.append(gaze_data)
            else:
                # Data collecting stopped on sample count condition, timer might still be running
                self.__timeout_thread.cancel()

                # Data collecting done for this point
                self.__collected_points[self.__current_point] += self.__current_gaze_data
                self.__current_gaze_data = []
                self.__is_collecting_data = False
        self.__lock.release()

    def __enter__(self):
        self.enter_validation_mode()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.is_validation_mode:
            if self.is_collecting_data:
                # Stop data collection
                self.__lock.acquire()
                self.__timeout_thread.cancel()
                self.__is_collecting_data = False
                self.__lock.release()
            self.leave_validation_mode()

    def enter_validation_mode(self):
        '''Enter the calibration validation mode and starts subscribing to gaze data from the eye tracker.

        Raises:
        RuntimeWarning
        '''
        if self.__validation_mode or self.__is_collecting_data:
            raise RuntimeWarning("Validation mode already entered")

        self.__collected_points = defaultdict(list)
        self.__eyetracker.subscribe_to(tobii_research.EYETRACKER_GAZE_DATA, self._gaze_data_received)
        self.__validation_mode = True

    def leave_validation_mode(self):
        '''Leaves the calibration validation mode, clears all collected data, and unsubscribes from the eye tracker.

        Raises:
        RuntimeWarning
        '''
        if not self.__validation_mode:
            raise RuntimeWarning("Not in validation mode")
        if self.__is_collecting_data:
            raise RuntimeWarning("Cannot leave validation mode while collecting data")

        self.__current_point = None
        self.__current_gaze_data = []
        self.__eyetracker.unsubscribe_from(tobii_research.EYETRACKER_GAZE_DATA, self._gaze_data_received)
        self.__validation_mode = False

    def start_collecting_data(self, screen_point):
        '''Starts collecting data for a calibration validation point.The argument used is the point the user
        is assumed to be looking at and is given in the active display area coordinate system.
        Please check State property to know when data collection is completed (or timed out).

        Args:
        screen_point: The normalized 2D point on the display area.

        Raises:
        ValueError
        RuntimeWarning
        '''
        if type(screen_point) is not vectormath.Point2:
            raise ValueError("A screen point must be of Point2 type")
        if not (0.0 <= screen_point.x <= 1.0 and 0.0 <= screen_point.y <= 1.0):
            raise ValueError("Screen point must be within coordinates (0.0, 0.0) and (1.0, 1.0)")
        if not self.__validation_mode:
            raise RuntimeWarning("Not in validation mode")
        if self.__is_collecting_data:
            raise RuntimeWarning("Already collecting data")

        self.__current_point = screen_point
        self.__current_gaze_data = []
        self.__timeout = False
        self.__timeout_thread = threading.Timer(self.__timeout_ms / 1000.0, self._calibration_timeout_handler)
        self.__timeout_thread.start()
        self.__is_collecting_data = True

    def clear(self):
        '''Clears all collected data.

        Raises:
        RuntimeWarning
        '''
        if self.__is_collecting_data:
            raise RuntimeWarning("Attempted to discard data while collecting data")

        self.__current_point = None
        self.__current_gaze_data = []
        self.__collected_points = defaultdict(list)

    def discard_data(self, screen_point):
        '''Removes the collected data for a specific calibration validation point.

        Args:
        screen_point: The calibration point to remove.

        Raises:
        RuntimeWarning
        '''
        if not self.__validation_mode:
            raise RuntimeWarning("Not in validation mode, no points to discard")
        if self.__is_collecting_data:
            raise RuntimeWarning("Attempted to discard data while collecting data")
        if screen_point not in self.__collected_points:
            raise RuntimeWarning("Attempt to discard non-collected point")
        del self.__collected_points[screen_point]

    def compute(self):
        '''Uses the collected data and tries to compute accuracy and precision values for all points.
        If the calculation is successful, the result is returned, and stored in the Result property
        of the CalibrationValidation object. If there is insufficient data to compute the results
        for a certain point that CalibrationValidationPoint will contain invalid data (NaN) for the
        results. Gaze data will still be untouched. If there is no valid data for any point, the
        average results of CalibrationValidationResult will be invalid (NaN) as well.

        Returns:
        An instance of @ref CalibrationValidationResult.
        '''
        if self.__is_collecting_data:
            raise RuntimeWarning("Still collecting data")

        points = defaultdict(list)
        accuracy_left_eye_all = []
        accuracy_right_eye_all = []
        precision_left_eye_all = []
        precision_right_eye_all = []
        precision_rms_left_eye_all = []
        precision_rms_right_eye_all = []

        for screen_point, samples in self.__collected_points.items():
            if len(samples) < self.__sample_count:
                # Timeout before collecting enough valid samples, no calculations to be done
                points[screen_point] += [CalibrationValidationPoint(
                    screen_point, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), True, samples)]
                continue

            stimuli_point = vectormath.calculate_normalized_point2_to_point3(
                self.__eyetracker.get_display_area(), screen_point)

            # Prepare data from samples
            gaze_origin_left_all = []
            gaze_origin_right_all = []
            gaze_point_left_all = []
            gaze_point_right_all = []
            direction_gaze_point_left_all = []
            direction_gaze_point_left_mean_all = []
            direction_gaze_point_right_all = []
            direction_gaze_point_right_mean_all = []

            for sample in samples:
                gaze_origin_left_all.append(
                    vectormath.Point3.from_list(sample.left_eye.gaze_origin.position_in_user_coordinates))
                gaze_origin_right_all.append(
                    vectormath.Point3.from_list(sample.right_eye.gaze_origin.position_in_user_coordinates))
                gaze_point_left_all.append(
                    vectormath.Point3.from_list(sample.left_eye.gaze_point.position_in_user_coordinates))
                gaze_point_right_all.append(
                    vectormath.Point3.from_list(sample.right_eye.gaze_point.position_in_user_coordinates))

            gaze_origin_left_mean = vectormath.calculate_mean_point(gaze_origin_left_all)
            gaze_origin_right_mean = vectormath.calculate_mean_point(gaze_origin_right_all)
            gaze_point_left_mean = vectormath.calculate_mean_point(gaze_point_left_all)
            gaze_point_right_mean = vectormath.calculate_mean_point(gaze_point_right_all)

            for sample in samples:
                gaze_origin_left = vectormath.Point3.from_list(
                    sample.left_eye.gaze_origin.position_in_user_coordinates)
                gaze_origin_right = vectormath.Point3.from_list(
                    sample.right_eye.gaze_origin.position_in_user_coordinates)
                gaze_point_left = vectormath.Point3.from_list(
                    sample.left_eye.gaze_point.position_in_user_coordinates)
                gaze_point_right = vectormath.Point3.from_list(
                    sample.right_eye.gaze_point.position_in_user_coordinates)
                direction_gaze_point_left_all.append(
                    vectormath.Vector3.from_points(gaze_origin_left, gaze_point_left).normalize())
                direction_gaze_point_left_mean_all.append(
                    vectormath.Vector3.from_points(gaze_origin_left, gaze_point_left_mean).normalize())
                direction_gaze_point_right_all.append(
                    vectormath.Vector3.from_points(gaze_origin_right, gaze_point_right).normalize())
                direction_gaze_point_right_mean_all.append(
                    vectormath.Vector3.from_points(gaze_origin_right, gaze_point_right_mean).normalize())

            # Accuracy calculations
            accuracy_left_eye = _calculate_eye_accuracy(gaze_origin_left_mean, gaze_point_left_mean, stimuli_point)
            accuracy_right_eye = _calculate_eye_accuracy(gaze_origin_right_mean, gaze_point_right_mean, stimuli_point)

            # Precision calculations
            precision_left_eye = _calculate_eye_precision(
                direction_gaze_point_left_all, direction_gaze_point_left_mean_all)
            precision_right_eye = _calculate_eye_precision(
                direction_gaze_point_right_all, direction_gaze_point_right_mean_all)

            # RMS precision calculations
            precision_rms_left_eye = _calculate_eye_precision_rms(direction_gaze_point_left_all)
            precision_rms_right_eye = _calculate_eye_precision_rms(direction_gaze_point_right_all)

            # Add a calibration validation point
            points[screen_point] += [CalibrationValidationPoint(
                accuracy_left_eye,
                accuracy_right_eye,
                precision_left_eye,
                precision_right_eye,
                precision_rms_left_eye,
                precision_rms_right_eye,
                False,  # no timeout
                screen_point,
                samples)]

            # Cache all calculations
            accuracy_left_eye_all.append(accuracy_left_eye)
            accuracy_right_eye_all.append(accuracy_right_eye)
            precision_left_eye_all.append(precision_left_eye)
            precision_right_eye_all.append(precision_right_eye)
            precision_rms_left_eye_all.append(precision_rms_left_eye)
            precision_rms_right_eye_all.append(precision_rms_right_eye)

        # Create a result
        num_points = len(accuracy_left_eye_all)
        if num_points > 0:
            accuracy_left_eye_average = sum(accuracy_left_eye_all) / num_points
            accuracy_right_eye_average = sum(accuracy_right_eye_all) / num_points
            precision_left_eye_average = sum(precision_left_eye_all) / num_points
            precision_right_eye_average = sum(precision_right_eye_all) / num_points
            precision_rms_left_eye_average = sum(precision_rms_left_eye_all) / num_points
            precision_rms_right_eye_average = sum(precision_rms_right_eye_all) / num_points
        else:
            accuracy_left_eye_average = float('nan')
            accuracy_right_eye_average = float('nan')
            precision_left_eye_average = float('nan')
            precision_right_eye_average = float('nan')
            precision_rms_left_eye_average = float('nan')
            precision_rms_right_eye_average = float('nan')

        result = CalibrationValidationResult(points,
                                             accuracy_left_eye_average,
                                             accuracy_right_eye_average,
                                             precision_left_eye_average,
                                             precision_right_eye_average,
                                             precision_rms_left_eye_average,
                                             precision_rms_right_eye_average)
        return result

    @property
    def is_collecting_data(self):
        '''Gets if data collecting is in progess.

        Returns:
        True if data collectin is in progress.
        '''
        return self.__is_collecting_data

    @property
    def is_validation_mode(self):
        '''Gets if in validation mode.

        Returns:
        True if in validation mode.
        '''
        return self.__validation_mode

    @property
    def sample_count(self):
        '''The number of samples to collect.
        '''
        return self.__sample_count
