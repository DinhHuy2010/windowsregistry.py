from .models import RegistryPermissionConfig, RegistryAlternateViewType


def get_permission_int(
    permconf: RegistryPermissionConfig
) -> int:
    if permconf.wow64_32key_access:
        alttype = RegistryAlternateViewType.KEY_WOW64_32KEY
    else:
        alttype = RegistryAlternateViewType.KEY_WOW64_64KEY
    return permconf.permission.value | alttype.value
