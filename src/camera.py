"""

"""

from math import degrees

from kivy.core.window import Window
from kivy.graphics import Color, Line, Triangle, Rectangle
from kivy.properties import (BooleanProperty, BoundedNumericProperty,
    ObjectProperty, ReferenceListProperty)

from kivy.uix.stencilview import StencilView
from kivy.uix.gridlayout import GridLayout

import shapes
from controls import set_cursor_position
from common import special_string, next_randint
from geometry import CameraLogic, PhysicsMesh, Mesh, RGBA


def _center_cursor(window=Window):
    """ Set the cursor to the center of window.
    """
    center_x = window.left + window.width // 2
    center_y = window.top + window.height // 2
    set_cursor_position(center_x, center_y)


class Camera3D(CameraLogic, StencilView):
    """ 
    """

    # When True, display debug information.
    show_debug = BooleanProperty(False)

    # When True rotate the camera through mouse input.
    mouse_control = BooleanProperty(False)

    drag_sensitivity = BoundedNumericProperty(4.0, min=1.0, max=10.0)

    mouse_sensitivity = BoundedNumericProperty(2.0, min=1.0, max=10.0)

    clear_r = BoundedNumericProperty(1.0, min=0.0, max=1.0)
    clear_g = BoundedNumericProperty(1.0, min=0.0, max=1.0)
    clear_b = BoundedNumericProperty(1.0, min=0.0, max=1.0)

    clear_color = ReferenceListProperty(clear_r, clear_g, clear_b)

    debug_label = ObjectProperty(None)

    _mouse_controlled = set()
    _last_mouse_controlled = None

    def __init__(self, position=(0, 0, 0), heading=(0, 0, 0), meshes=(),
                 fov=100, **keywords):
        """ 
        """
        StencilView.__init__(self, **keywords)
        CameraLogic.__init__(self, position, heading, meshes, fov)

    def __str__(self):
        angles = (self.angle_x, self.angle_y, self.angle_z)
        heading = tuple(f'{degrees(angle):.2f}' for angle in angles)
        return special_string(self, position=self.position, heading=heading)

    def pixel_rotate(self, x, y, radians_per_pixel):
        """ 
        """
        x *= radians_per_pixel
        y *= -radians_per_pixel
        self.rotate(y, x, 0)

    def _on_bound_mouse_move(self, win, mouse_pos):
        x, y = mouse_pos[0], mouse_pos[1] - 1
        if (x, y) != win.center:
            center_x = win.width // 2
            center_y = win.height // 2
            x, y = center_x - x, center_y - y
            self.pixel_rotate(x, y, self.mouse_sensitivity / 1000)
            _center_cursor()

    def enter_mouse_control(self):
        """ 
        """
        _center_cursor()
        self._mouse_controlled.add(self)
        self._last_mouse_controlled = self
        Window.bind(mouse_pos=self._on_bound_mouse_move)
        if self._mouse_controlled:
            Window.show_cursor = False
            Window.grab_mouse()

    def exit_mouse_control(self):
        """ 
        """
        Window.unbind(mouse_pos=self._on_bound_mouse_move)
        self._mouse_controlled.remove(self)
        if not self._mouse_controlled:
            Window.ungrab_mouse()
            Window.show_cursor = True

    def on_mouse_control(self, view, mouse_control):
        """ 
        """
        if mouse_control:
            self.enter_mouse_control()
        else:
            self.exit_mouse_control()

    def on_touch_down(self, touch):
        if self.mouse_control and touch.button == 'left':
            self.parent.parent.notify(f'{self}: {touch.x:.5}, {touch.y:.5}')

    def on_touch_up(self, touch):
        if touch == touch.ud.get('drag', None):
            del touch.ud['drag']
            return True
        if touch.button == 'right' and self._last_mouse_controlled:
            self._last_mouse_controlled.mouse_control = False
            return True
        if self.collide_point(touch.x, touch.y) and touch.button == 'left':
            self.mouse_control = True

    def on_touch_move(self, touch):
        if self.collide_point(touch.x, touch.y):
            touch.ud['drag'] = touch
            self.pixel_rotate(touch.dx, touch.dy, self.drag_sensitivity / 1000)

    @staticmethod
    def draw_triangle(x1: float, y1: float, x2: float,
                      y2: float, x3: float, y3: float):
        """ 
        """
        Triangle(points=(x1, y1, x2, y2, x3, y3))
        # Line(points=(x1, y1, x2, y2, x3, y3), close=True)

    def _debug_instructions(self):
        Color(0.0, 0.0, 0.0, 1.0)
        Line(rectangle=(self.x + 1.5, self.y + 1.5, self.width - 3,
                        self.height - 3))

    def draw_frame(self):
        self.canvas.clear()
        with self.canvas:
            for mesh in sorted(self.meshes, key=self.distance_to_mesh,
                               reverse=True):
                Color(*mesh.color)
                self.draw_mesh(mesh)

            if self.show_debug:
                self._debug_instructions()


class CameraGrid(GridLayout):
    """ A grid of Camera Widgets.
    """

    def __init__(self, meshes=(), **kwargs):
        super().__init__(**kwargs)

        self.meshes = set(meshes)
        self.load_meshes_initial()

    def __iter__(self) -> iter:
        return iter(self.children)

    def add_widget(self, widget):
        """ Add widget if it is a Camera3D, else raise a
        ValueError.
        """
        if not isinstance(widget, Camera3D):
            raise TypeError('Can only add Camera3D widgets.')

        widget.meshes = self.meshes
        super().add_widget(widget)

    def load_meshes_initial(self):
        self.load_meshes_1()
        self.load_meshes_4()

    def load_meshes_1(self):
        cube = PhysicsMesh(shapes.cube(10000), (10000, -2000, 40000),
                           color=(0.0, 0.4, 0.8))
        cube_2 = PhysicsMesh(shapes.cube(1), (1, -0.2, 4),
                             color=(0.0, 1.0, 0.0))
        cuboid = PhysicsMesh(shapes.cuboid(0.8, 1.8, 0.2), (-2, 0.3, 5),
                             color=(0.0, 0.0, 0.0))
        pyramid = PhysicsMesh(shapes.square_based_pyramid(2, 2), (-0.5, -1, 6),
                              color=(1.0, 0.0, 0.0))
        triangle = PhysicsMesh.from_raw(
            [(1, 1, 6), (2, 1, 6), (1, 2, 6)], [(0, 1, 2)])

        cube.velocity = (-100, 0, 0)
        cube_2.velocity = (0.03, 0, 0)
        pyramid.velocity = (0, 0, 0.1)
        triangle.acceleration = (0, -0.01, 0)

        self.meshes.update({
            cube,
            cube_2,
            cuboid,
            pyramid,
            triangle,
        })

        self.meshes.add(PhysicsMesh(shapes.cube(0.3), (0, 0, 5),
                                    color=(0.9, 0.8, 0.8)))

    def load_meshes_2(self):
        cube = PhysicsMesh(shapes.cube(0.2), (0, 0, 4))
        cube.velocity = (0, 10, -1.5)
        cube.acceleration = (0, -9.81, 0)
        self.meshes.add(cube)

    def load_meshes_3(self):
        sides = next_randint(3, 12)
        self.meshes.add(Mesh(shapes.polygon(sides, 0.2), (0, 0, 3)))

    def load_meshes_4(self):
        def add_circle(rad, sides, z, func=shapes.circle):
            self.meshes.add(Mesh(func(rad, sides), (0, 0, z),
                color=RGBA.random(0.5)))
        add_circle(1, 64, 4.1)
        add_circle(0.8, 12, 4)
        add_circle(0.6, 8, 3.9)
        add_circle(0.4, 5, 3.8, shapes.centered_circle)
        add_circle(0.2, 3, 3.7)

    def load_meshes_5(self):
        cuboid = PhysicsMesh(shapes.cuboid(2, 2, 1), (0, 0, 5))
        cuboid.velocity = (0, 0, -0.2)
        self.meshes.add(cuboid)

    def load_meshes_6(self):
        def add_cube(x, y, z):
            self.meshes.add(Mesh(shapes.cube(1), (x, y, z)))
        add_cube(5, 0, 0)
        add_cube(-5, 0, 0)
        add_cube(0, 5, 0)
        add_cube(0, -5, 0)
        add_cube(0, 0, 5)
        add_cube(0, 0, -5)

    def load_meshes_7(self):
        pass

    def load_meshes_8(self):
        pass

    def load_meshes_9(self):
        pass

    def draw_frame(self):
        """ Draw frames for each child view.
        """
        for view in self:
            view.draw_frame()
