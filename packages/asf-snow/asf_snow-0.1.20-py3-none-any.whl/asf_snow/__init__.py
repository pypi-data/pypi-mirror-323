import logging
import os
import sys
from importlib.metadata import version
from pathlib import Path

# import pdb


'''
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    from importlib_metadata import metadata
'''
'''
pdb.set_trace()
'''

__version__ = version(__name__)

__all__ = [
    '__version__',
]
