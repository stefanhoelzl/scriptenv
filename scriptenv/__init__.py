"""scriptenv"""
import io
import re
import sys
from contextlib import redirect_stdout
from typing import Tuple

from pip._internal.commands import create_command


def requires(*requirements: str) -> None:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adds each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        create_command("download").main(
            ["--dest", "/tmp/scriptenv/cache", *requirements]
        )

        packages = {
            match.group("pkg")
            for match in re.finditer(r"/(?P<pkg>[^/]+?\.tar\.gz)", stdout.getvalue())
        }

        for package in packages:
            create_command("install").main(
                [
                    "--no-deps",
                    "--no-user",
                    "--target",
                    f"/tmp/scriptenv/{package}",
                    f"/tmp/scriptenv/cache/{package}",
                ]
            )
            sys.path[0:0] = [f"/tmp/scriptenv/{package}"]
