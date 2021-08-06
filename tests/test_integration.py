# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
import os
import subprocess
import sys
from pathlib import Path
from typing import Generator

import pytest
from mockpi import MockPI, Package

import scriptenv

DefaultPackage = Package()


@pytest.fixture
def default_pkg(mockpi: MockPI) -> Generator[Package, None, None]:
    mockpi.add(DefaultPackage)
    yield DefaultPackage


def test_install_package(default_pkg: Package) -> None:
    scriptenv.requires(default_pkg.name)

    __import__(default_pkg.name)


def test_forward_to_subprocess(default_pkg: Package) -> None:
    scriptenv.requires(default_pkg.name)
    subprocess.run(
        [sys.executable, "-c", f"import {default_pkg.name}"],
        check=True,
    )


def test_forward_binaries_to_subprocesses(mockpi: MockPI) -> None:
    package = Package(entry_points=dict(main="pass"))
    mockpi.add(package)
    scriptenv.requires(package.name)
    subprocess.run(["main"], check=True)


def test_cli_run(mockpi: MockPI, tmp_path: Path) -> None:
    distinct_error_code = 99
    package = Package(entry_points=dict(main=f"return {distinct_error_code}"))
    mockpi.add(package)
    process = subprocess.run(
        ["scriptenv", "run", package.name, "-c", "main"],
        env=dict(
            SCRIPTENV_CACHE_PATH=str(tmp_path / "subprocess_cache_path"), **os.environ
        ),
        check=False,
    )
    assert process.returncode == distinct_error_code
