"""configures pytest"""
import os
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import appdirs
import pytest
from _pytest.config import Config
from pytest_cov.plugin import CovPlugin
from pytest_mock import MockerFixture

from testlibs.mockpi import MockPI

pytest_plugins = ["testlibs.markdown"]


@pytest.mark.tryfirst
def pytest_configure(config: Config) -> None:
    """Setup default pytest options."""
    config.option.newfirst = True
    config.option.failedfirst = True
    config.option.tbstyle = "short"

    config.option.pylint = True
    config.option.black = True
    config.option.isort = True
    config.option.markdown = True

    config.option.mypy = True
    config.option.mypy_ignore_missing_imports = True
    config.pluginmanager.getplugin("mypy").mypy_argv.extend(
        ["--strict", "--implicit-reexport"]
    )

    config.option.mccabe = True
    config.addinivalue_line("mccabe-complexity", "3")

    config.option.cov_source = ["scriptenv", "release"]
    config.option.cov_fail_under = 100
    config.option.cov_report = {
        "term-missing": None,
        "html": "cov_html",
    }
    config.option.cov_branch = True
    config.pluginmanager.register(
        CovPlugin(config.option, config.pluginmanager), "_cov"
    )


@pytest.fixture(autouse=True)
def set_cache_path(tmp_path: Path) -> None:
    """Patches the default cache dir for scriptenv"""
    os.environ["SCRIPTENV_CACHE_PATH"] = str(tmp_path / "temp_cache_path")


@pytest.fixture(autouse=True)
def patch_appdirs(tmp_path: Path) -> Generator[None, None, None]:
    """Patches appdirs to use a temporary directory"""
    with patch.object(
        appdirs, "user_cache_dir", return_value=tmp_path / "appdirs" / "user_cache_dir"
    ):
        yield


@pytest.fixture(autouse=True)
def save_and_restore_sys_path(mocker: MockerFixture) -> None:
    """Saves and restores sys.path."""
    mocker.patch("sys.path", list(sys.path))


@pytest.fixture(autouse=True)
def save_and_restore_os_environ() -> Generator[None, None, None]:
    """Saves and restores os.environ."""
    backup = dict(os.environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(backup)


@pytest.fixture(autouse=True)
def cleanup_sys_modules() -> None:
    """Removes test packages from sys.modules."""
    for name, module in list(sys.modules.items()):
        if getattr(module, "__mock__", False):
            del sys.modules[name]


@pytest.fixture
def mockpi(tmp_path: Path) -> Generator[MockPI, None, None]:
    """Fixture to setup a Python Package Index"""
    mock_pi = MockPI(tmp_path / "mockpi")
    with mock_pi.server():
        yield mock_pi
