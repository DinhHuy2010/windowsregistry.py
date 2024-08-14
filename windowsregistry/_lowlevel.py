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

from typing import TYPE_CHECKING, Any

from .models import RegistryPermissionConfig
from .utils import get_permission_int

if TYPE_CHECKING:
    from winreg import _KeyType as _RegistryHandlerType

try:
    import winreg
except ImportError as exc:
    raise RuntimeError("not running on windows") from exc


class lowlevel:
    def __init__(self, *, permconf: RegistryPermissionConfig) -> None:
        self._permconf = permconf
        self._access = get_permission_int(self._permconf)

    def open_subkey(self, handler: _RegistryHandlerType, path: str):
        return winreg.OpenKeyEx(handler, path, access=self._access)

    def query_subkey(self, handler: _RegistryHandlerType) -> tuple[int, int, int]:
        return winreg.QueryInfoKey(handler)

    def subkey_from_index(self, handler: _RegistryHandlerType, index: int) -> str:
        return winreg.EnumKey(handler, index)

    def create_subkey(self, handler: _RegistryHandlerType, subkey: str):
        winreg.CreateKeyEx(handler, subkey, access=self._access)

    def delete_subkey(self, handler: _RegistryHandlerType, subkey: str):
        winreg.DeleteKeyEx(handler, subkey, access=self._access)

    def query_value(self, handler: _RegistryHandlerType, name: str):
        return winreg.QueryValueEx(handler, name)

    def set_value(
        self, handler: _RegistryHandlerType, name: str, dtype: int, data: Any
    ):
        winreg.SetValueEx(handler, name, 0, dtype, data)

    def delete_value(self, handler: _RegistryHandlerType, name: str):
        winreg.DeleteValue(handler, name)

    def value_from_index(
        self, handler: _RegistryHandlerType, index: int
    ) -> tuple[str, Any, int]:
        return winreg.EnumValue(handler, index)
