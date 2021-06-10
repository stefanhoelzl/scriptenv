# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
from pathlib import Path
from typing import Generator

from mockpi import MockPI

import pytest

import scriptenv


DefaultPackageName = "scriptenvtestpackage"


@pytest.fixture
def mockpi(tmp_path: Path) -> MockPI:
    return MockPI(tmp_path / "mockpi")


@pytest.fixture
def pkg(mockpi: MockPI) -> Generator[None, None, None]:
    mockpi.add(DefaultPackageName)
    with mockpi.server():
        yield


def test_install_package(pkg: None) -> None:
    scriptenv.requires(DefaultPackageName)

    __import__(DefaultPackageName)


def test_install_multiple_packages(mockpi: MockPI) -> None:
    another_package = DefaultPackageName + "another"
    mockpi.add(DefaultPackageName)
    mockpi.add(another_package)

    with mockpi.server():
        scriptenv.requires(DefaultPackageName, another_package)

    __import__(DefaultPackageName)
    __import__(another_package)


def test_suppess_stdout(pkg: None, capsys: pytest.CaptureFixture[str]) -> None:
    scriptenv.requires(DefaultPackageName)

    out, _ = capsys.readouterr()
    assert not out
