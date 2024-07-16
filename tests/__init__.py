from windowsregistry.core import open_subkey
from windowsregistry.models import (
    RegistryHKEYEnum,
    RegistryKeyPermissionType,
    RegistryValueType,
)


def main():
    HKCUSOFT = open_subkey(
        "SOFTWARE",
        root_key=RegistryHKEYEnum.HKEY_CURRENT_USER,
        permission=RegistryKeyPermissionType.KEY_ALL_ACCESS,
    )
    testing = HKCUSOFT.create_subkey("windowsregistry.py", exist_ok=True)
    hw = testing.create_subkey("hello-world", exist_ok=True)
    nk = hw.create_subkey("newkey", exist_ok=True)
    nk.set_value("hi", "hello, world!", dtype=RegistryValueType.REG_SZ, overwrite=True)
    input("press enter to continue...")
    nk.delete_value("hi")
    testing.delete_subkey("hello-world", recursive=True)


if __name__ == "__main__":
    main()
