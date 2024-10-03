# windowsregistry

windowsregistry is a Python library for interacting with the Windows Registry. It provides a high-level interface to manage registry keys and values, abstracting away from the standard library [winreg](https://docs.python.org/3/library/winreg.html)

## Installation

To install the windowsregistry library, you can use pip:

```bash
pip install windowsregistry
```

## Usage

Below is a basic example of how to use the windowsregistry library to interact with the Windows Registry.

```python
from windowsregistry import HKCU
from windowsregistry.models import RegistryValueType

# Open a registry key
reg_key = HKCU.open_subkey(r"Software\MyApp")

# Check if a subkey exists
if reg_key.subkey_exists("Settings"):
	...

# Create a new subkey
new_key = reg_key.create_subkey("NewSettings")

new_key.set_value("MyValue", 1234, dtype=RegistryValueType.REG_DWORD) # Set a value in the registry

my_value = new_key.get_value("MyValue") # Query a value from the registry
print(f"Value: {my_value.data}")

new_key.delete_value("MyValue") # Delete a registry value

reg_key.delete_subkey("NewSettings", recursive=True) # Delete a registry subkey
```

## License

This project is licensed under the MIT License.
