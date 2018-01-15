"""
Console widget and subwidgets.
"""

from collections import deque
from string import whitespace as WHITESPACE

from kivy.properties import (NumericProperty, ListProperty, ObjectProperty,
                             StringProperty)

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


def is_whitespace(string):
    """ Return True if all characters in string are whitespace.
    """
    for char in string:
        if char not in WHITESPACE:
            return False
    return True


class BufferedTextInput(TextInput):
    """ A single line text input that saves a buffer of previously
    entered text that can be navigated with the up and down arrow keys.
    """

    buffer_max = NumericProperty(256)
    _buffer_index = -1

    @property
    def buffer_index(self):
        return self._buffer_index

    @buffer_index.setter
    def buffer_index(self, value):
        if value < 0:
            self._buffer_index = -1
            self.text = ''
        elif value >= len(self.buffer):
            self._buffer_index = len(self.buffer) - 1
        else:
            self._buffer_index = value 
            self.text = self.buffer[value]

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            super().on_touch_down(touch)
            return True

    def __init__(self, **kwargs):
        """ Make single line TextInput.  Buffer deque's maxlen is set to
        buffer_max.
        """
        super().__init__(multiline=False, **kwargs)
        self.buffer = deque(maxlen=self.buffer_max)

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ Add up and down key binds; change enter bind so that focus
        is retained.
        """
        key = keycode[1]

        if key == 'up':
            self.buffer_index += 1
        elif key == 'down':
            self.buffer_index -= 1
        elif key == 'enter':
            self._add_to_buffer(self.text)
            self.dispatch('on_text_validate')
            self.buffer_index = -1

    def _add_to_buffer(self, text):
        """ Add valid text to the buffer.
        """
        buffer_ = self.buffer
        # text is not duplicate of last buffered text.
        text_not_duplicate = not buffer_ or buffer_[0] != text
        if text_not_duplicate and text and not text.isspace():
            buffer_.appendleft(text)


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class ConsoleOutput(ScrollableLabel):
    pass


class Console(BufferedTextInput):
    """ Text input that can execute functions.
    """

    ignored_keys = ListProperty(['`'])

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """ Add tab autocompletion selection.
        """
        _, key = keycode

        if key in self.ignored_keys:
            print('value')
            return False
        if key == 'tab':
            pass
        else:
            super().keyboard_on_key_down(window, keycode, text, modifiers)

    def on_text_validate(self):
        text = self.text
        if text:
            self.command(text)
        else:
            self.command('help')

    def output(self, text, style='info'):
        # Temporary:
        print(text)

    def command(self, text):
        # Temporary:
        if text == 'help':
            self.output("Here's some help!")
        else:
            self.output(text)
