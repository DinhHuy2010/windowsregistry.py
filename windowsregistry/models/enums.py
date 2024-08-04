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

import enum
import winreg


class RegistryHKEYEnum(enum.Enum):
    HKEY_CLASSES_ROOT = winreg.HKEY_CLASSES_ROOT
    HKEY_CURRENT_USER = winreg.HKEY_CURRENT_USER
    HKEY_LOCAL_MACHINE = winreg.HKEY_LOCAL_MACHINE
    HKEY_USERS = winreg.HKEY_USERS
    HKEY_PERFORMANCE_DATA = winreg.HKEY_PERFORMANCE_DATA
    HKEY_CURRENT_CONFIG = winreg.HKEY_CURRENT_CONFIG
    HKEY_DYN_DATA = winreg.HKEY_DYN_DATA


class RegistryKeyPermissionType(enum.Enum):
    KEY_ALL_ACCESS = winreg.KEY_ALL_ACCESS
    KEY_WRITE = winreg.KEY_WRITE
    KEY_READ = winreg.KEY_READ
    KEY_EXECUTE = winreg.KEY_EXECUTE
    KEY_QUERY_VALUE = winreg.KEY_QUERY_VALUE
    KEY_SET_VALUE = winreg.KEY_SET_VALUE
    KEY_CREATE_SUB_KEY = winreg.KEY_CREATE_SUB_KEY
    KEY_ENUMERATE_SUB_KEYS = winreg.KEY_ENUMERATE_SUB_KEYS
    KEY_NOTIFY = winreg.KEY_NOTIFY
    KEY_CREATE_LINK = winreg.KEY_CREATE_LINK


class RegistryAlternateViewType(enum.Enum):
    KEY_WOW64_64KEY = winreg.KEY_WOW64_64KEY
    KEY_WOW64_32KEY = winreg.KEY_WOW64_32KEY


class RegistryValueType(enum.Enum):
    REG_BINARY = winreg.REG_BINARY
    REG_DWORD = winreg.REG_DWORD
    REG_DWORD_LITTLE_ENDIAN = winreg.REG_DWORD_LITTLE_ENDIAN
    REG_DWORD_BIG_ENDIAN = winreg.REG_DWORD_BIG_ENDIAN
    REG_EXPAND_SZ = winreg.REG_EXPAND_SZ
    REG_LINK = winreg.REG_LINK
    REG_MULTI_SZ = winreg.REG_MULTI_SZ
    REG_NONE = winreg.REG_NONE
    REG_QWORD = winreg.REG_QWORD
    REG_QWORD_LITTLE_ENDIAN = winreg.REG_QWORD_LITTLE_ENDIAN
    REG_RESOURCE_LIST = winreg.REG_RESOURCE_LIST
    REG_FULL_RESOURCE_DESCRIPTOR = winreg.REG_FULL_RESOURCE_DESCRIPTOR
    REG_RESOURCE_REQUIREMENTS_LIST = winreg.REG_RESOURCE_REQUIREMENTS_LIST
    REG_SZ = winreg.REG_SZ


class OtherRegistryType(enum.IntEnum):
    REG_CREATED_NEW_KEY = winreg.REG_CREATED_NEW_KEY
    REG_LEGAL_CHANGE_FILTER = winreg.REG_LEGAL_CHANGE_FILTER
    REG_LEGAL_OPTION = winreg.REG_LEGAL_OPTION
    REG_NOTIFY_CHANGE_ATTRIBUTES = winreg.REG_NOTIFY_CHANGE_ATTRIBUTES
    REG_NOTIFY_CHANGE_LAST_SET = winreg.REG_NOTIFY_CHANGE_LAST_SET
    REG_NOTIFY_CHANGE_NAME = winreg.REG_NOTIFY_CHANGE_NAME
    REG_NOTIFY_CHANGE_SECURITY = winreg.REG_NOTIFY_CHANGE_SECURITY
    REG_NO_LAZY_FLUSH = winreg.REG_NO_LAZY_FLUSH
    REG_OPENED_EXISTING_KEY = winreg.REG_OPENED_EXISTING_KEY
    REG_OPTION_BACKUP_RESTORE = winreg.REG_OPTION_BACKUP_RESTORE
    REG_OPTION_CREATE_LINK = winreg.REG_OPTION_CREATE_LINK
    REG_OPTION_NON_VOLATILE = winreg.REG_OPTION_NON_VOLATILE
    REG_OPTION_OPEN_LINK = winreg.REG_OPTION_OPEN_LINK
    REG_OPTION_RESERVED = winreg.REG_OPTION_RESERVED
    REG_OPTION_VOLATILE = winreg.REG_OPTION_VOLATILE
    REG_REFRESH_HIVE = winreg.REG_REFRESH_HIVE
    REG_WHOLE_HIVE_VOLATILE = winreg.REG_WHOLE_HIVE_VOLATILE
