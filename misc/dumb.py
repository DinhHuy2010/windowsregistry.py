from importlib import import_module
from inspect import getsource
import pathlib
import pkgutil
import sysconfig
from types import ModuleType

stacks = [import_module("windowsregistry")]
modules: dict[str, ModuleType] = {}

while stacks:
    pkg = stacks.pop(0)
    modules[pkg.__name__] = pkg
    for mod in pkgutil.iter_modules(pkg.__path__):
        name = mod.name
        try:
            rmod = import_module(f"{pkg.__name__}.{name}")
            modules[rmod.__name__] = rmod
        except Exception:
            continue
        else:
            if mod.ispkg:
                stacks.append(rmod)

curr = pathlib.Path(sysconfig.get_path("platlib"))

for mod in modules.values():
    print(f"# mod: ({mod.__name__})")
    try:
        print("# START SOURCE CODE -------------------")
        print(getsource(mod))
    except OSError:
        print("# FAIL TO GET SOURCE CODE -------------------")
        continue
    print("# END SOURCE CODE -------------------")
