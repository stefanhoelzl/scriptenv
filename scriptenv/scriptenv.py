"""Installs packages and makes them available to import"""

import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Set

from . import pip


class ScriptEnv:
    """Builds a environment to import packages within a script."""

    def __init__(self, path: Path) -> None:
        """Initializes a ScriptEnv with `path` as cache directory."""
        self._path = path.absolute()
        self.locks_path.mkdir(parents=True, exist_ok=True)

    @property
    def locks_path(self) -> Path:
        """Path where the lock files are stored"""
        return self._path / "locks"

    @property
    def install_path(self) -> Path:
        """Path where the packages are installed"""
        return self._path / "install"

    @property
    def package_cache_path(self) -> Path:
        """Paths where the downloaded packages are cached"""
        return self._path / "cache"

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

        sys.path gets updated so will imports work.
        """
        sys.path[0:0] = [str(self.install_path / pkg) for pkg in packages]
