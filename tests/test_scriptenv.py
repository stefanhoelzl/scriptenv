# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument

import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import call

from pytest_mock import MockerFixture

from scriptenv.scriptenv import ScriptEnv


def test_paths(tmp_path: Path) -> None:
    base_path = tmp_path / "base"

    env = ScriptEnv(base_path)

    assert env.install_path == base_path / "install"
    assert env.locks_path == base_path / "locks"
    assert env.package_cache_path == base_path / "cache"

    assert env.locks_path.is_dir()


def test_fetch_requirements_from_cached_file(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    download_mock = mocker.patch("scriptenv.pip.download")
    lockfile = (
        tmp_path / "locks" / hashlib.md5(b"requirement0\nrequirement1").hexdigest()
    )
    lockfile.parent.mkdir(parents=True)
    lockfile.write_text('["cached", "packages"]')

    env = ScriptEnv(tmp_path)
    assert env.fetch_requirements(["requirement0", "requirement1"]) == {
        "cached",
        "packages",
    }
    download_mock.assert_not_called()


def test_fetch_requirements_with_pip(tmp_path: Path, mocker: MockerFixture) -> None:
    download_mock = mocker.patch("scriptenv.pip.download")
    download_mock.return_value = {"resolved", "packages"}
    lockfile = (
        tmp_path / "locks" / hashlib.md5(b"requirement0\nrequirement1").hexdigest()
    )

    env = ScriptEnv(tmp_path)
    resolved_packages = env.fetch_requirements(["requirement0", "requirement1"])

    assert resolved_packages == {
        "resolved",
        "packages",
    }
    download_mock.assert_called_once_with(
        ["requirement0", "requirement1"], tmp_path / "cache"
    )
    assert set(json.loads(lockfile.read_text())) == {"resolved", "packages"}


def test_install_packages(tmp_path: Path, mocker: MockerFixture) -> None:
    install_mock = mocker.patch("scriptenv.pip.install")
    (tmp_path / "install" / "already_installed").mkdir(parents=True)

    env = ScriptEnv(tmp_path)
    env.install_packages(["pkg0", "already_installed", "pkg1"])

    install_mock.assert_has_calls(
        [
            call(tmp_path / "cache" / "pkg0", tmp_path / "install" / "pkg0"),
            call(tmp_path / "cache" / "pkg1", tmp_path / "install" / "pkg1"),
        ]
    )


def test_update_runtime(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", ["existing_path"])
    mocker.patch(
        "os.environ", dict(PATH="existing_path", PYTHONPATH="existing_pythonpath")
    )

    env = ScriptEnv(tmp_path)
    env.update_runtime(["pkg0", "pkg1"])

    assert sys.path == [
        str(tmp_path / "install" / "pkg0"),
        str(tmp_path / "install" / "pkg1"),
        "existing_path",
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(tmp_path / "install" / "pkg0"),
            str(tmp_path / "install" / "pkg1"),
            "existing_pythonpath",
        ]
    )


def test_update_empty_runtime(tmp_path: Path, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", [])
    mocker.patch("os.environ", dict())

    env = ScriptEnv(tmp_path)
    env.update_runtime(["pkg0", "pkg1"])

    assert sys.path == [
        str(tmp_path / "install" / "pkg0"),
        str(tmp_path / "install" / "pkg1"),
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(tmp_path / "install" / "pkg0"),
            str(tmp_path / "install" / "pkg1"),
        ]
    )
