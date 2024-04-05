from . import models
from .core import RegistryPath, open_subkey
from .errors import WindowsRegistryError

HKCR = HKEY_CLASSES_ROOT = open_subkey("HKCR")
HKCU = HKEY_CURRENT_USER = open_subkey("HKCU")
HKLM = HKEY_LOCAL_MACHINE = open_subkey("HKLM")

__all__ = [
    "models",
    "RegistryPath",
    "open_subkey",
    "WindowsRegistryError",
    "HKCR",
    "HKCU",
    "HKLM",
    "HKEY_CLASSES_ROOT",
    "HKEY_LOCAL_MACHINE",
    "HKEY_CURRENT_USER"
]
