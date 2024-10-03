from __future__ import annotations

import pytest
from typing_extensions import Generator

from windowsregistry.core import RegistryPath, open_subkey
from windowsregistry.errors import OperationError
from windowsregistry.models import (
    RegistryHKEYEnum,
    RegistryKeyPermissionType,
    RegistryValueType,
)


@pytest.fixture
def setup_registry() -> Generator[RegistryPath, None, None]:
    """Fixture to set up the registry environment."""
    HKCUSOFT = open_subkey(
        "SOFTWARE",
        root_key=RegistryHKEYEnum.HKEY_CURRENT_USER,
        permission=RegistryKeyPermissionType.KEY_ALL_ACCESS,
    )
    yield HKCUSOFT
    # Clean up the registry after the test
    try:  # noqa: SIM105
        HKCUSOFT.delete_subkey("windowsregistry.py", recursive=True)
    except FileNotFoundError:
        pass

def test_create_and_delete_registry_key(setup_registry: RegistryPath):
    """Test creating and deleting subkeys and values in the registry."""
    HKCUSOFT = setup_registry

    # Create a subkey called 'windowsregistry.py'
    testing = HKCUSOFT.create_subkey("windowsregistry.py", exist_ok=True)
    assert testing is not None

    # Create a subkey 'hello-world' inside 'windowsregistry.py'
    hw = testing.create_subkey("hello-world", exist_ok=True)
    assert hw is not None

    # Create a subkey 'newkey' inside 'hello-world'
    nk = hw.create_subkey("newkey", exist_ok=True)
    assert nk is not None

    # Set a value 'hi' in the 'newkey' subkey
    nk.set_value("hi", "hello, world!", dtype=RegistryValueType.REG_SZ, overwrite=True)
    assert nk.get_value("hi").data == "hello, world!"

    # Delete the value 'hi'
    nk.delete_value("hi")
    with pytest.raises(OperationError):
        nk.get_value("hi")

    # Delete the 'hello-world' subkey recursively
    testing.delete_subkey("hello-world", recursive=True)
    with pytest.raises(OperationError):
        testing.open_subkey("hello-world")
