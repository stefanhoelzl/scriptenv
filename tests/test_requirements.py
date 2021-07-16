# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
from pathlib import Path
from typing import Generator

import appdirs
import pytest
from mockpi import MockPI

import scriptenv

DefaultPackageName = "scriptenvtestpackage"


@pytest.fixture
def mockpi(tmp_path: Path) -> MockPI:
    return MockPI(tmp_path / "mockpi")


@pytest.fixture
def default_pkg(mockpi: MockPI) -> Generator[str, None, None]:
    mockpi.add(DefaultPackageName)
    with mockpi.server():
        yield DefaultPackageName


def test_install_package(default_pkg: str) -> None:
    scriptenv.requires(default_pkg)

    __import__(default_pkg)


def test_install_multiple_packages(mockpi: MockPI) -> None:
    another_package = DefaultPackageName + "another"
    mockpi.add(DefaultPackageName)
    mockpi.add(another_package)

    with mockpi.server():
        scriptenv.requires(DefaultPackageName, another_package)

    __import__(DefaultPackageName)
    __import__(another_package)


def test_install_specific_version(mockpi: MockPI) -> None:
    wanted_version = "0.1.0"
    mockpi.add(DefaultPackageName, version=wanted_version)
    mockpi.add(DefaultPackageName, version="0.2.0")

    with mockpi.server():
        scriptenv.requires(f"{DefaultPackageName}=={wanted_version}")

    assert __import__(DefaultPackageName).__version__ == wanted_version


def test_install_dependencies(mockpi: MockPI) -> None:
    dependency = DefaultPackageName + "dependency"
    mockpi.add(dependency)
    mockpi.add(DefaultPackageName, dependencies=[dependency])

    with mockpi.server():
        scriptenv.requires(DefaultPackageName)

    __import__(dependency)


def test_supported_package_types(mockpi: MockPI) -> None:
    packages = dict(tarpackage="sdist", wheelpackage="bdist_wheel")
    for name, dist_type in packages.items():
        mockpi.add(name, dist_type=dist_type)

    with mockpi.server():
        scriptenv.requires(*packages)

    for package in packages:
        __import__(package)


def test_cache_packages(mockpi: MockPI) -> None:
    version = "0.1.0"
    another_package = DefaultPackageName + "another"
    mockpi.add(DefaultPackageName, version=version)
    mockpi.add(another_package, dependencies=[DefaultPackageName])

    with mockpi.server():
        scriptenv.requires(DefaultPackageName)
        scriptenv.requires(another_package)

    assert mockpi.count_package_requests(DefaultPackageName, version) == 1


def test_cache_dependency_list(mockpi: MockPI) -> None:
    version = "0.1.0"
    mockpi.add(DefaultPackageName, version=version)

    with mockpi.server():
        scriptenv.requires(DefaultPackageName)
        mockpi.reset_requests()
        scriptenv.requires(DefaultPackageName)

    assert mockpi.count_requests() == 0


def test_use_cache_dir(default_pkg: str) -> None:
    cache_path = Path(appdirs.user_cache_dir(scriptenv.__name__, scriptenv.__author__))
    download_path = cache_path / "download"
    install_path = cache_path / "install"

    assert not cache_path.exists()

    scriptenv.requires(default_pkg)

    assert len(list(download_path.iterdir())) == 1
    assert len(list(install_path.iterdir())) == 1


def test_suppess_stdout(default_pkg: str, capsys: pytest.CaptureFixture[str]) -> None:
    scriptenv.requires(default_pkg)

    out, _ = capsys.readouterr()
    assert not out
