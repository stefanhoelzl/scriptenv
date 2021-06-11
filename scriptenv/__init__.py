"""scriptenv"""
import io
import re
import sys
from contextlib import redirect_stdout
from typing import Tuple
from pathlib import Path

import appdirs
from pip._internal.commands import create_command

__version__ = "0.0.1"
__author__ = "stefanhoelzl"


def requires(*requirements: str) -> None:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adds each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    base_path = Path(appdirs.user_cache_dir(__name__, __author__, version=__version__))
    download_path = (base_path / "download").absolute()
    install_path = (base_path / "install").absolute()

    stdout = io.StringIO()
    with redirect_stdout(stdout):
        create_command("download").main(["--dest", str(download_path), *requirements])

        packages = {
            match.group("pkg")
            for match in re.finditer(r"/(?P<pkg>[^/]+?\.tar\.gz)", stdout.getvalue())
        }

        for package in packages:
            package_install_path = install_path / package
            if not package_install_path.exists():
                create_command("install").main(
                    [
                        "--no-deps",
                        "--no-user",
                        "--target",
                        str(package_install_path),
                        str(download_path / package),
                    ]
                )
            sys.path[0:0] = [str(package_install_path)]
