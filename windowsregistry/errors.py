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

from enum import Enum, auto
from typing import Optional


class OperationErrorKind(Enum):
    ON_CREATE = auto()
    ON_READ = auto()
    ON_UPDATE = auto()
    ON_DELETE = auto()

class OperationDataErrorKind(Enum):
    SUBKEY = auto()
    VALUE = auto()

def _to_friendly_from_oek(oek: OperationErrorKind, odek: OperationDataErrorKind) -> str:
    slugs = {
        OperationErrorKind.ON_CREATE: "creating",
        OperationErrorKind.ON_READ: "reading",
        OperationErrorKind.ON_UPDATE: "updating",
        OperationErrorKind.ON_DELETE: "deleting",
    }
    kinds = {
        OperationDataErrorKind.SUBKEY: "subkey",
        OperationDataErrorKind.VALUE: "value"
    }
    return f"on {slugs[oek]} {kinds[odek]}"

class WindowsRegistryError(Exception):
    pass


class OperationError(WindowsRegistryError):
    def __init__(
        self,
        operation: OperationErrorKind,
        kind: OperationDataErrorKind,
        message: str,
        exc: Optional[BaseException] = None,
    ) -> None:
        self.operation = operation
        self.kind = kind
        self.message = message
        self.exc = exc

    def __str__(self) -> str:
        msg = f"error {_to_friendly_from_oek(self.operation, self.kind)}: {self.message}"
        if self.exc:
            msg += f" (from exception: {self.exc!r})"
        return msg

class RegistryPathError(WindowsRegistryError):
    def __init__(self, message: str) -> None:
        self.message = message
    
    def __str__(self) -> str:
        return f"error on parsing path: {self.message}"
