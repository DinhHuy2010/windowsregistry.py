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

from typing_extensions import TYPE_CHECKING, Any, Iterable, Optional, Sequence, Union

from windowsregistry._lowlevel import lowlevel
from windowsregistry._typings import RegistryKeyPermissionTypeArgs
from windowsregistry.errors import OperationDataErrorKind, OperationError, OperationErrorKind
from windowsregistry.models import (
    RegistryHKEYEnum,
    RegistryInfoKey,
    RegistryKeyPermissionType,
    RegistryPermissionConfig,
)
from windowsregistry.regpath import RegistryPathString

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
        self.regpath = RegistryPathString(*subkey, root_key=root_key)
        self.low_level = lowlevel(
            permconf=RegistryPermissionConfig(permissions=tuple(permission), wow64_32key_access=wow64_32key_access)
        )
        try:
            self._winreg_handler = self.low_level.open_subkey(self.regpath.root_key.value, self.regpath.path)
        except OSError as exc:
            raise OperationError(
                OperationErrorKind.ON_READ,
                OperationDataErrorKind.SUBKEY,
                f"fail to open {self.regpath.fullpath!r}",
                exc,
            ) from exc

        self._winreg_query = RegistryInfoKey(*self.low_level.query_subkey(self._winreg_handler))

    @property
    def winreg_handler(self) -> "HKEYType":
        return self._winreg_handler

    @property
    def winreg_query(self) -> RegistryInfoKey:
        return self._winreg_query

    def itersubkeys(self) -> Iterable[str]:
        yield from map(
            partial(self.low_level.subkey_from_index, self.winreg_handler),
            range(self.winreg_query.total_subkeys),
        )

    def itervalues(self) -> Iterable[tuple[str, Any, int]]:
        yield from map(
            partial(self.low_level.value_from_index, self.winreg_handler),
            range(self.winreg_query.total_values),
        )

    def new_handler_from_path(self, subkey_parts: Sequence[str]) -> "WindowsRegistryHandler":
        return self.__class__(
            subkey=subkey_parts,
            root_key=self.regpath.root_key,
            permission=self.low_level.permconf.permissions,
            wow64_32key_access=self.low_level.permconf.wow64_32key_access,
        )

    def subkey_exists(self, subkey: str):
        try:
            self.low_level.open_subkey(self.winreg_handler, subkey)
            return True
        except OSError:
            return False

    def new_subkey(self, subkey: str):
        try:
            self.low_level.create_subkey(self.winreg_handler, subkey)
        except OSError as exc:
            raise OperationError(
                OperationErrorKind.ON_CREATE,
                OperationDataErrorKind.SUBKEY,
                f"fail to create subkey {subkey!r}",
                exc,
            ) from exc

    def delete_subkey_tree(self, subkey: str, recursive: bool):
        af = self.regpath.joinpath(subkey)
        af_handler = self.new_handler_from_path(af.parts)
        if af_handler.winreg_query.total_subkeys != 0:
            if not recursive:
                raise OperationError(
                    OperationErrorKind.ON_DELETE,
                    OperationDataErrorKind.SUBKEY,
                    "subkey is not empty",
                )
            for subaf in af_handler.itersubkeys():
                af_handler.delete_subkey_tree(subaf, recursive=True)
        try:
            self.low_level.delete_subkey(self.winreg_handler, subkey)
        except OSError as exc:
            raise OperationError(
                OperationErrorKind.ON_DELETE,
                OperationDataErrorKind.SUBKEY,
                f"fail to delete subkey {subkey!r}",
                exc,
            ) from exc

    def value_exists(self, name: str):
        try:
            self.low_level.query_value(self.winreg_handler, name)
            return True
        except OSError:
            return False

    def query_value(self, name: str) -> tuple[str, Any, int]:
        try:
            return (name, *self.low_level.query_value(self.winreg_handler, name))
        except FileNotFoundError as e:
            raise OperationError(
                operation=OperationErrorKind.ON_READ,
                kind=OperationDataErrorKind.VALUE,
                message=f"value {name!r} not found",
                exc=e,
            ) from e

    def set_value(self, name: str, dtype: int, data: Any) -> None:
        try:
            self.low_level.set_value(self.winreg_handler, name, dtype, data)
        except OSError as exc:
            kind = OperationErrorKind.ON_UPDATE if self.value_exists(name) else OperationErrorKind.ON_CREATE
            raise OperationError(
                kind,
                OperationDataErrorKind.VALUE,
                f"fail to create/update value {name!r}",
                exc,
            ) from exc

    def delete_value(self, name: str) -> None:
        try:
            self.low_level.delete_value(self._winreg_handler, name)
        except OSError as exc:
            raise OperationError(
                OperationErrorKind.ON_DELETE,
                OperationDataErrorKind.VALUE,
                f"fail to delete value {name!r}",
                exc,
            ) from exc
