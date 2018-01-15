# -*- coding: utf-8 -*-

import cProfile
import numpy as np

from kivy.app import App
from kivy.uix.widget import Widget


class PixelGridApp(App):
    def build(self):
        return PixelGridWidget()


class PixelRGB(bytes):

    def __new__(cls, red: int, green: int, blue: int):
        return super().__new__(cls, [red, green, blue])

    def __repr__(self) -> str:
        arguments = ', '.join(map(repr, self))
        return f'{self.__class__.__name__}({arguments})'

    def __str__(self) -> str:
        rgb = '-'.join(format(byte, '02x') for byte in self)
        return f'<{self.__class__.__name__} {rgb}>'

    def __index__(self) -> int:
        return self[0]*256**2 + self[1]*256 + self[2]


class PixelGrid(object):
    """ .
    """

    @property
    def red(self):
        return self.pixels[self._index,0]

    @property
    def green(self):
        return self.pixels[self._index,1]

    @property
    def blue(self):
        return self.pixels[self._index,2]

    @classmethod
    def from_bitmap(cls, file):
        with open(file, 'rb') as fh:
            bmp = fh.read()

        if bmp.startswith(b'BM'):
            print('is bitmap')
            length = int.from_bytes(bmp[2:6], byteorder='little')
            print(length)
        print(bmp[:len(bmp) - 256*173*3])
        return cls()

    def __init__(self) -> None:
        """ Initialize three identical red, green, and blue 2D arrays.
        """
        self.pixels = np.zeros([2, 3, 100, 100], dtype=np.uint8)
        self._index = 0

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'

    def __str__(self) -> str:
        return f'<{self.__class__.__name__}:\n{self.pixels}>'

    def flip(self) -> None:
        """ .
        """
        self._index ^= 1

    @staticmethod
    def apply_to_pixels(grid, function) -> None:
        """ Apply ``function`` to each pixel of ``grid``. `function``
        should take two integer arguments for the x and y coordinates
        and return an integer in range(2**32). This returned value is
        set as the new value of the pixel.

        WARNING: Currently this can be a lengthy operation, depending on
                 the size of ``grid``.
        """
        for coord, pixel in np.ndenumerate(grid):
            grid[coord] = function(*coord)

    def resize_grids(self, width, height):
        """ Resize all pixel grids to ``width`` by ``height``, without
        resizing the other axes.
        """
        shape = self.pixels.shape
        self.pixels.resize(shape[0], shape[1], width, height)


class PixelGridWidget(Widget, PixelGrid):

    def draw(self) -> None:
        """ .
        """
        self.flip()

    def on_width(self, _, width):
        self.resize_grids(width, self.height)
        print('width changed to:', width)

    def on_height(self, _, height):
        self.resize_grids(self.width, height)
        self.apply_to_pixels(self.red, lambda x, y: x^y)
        print('height changed to:', height)

    def on_touch_down(self, touch):
        if touch.button == 'right':
            self.flip()
        elif touch.button == 'middle':
            print(self)
        else:
            x, y = round(touch.x), round(touch.y) - 2
            pixel = PixelRGB(self.red[x,y], self.green[x,y], self.blue[x,y])
            print(f'{pixel} ({x}, {y})')


def main():
    # p = PixelGrid()
    # p.apply_to_pixels(p.red, lambda x, y: x^y)
    # p.apply_to_pixels(p.green, lambda x, y: (x+y)/2)
    PixelGrid.from_bitmap('data/textures/Watermelon.256.bmp')
    # PixelGridApp().run()

if __name__ == '__main__':
    main()
