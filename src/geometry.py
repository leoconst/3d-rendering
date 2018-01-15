"""
Contains the Mesh class and its component classes.
"""

from typing import (FrozenSet, Iterable, Optional,
    NamedTuple, Sequence, Set, Tuple, Union)
Key = Union[int, slice]
Aliases = Union[str, Sequence[str]]
Point = TripleFloat = Tuple[float, float, float]
Points = Sequence[Point]
Triangles = Sequence[Tuple[int, int, int]]

import operator
import functools
from array import array as Array
from itertools import chain, combinations, islice
from math import cos, degrees, radians, hypot, sin, tan
from numbers import Real
from random import random
from statistics import mean

import attr

import shapes
from common import represent, sequence_str


def lines(triangles: Triangles) -> Set[FrozenSet[int]]:
    """ Return the lines.
    """
    return {frozenset(line) for triangle in triangles for line in
        combinations(triangle, 2)}


class RGBA(NamedTuple):
    """ Color in RGBA format.
    """

    r: float = 0.0
    g: float = 0.0
    b: float = 0.0
    a: float = 1.0

    @classmethod
    def random(cls, a=1.0):
        return cls(random(), random(), random(), a)


class Arrays(object):
    """ Wrapper around an arbitrary number of ``array.array`` objects.
    """

    int8 = 'b'
    uint8 = 'B'
    int16 = 'h'
    uint16 = 'H'

    float32 = 'f'
    float64 = 'd' 

    def __init__(self, array_count: int, typecode: str, items=()):
        if array_count < 2:
            raise ValueError(f'array_count below minimum of 2: {array_count}')

        self.array_count = array_count
        self.typecode = typecode

        self.arrays = tuple(Array(typecode) for _ in range(array_count))
        self.extend(items)

    def __repr__(self) -> str:
        return represent(self, self.array_count, self.typecode, list(self))

    def __str__(self) -> str:
        items = sequence_str(self)
        class_name = self.__class__.__name__
        return (f'{class_name}({self.array_count!r},'
                f'{self.typecode!r}, {items})')

    def __len__(self) -> int:
        return len(self.arrays[0])

    def __getitem__(self, key):
        items = (array[key] for array in self.arrays)

        if isinstance(key, int):
            return tuple(items)
        else:
            return self.__class__(self._first, self.typecode, zip(*items))

    def __setitem__(self, key: Key, value: Sequence[Real]) -> None:
        for array, part in zip(self.arrays, value):
            array[key] = part

    def __delitem__(self, key: Key) -> None:
        for array in self.arrays:
            del array[key]

    def __iter__(self) -> iter:
        return zip(*self.arrays)

    def append(self, item) -> None:
        """ Append item to the end of self.
        """
        if len(item) != self.array_count:
            raise ValueError(
                f'item should have {self.array_count} values: {item}')

        for array, part in zip(self.arrays, item):
            array.append(part)

    def extend(self, items) -> None:
        """ Append all items to the end of self.
        """
        items = tuple(chain.from_iterable(items))
        if len(items) % self.array_count:
            raise ValueError(f'Items should be of length {self.array_count}.')

        for index, array in enumerate(self.arrays):
            array.extend(islice(items, index, None, self.array_count))


class TriangleArray(Arrays):
    """ 
    """

    def __init__(self, triangles: Triangles = ()) -> None:
        super().__init__(3, Arrays.uint16, triangles)

    def __repr__(self) -> str:
        return represent(self, list(self))

    def __add__(self, other) -> 'TriangleArray':
        if isinstance(other, int):
            return self.__class__(
                (i1 + other, i2 + other, i3 + other) for i1, i2, i3 in self)
        elif isinstance(other, self.__class__):
            offset = len(self)
            return self.__class__(chain(self, other + offset))
        return NotImplemented


class _Shape(object):

    def shape_func(self, wrapped):
        functools.wraps(wrapped)
        def wrapper(position, rotation, *, color=None):
            shape_info = wrapped()
            return self.__class__()
        return wrapped

    def __init__(self, owner):
        self.owner = owner

        for name, function in shapes.SHAPE_FUNCTIONS.items():
            setattr(self, name, self.shape_func(function))


class Mesh(object):
    """ A group of points connected as triangles.
    """

    __slots__ = ('color', 'points', 'triangles')

    def __init__(self, shape_info, position: TripleFloat,
                 rotation=(0, 0, 0), *, color: Optional[TripleFloat] = None):
        point_info, triangle_info = shape_info

        self.points = Arrays(3, Arrays.float64, point_info)
        self.move_by(*position)

        self.triangles = TriangleArray(triangle_info)

        self.color = RGBA.random() if color is None else RGBA(*color)

    @classmethod
    def from_raw(cls, points: Points = (), triangles: Triangles = (),
                 **keywords):
        return cls((points, triangles), (0.0, 0.0, 0.0), **keywords)

    @classmethod
    def from_path(cls, path):
        mesh = cls.from_raw()
        mesh.load(path)
        return mesh

    def __repr__(self) -> str:
        shape_info = (list(self.points), list(self.triangles))
        return represent(self, shape_info, color=tuple(self.color))

    @property
    def center(self) -> TripleFloat:
        """ Return the mean of the points as a 3-tuple of floats.
        """
        return tuple(map(mean, self.arrays))

    def move_by(self, x: float, y: float, z: float) -> None:
        """ Move self by x, y, and z.
        """
        for index, (point_x, point_y, point_z) in enumerate(self.points):
            self.points[index] = (point_x + x, point_y + y, point_z + z)

    def load(self, path):
        """ Load from a mesh file.
        """
        with open(path) as file:
            source = file.read().strip()

        try:
            point_section, triangle_section = source.split('\n\n')
        except ValueError:
            raise SyntaxError('There should be a single blank line.')

        self.points.extend(map(float, point_string.strip().split())
            for point_string in point_section.split('\n'))
        self.triangles.extend(map(int, triangle_string.strip().split())
            for triangle_string in triangle_section.split('\n'))

    def save(self, path):
        """ Save to a mesh file.
        """
        with open(path, 'w') as file:

            for x, y, z in self.points:
                file.write(f'{x} {y} {z}\n')

            file.write('\n')

            for i1, i2, i3 in self.triangles:
                file.write(f'{i1} {i2} {i3}\n')


Mesh.shape = _Shape(Mesh)


class Physics(object):
    """ 
    """

    def __init__(self, velocity=None, acceleration=None, mass=None):
        """ 
        """
        accel = acceleration

        super().__init__(shape_info, position, color=color)

        self.velocity = FixedVector(0, 0, 0) if velocity is None else velocity
        self.acceleration = FixedVector(0, 0, 0) if accel is None else accel

        self.mass = mass

    def move_by(self, x: float, y: float, z: float):
        """ Move self by x, y, and z.
        """
        raise NotImplementedError

    def rotate(self, x: float, y: float, z: float, point: TripleFloat=None):
        """ Rotate self around point by the angles x, y, and z.
        """
        raise NotImplementedError

    def simulate(self, time: float):
        """ 
        """
        acceleration_x, acceleration_y, acceleration_z = self.acceleration
        velocity_x, velocity_y, velocity_z = self.velocity

        # s = u*t + 0.5*a*t*t
        delta_x = velocity_x*time + 0.5*acceleration_x*time*time
        delta_y = velocity_y*time + 0.5*acceleration_y*time*time
        delta_z = velocity_z*time + 0.5*acceleration_z*time*time

        self.move_by(delta_x, delta_y, delta_z)

        # v = u + a*t
        velocity_x += acceleration_x*time
        velocity_y += acceleration_y*time
        velocity_z += acceleration_z*time

        self.velocity = velocity_x, velocity_y, velocity_z


class PhysicsMesh(Mesh, Physics):
    """ A 3D shape with physics simulation functionality.
    """

    def __init__(self, shape_info, position, *, color=None,
                 velocity=None, acceleration=None, mass=None):
        """ 
        """
        super().__init__(shape_info, position, color=color)

        self.velocity = (0, 0, 0) or velocity
        self.acceleration = (0, 0, 0) or acceleration

        self.mass = mass #or self.volume


@attr.s(slots=True)
class Point(object):
    """ A 3-D point in space.
    """

    x: float = attr.ib(0.0)
    y: float = attr.ib(0.0)
    z: float = attr.ib(0.0)

    def __str__(self) -> str:
        return format(self, '.2f')

    def __format__(self, format_spec) -> str:
        fs = format_spec
        class_name = self.__class__.__name__
        return f'{class_name}({self.x:{fs}}, {self.y:{fs}}, {self.z:{fs}})'

    def __bool__(self) -> bool:
        return True

    def __len__(self) -> int:
        return 3

    def __iter__(self) -> iter:
        return iter((self.x, self.y, self.z))

    def __set__(self, instance: object, value) -> None:
        self.x, self.y, self.z = value

    def __add__(self, other) -> 'Point':
        x, y, z = other
        return self.__class__(self.x + x, self.y + y, self.z + z)

    def __sub__(self, other) -> 'Point':
        x, y, z = other
        return self.__class__(self.x - x, self.y - y, self.z - z)

    __radd__ = __add__
    __rsub__ = __sub__

    def __iadd__(self, other):
        x, y, z = other
        self.x += x
        self.y += y
        self.z += z
        return self

    def __isub__(self, other):
        x, y, z = other
        self.x -= x
        self.y -= y
        self.z -= z
        return self

    def distance_to(self, x: float, y: float, z: float) -> float:
        x += self.x
        y += self.y
        z += self.z
        return (x*x + y*y + z*z)**0.5


class StaticCameraLogic(object):
    """ 
    """

    def __init__(self, meshes: Iterable=(), fov: int=100, width: int=1,
                 height: int=1):
        """ 
        """
        self.width = width
        self.height = height

        self.meshes = set(meshes)

        self.fov = radians(fov)
        self.pro_depth = 0.01
        self.pro_width = 2*self.pro_depth*tan(self.fov / 2)

    def __repr__(self) -> str:
        return represent(
            self, self.meshes, self.width, self.height, degrees(self.fov))

    def project_point(self, x: float, y: float, z: float):
        """ 
        """
        if z > 0:
            num = (self.width*self.pro_depth) / (z*self.pro_width)
            return (
                self.x + (self.width / 2) + x*num,
                self.y + (self.height / 2) + y*num
            )
        else:
            return 0, 0


class CameraLogic(StaticCameraLogic, Physics):
    """ TODO. """

    def __init__(self, position, rotation, *args, **keywords):
        super().__init__(*args, **keywords)

        self.position = self._original_position = Point(*position)
        self._original_rotation = rotation
        self.angle_x, self.angle_y, self.angle_z = rotation

    def __repr__(self) -> str:
        return represent(
            self, self.position, self.rotation, self.meshes, self.width,
            self.height, degrees(self.fov))

    def rotate(self, x, y, z):
        self.angle_x += x
        self.angle_y += y
        self.angle_z += z

    def reset(self, *, position: bool = True, rotation: bool = True):
        """ Reset the camera to its original position and rotation.
        """
        if position:
            self.position = self._original_position
        if rotation:
            self.angle_x, self.angle_y, self.angle_z = self._original_rotation

    def resolve_point(self, x, y, z):
        # Point translations
        x -= self.position.x
        y -= self.position.y
        z -= self.position.z

        sin_x = sin(self.angle_x)
        cos_x = cos(self.angle_x)
        sin_y = sin(self.angle_y)
        cos_y = cos(self.angle_y)
        sin_z = sin(self.angle_z)
        cos_z = cos(self.angle_z)

        # y rotation
        z1 = z*cos_y - x*sin_y
        x1 = z*sin_y + x*cos_y
        # x rotation
        y1 = y*cos_x - z1*sin_x
        z2 = y*sin_x + z1*cos_x
        # z rotation
        x2 = x1*cos_z - y1*sin_z
        y2 = x1*sin_z + y1*cos_z

        return self.project_point(x2, y2, z2)

    def draw_triangle(self, x1, y1, x2, y2, x3, y3):
        raise NotImplementedError('Implement a draw_triangle method.')

    def draw_mesh(self, mesh):
        point_buffer = tuple(
            self.resolve_point(x, y, z) for x, y, z in mesh.points)

        for index_1, index_2, index_3 in mesh.triangles:
            x1, y1 = point_buffer[index_1]
            x2, y2 = point_buffer[index_2]
            x3, y3 = point_buffer[index_3]
            self.draw_triangle(x1, y1, x2, y2, x3, y3)

    def distance_to_mesh(self, mesh: Mesh) -> float:
        return self.position.distance_to(*mesh.points[0])
