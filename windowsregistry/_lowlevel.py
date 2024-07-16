from __future__ import annotations

import winreg
from typing import TYPE_CHECKING, Any

from .models import RegistryPermissionConfig
from .utils import get_permission_int

if TYPE_CHECKING:
    from winreg import _KeyType as _RegistryHandlerType


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
