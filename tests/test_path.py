from __future__ import annotations

import pytest

from windowsregistry.errors import RegistryPathError
from windowsregistry.models import RegistryHKEYEnum
from windowsregistry.regpath import (
    RegistryPathString,
    _determine_root_key,  # pyright: ignore[reportPrivateUsage]
    _parse_parts,  # pyright: ignore[reportPrivateUsage]
    _parse_paths,  # pyright: ignore[reportPrivateUsage]
)


def test_determine_root_key_valid():
    # Test valid HK root key abbreviations
    assert _determine_root_key("HKCR") == RegistryHKEYEnum.HKEY_CLASSES_ROOT
    assert _determine_root_key("HKCU") == RegistryHKEYEnum.HKEY_CURRENT_USER
    assert _determine_root_key("HKLM") == RegistryHKEYEnum.HKEY_LOCAL_MACHINE
    assert _determine_root_key("HKU") == RegistryHKEYEnum.HKEY_USERS

    # Test valid full HKEY names
    assert _determine_root_key("HKEY_CLASSES_ROOT") == RegistryHKEYEnum.HKEY_CLASSES_ROOT
    assert _determine_root_key("HKEY_CURRENT_USER") == RegistryHKEYEnum.HKEY_CURRENT_USER


def test_determine_root_key_invalid():
    # Test invalid root key
    with pytest.raises(RegistryPathError):
        _determine_root_key("INVALID")


def test_parse_parts():
    # Test path splitting
    assert _parse_parts(["HKCU\\Software\\Test"]) == ("HKCU", "Software", "Test")
    assert _parse_parts(["HKEY_LOCAL_MACHINE\\System\\CurrentControlSet"]) == (
        "HKEY_LOCAL_MACHINE",
        "System",
        "CurrentControlSet",
    )


def test_parse_paths():
    # Test parsing paths with a root key provided
    paths = ["Software\\Test"]
    root_key = RegistryHKEYEnum.HKEY_CURRENT_USER
    result, rk = _parse_paths(paths, root_key)
    assert result == ("Software", "Test")
    assert rk == RegistryHKEYEnum.HKEY_CURRENT_USER

    # Test parsing paths without a root key (determined by first part of the path)
    paths = ["HKCU\\Software\\Test"]
    result, rk = _parse_paths(paths, None)
    assert result == ("Software", "Test")
    assert rk == RegistryHKEYEnum.HKEY_CURRENT_USER

# @pytest.mark.skip(reason="Not implemented yet")
def test_parse_path_with_forward_slash():
    # Test parsing paths with a root key provided
    paths = ["Software/Test"]
    root_key = RegistryHKEYEnum.HKEY_CURRENT_USER
    result, rk = _parse_paths(paths, root_key)
    assert result == ("Software", "Test")
    assert rk == RegistryHKEYEnum.HKEY_CURRENT_USER

    # Test parsing paths without a root key (determined by first part of the path)
    paths = ["HKCU/Software/Test"]
    result, rk = _parse_paths(paths, None)
    assert result == ("Software", "Test")
    assert rk == RegistryHKEYEnum.HKEY_CURRENT_USER


def test_registry_path_string():
    # Test basic usage of RegistryPathString
    rps = RegistryPathString("Software", "Test", root_key=RegistryHKEYEnum.HKEY_CURRENT_USER)
    assert rps.root_key == RegistryHKEYEnum.HKEY_CURRENT_USER
    assert rps.parts == ("Software", "Test")
    assert rps.path == "Software\\Test"
    assert rps.fullpath == "HKEY_CURRENT_USER\\Software\\Test"


def test_registry_path_string_parent():
    # Test getting the parent path
    rps = RegistryPathString("Software", "Test", root_key=RegistryHKEYEnum.HKEY_CURRENT_USER)
    parent = rps.parent
    assert parent.path == "Software"
    assert parent.fullpath == "HKEY_CURRENT_USER\\Software"


def test_registry_path_string_joinpath():
    # Test joining paths
    rps = RegistryPathString("Software", root_key=RegistryHKEYEnum.HKEY_CURRENT_USER)
    joined = rps.joinpath("Test", "Subkey")
    assert joined.path == "Software\\Test\\Subkey"
    assert joined.fullpath == "HKEY_CURRENT_USER\\Software\\Test\\Subkey"


def test_registry_path_string_repr_str():
    # Test __repr__ and __str__
    rps = RegistryPathString("Software", "Test", root_key=RegistryHKEYEnum.HKEY_CURRENT_USER)
    assert repr(rps) == r"RegistryPathString('HKEY_CURRENT_USER\\Software\\Test')"
    assert str(rps) == "HKEY_CURRENT_USER\\Software\\Test"
