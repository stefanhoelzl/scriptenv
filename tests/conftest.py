# pylint: disable=missing-module-docstring
import sys
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import appdirs
import pytest


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
