Python Coding Style
===================

All Python code in the project should be formatted as defined below.


Basics
------

- Follow PEP8_ and PEP257_.
- Code line length is 79, docstring line length is 72.
- All strings should use single quote characters ``'`` over double quote
  characters ``"`` when appropriate, like ``repr``.


Imports
-------

Imports should be alphabetised.

Imports should be grouped (separated by a blank line) in the order:

1. ``__future__`` imports
#. Standard library imports
#. Third party imports
#. Internal imports

Imports from typing and custom type definitions should be placed above
all other import statements, separated by a blank line::

    from typing import Tuple
    Point = Tuple[float, float, float]

    import re
    from math import degrees


Classes
-------

Methods should be grouped in the order:

1. Properties
#. Construction function (``__init__`` or ``__new__``)
#. Alternate construction functions (class methods)
#. Magic (dunder) methods
#. Regular methods
#. Other class methods
#. Static methods


Docstrings
----------

Use reStructuredText for mark-up.

The general format of a docstring is a triple double-quoted string followed by
a space and the content of the docstring then closed on a new line::

    def foo():
        """ Do the thing.
        """

Add a blank line after class docstrings::

    class Point(object):
        """ A point in 3D space.
        """

        def __init__(self, x, y, z):
            """ Initialise x, y, and z attributes.
            """
            self.x, self.y, self.z = x, y, z

Unless the class body contains no methods (in enums, NamedTuples etc.)::

    class Point(typing.NamedTuple):
        """ A 2-D point.
        """
        x: float
        y: float

::

    class LogLevel(enum.Enum):
        """ The priority of a log.
        """
        DEBUG = enum.auto()
        INFO = enum.auto()
        WARN = enum.auto()
        ERROR = enum.auto()


.. _PEP8:   https://www.python.org/dev/peps/pep-0008/
.. _PEP257: https://www.python.org/dev/peps/pep-0257/
