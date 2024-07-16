from .models import RegistryAlternateViewType, RegistryPermissionConfig


def get_permission_int(permconf: RegistryPermissionConfig) -> int:
    if permconf.wow64_32key_access:
        alttype = RegistryAlternateViewType.KEY_WOW64_32KEY
    else:
        alttype = RegistryAlternateViewType.KEY_WOW64_64KEY
    fr, *rn = permconf.permissions
    v = fr.value
    for r in rn:
        v |= r.value
    return v | alttype.value
