# pylint: disable=missing-module-docstring,missing-function-docstring

import os
from dataclasses import FrozenInstanceError
from pathlib import Path

import appdirs
import pytest
from pytest_mock import MockFixture

from scriptenv.config import Config


def test_defaults() -> None:
    del os.environ["SCRIPTENV_CACHE_PATH"]
    assert Config() == Config(
        cache_path=Path(appdirs.user_cache_dir("scriptenv")),
        use_lockfile=True,
    )


def test_environ_overrides(mocker: MockFixture) -> None:
    mocker.patch.dict(
        os.environ,
        dict(SCRIPTENV_CACHE_PATH="/custom/path", SCRIPTENV_USE_LOCKFILE="false"),
    )
    assert Config() == Config(
        cache_path=Path("/custom/path"),
        use_lockfile=False,
    )


@pytest.mark.parametrize(
    "env_value, casted_value",
    [
        ("false", False),
        ("no", False),
        ("off", False),
        ("OFF", False),
        ("", True),
        ("everything-else", True),
    ],
)
def test_environ_bool_casts(
    env_value: str, casted_value: bool, mocker: MockFixture
) -> None:
    mocker.patch.dict(
        os.environ,
        dict(SCRIPTENV_USE_LOCKFILE=env_value),
    )
    assert Config() == Config(
        use_lockfile=casted_value,
    )


def test_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        Config().cache_path = Path()  # type: ignore
