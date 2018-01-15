"""
Input classes.
"""

from typing import Dict, FrozenSet, Tuple

import inspect
from enum import auto, Flag
from functools import partial, partialmethod
from warnings import warn

from kivy.uix.behaviors.focus import FocusBehavior
from kivy.core.window import Keyboard, Window
from kivy.properties import AliasProperty, NumericProperty

from common import represent


try:
    from ctypes import windll, c_uint
except OSError:
    warn('set_cursor_position(x, y) will have no effect')
    _set_cursor_position = lambda x, y: None
else:
    _set_cursor_position = windll.user32.SetCursorPos
    _set_cursor_position.argtypes = [c_uint, c_uint]


def set_cursor_position(x: int, y: int):
    """ Set the cursor position relative to the top-left of the screen.
    """
    _set_cursor_position(round(x), round(y))


def _on_bound_mouse_move(win, mouse_pos):
    center_x = win.width // 2
    center_y = win.height // 2
    x, y = mouse_pos[0], mouse_pos[1] - 1
    if (x, y) != (center_x, center_y):
        win._mouse_bound_function((center_x - x, center_y - y))
        win_center_x = win.left + center_x
        win_center_y = win.top + center_y
        set_cursor_position(win_center_x, win_center_y)


def bind_mouse(function):
    Window.show_cursor = False
    win_center_x = Window.left + Window.width // 2
    win_center_y = Window.top + Window.height // 2
    Window.grab_mouse()
    set_cursor_position(win_center_x, win_center_y)
    Window._mouse_bound = True
    Window._mouse_bound_function = function
    Window.bind(mouse_pos=_on_bound_mouse_move)


def unbind_mouse():
    Window.unbind(mouse_pos=_on_bound_mouse_move)
    Window.ungrab_mouse()
    Window._mouse_bound = False
    Window.show_cursor = True


class BaseWindowWithExtras(type(Window)):

    relative_move_x = NumericProperty(0)
    relative_move_y = NumericProperty(0)
    relative_move = AliasProperty(relative_move_x, relative_move_y)

    @property
    def relative_mouse_input(self):
        return self._relative_mouse_input

    @relative_mouse_input.setter
    def relative_mouse_input(self, relative_mouse_input):
        print(relative_mouse_input)
        if relative_mouse_input:
            self.grab_mouse()
            win_center_x = self.left + self.width // 2
            win_center_y = self.top + self.height // 2
            set_cursor_position(win_center_x, win_center_y)
            self.bind(mouse_pos=_on_bound_mouse_move)
        else:
            self.unbind(mouse_pos=_on_bound_mouse_move)
            self.ungrab_mouse()
        self.show_cursor = not relative_mouse_input
        self._relative_mouse_input = relative_mouse_input

    def _on_relative_mouse_move(self, mouse_pos):
        center_x = self.width // 2
        center_y = self.height // 2
        x, y = mouse_pos[0], mouse_pos[1] - 1
        if (x, y) != (center_x, center_y):
            self.relative_move_x = center_x - x
            self.relative_move_y = center_y - y
            win_center_x = self.left + center_x
            win_center_y = self.top + center_y
            set_cursor_position(win_center_x, win_center_y)


Window = BaseWindowWithExtras()
Window.create_property('relative_move')


class ControlGroups(Flag):
    GENERAL = auto()
    MENU = auto()
    CAMERA_1 = auto()


class Input(object):
    """ 
    """

    # Window.bind(on_key_down=_on_key_down)

    _bound = False

    _modifier_keys = ('alt', 'ctrl', 'meta', 'shift')
    _shortcut_seperator = '+'

    @property
    def bound(self):
        return self._bound

    @bound.setter
    def bound(self, bound):
        if bound:
            function = Window.bind
        else:
            function = Window.unbind
        function(on_key_down=self._on_key_down)
        self._bound = bound

    @property
    def shortcut(self):
        return self._shortcut

    @shortcut.setter
    def shortcut(self, shortcut):
        """ Verify shortcut, raise ValueError if invalid.
        """
        *modifiers, trigger = shortcut.split(self._shortcut_seperator)
        trigger_keycode = Keyboard.keycodes.get(trigger)

        if trigger_keycode is None:
            raise ValueError("'{}' is not a valid key name".format(trigger))

        for modifier in modifiers:
            if modifier not in self._modifier_keys:
                raise ValueError(
                    "'{}' is not a valid modifier key name".format(modifier))

        self._shortcut = shortcut

    def bind(shortcut: str):
        """ Return a decorator for binding a function to an input.
        """
        def decorator(function):
            return Input(shortcut, function)
        return decorator

    def __init__(self, shortcut, function, *args, **keywords):
        """ 
        """
        self.shortcut = shortcut
        self._callback = partial(function, *args, **keywords)

    def __call__(self):
        self._callback()


class GamepadsBase(object):
    """ TODO
    """

    _bound = False
    _gamepads = {}

    window = Window

    @property
    def bound(self):
        return self._bound

    @bound.setter
    def bound(self, bound):
        if bound:
            self._bind(self.window.bind)
        else:
            self._bind(self.window.unbind)
        self._bound = bound

    @classmethod
    def _bind(cls, bind_function):
        bind_function(on_joy_axis=cls._on_stick,
                      on_joy_button_down=cls._on_button,
                      on_joy_hat=cls._on_dpad)

    def __init__(self, window=None, bound=True):
        self.window = window if window else Window
        self.bound = bound

    def __getitem__(self, key):
        return self._gamepads[key]

    def __setitem__(self, key, value):
        self._gamepads[key] = value

    def __delitem__(self, key):
        del self._gamepads[key]

    @classmethod
    def _on_stick(cls, window, stickid, axisid, value):
        pass

    @classmethod
    def _on_button(cls, window, stickid, buttonid):
        pass

    @classmethod
    def _on_dpad(cls, window, stickid, hatid, value):
        pass


Gamepads = GamepadsBase()


class Gamepad(object):
    """ TODO.
    """

    def __init__(self, pad_id):
        self.id = pad_id
        Gamepads[pad_id] = self

    def _on_stick(self, stickid, axisid, value):
        pass

    def _on_button(self, stickid, buttonid):
        pass

    def _on_dpad(self, stickid, hatid, value):
        pass


_MODIFIER_KEYS = {'alt', 'ctrl', 'meta', 'shift'}
_SHORTCUT_SEPERATOR = '+'
_KEY_NAMES = {code: name for name, code in Keyboard.keycodes.items()}

_shortcuts: Dict[Tuple[int, FrozenSet[str]], callable] = {}


class Shortcut(object):
    """ 
    """

    _MODIFIER_KEYS = {'alt', 'ctrl', 'meta', 'shift'}
    _SHORTCUT_SEPERATOR = '+'

    @property
    def shortcut(self):
        return self._shortcut

    @shortcut.setter
    def shortcut(self, shortcut):

        *modifiers, trigger = shortcut.split(self._SHORTCUT_SEPERATOR)
        trigger_key_number = Keyboard.keycodes.get(trigger)

        if trigger_key_number is None:
            raise ValueError(f'Invalid key name: {trigger}')

        for modifier in modifiers:
            if modifier not in self._MODIFIER_KEYS:
                raise ValueError(f'Invalid modifier key name: {modifier}')

        shortcut = (trigger_key_number, frozenset(modifiers))

        self._shortcut = shortcut

    def __init__(self, shortcut: str, function: callable, *args, **keywords):
        """ TODO
        """
        self.shortcut = shortcut

        self._callback = partial(function, *args, **keywords)

    def __repr__(self):
        cb = self._callback
        return represent(self, self.shortcut, cb.func, *cb.args, **cb.keywords)

    def __str__(self):
        return f'{self.shortcut.title()}: {self._callback}'

    def __call__(self):
        return self._callback()

    @classmethod
    def shortcut_string(cls, key: str, modifiers):
        """ Return the shortcut string from a key name and an iterable
        of modifiers.
        """
        return cls._SHORTCUT_SEPERATOR.join(list(modifiers) + [key])


def shortcut(shortcut, *positionals, **keywords):
    """ Second order decorator for converting functions into Shortcuts.

    >>> @shortcut('ctrl+f', 3)
    ... def print_foo(foo):
    ...     print(foo)
    """
    def wrapper(function):
        return Shortcut(shortcut, function, *positionals, **keywords)
    return wrapper


class Bindable(object):
    """ Mixin for Widget class to allow for easy shortcuts
    """

    def __init__(self):
        self.shortcuts = [shortcut for shortcut in
            self.__class__.__dict__.values() if isinstance(shortcut, Shortcut)]
        Window.bind(on_key_down=self._on_key_down)

    def _on_key_down(*args):
        print(args)

    def add_shortcut(self, shortcut, function, *args, **kwargs):
        self.shortcuts.append(Shortcut(shortcut, function, *args, **kwargs))


class ShortcutBehavior(FocusBehavior):

    _shortcuts = {}

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ 
        """
        shortcut = '+'.join(modifiers + [keycode[1]])
        try:
            self._shortcuts[shortcut]()
        except KeyError:
            super().keyboard_on_key_down(window, keycode, text, modifiers)

    def add_shortcut(self, shortcut, function, *args, **kwargs):
        """ 
        """
        *modifiers, trigger = shortcut.split('+')

        # Validate trigger key name:
        if trigger not in Keyboard.keycodes:
            raise ValueError(f"'{trigger}' is not a valid key name")
        # Validate modifier key names:
        for key in modifiers:
            if key not in ('alt', 'ctrl', 'meta', 'shift'):
                raise ValueError(f"'{key}' is not a valid modifier key name")

        self._shortcuts[shortcut] = partial(function, *args, **kwargs)


def shortcut(shortcut: str, *args, **keywords):
    """ 
    """
    *modifiers, trigger = shortcut.split(_SHORTCUT_SEPERATOR)
    trigger_key_number = Keyboard.keycodes.get(trigger)

    if trigger_key_number is None:
        raise ValueError(f'Invalid key name: {trigger}')

    for modifier in modifiers:
        if modifier not in _MODIFIER_KEYS:
            raise ValueError(f'Invalid modifier key name: {modifier}')

    shortcut = (trigger_key_number, frozenset(modifiers))

    def bind_shortcut(function):
        _shortcuts[shortcut] = partial(function, *args, **keywords)
        return function

    return bind_shortcut


def _on_keyboard(window, key, scancode, codepoint, modifiers):
    try:
        _shortcuts[key, frozenset(modifiers)]()
        return True
    except KeyError:
        sep = _SHORTCUT_SEPERATOR
        shortcut = sep.join([*modifiers, _KEY_NAMES.get(key, str(key))])


Window.bind(on_keyboard=_on_keyboard)


def unbind(win, ctx):
    Window.unbind(on_keyboard=_on_keyboard)


def get_class_of_function(function):
    cls = getattr(inspect.getmodule(function),
        function.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
    if isinstance(cls, type):
        return cls


class Foo(object):
    @shortcut('ctrl+f')
    def bar():
        print('hi')


def main():
    s = Shortcut('ctrl+f', print, *'foo', sep='.')
    s()
    # print(s)
    print(repr(s))

if __name__ == '__main__':
    main()
