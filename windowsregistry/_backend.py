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

from functools import partial
from typing import TYPE_CHECKING, Any, Iterable, Optional, Sequence, Union

from ._lowlevel import lowlevel
from ._typings import RegistryKeyPermissionTypeArgs
from .errors import WindowsRegistryError
from .models import (
    RegistryHKEYEnum,
    RegistryInfoKey,
    RegistryKeyPermissionType,
    RegistryPermissionConfig,
)
from .regpath import RegistryPathString

if TYPE_CHECKING:
    from winreg import HKEYType


class WindowsRegistryHandler:
    def __init__(
        self,
        subkey: Union[str, Sequence[str], None] = None,
        *,
        root_key: Optional[RegistryHKEYEnum] = None,
        permission: Optional[RegistryKeyPermissionTypeArgs] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        if subkey is None:
            subkey = []
        elif isinstance(subkey, str):
            subkey = [subkey]
        if permission is None:
            permission = RegistryKeyPermissionType.KEY_READ
        if isinstance(permission, RegistryKeyPermissionType):
            permission = [permission]
        self._regpath = RegistryPathString(*subkey, root_key=root_key)
        self._ll = lowlevel(
            permconf=RegistryPermissionConfig(
                permissions=tuple(permission), wow64_32key_access=wow64_32key_access
            )
        )
        self._winreg_handler = self._ll.open_subkey(
            self._regpath.root_key.value, self._regpath.path
        )
        self._winreg_query = RegistryInfoKey(
            *self._ll.query_subkey(self._winreg_handler)
        )

    @property
    def winreg_handler(self) -> "HKEYType":
        return self._winreg_handler

    @property
    def winreg_query(self) -> RegistryInfoKey:
        return self._winreg_query

    def itersubkeys(self) -> Iterable[str]:
        yield from map(
            partial(self._ll.subkey_from_index, self.winreg_handler),
            range(self.winreg_query.total_subkeys),
        )

    def itervalues(self) -> Iterable[tuple[str, Any, int]]:
        yield from map(
            partial(self._ll.value_from_index, self.winreg_handler),
            range(self.winreg_query.total_values),
        )

    def new_handler_from_path(
        self, subkey_parts: Sequence[str]
    ) -> "WindowsRegistryHandler":
        return self.__class__(
            subkey=subkey_parts,
            root_key=self._regpath.root_key,
            permission=self._ll._permconf.permissions,
            wow64_32key_access=self._ll._permconf.wow64_32key_access,
        )

    def subkey_exists(self, subkey: str):
        try:
            self._ll.open_subkey(self.winreg_handler, subkey)
            return True
        except OSError:
            return False

    def new_subkey(self, subkey: str):
        try:
            self._ll.create_subkey(self.winreg_handler, subkey)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}") from None

    def delete_subkey_tree(self, subkey: str, recursive: bool):
        af = self._regpath.joinpath(subkey)
        af_handler = self.new_handler_from_path(af.parts)
        if af_handler.winreg_query.total_subkeys != 0:
            if not recursive:
                raise WindowsRegistryError("subkey is not empty")
            for subaf in af_handler.itersubkeys():
                af_handler.delete_subkey_tree(subaf, recursive=True)
        try:
            self._ll.delete_subkey(self.winreg_handler, subkey)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}") from None

    def value_exists(self, name: str):
        try:
            self._ll.query_value(self.winreg_handler, name)
            return True
        except OSError:
            return False

    def query_value(self, name: str) -> tuple[str, Any, int]:
        return (name, *self._ll.query_value(self.winreg_handler, name))

    def set_value(self, name: str, dtype: int, data: Any) -> None:
        try:
            self._ll.set_value(self.winreg_handler, name, dtype, data)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}") from None

    def delete_value(self, name: str) -> None:
        try:
            self._ll.delete_value(self._winreg_handler, name)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}") from None
