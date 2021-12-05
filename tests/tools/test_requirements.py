# pylint: disable=missing-module-docstring,missing-function-docstring,unused-argument,redefined-outer-name
import os
from pathlib import Path
from typing import Generator

import pytest
from requests_mock.mocker import Mocker as RequestsMocker

from tools import requirements


@pytest.fixture(autouse=True)
def create_workspace(tmp_path: Path) -> Generator[None, None, None]:
    current_directory = os.getcwd()
    os.chdir(str(tmp_path))
    try:
        yield
    finally:
        os.chdir(current_directory)


def test_get() -> None:
    Path("requirements.txt").write_text("pkg0==1.0.0\npkg1==1.0.0")
    assert list(requirements.get()) == [
        requirements.Requirement("pkg0", "1.0.0", Path("requirements.txt")),
        requirements.Requirement("pkg1", "1.0.0", Path("requirements.txt")),
    ]


def test_get_ignore_empty_lines() -> None:
    Path("requirements.txt").write_text("pkg==1.0.0\n   \n")
    assert list(requirements.get()) == [
        requirements.Requirement("pkg", "1.0.0", Path("requirements.txt")),
    ]


def test_get_from_multiple_files() -> None:
    Path("sub").mkdir()
    Path("requirements.txt").write_text("pkg==1.0.0\n-r sub/requirements.txt")
    Path("sub/requirements.txt").write_text("sub==1.0.0")

    assert list(requirements.get()) == [
        requirements.Requirement("pkg", "1.0.0", Path("requirements.txt")),
        requirements.Requirement("sub", "1.0.0", Path("sub/requirements.txt")),
    ]


def test_get_updates(requests_mock: RequestsMocker) -> None:
    Path("requirements.txt").write_text("update==1.0.0\nlatest==1.0.0")
    requests_mock.get(
        "https://www.pypi.org/pypi/update/json", json=dict(info=dict(version="2.0.0"))
    )
    requests_mock.get(
        "https://www.pypi.org/pypi/latest/json", json=dict(info=dict(version="1.0.0"))
    )

    assert list(requirements.get_updates()) == [
        (requirements.Requirement("update", "1.0.0", Path("requirements.txt")), "2.0.0")
    ]


def test_update(requests_mock: RequestsMocker) -> None:
    Path("requirements.txt").write_text("pkg==1.0.0")
    requests_mock.get(
        "https://www.pypi.org/pypi/pkg/json", json=dict(info=dict(version="2.0.0"))
    )

    assert list(requirements.update()) == ["pkg: 1.0.0 => 2.0.0"]

    assert Path("requirements.txt").read_text() == "pkg==2.0.0"
