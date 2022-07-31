#!/usr/bin/env python

try:
    __import__("pkg_resources").declare_namespace(__name__)
except ImportError:
    __path__ = __import__("pkgutil").extend_path(__path__, __name__)

from . import path
from ._fscompat import fsdecode, fsencode
from ._version import __version__
from .enums import ResourceType, Seek
from .opener import open_fs

__all__ = [
    "path",
    "fsdecode",
    "fsencode",
    "__version__",
    "ResourceType",
    "Seek",
    "open_fs",
]
