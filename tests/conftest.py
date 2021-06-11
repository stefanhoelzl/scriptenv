# pylint: disable=missing-module-docstring
import sys
import shutil
from typing import Generator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="function")
def save_and_restore_sys_path_and_modules() -> Generator[None, None, None]:
    """Saves and restores sys.path."""
    sys_path_backup = list(sys.path)
    sys.modules.pop("scriptenvtestpackage", None)
    yield
    sys.path = sys_path_backup


@pytest.fixture(autouse=True, scope="function")
def cleanup_tmp_path() -> None:
    """Cleans up the tmp path."""
    if Path("/tmp/scriptenv").exists():
        shutil.rmtree("/tmp/scriptenv")


@pytest.fixture(autouse=True, scope="function")
def cleanup_sys_modules() -> None:
    """Removes old test packages from sys.modules."""
    for name, module in list(sys.modules.items()):
        if (getattr(module, "__file__", None) or "").startswith("/tmp/scriptenv"):
            del sys.modules[name]
