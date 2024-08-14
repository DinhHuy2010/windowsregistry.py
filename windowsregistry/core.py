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

from collections import deque
from typing import Any, Iterator, Optional, Sequence, Union

from ._backend import WindowsRegistryHandler
from ._typings import RegistryKeyPermissionTypeArgs
from .errors import (
    OperationDataErrorKind,
    OperationError,
    OperationErrorKind,
    WindowsRegistryError,
)
from .models import (
    RegistryHKEYEnum,
    RegistryInfoKey,
    RegistryKeyPermissionType,
    RegistrySize,
    RegistryValue,
    RegistryValueType,
)
from .regpath import RegistryPathString


class RegistryPath:
    def __init__(
        self,
        subkey: Union[None, str, Sequence[str]] = None,
        *,
        root_key: Optional[RegistryHKEYEnum] = None,
        permission: Optional[RegistryKeyPermissionTypeArgs] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        self._backend = WindowsRegistryHandler(
            subkey=subkey,
            root_key=root_key,
            permission=permission,
            wow64_32key_access=wow64_32key_access,
        )

    def _sanargs(
        self, perm: Optional[RegistryKeyPermissionTypeArgs], w64: Optional[bool]
    ):
        perm = perm if perm is not None else self._backend._ll._permconf.permissions
        wow64_32key_access = (
            w64 if w64 is not None else self._backend._ll._permconf.wow64_32key_access
        )

        return perm, wow64_32key_access

    def _internal_open_subkey(
        self,
        r: RegistryPathString,
        perm: Optional[RegistryKeyPermissionTypeArgs] = None,
        w64: Optional[bool] = None,
    ):
        perm, w64 = self._sanargs(perm, w64)
        return self.__class__(
            subkey=r.path, root_key=r.root_key, permission=perm, wow64_32key_access=w64
        )

    @property
    def regpath(self) -> RegistryPathString:
        return self._backend._regpath

    @property
    def query_info(self) -> RegistryInfoKey:
        return self._backend.winreg_query

    @property
    def parent(self) -> "RegistryPath":
        return self._internal_open_subkey(self.regpath.parent)

    def open_subkey(
        self,
        *paths: str,
        permission: Optional[RegistryKeyPermissionTypeArgs] = None,
        wow64_32key_access: Optional[bool] = None,
    ) -> "RegistryPath":
        return self._internal_open_subkey(
            self.regpath.joinpath(*paths), permission, wow64_32key_access
        )

    def subkeys(self) -> Iterator["RegistryPath"]:
        for subkey in self._backend.itersubkeys():
            try:
                yield self.open_subkey(subkey)
            except (OSError, WindowsRegistryError):
                continue

    def subkey_exists(self, subkey: str) -> bool:
        return self._backend.subkey_exists(subkey)

    def create_subkey(self, subkey: str, *, exist_ok: bool = False) -> "RegistryPath":
        if self.subkey_exists(subkey):
            if exist_ok:
                return self.open_subkey(subkey)
            raise OperationError(
                OperationErrorKind.ON_CREATE,
                OperationDataErrorKind.SUBKEY,
                f"subkey {subkey!r} already exists"
            )

        self._backend.new_subkey(subkey)
        return self.open_subkey(subkey)

    def delete_subkey(self, subkey: str, *, recursive: bool = False) -> None:
        if not self.subkey_exists(subkey):
            raise OperationError(
                OperationErrorKind.ON_DELETE,
                OperationDataErrorKind.SUBKEY,
                f"subkey {subkey!r} does not exists"
            )
        self._backend.delete_subkey_tree(subkey, recursive)

    def value_exists(self, name: str) -> bool:
        return self._backend.value_exists(name)

    def values(self) -> Iterator[RegistryValue]:
        for name, data, dtype in self._backend.itervalues():
            yield RegistryValue(name, data, RegistryValueType(dtype))

    def get_value(self, key: str = "") -> RegistryValue:
        result = self._backend.query_value(key)
        name, data, dtype = result
        return RegistryValue(name, data, RegistryValueType(dtype))

    def set_value(
        self, name: str, data: Any, *, dtype: RegistryValueType, overwrite: bool = False
    ) -> RegistryValue:
        if self.value_exists(name) and not overwrite:
            raise OperationError(
                OperationErrorKind.ON_CREATE,
                OperationDataErrorKind.VALUE,
                f"value name {name!r} already exists"
            )

        self._backend.set_value(name, dtype.value, data)
        return self.get_value(name)

    def delete_value(self, name: str) -> None:
        if not self.value_exists(name):
            raise OperationError(
                OperationErrorKind.ON_DELETE,
                OperationDataErrorKind.VALUE,
                f"value name {name!r} does not exists"
            )
        self._backend.delete_value(name)

    def traverse(
        self,
    ) -> Iterator[
        tuple["RegistryPath", tuple["RegistryPath", ...], tuple[RegistryValue, ...]]
    ]:
        stacks: deque[RegistryPath] = deque([self])
        while stacks:
            curr = stacks.popleft()
            subkeys_in_curr = tuple(curr.subkeys())
            values_in_curr = tuple(curr.values())
            yield curr, subkeys_in_curr, values_in_curr
            stacks.extend(subkeys_in_curr)

    def sizeof(self) -> RegistrySize:
        cached = getattr(self, "__cached_sizeof", None)
        if cached is not None:
            return cached
        sub, val = 0, 0
        for r, _, _ in self.traverse():
            sub += r.query_info.total_subkeys
            val += r.query_info.total_values
        final = RegistrySize(self.regpath, sub, val)
        setattr(self, "__cached_sizeof", final)
        return final

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}: {self.regpath.fullpath} at {hex(id(self))}>"
        )


def open_subkey(
    *path: str,
    root_key: Optional[RegistryHKEYEnum] = None,
    permission: Optional[RegistryKeyPermissionType] = None,
    wow64_32key_access: bool = False,
) -> RegistryPath:
    return RegistryPath(
        root_key=root_key,
        subkey=path,
        permission=permission,
        wow64_32key_access=wow64_32key_access,
    )
