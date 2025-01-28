import sys

from ..logging import internal_logger
from ..schemas.events import InstalledPackages, LoadedModules, ModuleData


def get_installed_packages() -> InstalledPackages:
    loaded_modules = []
    try:
        from importlib import metadata

        for d in metadata.distributions():
            try:
                loaded_modules.append(ModuleData(d.metadata["Name"], d.version))
            except Exception:
                internal_logger.warning(
                    "Failed to get metadata for module", exc_info=True
                )
    except ImportError:
        # Supported in Python 3.8+
        pass

    return InstalledPackages(loaded_modules)


def get_loaded_modules() -> LoadedModules:
    loaded_modules = []

    items = list(sys.modules.items())
    for module_name, module in items:
        version = getattr(module, "__version__", getattr(module, "version", None))
        if isinstance(version, bytes):
            try:
                version = version.decode("utf-8")
            except Exception:
                internal_logger.warning("Failed to decode version", exc_info=True)
                version = None
        elif isinstance(version, int):
            version = str(version)
        elif isinstance(version, float):
            version = str(version)
        elif not isinstance(version, str):
            version = None

        loaded_modules.append(ModuleData(module_name, version))
    return LoadedModules(loaded_modules)
