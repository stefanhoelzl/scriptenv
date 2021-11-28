"""scriptenv"""
from pathlib import Path

from .builder import ScriptEnvBuilder
from .pipfile import parse_pipfile_lock
from .scriptenv import ScriptEnv

__all__ = ["ScriptEnv", "ScriptEnvBuilder", "requires", "from_pipfile_lock"]


def requires(*requirements: str) -> ScriptEnv:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adds each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    builder = ScriptEnvBuilder()
    env = builder.build(requirements)
    env.enable()
    return env


def from_pipfile_lock(pipfile_lock: Path) -> ScriptEnv:
    """Creates a ScriptEnv based on a Pipfile.lock"""
    return requires(*parse_pipfile_lock(pipfile_lock))
