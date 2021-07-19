# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
from pathlib import Path
from typing import Generator

import appdirs
import pytest
from mockpi import MockPI, Package

import scriptenv

DefaultPackage = Package()


@pytest.fixture
def mockpi(tmp_path: Path) -> MockPI:
    return MockPI(tmp_path / "mockpi")


@pytest.fixture
def default_pkg(mockpi: MockPI) -> Generator[Package, None, None]:
    mockpi.add(DefaultPackage)
    with mockpi.server():
        yield DefaultPackage


def test_install_package(default_pkg: Package) -> None:
    scriptenv.requires(default_pkg.name)

    __import__(default_pkg.name)


def test_install_multiple_packages(mockpi: MockPI) -> None:
    another_package = Package(name="another")
    mockpi.add(DefaultPackage)
    mockpi.add(another_package)

    with mockpi.server():
        scriptenv.requires(DefaultPackage.name, another_package.name)

    __import__(DefaultPackage.name)
    __import__(another_package.name)


def test_install_specific_version(mockpi: MockPI) -> None:
    wanted = Package(version="0.1.0")
    mockpi.add(wanted)
    mockpi.add(Package(version="0.2.0"))

    with mockpi.server():
        scriptenv.requires(f"{wanted.name}=={wanted.version}")

    assert __import__(wanted.name).__version__ == wanted.version


def test_install_dependencies(mockpi: MockPI) -> None:
    dependency = Package("dependency")
    package = Package(dependencies=[dependency])
    mockpi.add(dependency)
    mockpi.add(package)

    with mockpi.server():
        scriptenv.requires(package.name)

    __import__(dependency.name)


@pytest.mark.parametrize("dist_type", ["sdist", "bdist_wheel"])
def test_supported_package_types(mockpi: MockPI, dist_type: str) -> None:
    package = Package(dist_type=dist_type)
    mockpi.add(package)

    with mockpi.server():
        scriptenv.requires(package.name)

    __import__(package.name)


def test_cache_packages(mockpi: MockPI) -> None:
    cached_package = Package(version="0.1.0")
    another_package = Package(name="another", dependencies=[cached_package])
    mockpi.add(cached_package)
    mockpi.add(another_package)

    with mockpi.server():
        scriptenv.requires(cached_package.name)
        scriptenv.requires(another_package.name)

    assert mockpi.count_package_requests(cached_package) == 1


def test_cache_dependency_list(mockpi: MockPI) -> None:
    mockpi.add(DefaultPackage)

    with mockpi.server():
        scriptenv.requires(DefaultPackage.name)
        mockpi.reset_requests()
        scriptenv.requires(DefaultPackage.name)

    assert mockpi.count_requests() == 0


def test_use_cache_dir(default_pkg: Package) -> None:
    cache_path = Path(appdirs.user_cache_dir(scriptenv.__name__))
    download_path = cache_path / "download"
    install_path = cache_path / "install"

    assert not cache_path.exists()

    scriptenv.requires(default_pkg.name)

    assert len(list(download_path.iterdir())) == 1
    assert len(list(install_path.iterdir())) == 1


def test_suppess_stdout(
    default_pkg: Package, capsys: pytest.CaptureFixture[str]
) -> None:
    scriptenv.requires(default_pkg.name)

    out, _ = capsys.readouterr()
    assert not out


def test_package_contains_invalid_python_file(mockpi: MockPI) -> None:
    package = Package(dist_type="bdist_wheel", body="invalid syntax")
    mockpi.add(package)

    with mockpi.server():
        scriptenv.requires(package.name)

    with pytest.raises(SyntaxError):
        __import__(package.name)
