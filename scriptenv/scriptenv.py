"""Installs packages and makes them available to import"""

import os
import sys
from pathlib import Path
from typing import Iterable, List


class ScriptEnv:
    """Environment which can be applied to the current runtime."""

    def __init__(self, install_base: Path, packages: Iterable[str]) -> None:
        """Initializes a ScriptEnv."""
        self.packages_path = install_base
        self.packages = list(packages)

    def enable(self) -> None:
        """
        Updates the current runtime to make the packages available.

        sys.path gets updated to support imports.
        PYTHONPATH gets updated to support imports in subprocesses.
        PATH gets updated to support entry points called from subprocesses.
        """
        # first disable to avoid duplicates when already enabled
        self.disable()

        def extend_environ_path(name: str, items: List[str]) -> None:
            existing_items = (
                os.environ[name].split(os.pathsep) if os.environ.get(name) else list()
            )
            os.environ[name] = os.pathsep.join(items + existing_items)

        sys.path[0:0] = [str(self.packages_path / pkg) for pkg in self.packages]
        extend_environ_path(
            "PYTHONPATH", [str(self.packages_path / pkg) for pkg in self.packages]
        )
        extend_environ_path(
            "PATH", [str(self.packages_path / pkg / "bin") for pkg in self.packages]
        )

    def disable(self) -> None:
        """Removes the entries from paths added by calling `self.enable`"""
        package_paths = [str(self.packages_path / pkg) for pkg in self.packages]

        def is_non_scriptenv_path(path: str) -> bool:
            return not any(
                (
                    path.startswith(package_path)
                    for package_path in package_paths
                    if package_path
                )
            )

        def revert_environ_path(name: str) -> None:
            os.environ[name] = os.pathsep.join(
                filter(
                    is_non_scriptenv_path, os.environ.get(name, "").split(os.pathsep)
                )
            )

        sys.path = list(filter(is_non_scriptenv_path, sys.path))
        revert_environ_path("PYTHONPATH")
        revert_environ_path("PATH")
