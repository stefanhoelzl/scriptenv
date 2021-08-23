"""Installs packages and makes them available to import"""

import os
import sys
from pathlib import Path
from types import ModuleType, TracebackType
from typing import Callable, Iterable, List, Optional, Type


class ScriptEnv:
    """Environment which can be applied to the current runtime."""

    def __init__(self, install_base: Path, packages: Iterable[str]) -> None:
        """Initializes a ScriptEnv."""
        self.packages_path = install_base
        self.packages = list(packages)

    def __enter__(self) -> None:
        self.enable()

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.disable()

    def enable(self) -> None:
        """
        Updates the current runtime to make the packages available.

        sys.path gets updated to support imports.
        PYTHONPATH gets updated to support imports in subprocesses.
        PATH gets updated to support entry points called from subprocesses.
        """
        # first disable to avoid duplicates when already enabled
        self.disable()

        sys.path[0:0] = [str(self.packages_path / pkg) for pkg in self.packages]
        _extend_environ_path(
            "PYTHONPATH", [str(self.packages_path / pkg) for pkg in self.packages]
        )
        _extend_environ_path(
            "PATH", [str(self.packages_path / pkg / "bin") for pkg in self.packages]
        )

    def disable(self) -> None:
        """
        Removes the entries from paths added by calling `self.enable`

        Additionally removes modules from `sys.modules`.
        """
        sys.path = list(filter(self._is_non_scriptenv_path, sys.path))
        _revert_environ_path("PYTHONPATH", self._is_non_scriptenv_path)
        _revert_environ_path("PATH", self._is_non_scriptenv_path)

        for name in list(sys.modules):
            if self._is_scriptenv_module(sys.modules[name]):
                sys.modules.pop(name, None)

    def _is_non_scriptenv_path(self, path: str) -> bool:
        package_paths = [str(self.packages_path / pkg) for pkg in self.packages]
        return not any(
            (
                path.startswith(package_path)
                for package_path in package_paths
                if package_path
            )
        )

    def _is_scriptenv_module(self, module: ModuleType) -> bool:
        if getattr(module, "__file__", None) is None:
            return False
        return not self._is_non_scriptenv_path(module.__file__)


def _extend_environ_path(name: str, items: List[str]) -> None:
    existing_items = os.environ[name].split(os.pathsep) if os.environ.get(name) else []
    os.environ[name] = os.pathsep.join(items + existing_items)


def _revert_environ_path(name: str, check: Callable[[str], bool]) -> None:
    os.environ[name] = os.pathsep.join(
        filter(check, os.environ.get(name, "").split(os.pathsep))
    )
