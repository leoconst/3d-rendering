#!/usr/bin/env python
"""
Main entry point for my 3-D rendering project.
"""


# Run the test suite:
if __debug__:
    import pytest

    error_code = pytest.main()

    if error_code:
        print('Not running main; test suite failed with error code:',
              error_code)
        exit(error_code)


# Delayed import to avoid Kivy's logging mangling the test report.
from widgets import RenderingApp
RenderingApp().run()
