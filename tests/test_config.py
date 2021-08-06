# pylint: disable=missing-module-docstring,missing-function-docstring

import os
from dataclasses import FrozenInstanceError
from pathlib import Path

import appdirs
import pytest
from pytest_mock import MockFixture

from scriptenv.config import Config


def test_defaults() -> None:
    assert Config() == Config(cache_path=Path(appdirs.user_cache_dir("scriptenv")))


def test_environ_overrides(mocker: MockFixture) -> None:
    mocker.patch.dict(os.environ, dict(SCRIPTENV_CACHE_PATH="/custom/path"))
    assert Config() == Config(cache_path=Path("/custom/path"))


def test_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        Config().cache_path = Path()  # type: ignore
