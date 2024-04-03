from windowsregistry.regpath import RegistryPathString
from windowsregistry.models.enums import RegistryHKEYEnum

# RegistryPathString(
#     "HKEY_CURRENT_USER", "SOFTWARE", "Microsoft\\Windows"
# )
# RegistryPathString(
#     "HKEY_CURRENT_USER\\SOFTWARE", "Microsoft", "Windows"
# )
# RegistryPathString(
#     "HKEY_CURRENT_USER\\SOFTWARE", "Microsoft\\Windows"
# )
# RegistryPathString(
#     "HKEY_CURRENT_USER\\SOFTWARE\\Microsoft\\Windows"
# )
hkcu_soft_mswin = RegistryPathString(
    "SOFTWARE", "Microsoft", "Windows",
    root_key=RegistryHKEYEnum.HKEY_CURRENT_USER
)
print(hkcu_soft_mswin.parent)
print(hkcu_soft_mswin.joinpath("CurrentVersion", "Run"))
print(hkcu_soft_mswin)
