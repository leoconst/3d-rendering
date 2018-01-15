"""
Program for rudimentary three dimensional rendering and editing.
Latest refactor of my 3D Rendering project using Kivy for GUI back-end.

Features:
- Camera3D widget that displays 3D shapes
- Console widget that executes functions from text input
- DebugOverlay widget for outputting debug text information
- ConfigMenu widget with tabs including settings access
- Key bindings that can be rebound in the settings tab of the menu

TODO:
- Complete Camera3D widget
- Complete Console widget
- Complete DebugOverlay widget
- Add ConfigMenu widget
- Implement key binding system

Started: April 9th 2017
"""

from typing import Optional, Tuple

import re
from collections import deque
from functools import partial
from math import degrees
from random import random
from statistics import mean

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')
Config.set('kivy', 'exit_on_escape', False)

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Keyboard, Window
from kivy.logger import Logger
from kivy.properties import (BooleanProperty, BoundedNumericProperty,
    ObjectProperty, NumericProperty)

from kivy.uix.behaviors.focus import FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from camera import Camera3D, CameraGrid
from common import TITLE, special_string
from console import Console
from controls import shortcut, ShortcutBehavior
from geometry import Mesh, Physics, PhysicsMesh, RGBA


@shortcut('ctrl+alt+f11')
def toggle_border():
    """ Toggle the window border if it's not in a fullscreen mode.
    """
    if not Window.fullscreen:
        Window.borderless = not Window.borderless


@shortcut('f11')
@shortcut('alt+f11', mode=True)
def toggle_fullscreen(window=Window, *, mode='auto'):
    """ Toggle the fullscreen mode between mode and off.
    """
    # if window.borderless:
    #     window.maximize()
    #     window.grab_mouse()
    # else:
    window.fullscreen = False if window.fullscreen else mode


class RenderingApp(App):

    setting_key = 283

    def build(self):

        self.icon = 'data/images/icon.png'
        self.title = TITLE
        self.use_kivy_settings = False

        Window.clearcolor = (0.8, 0.9, 1.0, 1.0)
        Window.bind(on_dropfile=self._on_dropfile, focus=self._on_focus)

        return WidgetManager()

    @staticmethod
    def _on_dropfile(win, path: str):
        Logger.info(f'File Dropped: path: {path}, position: {win.mouse_pos}')

    @staticmethod
    def _on_focus(win, focus):
        pass

    def _on_keyboard_settings(self, window, key, *_):
        default_setting_key = 282
        if key == self.setting_key:
            key = default_setting_key
        elif key == default_setting_key:
            key = self.setting_key
        super()._on_keyboard_settings(window, key)


class ShownBehaviour(object):
    """ Widget mix-in to provide show and hide functionality.
    """

    __hidden = set()

    shown = BooleanProperty(True)

    @classmethod
    def on_shown(cls, instance, shown):
        if shown:
            instance._previous_parent.add_widget(instance)
            cls.__hidden.remove(instance)
        else:
            # Add instance to cls.__hidden to avoid garbage collection.
            cls.__hidden.add(instance)
            instance._previous_parent = instance.parent
            instance._previous_parent.remove_widget(instance)


class WidgetManager(ShortcutBehavior, FloatLayout):
    """ 
    """

    frame_rate = NumericProperty(60)

    show_debug = BooleanProperty(False)

    # Multiplier for physics simulation.
    time_scale = NumericProperty(1)

    # CameraGrid widget containing child cameras.
    cameras = ObjectProperty(None)

    def __init__(self, **kwargs):
        """ 
        """
        super().__init__(**kwargs)

        self.focus = True
        Clock.schedule_interval(self.update, 1 / self.frame_rate)

        self.add_shortcut('`', self.toggle_console)
        self.add_shortcut('f12', self.toggle_debug)

        self.add_shortcut('0', self.cameras.meshes.clear)
        self.add_shortcut('1', self.cameras.load_meshes_1)
        self.add_shortcut('2', self.cameras.load_meshes_2)
        self.add_shortcut('3', self.cameras.load_meshes_3)
        self.add_shortcut('4', self.cameras.load_meshes_4)
        self.add_shortcut('5', self.cameras.load_meshes_5)
        self.add_shortcut('6', self.cameras.load_meshes_6)
        self.add_shortcut('7', self.cameras.load_meshes_7)
        self.add_shortcut('8', self.cameras.load_meshes_8)
        self.add_shortcut('9', self.cameras.load_meshes_9)

        self.add_shortcut('r', self.reset)

        def rotate_cam():
            self.cameras.children[0].angle_z += 0.1
        def reverse_rotate_cam():
            self.cameras.children[0].angle_z -= 0.1

        self.add_shortcut('q', reverse_rotate_cam)
        self.add_shortcut('e', rotate_cam)

        self.add_shortcut('a', self.notify, 'Hello, my name\nKeyes')
        self.add_shortcut('shift+q', self.notify, 1, 2, 3, *'qwerty', sep='.')

        self.add_shortcut('escape', self.release_mouse)
        self.cameras.children[0].velocity = (0, 0, 1)

    def release_mouse(self):
        for view in self.cameras:
            view.mouse_control = False

    def reset(self):
        """ Clear meshes, reload initial mesh set and reset all cameras.
        """
        self.cameras.meshes.clear()
        self.cameras.load_meshes_initial()

        for view in self.cameras:
            view.reset()

    def update(self, time_delta):
        """ Draw frames for all cameras, update debug information,
        simulate physics objects.
        """
        self.cameras.draw_frame()
        self.fps_counter.update(time_delta)

        true_time_delta = self.time_scale*time_delta

        for physics_object in self.cameras.meshes:
            if isinstance(physics_object, Physics):
                physics_object.simulate(true_time_delta)

    def notify(self, *objects, duration=None, sep=' '):
        """ Overlay a temporary text notification lasting `duration`
        milliseconds.
        """
        notification = Notification(*objects, duration=duration, sep=sep)
        self.notification_layout.add_widget(notification)

    def toggle_console(self):
        """ 
        """
        try:
            console = self.console
        except AttributeError:
            console = self.console = Console()

        layout = self.console_layout
        if layout.children:
            layout.remove_widget(console)
        else:
            layout.add_widget(console)

    @staticmethod
    def on_show_debug(instance, show_debug):
        """ Set show_debug for all child cameras.
        """
        for view in instance.cameras:
            view.show_debug = show_debug
        instance.fps_counter.shown = show_debug

    def toggle_debug(self):
        self.show_debug = not self.show_debug


class FPSCounter(Label, ShownBehaviour):
    """ A Debug label used to keep track of frame rate statistics.
    """

    # The amount of time deltas tracked, the more deltas
    # the higher the  accuracy of the displayed fps.
    buffer_length = BoundedNumericProperty(60, min=1, max=256)

    # The number of self.update() calls between each text update.
    update_frequency = BoundedNumericProperty(1, min=1)

    def __init__(self, **kwargs):
        """ Make empty collections.deque of length self.buffer_length
        """
        super().__init__(**kwargs)

        self.time_delta_buffer = deque(maxlen=self.buffer_length)
        self._counter = 0

    def update(self, time_delta):
        """ Add time_delta to self.time_delta_buffer and update
        self.text every self.update_frequency calls.
        """
        self.time_delta_buffer.append(time_delta)

        if self._counter == self.update_frequency:
            # Calculate average time delta and update self.text.
            average_time_delta = mean(self.time_delta_buffer)

            ms = 1000*average_time_delta
            fps = 1 / average_time_delta
            self.text = f'ms: {ms:.2f} | fps: {fps:.2f}'

            self._counter = 0

        self._counter += 1


class DebugLabel(Label):
    pass


class Notification(Label):
    """ Temporary text notification.
    """

    def __init__(self, *objects, auto_show: bool = True,
                 duration: Optional[float] = None, sep: str = ' ',
                 words_per_minute: int = 200, **kwargs):
        """ Similar to print, the text shown is the str representations
        of the given objects joined with sep. If duration is not
        specified it is based on the number of words in the text and
        words_per_minute.
        """
        text = sep.join(str(obj) for obj in objects)
        super().__init__(text=text, opacity=0, **kwargs)

        self.auto_show = auto_show

        if duration is None:
            word_count = len(re.split(r'\W+', text))
            print(word_count)
            words_per_second = words_per_minute / 60
            duration = word_count / words_per_second

        fade_in = Animation(opacity=1, duration=0.2, transition='out_circ')
        fade_out = Animation(opacity=0, duration=0.2, transition='in_circ')
        fade_out.bind(on_complete=lambda *_: self.parent.remove_widget(self))

        self.animation = fade_in + Animation(duration=duration) + fade_out

    def on_parent(self, instance, parent):
        """ Remove self from parent after self.duration seconds.
        """
        if isinstance(parent, Widget) and self.auto_show:
            self.animation.start(self)
