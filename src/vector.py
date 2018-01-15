"""
"""

from math import atan, cos, hypot, radians as degrees_to_radians, sin
from numbers import Real

import attr


def real_to_float(value):
    return 1.0*value


@attr.s
class Vector2D(object):
    """ A two-dimensional vector.

    >>> v = Vector2D(3, 4)
    >>> repr(v)
    'Vector2D(x=3.0, y=4.0)'
    >>> v.length
    5.0
    >>> v + (-2.1, 53)
    Vector2D(x=0.9, y=57.0)
    >>> v.rotate_clockwise(90)
    Vector2D(x=4.0, y=-3.0)
    """

    x = attr.ib(convert=real_to_float)
    y = attr.ib(convert=real_to_float)

    @property
    def length(self):
        return hypot(self.x, self.y)

    @length.setter
    def length(self, length):
        try:
            length_ratio = length / self.length
        except ZeroDivisionError:
            raise ValueError('Cannot change length value of zero vector.')

        self.x *= length_ratio
        self.y *= length_ratio

        assert length == self.length, 'Vector2D length calculation incorrect.'

    def __set__(self, instance, value):
        self.x, self.y = map(real_to_float, value)

    def __iter__(self):
        yield self.x
        yield self.y

    def __add__(self, other):
        try:
            x, y = other
        except ValueError:
            return NotImplemented
        return self.__class__(self.x + x, self.y + y)

    __radd__ = __add__

    def __sub__(self, other):
        try:
            x, y = other
        except ValueError:
            return NotImplemented
        return self.__class__(self.x - x, self.y - y)

    def __mul__(self, other):
        if not isinstance(other, Real):
            return NotImplemented
        return self.__class__(self.x*other, self.y*other)

    __rmul__ = __mul__

    def __matmul__(self, other):
        try:
            x, y = other
        except ValueError:
            return NotImplemented
        return self.x*x + self.y*y

    def __truediv__(self, other):
        return self*(1 / other)

    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    def rotate_clockwise(self, angle):
        """ Rotate the vector clockwise by the given angle in degrees.

        >>> vector = Vector2D(3, 4)
        >>> vector.rotate_clockwise(90)
        >>> vector
        Vector2D(x=4.0, y=-3.0)
        """
        angle = degrees_to_radians(angle)
        current_angle = atan(self.x / self.y)
        angle += current_angle

        length = self.length
        self.x = length*sin(angle)
        self.y = length*cos(angle)

    def rotate_anti_clockwise(self, angle):
        """ Rotate the vector anti-clockwise by the given angle in
        degrees.

        >>> vector = Vector2D(3, 4)
        >>> vector.rotate_clockwise(90)
        >>> vector
        Vector2D(x=-4.0, y=3.0)
        """
        self.rotate_clockwise(-angle)
