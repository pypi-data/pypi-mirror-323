import sys

if sys.version_info >= (3, 5): # the following import is not compatible with older Python versions
    from .listener import Listener
