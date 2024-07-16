from typing import Optional, Sequence

from .errors import WindowsRegistryError
from .models import RegistryHKEYEnum

REGISTRY_SEP = "\\"


def _determine_root_key(rk: str) -> RegistryHKEYEnum:
    rk = rk.upper()
    if rk.startswith("HK"):
        fullname = {
            "HKCR": "HKEY_CLASSES_ROOT",
            "HKCU": "HKEY_CURRENT_USER",
            "HKLM": "HKEY_LOCAL_MACHINE",
            "HKU": "HKEY_USERS",
        }[rk]
    elif rk.startswith("HKEY_"):
        fullname = rk
    else:
        raise WindowsRegistryError("root key not found")
    return getattr(RegistryHKEYEnum, fullname)


def _parse_parts(paths: Sequence[str]) -> tuple[str, ...]:
    r: list[str] = []
    ps = tuple(paths)
    for p in ps:
        r.extend(p.split(REGISTRY_SEP))
    return tuple(r)


def _parse_paths(
    paths: Sequence[str], root_key: Optional[RegistryHKEYEnum]
) -> tuple[tuple[str, ...], RegistryHKEYEnum]:
    r = _parse_parts(paths)
    rk = root_key
    if rk is None:
        rk = _determine_root_key(r[0])
        r = r[1:]
    return r, rk


class RegistryPathString:
    def __init__(
        self, *paths: str, root_key: Optional[RegistryHKEYEnum] = None
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
        return f"{self.__class__.__name__}({self.fullpath!r})"

    def __str__(self) -> str:
        return self.fullpath
