from typing import Any
import winreg

from .models import RegistryPermissionConfig
from .utils import get_permission_int

class lowlevel:
    def __init__(self, *, permconf: RegistryPermissionConfig) -> None:
        self._permconf = permconf
        self._access = get_permission_int(self._permconf)

    def open_subkey(self, handler: winreg.HKEYType | int, path: str):
        return winreg.OpenKeyEx(handler, path, access=self._access)

    def query_subkey(self, handler: winreg.HKEYType) -> tuple[int, int, int]:
        return winreg.QueryInfoKey(handler)

    def subkey_from_index(self, handler: winreg.HKEYType, index: int) -> str:
        return winreg.EnumKey(handler, index)
    
    def create_subkey(self, handler: winreg.HKEYType, subkey: str):
        winreg.CreateKeyEx(handler, subkey, access=self._access)

    def delete_subkey(self, handler: winreg.HKEYType, subkey: str):
        winreg.DeleteKeyEx(handler, subkey, access=self._access)

    def query_value(self, handler: winreg.HKEYType, name: str):
        return winreg.QueryValueEx(handler, name)
    
    def set_value(self, handler: winreg.HKEYType, name: str, dtype: int, data: Any):
        winreg.SetValueEx(handler, name, 0, dtype, data)

    def delete_value(self, handler: winreg.HKEYType, name: str):
        winreg.DeleteValue(handler, name)

    def value_from_index(self, handler: winreg.HKEYType, index: int) -> tuple[str, Any, int]:
        return winreg.EnumValue(handler, index)
