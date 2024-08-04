from . import models
from .core import RegistryPath, open_subkey
from .errors import WindowsRegistryError


def _is_windows():
    try:
        import winreg  # type: ignore  # noqa: F401
    except ImportError:
        raise RuntimeError("not running on windows")  # noqa: B904


_is_windows()
del _is_windows  # noqa: E702

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
    "HKEY_CURRENT_USER",
]
