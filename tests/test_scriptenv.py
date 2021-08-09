# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument

import os
import sys
from pathlib import Path

from pytest_mock import MockerFixture

from scriptenv.scriptenv import ScriptEnv


def test_update_runtime(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", ["existing_path"])
    mocker.patch(
        "os.environ", dict(PATH="existing_path", PYTHONPATH="existing_pythonpath")
    )

    env = ScriptEnv(install_base=tmp_path, packages=["pkg0", "pkg1"])
    env.update_runtime()

    assert sys.path == [
        str(tmp_path / "pkg0"),
        str(tmp_path / "pkg1"),
        "existing_path",
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(tmp_path / "pkg0"),
            str(tmp_path / "pkg1"),
            "existing_pythonpath",
        ]
    )
    assert os.environ["PATH"] == os.pathsep.join(
        [
            str(tmp_path / "pkg0" / "bin"),
            str(tmp_path / "pkg1" / "bin"),
            "existing_path",
        ]
    )


def test_update_empty_runtime(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", [])
    mocker.patch("os.environ", dict())

    env = ScriptEnv(install_base=tmp_path, packages=["pkg0", "pkg1"])
    env.update_runtime()

    assert sys.path == [
        str(tmp_path / "pkg0"),
        str(tmp_path / "pkg1"),
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(tmp_path / "pkg0"),
            str(tmp_path / "pkg1"),
        ]
    )
    assert os.environ["PATH"] == os.pathsep.join(
        [
            str(tmp_path / "pkg0" / "bin"),
            str(tmp_path / "pkg1" / "bin"),
        ]
    )
