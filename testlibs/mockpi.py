"""Mocks a pypi server"""

import io
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from enum import Enum
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Generator, Iterable, Mapping, NamedTuple
from unittest.mock import patch

from setuptools import sandbox


class DistType(Enum):
    """Enumerates all supported distribution types"""

    TAR = "sdist"
    WHEEL = "bdist_wheel"


class Package(NamedTuple):
    """MockPI Package definition"""

    name: str = "scriptenvtestpackage"
    version: str = "0.1.0"
    # recursive types not yet supported in mypy (https://github.com/python/mypy/issues/731)
    dependencies: Iterable["Package"] = tuple()  # type: ignore
    dist_type: DistType = DistType.TAR
    body: str = ""
    entry_points: Mapping[str, str] = {}

    def build(self, build_path: Path) -> Path:
        """Builds a package and returns the dist path."""
        package_path = build_path / f"{self.name}_{self.version}"
        package_path.mkdir(parents=True)

        setup_py = package_path / "setup.py"
        setup_py.write_text(self._generate_setup_py())
        (package_path / f"{self.name}.py").write_text(self._generate_module())

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            sandbox.run_setup(str(setup_py.absolute()), [self.dist_type.value])

        return next((package_path / "dist").iterdir())

    def _generate_setup_py(self) -> str:
        """Generates the content for setup.py."""
        return f"""
from setuptools import setup

setup(
    name="{self.name}",
    version="{self.version}",
    py_modules=["{self.name}"],
    install_requires={[pkg.name for pkg in self.dependencies]},
    entry_points={{
        "console_scripts":
            [{','.join(f"'{name}={self.name}:{name}'" for name in self.entry_points)}]
    }},
)
"""

    def _generate_module(self) -> str:
        """Generates the content for the python module."""
        newline = "\n"
        return f"""
__version__ = '{self.version}'
__mock__ = True

{newline.join(f'def {name}(): {body}{newline}' for name, body in self.entry_points.items())}

{self.body}
"""


@contextmanager
def _serve_directory(path: Path) -> Generator[str, None, None]:
    host, port = "localhost", 9000

    class SilentHTTPRequestHandler(SimpleHTTPRequestHandler):
        """SimpleHTTPRequestHandler without logging."""

        def log_message(
            self,
            format: str,  # pylint: disable=unused-argument,redefined-builtin
            *args: str,
        ) -> None:
            """Discard all log messages."""
            return

    with ThreadingHTTPServer(
        (host, port), partial(SilentHTTPRequestHandler, directory=path.absolute())
    ) as httpd:
        thread = Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://{host}:{port}"
        finally:
            httpd.shutdown()
            thread.join(1)


class MockPI:
    """Serves a python package index server with dummy packages"""

    def __init__(self, path: Path):
        self._serve_path = path / "packages"
        self._build_path = path / "build"

    def add(self, pkg: Package) -> None:
        """Adds a dummy package to the pypi server"""
        serve_path = self._serve_path / pkg.name
        serve_path.mkdir(parents=True, exist_ok=True)
        dist_path = pkg.build(self._build_path)
        (serve_path / dist_path.name).write_bytes(dist_path.read_bytes())

    @contextmanager
    def server(self) -> Generator[None, None, None]:
        """Starts the pypi server"""
        with _serve_directory(self._serve_path) as url:
            with patch.dict(
                os.environ, dict(PIP_INDEX_URL=url, PIP_NO_CACHE_DIR="off")
            ):
                yield
