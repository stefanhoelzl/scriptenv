# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import call

import pytest
from pytest_mock import MockerFixture

from scriptenv.builder import ScriptEnvBuilder
from scriptenv.config import Config


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return Config(cache_path=tmp_path / "base")


def test_paths(config: Config) -> None:
    builder = ScriptEnvBuilder(config)

    assert builder.install_path == config.cache_path / "install"
    assert builder.locks_path == config.cache_path / "locks"
    assert builder.package_cache_path == config.cache_path / "cache"

    assert builder.locks_path.is_dir()


def test_fetch_requirements_from_lockfile(
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

    builder = ScriptEnvBuilder(config)
    assert builder.fetch_requirements(["requirement0", "requirement1"]) == {
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

    builder = ScriptEnvBuilder(config)
    resolved_packages = builder.fetch_requirements(["requirement0", "requirement1"])

    assert resolved_packages == {
        "resolved",
        "packages",
    }
    download_mock.assert_called_once_with(
        ["requirement0", "requirement1"], config.cache_path / "cache"
    )
    assert set(json.loads(lockfile.read_text())) == {"resolved", "packages"}


def test_fetch_requirements_disable_lockfile(
    config: Config, mocker: MockerFixture
) -> None:
    download_mock = mocker.patch("scriptenv.pip.download")
    download_mock.return_value = {"resolved", "packages"}
    lockfile = (
        config.cache_path
        / "locks"
        / hashlib.md5(b"requirement0\nrequirement1").hexdigest()
    )
    lockfile.parent.mkdir(parents=True)
    lockfile.write_text('["cached", "packages"]')

    builder = ScriptEnvBuilder(replace(config, use_lockfile=False))
    assert builder.fetch_requirements(["requirement0", "requirement1"]) == {
        "resolved",
        "packages",
    }


def test_install_packages(config: Config, mocker: MockerFixture) -> None:
    install_mock = mocker.patch("scriptenv.pip.install")
    (config.cache_path / "install" / "already_installed").mkdir(parents=True)

    builder = ScriptEnvBuilder(config)
    builder.install_packages(["pkg0", "already_installed", "pkg1"])

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


def test_build(mocker: MockerFixture) -> None:
    builder = ScriptEnvBuilder()

    requirements = ["requirement"]
    packages = {"requirement", "dependency"}

    fetch_mock = mocker.patch.object(builder, "fetch_requirements")
    fetch_mock.return_value = packages

    install_mock = mocker.patch.object(builder, "install_packages")

    env = builder.build(["requirement"])

    assert env.packages_path == builder.install_path
    assert env.packages == list(packages)

    fetch_mock.assert_called_once_with(requirements)
    install_mock.assert_called_once_with(packages)
