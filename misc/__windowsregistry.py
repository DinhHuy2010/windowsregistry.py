# Single file version of "windowsregistry" package
# version: undefined

import enum
import winreg
from collections import deque
from functools import partial
from typing import Any, Iterable, Iterator, NamedTuple, Optional, Union, cast

__all__ = [
    "OtherRegistryType",
    "RegistryAlternateViewType",
    "RegistryHKEYEnum",
    "RegistryInfoKey",
    "RegistryPath",
    "RegistryKeyPermissionType",
    "RegistryValueType",
    "RegistryValue",
    "WindowsRegistryError",
    "open_subkey",
]

class WindowsRegistryError(Exception):
    pass

def _get_permission_int(
    permission: "RegistryKeyPermissionType", wow64_32key_access: bool
) -> int:
    if wow64_32key_access:
        alttype = RegistryAlternateViewType.KEY_WOW64_32KEY
    else:
        alttype = RegistryAlternateViewType.KEY_WOW64_64KEY
    return permission.value | alttype.value

class RegistryHKEYEnum(enum.Enum):
    HKEY_CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_USERS = winreg.HKEY_USERS
    HKEY_PERFORMANCE_DATA = winreg.HKEY_PERFORMANCE_DATA
    HKEY_CURRENT_CONFIG = winreg.HKEY_CURRENT_CONFIG
    HKEY_DYN_DATA = winreg.HKEY_DYN_DATA

class RegistryKeyPermissionType(enum.Enum):
    KEY_ALL_ACCESS = winreg.KEY_ALL_ACCESS
    KEY_WRITE = winreg.KEY_WRITE
    KEY_READ = winreg.KEY_READ
    KEY_EXECUTE = winreg.KEY_EXECUTE
    KEY_QUERY_VALUE = winreg.KEY_QUERY_VALUE
    KEY_SET_VALUE = winreg.KEY_SET_VALUE
    KEY_CREATE_SUB_KEY = winreg.KEY_CREATE_SUB_KEY
    KEY_ENUMERATE_SUB_KEYS = winreg.KEY_ENUMERATE_SUB_KEYS
    KEY_NOTIFY = winreg.KEY_NOTIFY
    KEY_CREATE_LINK = winreg.KEY_CREATE_LINK

class RegistryAlternateViewType(enum.Enum):
    KEY_WOW64_64KEY = winreg.KEY_WOW64_64KEY
    KEY_WOW64_32KEY = winreg.KEY_WOW64_32KEY

class RegistryValueType(enum.Enum):
    REG_BINARY = winreg.REG_BINARY
    REG_DWORD = winreg.REG_DWORD
    REG_DWORD_LITTLE_ENDIAN = winreg.REG_DWORD_LITTLE_ENDIAN
    REG_DWORD_BIG_ENDIAN = winreg.REG_DWORD_BIG_ENDIAN
    REG_EXPAND_SZ = winreg.REG_EXPAND_SZ
    REG_LINK = winreg.REG_LINK
    REG_MULTI_SZ = winreg.REG_MULTI_SZ
    REG_NONE = winreg.REG_NONE
    REG_QWORD = winreg.REG_QWORD
    REG_QWORD_LITTLE_ENDIAN = winreg.REG_QWORD_LITTLE_ENDIAN
    REG_RESOURCE_LIST = winreg.REG_RESOURCE_LIST
    REG_FULL_RESOURCE_DESCRIPTOR = winreg.REG_FULL_RESOURCE_DESCRIPTOR
    REG_RESOURCE_REQUIREMENTS_LIST = winreg.REG_RESOURCE_REQUIREMENTS_LIST
    REG_SZ = winreg.REG_SZ

class OtherRegistryType(enum.IntEnum):
    REG_CREATED_NEW_KEY = winreg.REG_CREATED_NEW_KEY
    REG_LEGAL_CHANGE_FILTER = winreg.REG_LEGAL_CHANGE_FILTER
    REG_LEGAL_OPTION = winreg.REG_LEGAL_OPTION
    REG_NOTIFY_CHANGE_ATTRIBUTES = winreg.REG_NOTIFY_CHANGE_ATTRIBUTES
    REG_NOTIFY_CHANGE_LAST_SET = winreg.REG_NOTIFY_CHANGE_LAST_SET
    REG_NOTIFY_CHANGE_NAME = winreg.REG_NOTIFY_CHANGE_NAME
    REG_NOTIFY_CHANGE_SECURITY = winreg.REG_NOTIFY_CHANGE_SECURITY
    REG_NO_LAZY_FLUSH = winreg.REG_NO_LAZY_FLUSH
    REG_OPENED_EXISTING_KEY = winreg.REG_OPENED_EXISTING_KEY
    REG_OPTION_BACKUP_RESTORE = winreg.REG_OPTION_BACKUP_RESTORE
    REG_OPTION_CREATE_LINK = winreg.REG_OPTION_CREATE_LINK
    REG_OPTION_NON_VOLATILE = winreg.REG_OPTION_NON_VOLATILE
    REG_OPTION_OPEN_LINK = winreg.REG_OPTION_OPEN_LINK
    REG_OPTION_RESERVED = winreg.REG_OPTION_RESERVED
    REG_OPTION_VOLATILE = winreg.REG_OPTION_VOLATILE
    REG_REFRESH_HIVE = winreg.REG_REFRESH_HIVE
    REG_WHOLE_HIVE_VOLATILE = winreg.REG_WHOLE_HIVE_VOLATILE

class RegistryInfoKey(NamedTuple):
    total_subkeys: int
    total_values: int
    last_modified: int

class RegistryValue(NamedTuple):
    value_name: str
    data: Any
    dtype: RegistryValueType

class WindowsRegistryHandler:
    def __init__(
        self,
        root_key: RegistryHKEYEnum,
        subkey: Union[str, list[str], None] = None,
        *,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        if subkey is None:
            subkey = []
        elif isinstance(subkey, str):
            subkey = [subkey]
        if permission is None:
            permission = RegistryKeyPermissionType.KEY_READ
        self.root_key = root_key
        self.subkey = subkey
        self.permission = permission
        self.wow64_32key_access = wow64_32key_access
        self._winreg_handler = winreg.OpenKey(
            self.root_key.value, "\\".join(self.subkey), access=self.permission_int
        )
        self._winreg_query = RegistryInfoKey(*winreg.QueryInfoKey(self._winreg_handler))
        self._parts = [self.root_key.name, *self.subkey]

    @property
    def winreg_handler(self) -> winreg.HKEYType:
        return self._winreg_handler

    @property
    def winreg_query(self) -> RegistryInfoKey:
        return self._winreg_query

    @property
    def permission_int(self) -> int:
        return _get_permission_int(self.permission, self.wow64_32key_access)

    def itersubkeys(self) -> Iterable[str]:
        yield from map(
            partial(winreg.EnumKey, self.winreg_handler),
            range(self.winreg_query.total_subkeys),
        )

    def itervalues(self) -> Iterable[tuple[str, Any, int]]:
        yield from map(
            partial(winreg.EnumValue, self.winreg_handler),
            range(self.winreg_query.total_values),
        )

    def resolve_path(self, new: list[str]) -> list[str]:
        newpath = [*self._parts[1:], *new]
        f = "\\".join(newpath)
        if not self.subkey_exists("\\".join(new)):
            raise WindowsRegistryError(
                f"registry path {f!r} does not exists or failed to open"
            )
        return newpath

    def new_handler_from_path(
        self, subkey_parts: list[str]
    ) -> "WindowsRegistryHandler":
        return self.__class__(
            self.root_key,
            subkey_parts,
            permission=self.permission,
            wow64_32key_access=self.wow64_32key_access,
        )

    def subkey_exists(self, subkey: str):
        try:
            winreg.OpenKey(self.winreg_handler, subkey)
            return True
        except OSError:
            return False

    def new_subkey(self, subkey: str):
        try:
            winreg.CreateKeyEx(self.winreg_handler, subkey, access=self.permission_int)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}")

    def delete_subkey_tree(self, subkey: str, recursive: bool):
        af = self.resolve_path([subkey])
        af_handler = self.new_handler_from_path(af)
        if af_handler.winreg_query.total_subkeys != 0:
            if not recursive:
                raise WindowsRegistryError("cannot delete subkeys inside subkey")
            for subaf in af_handler.itersubkeys():
                af_handler.delete_subkey_tree(subaf, recursive=True)
        try:
            winreg.DeleteKeyEx(self.winreg_handler, subkey, access=self.permission_int)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}")

    def value_exists(self, name: str):
        try:
            winreg.QueryValueEx(self.winreg_handler, name)
            return True
        except OSError:
            return False

    def query_value(self, name: str) -> tuple[str, Any, int]:
        return (
            name,
            *winreg.QueryValueEx(self.winreg_handler, name)
        )

    def set_value(self, name: str, dtype: int, data: Any) -> None:
        try:
            winreg.SetValueEx(self.winreg_handler, name, 0, dtype, data)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}")

    def delete_value(self, name: str) -> None:
        try:
            winreg.DeleteValue(self._winreg_handler, name)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}")

class RegistryPath:
    def __init__(
        self,
        root_key: RegistryHKEYEnum,
        subkey: Union[None, str, list[str]] = None,
        *,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        self._backend = WindowsRegistryHandler(
            root_key=root_key,
            subkey=subkey,
            permission=permission,
            wow64_32key_access=wow64_32key_access,
        )

    @property
    def registry_path(self) -> str:
        return "\\".join(self._backend._parts[1:])

    @property
    def full_registry_path(self) -> str:
        return "\\".join(self._backend._parts)

    @property
    def subkey(self) -> str:
        return self._backend._parts[-1]

    @property
    def parent(self) -> Optional["RegistryPath"]:
        subkey = self._backend._parts[0:][:-1]
        if not subkey:
            return None
        return self.__class__(self._backend.root_key, subkey)

    def open_subkey(
        self,
        *path: str,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: Optional[bool] = None,
    ) -> "RegistryPath":
        permission = permission if permission is not None else self._backend.permission
        wow64_32key_access = (
            wow64_32key_access
            if wow64_32key_access is not None
            else self._backend.wow64_32key_access
        )
        resolved_path = (*self._backend._parts, *path)
        return open_subkey(
            *resolved_path, permission=permission, wow64_32key_access=wow64_32key_access
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
            raise WindowsRegistryError(f"subkey {subkey!r} already exists")
        self._backend.new_subkey(subkey)
        return self.open_subkey(subkey)

    def delete_subkey(self, subkey: str, *, recursive: bool = False) -> None:
        if not self.subkey_exists(subkey):
            raise WindowsRegistryError(f"subkey {subkey!r} does not exists")
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
            raise WindowsRegistryError(f"value name {name!r} already exists")
        self._backend.set_value(name, dtype.value, data)
        return self.get_value(name)

    def delete_value(self, name: str) -> None:
        if not self.value_exists(name):
            raise WindowsRegistryError(f"value name {name!r} does not exists")
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

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.full_registry_path}, permission={self._backend.permission} at {hex(id(self))}>"

def open_subkey(
    *path: str,
    root_key: Optional[RegistryHKEYEnum] = None,
    permission: Optional[RegistryKeyPermissionType] = None,
    wow64_32key_access: bool = False,
) -> RegistryPath:
    if root_key is None:
        if path[0].startswith("HKEY_"):
            root_key = cast(RegistryHKEYEnum, getattr(RegistryHKEYEnum, path[0]))
            path = path[1:]
        else:
            raise ValueError("root key not defined")
    return RegistryPath(
        root_key=root_key,
        subkey=list(path),
        permission=permission,
        wow64_32key_access=wow64_32key_access,
    )

