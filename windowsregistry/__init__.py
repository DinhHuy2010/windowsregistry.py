# This file is part of windowsregistry (https://github.com/DinhHuy2010/windowsregistry.py)
#
# MIT License
#
# Copyright (c) 2024 DinhHuy2010 (https://github.com/DinhHuy2010)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import annotations

from typing_extensions import Final

from windowsregistry import models
from windowsregistry.core import RegistryPath, open_subkey
from windowsregistry.errors import WindowsRegistryError

HKEY_CLASSES_ROOT: Final[RegistryPath] = open_subkey("HKCR")
HKEY_CURRENT_USER: Final[RegistryPath] = open_subkey("HKCU")
HKEY_LOCAL_MACHINE: Final[RegistryPath] = open_subkey("HKLM")
HKCR: Final[RegistryPath] = HKEY_CLASSES_ROOT
HKCU: Final[RegistryPath] = HKEY_CURRENT_USER
HKLM: Final[RegistryPath] = HKEY_LOCAL_MACHINE

__all__ = [
    "models",
    "RegistryPath",
    "open_subkey",
    "WindowsRegistryError",
    "HKCR",
    "HKCU",
    "HKLM",
    "HKEY_CLASSES_ROOT",
    "HKEY_LOCAL_MACHINE",
    "HKEY_CURRENT_USER",
]

__version__: Final[str] = "0.1.3"
