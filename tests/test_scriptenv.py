# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument

import hashlib
import json
import os
import sys
from pathlib import Path
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from scriptenv.config import Config
from scriptenv.scriptenv import ScriptEnv


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return Config(cache_path=tmp_path / "base")


def test_paths(config: Config) -> None:
    env = ScriptEnv(config)

    assert env.install_path == config.cache_path / "install"
    assert env.locks_path == config.cache_path / "locks"
    assert env.package_cache_path == config.cache_path / "cache"

    assert env.locks_path.is_dir()


def test_fetch_requirements_from_cached_file(
    config: Config, mocker: MockerFixture
) -> None:
    download_mock = mocker.patch("scriptenv.pip.download")
    lockfile = (
        config.cache_path
        / "locks"
        / hashlib.md5(b"requirement0\nrequirement1").hexdigest()
    )
    lockfile.parent.mkdir(parents=True)
    lockfile.write_text('["cached", "packages"]')

    env = ScriptEnv(config)
    assert env.fetch_requirements(["requirement0", "requirement1"]) == {
        "cached",
        "packages",
    }
    download_mock.assert_not_called()


def test_fetch_requirements_with_pip(config: Config, mocker: MockerFixture) -> None:
    download_mock = mocker.patch("scriptenv.pip.download")
    download_mock.return_value = {"resolved", "packages"}
    lockfile = (
        config.cache_path
        / "locks"
        / hashlib.md5(b"requirement0\nrequirement1").hexdigest()
    )

    env = ScriptEnv(config)
    resolved_packages = env.fetch_requirements(["requirement0", "requirement1"])

    assert resolved_packages == {
        "resolved",
        "packages",
    }
    download_mock.assert_called_once_with(
        ["requirement0", "requirement1"], config.cache_path / "cache"
    )
    assert set(json.loads(lockfile.read_text())) == {"resolved", "packages"}


def test_install_packages(config: Config, mocker: MockerFixture) -> None:
    install_mock = mocker.patch("scriptenv.pip.install")
    (config.cache_path / "install" / "already_installed").mkdir(parents=True)

    env = ScriptEnv(config)
    env.install_packages(["pkg0", "already_installed", "pkg1"])

    install_mock.assert_has_calls(
        [
            call(
                config.cache_path / "cache" / "pkg0",
                config.cache_path / "install" / "pkg0",
            ),
            call(
                config.cache_path / "cache" / "pkg1",
                config.cache_path / "install" / "pkg1",
            ),
        ]
    )


def test_update_runtime(config: Config, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", ["existing_path"])
    mocker.patch(
        "os.environ", dict(PATH="existing_path", PYTHONPATH="existing_pythonpath")
    )

    env = ScriptEnv(config)
    env.update_runtime(["pkg0", "pkg1"])

    assert sys.path == [
        str(config.cache_path / "install" / "pkg0"),
        str(config.cache_path / "install" / "pkg1"),
        "existing_path",
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(config.cache_path / "install" / "pkg0"),
            str(config.cache_path / "install" / "pkg1"),
            "existing_pythonpath",
        ]
    )
    assert os.environ["PATH"] == os.pathsep.join(
        [
            str(config.cache_path / "install" / "pkg0" / "bin"),
            str(config.cache_path / "install" / "pkg1" / "bin"),
            "existing_path",
        ]
    )


def test_update_empty_runtime(config: Config, mocker: MockerFixture) -> None:
    mocker.patch("sys.path", [])
    mocker.patch("os.environ", dict())

    env = ScriptEnv(config)
    env.update_runtime(["pkg0", "pkg1"])

    assert sys.path == [
        str(config.cache_path / "install" / "pkg0"),
        str(config.cache_path / "install" / "pkg1"),
    ]
    assert os.environ["PYTHONPATH"] == os.pathsep.join(
        [
            str(config.cache_path / "install" / "pkg0"),
            str(config.cache_path / "install" / "pkg1"),
        ]
    )
    assert os.environ["PATH"] == os.pathsep.join(
        [
            str(config.cache_path / "install" / "pkg0" / "bin"),
            str(config.cache_path / "install" / "pkg1" / "bin"),
        ]
    )


def test_apply(mocker: MockerFixture) -> None:
    env = ScriptEnv()

    requirements = ["requirement"]
    packages = {"requirement", "dependency"}

    fetch_mock = mocker.patch.object(env, "fetch_requirements")
    fetch_mock.return_value = packages

    install_mock = mocker.patch.object(env, "install_packages")
    update_mock = mocker.patch.object(env, "update_runtime")

    env.apply(["requirement"])

    fetch_mock.assert_called_once_with(requirements)
    install_mock.assert_called_once_with(packages)
    update_mock.assert_called_once_with(packages)
