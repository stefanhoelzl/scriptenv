# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from mockpi import DistType, MockPI, Package

from scriptenv import pip
from scriptenv.pip import _pip as pip_exec


@pytest.mark.parametrize("dist_type", list(DistType))
def test_download_packages(dist_type: DistType, mockpi: MockPI, tmp_path: Path) -> None:
    mockpi.add(Package(name="pkg0", dist_type=dist_type))
    mockpi.add(Package(name="pkg1", dist_type=dist_type))

    package_names = pip.download(["pkg0", "pkg1"], tmp_path)

    assert len(package_names) == 2
    for pkg_name in package_names:
        assert (tmp_path / pkg_name).is_file()


def test_download_dependencies(mockpi: MockPI, tmp_path: Path) -> None:
    dep = Package(name="dep")
    mockpi.add(dep)
    mockpi.add(Package(name="pkg", dependencies=[dep]))

    package_names = pip.download(["pkg"], tmp_path)

    assert len(package_names) == 2


def test_download_cached(mockpi: MockPI, tmp_path: Path) -> None:
    mockpi.add(Package(name="pkg"))
    assert pip.download(["pkg"], tmp_path / "cached") == {"pkg-0.1.0.tar.gz"}
    assert pip.download(["pkg"], tmp_path / "cached") == {"pkg-0.1.0.tar.gz"}


@pytest.mark.parametrize("dist_type", list(DistType))
def test_install(dist_type: DistType, tmp_path: Path) -> None:
    install_path = tmp_path / "install"
    pkg = Package(name="pkg", version="0.1.0", dist_type=dist_type)
    dist = pkg.build(tmp_path)

    pip.install(dist, install_path)

    assert (install_path / "pkg.py").is_file()
    assert (install_path / "pkg-0.1.0.dist-info").is_dir()


def test_install_override_user(tmp_path: Path) -> None:
    install_path = tmp_path / "install"
    pkg = Package()
    dist = pkg.build(tmp_path)

    with patch.dict(os.environ, dict(PIP_USER="yes")):
        pip.install(dist, install_path)


def test_install_wheel_with_invalid_file(tmp_path: Path) -> None:
    install_path = tmp_path / "install"
    pkg = Package(dist_type=DistType.WHEEL, body="invalid syntax")
    dist = pkg.build(tmp_path)

    pip.install(dist, install_path)


def test_pip_exit_code() -> None:
    with pytest.raises(pip.PipError):
        pip_exec("cache")


def test_stdout_supression(capsys: pytest.CaptureFixture[str]) -> None:
    pip_exec("help")

    out, _err = capsys.readouterr()
    assert not out
