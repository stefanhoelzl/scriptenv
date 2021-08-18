"""Installs packages and makes them available to import"""

import hashlib
import json
from pathlib import Path
from typing import Iterable, Optional, Set

from . import pip
from .config import Config
from .scriptenv import ScriptEnv


class ScriptEnvBuilder:
    """Builds a environment to import packages within a script."""

    def __init__(self, config: Optional[Config] = None) -> None:
        """Initializes a ScriptEnvBuilder."""
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

    def build(self, requirements: Iterable[str]) -> ScriptEnv:
        """Builds a ScriptEnv."""
        packages = self.fetch_requirements(requirements)
        self.install_packages(packages)
        return ScriptEnv(self.install_path, packages)

    def fetch_requirements(self, requirements: Iterable[str]) -> Set[str]:
        """Resolves a set of requirements and returns a list of packages."""
        lock = hashlib.md5("\n".join(requirements).encode("utf-8")).hexdigest()
        lockfile_path = self.locks_path / lock

        if not lockfile_path.is_file() or not self._config.use_lockfile:
            packages = pip.download(requirements, self.package_cache_path)
            if not self._config.use_lockfile:
                return packages
            lockfile_path.write_text(json.dumps(list(packages), indent=2))
        return set(json.loads(lockfile_path.read_text()))

    def install_packages(self, packages: Iterable[str]) -> None:
        """Installs a set of packages"""
        for package in packages:
            if not (self.install_path / package).exists():
                pip.install(
                    self.package_cache_path / package, self.install_path / package
                )
