"""
Shape construction functions.  All functions should return 2 sequences
(the first to initialize points, the second to initialize triangles).

The points and triangles (shape info) returned should be treated as
having an origin at (0, 0, 0), ideally its volumetric center.
"""

from typing import Iterator, Sequence, Tuple
Coords = Iterator[Tuple[float, float]]

from collections import namedtuple
from math import cos, pi, sin, tau


SEGMENTS_DEFAULT = 16


SHAPE_FUNCTIONS = {}


def register_shape(function):
    SHAPE_FUNCTIONS[function.__name__] = function
    return function


class Geometry(namedtuple('GeometryBase', 'points, triangles')):

    def __new__(cls, points, triangles):
        assert all(len(point) == 3 for point in points)
        assert all(len(triangle) == 3 for triangle in triangles)

        return super().__new__(cls, tuple(points), tuple(triangles))


@register_shape
def cube(size: float) -> Geometry:
    """ Axis-aligned cuboid with identical width, height and length.
    """
    return cuboid(size, size, size)


CUBOID = [
    (+.5, +.5, +.5), (+.5, +.5, -.5), (+.5, -.5, +.5), (+.5, -.5, -.5),
    (-.5, +.5, +.5), (-.5, +.5, -.5), (-.5, -.5, +.5), (-.5, -.5, -.5),
], [
    (0, 1, 4), (0, 2, 1), (0, 4, 2), (3, 1, 2), (3, 2, 7), (3, 7, 1),
    (5, 1, 7), (5, 4, 1), (5, 7, 4), (6, 2, 4), (6, 4, 7), (6, 7, 2),
]


@register_shape
def cuboid(x: float, y: float, z: float) -> Geometry:
    """ Axis-aligned cuboid.
    """
    x /= 2
    y /= 2
    z /= 2

    return [
        (+x, +y, +z), (+x, +y, -z), (+x, -y, +z), (+x, -y, -z),
        (-x, +y, +z), (-x, +y, -z), (-x, -y, +z), (-x, -y, -z),
    ], [
        (0, 1, 4), (0, 2, 1), (0, 4, 2), (3, 1, 2), (3, 2, 7), (3, 7, 1),
        (5, 1, 7), (5, 4, 1), (5, 7, 4), (6, 2, 4), (6, 4, 7), (6, 7, 2),
    ]


@register_shape
def pyramid(base_radius: float, base_sides: int, height: float) -> Geometry:
    """ 
    """
    lower = -height / 3
    base_coords = _circle_coords(base_radius, base_sides)

    return [
        (0, height + lower, 0), *((x, lower, y) for x, y in base_coords)
    ], [
        *((index, 0, index + 1) for index in range(1, base_sides - 1))
        # Base triangles missing
    ]


@register_shape
def square_based_pyramid(base_width: float, height: float) -> Geometry:
    """ 
    """
    base = base_width / 2
    height /= 2

    return Geometry([
        (base, -height, base), (base, -height, -base), (-base, -height, base),
        (-base, -height, -base), (0, height, 0)
    ], [
        (0, 2, 1), (3, 1, 2), (4, 0, 1), (4, 1, 3), (4, 3, 2), (4, 2, 0)
    ])


def _points_2d_to_3d(coords):
    return ((x, y, 0.0) for x, y in coords)


def _polygon_coords(sides: int, side_length: float) -> Coords:
    """ Polygon perimeter coordinates.
    """
    if sides < 2:
        raise ValueError('sides should be an integer greater than 1')

    angle_offset = pi + pi / sides
    side_length /= 2

    for side_index in range(sides):
        angle = angle_offset + side_index*tau / sides
        radius = side_length / sin(pi / sides)
        yield radius*sin(angle), radius*cos(angle)


@register_shape
def polygon(sides: int, side_length: float) -> Geometry:
    """ x-y aligned polygon.
    """
    coords = _polygon_coords(sides, side_length)

    return Geometry(
        tuple(_points_2d_to_3d(coords)),
        tuple((0, index, index + 1) for index in range(1, sides - 1))
    )


def _circle_coords(radius: float, sides: int) -> Coords:
    """ Circle perimeter coordinates.
    """
    if sides < 2:
        raise ValueError('sides should be an integer over 1')

    for side_index in range(sides):
        angle = side_index*tau / sides
        yield radius*sin(angle), radius*cos(angle)


@register_shape
def circle(radius: float, sides: int = 16) -> Geometry:
    """ x-y aligned circle.
    """
    coords = _circle_coords(radius, sides)

    return Geometry(
        tuple(_points_2d_to_3d(coords)),
        tuple((0, index, index + 1) for index in range(1, sides - 1))
    )


@register_shape
def centered_circle(radius: float, sides: int = 16) -> Geometry:
    """ x-y aligned circle with all triangles attached to a centre
    point.
    """
    coords = _circle_coords(radius, sides)

    return Geometry(
        [(0.0, 0.0, 0.0)] + [(x, y, 0.0) for x, y in coords],
        [(0, index, index + 1) for index in range(1, sides)] + [(0, sides, 1)]
    )


@register_shape
def cylinder(radius: float, length: float, segments: int = 16):
    """ 
    """
    length /= 2
    tuple(_circle_coords(radius, segments))


@register_shape
def ring(radius, width, thickness=0, segments: int = 16) -> Geometry:
    """ 
    """


@register_shape
def sphere(radius, segments: int = 16) -> Geometry:
    """ Axis-aligned spheroid with identical width, height and length.
    """
    return spheroid(radius, radius, radius, segments)


@register_shape
def spheroid(x, y, z, segments: int = 16) -> Geometry:
    """ Axis-aligned spheroid.
    """


if __name__ == '__main__':
    from pprint import pprint
    pprint(SHAPE_FUNCTIONS)
    pprint(centered_circle(1, 5))
