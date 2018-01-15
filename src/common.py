"""
Common constants and functions used throughout the package.
"""

import sys
from itertools import count
from math import ceil, floor
from random import random, randint


TITLE = '3-D Rendering Project'


_previous_randint = sys.maxsize
def next_randint(a: int, b: int) -> int:
    """ Return random integer in range(a, b+1).  Will never return the
    same value twice in a row.

    NOTE: Calculates an arbitrary number of random integers before
          returning.
    """
    if a == b:
        raise ValueError('a and b cannot be equal.')

    global _previous_randint
    while True:
        out = randint(a, b)
        if out != _previous_randint:
            _previous_randint = out
            return out


def represent(instance: object, *args, **kwargs) -> str:
    """ Return an appropriate representation string for the instance.

    >>> class Cat(object):
    ...     def __init__(self, name, *, age=0):
    ...         self.name, self.age = name, age
    ...     def __repr__(self):
    ...         return represent(self, self.name, age=self.age)
    >>> my_cat = Cat('Lulu', age=10)
    >>> repr(my_cat)
    "Cat('Lulu', age=10)"
    """
    argument_names = [repr(arg) for arg in args]
    argument_names.extend(f'{key}={value!r}' for key, value in kwargs.items())
    return f"{instance.__class__.__name__}({', '.join(argument_names)})"


def sequence_str(sequence, limit=2, brackets='[]') -> str:
    """ 
    """
    def comma_separated(iterable):
        return ', '.join(repr(item) for item in iterable)

    length = len(sequence)
    if limit is None:
        limit = length

    if length > limit:
        extra = length - limit
        if extra == 1:
            hidden = '<1 hidden item>'
        else:
            hidden = f'<{extra} hidden items>'
        limit /= 2
        head = comma_separated(sequence[:ceil(limit)])
        tail = comma_separated(sequence[-floor(limit):])
        items = f'{head}, {hidden}, {tail}'
    else:
        items = comma_separated(sequence)

    start, end = brackets
    return f'{start}{items}{end}'


def special_string(instance: object, **kwargs) -> str:
    """ Return a string that can be used if a standard 'eval repr' is
    not appropriate.
    """
    class_name = instance.__class__.__name__

    if not kwargs:
        return f'<{class_name}>'
    else:
        args = ' '.join(f'{name}={value!r}' for name, value in kwargs.items())
        return f'<{class_name} {args}>'
