from typing import Sequence, TypeAlias, Union

from .models import RegistryKeyPermissionType

RegistryKeyPermissionTypeArgs: TypeAlias = Union[
    RegistryKeyPermissionType, Sequence[RegistryKeyPermissionType]
]
