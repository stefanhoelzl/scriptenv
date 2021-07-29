"""scriptenv"""

from .scriptenv import ScriptEnv


def requires(*requirements: str) -> None:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adds each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    env = ScriptEnv()
    env.apply(requirements)
