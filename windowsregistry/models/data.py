from typing import Any, NamedTuple

from .enums import RegistryKeyPermissionType, RegistryValueType

class RegistryInfoKey(NamedTuple):
    total_subkeys: int
    total_values: int
    last_modified: int

class RegistryValue(NamedTuple):
    value_name: str
    data: Any
    dtype: RegistryValueType

class RegistryPermissionConfig(NamedTuple):
    permission: RegistryKeyPermissionType
    wow64_32key_access: bool
