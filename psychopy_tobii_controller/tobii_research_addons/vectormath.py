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


def _isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def _clamp(value, lower, upper):
    return max(lower, min(value, upper))


class Point2(object):
    '''Represents a 2D point.
    '''
    def __init__(self, x=0.0, y=0.0):
        self.__x = float(x)
        self.__y = float(y)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __eq__(self, other):
        return _isclose(self.x, other.x) and _isclose(self.y, other.y)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return "{0}({1:.3f}, {2:.3f})".format(self.__class__.__name__, self.x, self.y)

    @classmethod
    def from_list(cls, lst):
        x, y = map(float, lst)
        return cls(x, y)


class Point3(object):
    '''Represents a 3D point.
    '''
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.__x = float(x)
        self.__y = float(y)
        self.__z = float(z)

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def z(self):
        return self.__z

    def __add__(self, rhs):
        return Point3(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)

    def __sub__(self, rhs):
        return Point3(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z)

    def __mul__(self, rhs):
        return Point3(self.x * float(rhs), self.y * float(rhs), self.z * float(rhs))

    def __eq__(self, other):
        return _isclose(self.x, other.x) and _isclose(self.y, other.y) and _isclose(self.z, other.z)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '{0}({1:.3f}, {2:.3f}, {3:.3f})'.format(self.__class__.__name__, self.x, self.y, self.z)

    def distance(self, other_point):
        return math.sqrt((other_point.x - self.x) ** 2 + (other_point.y - self.y) ** 2 + (other_point.z - self.z) ** 2)

    @classmethod
    def from_list(cls, lst):
        x, y, z = map(float, lst)
        return cls(x, y, z)


class Vector3(Point3):
    '''Represents a 3D vector.
    '''
    def __init__(self, x=0.0, y=0.0, z=0.0):
        super(Vector3, self).__init__(x, y, z)

    def __add__(self, rhs):
        if isinstance(rhs, Point3):
            return Vector3(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)
        elif type(rhs) in [float, int]:
            return Vector3(self.x + float(rhs), self.y + float(rhs), self.z + float(rhs))
        else:
            raise TypeError

    def __sub__(self, rhs):
        if isinstance(rhs, Point3):
            return Vector3(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z)
        elif type(rhs) in [float, int]:
            return Vector3(self.x - float(rhs), self.y - float(rhs), self.z - float(rhs))
        else:
            raise TypeError

    def __mul__(self, rhs):
        if type(rhs) in [float, int]:
            return Vector3(self.x * float(rhs), self.y * float(rhs), self.z * float(rhs))
        else:
            # Do not allow dot or cross products with multiplication operator due to ambiguity issues
            raise TypeError

    def dot(self, vector3):
        '''Dot product.'''
        return self.x * vector3.x + self.y * vector3.y + self.z * vector3.z

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        return self * (1.0 / self.magnitude())

    def angle(self, vector3):
        '''Return the angle between two vectors in degrees.'''
        tmp = self.dot(vector3) / (self.magnitude() * vector3.magnitude())
        return math.degrees(math.acos(_clamp(tmp, -1.0, 1.0)))

    @classmethod
    def from_points(cls, from_point, to_point):
        if isinstance(from_point, Point3) and isinstance(to_point, Point3):
            displacement = to_point - from_point
            return cls(displacement.x, displacement.y, displacement.z)
        raise TypeError


def calculate_normalized_point2_to_point3(display_area, target_point):
    '''Get the 3D gaze point representation based on the normalized 2D point and the @ref GazeData information.

    Args:
    display_area: @ref DisplayArea object.
    target_point: Screen point as a normalized @ref Point2 object.

    Returns:
    The @ref Point3 gaze point.
    '''
    display_area_top_right = Point3.from_list(display_area.top_right)
    display_area_top_left = Point3.from_list(display_area.top_left)
    display_area_bottom_left = Point3.from_list(display_area.bottom_left)
    dx = (display_area_top_right - display_area_top_left) * target_point.x
    dy = (display_area_bottom_left - display_area_top_left) * target_point.y
    return display_area_top_left + dx + dy


def calculate_mean_point(points):
    '''Calculate an average point from a set of points.

    Args:
    points: An iterable container of @ref Point3 objects.

    Returns:
    The mean point as a @ref Point3 object.
    '''
    average_point = Point3()
    for point in points:
        average_point = average_point + point
    average_point = average_point * (1.0 / len(points))
    return average_point
