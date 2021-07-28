# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
from pathlib import Path
from typing import Generator

import appdirs
import pytest
from mockpi import MockPI, Package

import scriptenv

DefaultPackage = Package()


@pytest.fixture
def default_pkg(mockpi: MockPI) -> Generator[Package, None, None]:
    mockpi.add(DefaultPackage)
    yield DefaultPackage


def test_install_package(default_pkg: Package) -> None:
    scriptenv.requires(default_pkg.name)

    __import__(default_pkg.name)


def test_use_cache_dir(default_pkg: Package) -> None:
    cache_path = Path(appdirs.user_cache_dir("scriptenv"))
    download_path = cache_path / "cache"
    install_path = cache_path / "install"
    locks_path = cache_path / "locks"

    assert not cache_path.exists()

    scriptenv.requires(default_pkg.name)

    assert len(list(download_path.iterdir())) == 1
    assert len(list(locks_path.iterdir())) == 1
    assert len(list(install_path.iterdir())) == 1
