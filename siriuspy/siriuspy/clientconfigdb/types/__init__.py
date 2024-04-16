"""Types subpackage."""

import pkgutil as _pkgutil

CONFIG_TYPES = []

for loader, module_name, is_pkg in _pkgutil.walk_packages(__path__):
    CONFIG_TYPES.append(module_name)

__all__ = CONFIG_TYPES
