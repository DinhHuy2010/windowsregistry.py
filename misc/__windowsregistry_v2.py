# Single file version of "windowsregistry" package
# version: 0.0.2

import enum
import winreg
from collections import deque
from functools import partial
from typing import (
    Any,
    Iterable,
    Optional,
    Sequence,
    Union,
    Iterator,
    cast,
    NamedTuple
)

REGISTRY_SEP = "\\"



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

class RegistryPermissionConfig(NamedTuple):
    permission: RegistryKeyPermissionType
    wow64_32key_access: bool

class WindowsRegistryError(Exception):
    pass


def _get_permission_int(
    permconf: RegistryPermissionConfig
) -> int:
    if permconf.wow64_32key_access:
        alttype = RegistryAlternateViewType.KEY_WOW64_32KEY
    else:
        alttype = RegistryAlternateViewType.KEY_WOW64_64KEY
    return permconf.permission.value | alttype.value

def _determine_root_key(rk: str) -> RegistryHKEYEnum:
    if rk.startswith("HKEY_"):
        return getattr(RegistryHKEYEnum, rk)
    raise WindowsRegistryError("root key not found")

def _parse_parts(paths):
    r = []
    ps = tuple(paths)
    for p in ps:
        if isinstance(p, str):
            r.extend(p.split(REGISTRY_SEP))
    return tuple(r)

def _parse_paths(paths, root_key: Optional[RegistryHKEYEnum]) -> tuple[tuple[str, ...], RegistryHKEYEnum]:
    r = _parse_parts(paths)
    rk = root_key
    if rk is None:
        rk = _determine_root_key(r[0])
        r = r[1:]
    return r, rk

class _lowlevel:
    def __init__(self, *, permconf: RegistryPermissionConfig) -> None:
        self._permconf = permconf
        self._access = _get_permission_int(self._permconf)

    def open_subkey(self, handler, path: str):
        return winreg.OpenKeyEx(handler, path, access=self._access)

    def query_subkey(self, handler) -> tuple[int, int, int]:
        return winreg.QueryInfoKey(handler)
    
    def subkey_from_index(self, handler, index: int) -> str:
        return winreg.EnumKey(handler, index)
    
    def create_subkey(self, handler, subkey: str):
        winreg.CreateKeyEx(handler, subkey, access=self._access)

    def delete_subkey(self, handler, subkey: str):
        winreg.DeleteKeyEx(handler, subkey, access=self._access)

    def query_value(self, handler, name: str):
        return winreg.QueryValueEx(handler, name)
    
    def set_value(self, handler, name: str, dtype: int, data: Any):
        winreg.SetValueEx(handler, name, 0, dtype, data)

    def delete_value(self, handler, name: str):
        winreg.DeleteValue(handler, name)

    def value_from_index(self, handler, index: int) -> tuple[str, Any, int]:
        return winreg.EnumValue(handler, index)



class RegistryPathString:
    def __init__(
        self,
        *paths: str,
        root_key: Optional[RegistryHKEYEnum] = None
    ) -> None:
        parts, rk = _parse_paths(paths, root_key)
        self._root_key = rk
        self._parts = parts

    @property
    def root_key(self) -> RegistryHKEYEnum:
        return self._root_key
    
    @property
    def parts(self) -> tuple[str, ...]:
        return self._parts
    
    @property
    def path(self) -> str:
        return REGISTRY_SEP.join(self.parts)

    @property
    def fullpath(self) -> str:
        return REGISTRY_SEP.join([self.root_key.name, *self.parts])
    
    @property
    def parent(self) -> "RegistryPathString":
        parts = self.parts[:-1]
        return self.__class__(*parts, root_key=self.root_key)
    
    @property
    def name(self) -> str:
        return self.parts[-1]
    
    def joinpath(self, *paths: str) -> "RegistryPathString":
        parts = [*self.parts, *_parse_parts(paths)]
        return self.__class__(*parts, root_key=self.root_key)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.fullpath})"
    
    def __str__(self) -> str:
        return self.fullpath

class WindowsRegistryHandler:
    def __init__(
        self,
        subkey: Union[str, Sequence[str], None] = None,
        *,
        root_key: Optional[RegistryHKEYEnum] = None,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        if subkey is None:
            subkey = []
        elif isinstance(subkey, str):
            subkey = [subkey]
        if permission is None:
            permission = RegistryKeyPermissionType.KEY_READ
        self._regpath = RegistryPathString(*subkey, root_key=root_key)
        self._ll = _lowlevel(
            permconf=RegistryPermissionConfig(
                permission=permission, wow64_32key_access=wow64_32key_access
            )
        )
        self._winreg_handler = self._ll.open_subkey(
            self._regpath.root_key.value, self._regpath.path
        )
        self._winreg_query = RegistryInfoKey(
            *self._ll.query_subkey(self._winreg_handler)
        )

    @property
    def winreg_handler(self) -> winreg.HKEYType:
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
            permission=self._ll._permconf.permission,
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
            raise WindowsRegistryError(f"error: {exc}")

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
            raise WindowsRegistryError(f"error: {exc}")

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
            raise WindowsRegistryError(f"error: {exc}")

    def delete_value(self, name: str) -> None:
        try:
            self._ll.delete_value(self._winreg_handler, name)
        except OSError as exc:
            raise WindowsRegistryError(f"error: {exc}")



class RegistryPath:
    def __init__(
        self,
        subkey: Union[None, str, list[str]] = None,
        *,
        root_key: Optional[RegistryHKEYEnum] = None,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: bool = False,
    ) -> None:
        self._backend = WindowsRegistryHandler(
            subkey=subkey,
            root_key=root_key,
            permission=permission,
            wow64_32key_access=wow64_32key_access,
        )

    @property
    def regpath(self) -> RegistryPathString:
        return self._backend._regpath

    def open_subkey(
        self,
        *paths: str,
        permission: Optional[RegistryKeyPermissionType] = None,
        wow64_32key_access: Optional[bool] = None,
    ) -> "RegistryPath":
        permission = (
            permission
            if permission is not None
            else self._backend._ll._permconf.permission
        )
        wow64_32key_access = (
            wow64_32key_access
            if wow64_32key_access is not None
            else self._backend._ll._permconf.wow64_32key_access
        )
        resolved_path = self.regpath.joinpath(*paths)
        return open_subkey(
            *resolved_path.parts,
            root_key=resolved_path.root_key,
            permission=permission,
            wow64_32key_access=wow64_32key_access
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
        return f"<{self.__class__.__name__}: {self.regpath.fullpath} at {hex(id(self))}>"

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
