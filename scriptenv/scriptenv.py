"""Installs packages and makes them available to import"""

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Set

from . import pip
from .config import Config


class ScriptEnv:
    """Builds a environment to import packages within a script."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initializes a ScriptEnv with `path` as cache directory."""
        self._config = config or Config()
        self.locks_path.mkdir(parents=True, exist_ok=True)

    @property
    def locks_path(self) -> Path:
        """Path where the lock files are stored"""
        return self._config.cache_path / "locks"

    @property
    def install_path(self) -> Path:
        """Path where the packages are installed"""
        return self._config.cache_path / "install"

    @property
    def package_cache_path(self) -> Path:
        """Paths where the downloaded packages are cached"""
        return self._config.cache_path / "cache"

    def apply(self, requirements: Iterable[str]) -> None:
        """Applies requirements to the current runtime."""
        packages = self.fetch_requirements(requirements)
        self.install_packages(packages)
        self.update_runtime(packages)

    def fetch_requirements(self, requirements: Iterable[str]) -> Set[str]:
        """Resolves a set of requirements and returns a list of packages."""
        lock = hashlib.md5("\n".join(requirements).encode("utf-8")).hexdigest()
        lockfile_path = self.locks_path / lock

        if not lockfile_path.is_file():
            packages = pip.download(requirements, self.package_cache_path)
            lockfile_path.write_text(json.dumps(list(packages), indent=2))

        return set(json.loads(lockfile_path.read_text()))

    def install_packages(self, packages: Iterable[str]) -> None:
        """Installs a set of packages"""
        for package in packages:
            if not (self.install_path / package).exists():
                pip.install(
                    self.package_cache_path / package, self.install_path / package
                )

    def update_runtime(self, packages: Iterable[str]) -> None:
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

        sys.path[0:0] = [str(self.install_path / pkg) for pkg in packages]
        extend_environ_path(
            "PYTHONPATH", [str(self.install_path / pkg) for pkg in packages]
        )
        extend_environ_path(
            "PATH", [str(self.install_path / pkg / "bin") for pkg in packages]
        )
