"""scriptenv"""
import io
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
    with redirect_stdout(io.StringIO()):
        create_command("install").main(
            ["--no-user", "--target", "/tmp/scriptenv", *requirements]
        )
        sys.path[0:0] = ["/tmp/scriptenv/"]
