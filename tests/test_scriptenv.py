# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument

import os
import sys
from pathlib import Path

from pytest_mock import MockerFixture

from scriptenv.scriptenv import ScriptEnv


def test_enable(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", ["existing_syspath"])
    mocker.patch(
        "os.environ", dict(PATH="existing_path", PYTHONPATH="existing_pythonpath")
    )

    env = ScriptEnv(install_base=tmp_path, packages=["pkg0", "pkg1"])
    env.enable()

    assert sys.path == [
        str(tmp_path / "pkg0"),
        str(tmp_path / "pkg1"),
        "existing_syspath",
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


def test_enable_empty_paths(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", [])
    mocker.patch("os.environ", dict())

    env = ScriptEnv(install_base=tmp_path, packages=["pkg0", "pkg1"])
    env.enable()

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


def test_enable_avoid_duplicates(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", [str(tmp_path / "package")])
    mocker.patch(
        "os.environ",
        dict(
            PATH=os.pathsep.join([str(tmp_path / "package" / "bin")]),
            PYTHONPATH=os.pathsep.join([str(tmp_path / "package")]),
        ),
    )

    env = ScriptEnv(install_base=tmp_path, packages=["package"])
    env.enable()

    assert sys.path == [str(tmp_path / "package")]
    assert os.environ["PYTHONPATH"] == os.pathsep.join([str(tmp_path / "package")])
    assert os.environ["PATH"] == os.pathsep.join([str(tmp_path / "package" / "bin")])


def test_disable(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", ["existing_syspath", str(tmp_path / "package")])
    mocker.patch(
        "os.environ",
        dict(
            PATH=os.pathsep.join(["existing_path", str(tmp_path / "package" / "bin")]),
            PYTHONPATH=os.pathsep.join(
                ["existing_pythonpath", str(tmp_path / "package")]
            ),
        ),
    )

    env = ScriptEnv(install_base=tmp_path, packages=["package"])
    env.disable()

    assert sys.path == ["existing_syspath"]
    assert os.environ["PYTHONPATH"] == "existing_pythonpath"
    assert os.environ["PATH"] == "existing_path"
