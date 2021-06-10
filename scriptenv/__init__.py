"""scriptenv"""
import sys
from pip._internal.commands import create_command


def requires(requirements: str) -> None:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adding each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    create_command("install").main(
        ["--no-user", "--target", f"/tmp/scriptenv/{requirements}", requirements]
    )
    sys.path[0:0] = [f"/tmp/scriptenv/{requirements}"]
