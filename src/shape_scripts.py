"""
TODO
"""

from typing import Iterator

from datetime import datetime
from math import frexp
from random import choice as random_choice


def init_fib_clock(fib_clock):

    fib_clock._previous_fifth_minute = -1

    fib_clock._COLOR_MIN = '98e8fa'         # Light blue.
    fib_clock._COLOR_HOUR = 'faaa98'        # Lightish red.
    fib_clock._COLOR_BOTH = 'b7fa98'        # Light green.
    fib_clock._COLOR_NEITHER = 'dddddd'     # Light grey.

    fib_clock._color_codes = (
        (0b00000,),
        (0b10000, 0b01000),
        (0b11000, 0b00100),
        (0b10100, 0b01100, 0b00010),
        (0b10010, 0b01010, 0b11100),
        (0b11010, 0b00110, 0b00001),
        (0b10110, 0b01110, 0b10001, 0b01001),
        (0b11110, 0b11001, 0b00101),
        (0b10101, 0b01101, 0b00011),
        (0b10011, 0b01011, 0b11101),
        (0b11011, 0b00111),
        (0b10111, 0b01111),
        (0b11111,),
    )

    fib_clock._colors = [fib_clock._COLOR_NEITHER]*5
    fib_clock.color_map = {
        0: fib_clock._colors[0],
        1: fib_clock._colors[0],
        2: fib_clock._colors[1],
        3: fib_clock._colors[1],
        4: fib_clock._colors[2],
        5: fib_clock._colors[2],
        6: fib_clock._colors[3],
        7: fib_clock._colors[3],
        8: fib_clock._colors[4],
        9: fib_clock._colors[4],
    }


def update_fib_clock(fib_clock):

    now = datetime.now()
    fifth_minute = now.minute // 5

    if fib_clock._previous_fifth_minute != fifth_minute:

        hour = now.hour
        if hour == 24:
            hour = 0
        elif hour > 12:
            hour -= 12

        color_codes = fib_clock._color_codes

        minute_codes = random_choice(color_codes[fifth_minute])
        hour_codes = random_choice(color_codes[hour])

        for minute, hour in zip([minute_codes, hour_codes]):
            if minute and hour:
                fib_clock.panel_colors = fib_clock._COLOR_BOTH
            elif minute:
                fib_clock.panel_colors = fib_clock._COLOR_MIN
            elif hour:
                fib_clock.panel_colors = fib_clock._COLOR_HOUR
            else:
                fib_clock.panel_colors = fib_clock._COLOR_NEITHER

        fib_clock._previous_fifth_minute = fifth_minute


def fibs(count, current=0, later=1):
    for _ in range(count):
        yield current
        current, later = later, current + later


def options(iterable, result):
    parts = sorted(iterable, reverse=True)
    for part in parts:
        if result >= part:
            yield True
            result -= part
        else:
            yield False


def code(value, iterable):
    sum_ = sum(iterable)
    if value > sum_:
        raise ValueError(f'value {value} is too high')
    if value == sum_:
        yield
        return


def options(iterable) -> Iterator[tuple]:
    iterable = tuple(iterable)
    for i in range(sum(iterable) + 1):
        yield tuple(code(i, iterable))


def fib_options(limit):
    fibos = tuple(fibs(limit, 1, 1))
    for i in range(sum(fibos) + 1):
        yield tuple(options(fibos, i))


if __name__ == '__main__':
    print(list(options(fibs(5, 1))))
