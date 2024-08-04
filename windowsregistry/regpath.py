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

from typing import Final, Optional, Sequence

from .errors import RegistryPathError
from .models import RegistryHKEYEnum

REGISTRY_SEP: Final[str] = "\\"


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
        raise RegistryPathError("root key not found")
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
        if not self.parts:
            return self.root_key.name
        return self.parts[-1]

    def joinpath(self, *paths: str) -> "RegistryPathString":
        parts = [*self.parts, *_parse_parts(paths)]
        return self.__class__(*parts, root_key=self.root_key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.fullpath!r})"

    def __str__(self) -> str:
        return self.fullpath
