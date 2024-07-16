from __future__ import annotations

from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from ..regpath import RegistryPathString
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
    permissions: tuple[RegistryKeyPermissionType, ...]
    wow64_32key_access: bool


class RegistrySize(NamedTuple):
    regpath: RegistryPathString
    total_subkeys: int
    total_values: int
