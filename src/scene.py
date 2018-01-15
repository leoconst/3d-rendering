import itertools
import numpy as np
from enum import Enum

import shapes
from common import special_string


class Node(object):
    def __init__(self):
        self.children = set()


class Scene(object):

    def __init__(self, *meshes):
        chain = itertools.chain.from_iterable

        points = list(chain(mesh.points for mesh in meshes))
        self.static_points = np.array(points, dtype=np.float)

        triangles = list(chain(mesh.triangles for mesh in meshes))
        self.triangles = np.array(triangles, dtype=np.uint16)

    def __str__(self):
        start = f'<{self.__class__.__name__} static_points=['
        offset = len(start)

        point_strings = (np.array_str(point, precision=3, suppress_small=True)
                         for point in self.static_points)
        points = pretty_string(point_strings, offset)

        triangle_strings = (f'({i1},{i2},{i3})'
                            for i1, i2, i3 in self.triangles)
        triangles = pretty_string(triangle_strings, offset)

        return f'{start}{points}]\n{"triangles=[":>{offset}}{triangles}]>'

    def add_static_point(self, x, y, z):
        self.static_points = np.concatenate((self.static_points, [[x, y, z]]))


def pretty_string(strings, offset=0, max_line_length=79, sep=' '):
    current_line_len = offset
    margin = ' '*(offset)
    sep_len = len(sep)

    lines = [[]]
    current_line = lines[0]

    for string in strings:
        current_line_len += len(string)
        if current_line_len > max_line_length:
            current_line_len = offset + len(string)
            current_line = []
            lines.append(current_line)
        current_line_len += sep_len
        current_line.append(string)

    return ('\n' + margin).join(sep.join(line) for line in lines)


s = Scene(shapes.circle(1, 3))
print(s)
s.add_static_point(3, -2, 0)
print(s)
