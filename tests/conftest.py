"""configures pytest"""
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import appdirs
import pytest
from _pytest.config import Config
from pytest_cov.plugin import CovPlugin


@pytest.mark.tryfirst
def pytest_configure(config: Config) -> None:
    """Setup default pytest options."""
    config.option.newfirst = True
    config.option.failedfirst = True
    config.option.capture = "no"
    config.option.tbstyle = "short"

    config.option.pylint = True
    config.option.black = True
    config.option.isort = True

    config.option.mypy = True
    config.option.mypy_ignore_missing_imports = True
    config.pluginmanager.getplugin("mypy").mypy_argv.extend(
        ["--strict", "--implicit-reexport"]
    )

    config.option.mccabe = True
    config.addinivalue_line("mccabe-complexity", "5")

    config.option.cov_source = ["scriptenv"]
    config.option.cov_fail_under = 100
    config.option.cov_report = "term-missing"
    config.option.cov_branch = True
    config.pluginmanager.register(
        CovPlugin(config.option, config.pluginmanager), "_cov"
    )


@pytest.fixture(autouse=True, scope="function")
def patch_cache_path(tmp_path: Path) -> Generator[None, None, None]:
    """Patches appdirs to use a temporary directory"""
    with patch.object(appdirs, "user_cache_dir", return_value=tmp_path / "cache"):
        yield


@pytest.fixture(autouse=True, scope="function")
def save_and_restore_sys_path() -> Generator[None, None, None]:
    """Saves and restores sys.path."""
    sys_path_backup = list(sys.path)
    yield
    sys.path = sys_path_backup


@pytest.fixture(autouse=True, scope="function")
def cleanup_sys_modules() -> None:
    """Removes test packages from sys.modules."""
    for name, module in list(sys.modules.items()):
        if getattr(module, "__mock__", False):
            del sys.modules[name]
