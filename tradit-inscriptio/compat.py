# -*- coding: utf-8 -*-
"""Python 2/3 compatibility module."""

import sys

PY3 = int(sys.version[0]) == 3

# if PY3:
text_type = str
binary_type = bytes
string_types = (str,)
unicode = str
basestring = (str, bytes)
