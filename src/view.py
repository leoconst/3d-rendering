"""
View3D Widget.
"""

import attr
from kivy.app import App
from kivy.uix.stencilview import StencilView


@attr.s(slots=True)
class Point(object):
    """ A mutable point in 3-D space.
    """

    x: float = attr.ib()
    y: float = attr.ib()
    z: float = attr.ib()

    def __str__(self) -> str:
        return format(self, '.3f')

    def __format__(self, format_spec) -> str:
        fs = format_spec
        class_name = self.__class__.__name__
        return f'{class_name}({self.x:{fs}}, {self.y:{fs}}, {self.z:{fs}})'

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

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


class View3D(StencilView):
    """ An object for viewing 3-D geometry.
    """

    def __init__(self, geometry=None, position=(0., 0., 0.),
                 rotation=(0., 0., 0.), **widget_args):
        super().__init__(**widget_args)
        self.geometry = geometry
        self.position = position
        self.rotation = rotation


def main():
    class MyApp(App):
        def build(self):
            return View3D()
    MyApp().run()


if __name__ == '__main__':
    main()
