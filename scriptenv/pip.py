"""Wrapper functions for pip."""
import io
import re
import sys
from contextlib import contextmanager, redirect_stdout
from pathlib import Path
from typing import Callable, Generator, Iterable, Set

from pip._internal.commands import create_command

PackageNamePattern = re.compile(r"(/|\\)(?P<name>[^(/|\\)]+?(\.tar\.gz|\.whl))")


class PipError(Exception):
    """Handles errors during pip invocations."""

    def __init__(  # pylint: disable=useless-super-delegation
        self, exit_code: int
    ) -> None:
        super().__init__(exit_code)


def download(requirements: Iterable[str], dest: Path) -> Set[str]:
    """
    Downloads requirements and its dependencies into a given directory.
    Returns a set with names of all downloaded packages.
    """
    stdout = _pip("download", "--dest", str(dest), *requirements)
    return {match.group("name") for match in PackageNamePattern.finditer(stdout)}


def install(package: Path, target: Path) -> None:
    """Installs a package without its dependencies to a given target directory."""
    _pip(
        "install",
        "--no-deps",
        "--no-user",
        "--target",
        str(target),
        str(package),
    )


def _pip(command: str, *args: str) -> str:
    with _redirect_stdout() as get_stdout:
        return_code = create_command(command).main(list(args))
        if return_code:
            raise PipError(return_code)
    return get_stdout()


@contextmanager
def _redirect_stdout() -> Generator[Callable[[], str], None, None]:
    """Redirects stdout with a workaround for https://bugs.python.org/issue44666"""
    stdout = io.BytesIO()
    encoding = sys.stdout.encoding
    wrapper = io.TextIOWrapper(
        stdout,
        encoding=encoding,
    )
    with redirect_stdout(wrapper):
        yield lambda: stdout.getvalue().decode(encoding)
