"""Installs packages and makes them available to import"""

import os
import sys
from pathlib import Path
from typing import Iterable, List


# pylint: disable=too-few-public-methods
class ScriptEnv:
    """Environment which can be applied to the current runtime."""

    def __init__(self, install_base: Path, packages: Iterable[str]) -> None:
        """Initializes a ScriptEnv."""
        self.packages_path = install_base
        self.packages = list(packages)

    def update_runtime(self) -> None:
        """
        Updates the current runtime to make the packages available.

        sys.path gets updated to support imports.
        PYTHONPATH gets updated to support imports in subprocesses.
        PATH gets updated to support entry points called from subprocesses.
        """

        def extend_environ_path(name: str, items: List[str]) -> None:
            existing_items = (
                os.environ[name].split(os.pathsep) if name in os.environ else list()
            )
            os.environ[name] = os.pathsep.join(items + existing_items)

        sys.path[0:0] = [str(self.packages_path / pkg) for pkg in self.packages]
        extend_environ_path(
            "PYTHONPATH", [str(self.packages_path / pkg) for pkg in self.packages]
        )
        extend_environ_path(
            "PATH", [str(self.packages_path / pkg / "bin") for pkg in self.packages]
        )
