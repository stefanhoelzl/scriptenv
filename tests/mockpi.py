"""Mocks a pypi server"""

import io
import os
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Generator, List, Optional
from unittest.mock import patch

from setuptools import sandbox

SetupPyTemplate = """
from setuptools import setup

setup(
    name="{package}",
    version="{version}",
    py_modules=["{package}"],
    install_requires={install_requires},
)
"""

PackagePyTemplate = """
__version__ = '{version}'
__mock__ = True
"""


@contextmanager
def _serve_directory(path: Path, requests: List[str]) -> Generator[str, None, None]:
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

        def do_GET(self) -> None:
            """Records all requests."""
            requests.append(self.path)
            return super().do_GET()

    with ThreadingHTTPServer(
        (host, port), partial(SilentHTTPRequestHandler, directory=path.absolute())
    ) as httpd:
        thread = Thread(target=httpd.serve_forever)
        thread.start()
        yield f"http://{host}:{port}"
        httpd.shutdown()
        thread.join(1)


class MockPI:
    """Serves a python package index server with dummy packages"""

    def __init__(self, path: Path):
        self._serve_path = path / "packages"
        self._build_path = path / "build"
        self._requests: List[str] = list()

    def add(
        self,
        pkg: str,
        version: str = "0.0.1",
        dependencies: Optional[List[str]] = None,
        dist_type: str = "sdist",
    ) -> None:
        """Adds a dummy package to the pypi server"""
        package_path = self._build_path / f"{pkg}_{version}"
        package_path.mkdir(parents=True)

        setup_py = package_path / "setup.py"
        setup_py.write_text(
            SetupPyTemplate.format(
                package=pkg, version=version, install_requires=str(dependencies)
            )
        )
        (package_path / f"{pkg}.py").write_text(
            PackagePyTemplate.format(version=version)
        )

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            sandbox.run_setup(str(setup_py.absolute()), [dist_type])

        dist_path = next((package_path / "dist").iterdir())
        serve_path = self._serve_path / pkg
        serve_path.mkdir(parents=True, exist_ok=True)
        (serve_path / dist_path.name).write_bytes(dist_path.read_bytes())

    @contextmanager
    def server(self) -> Generator[None, None, None]:
        """Starts the pypi server"""
        with _serve_directory(self._serve_path, self._requests) as url:
            with patch.dict(
                os.environ, dict(PIP_INDEX_URL=url, PIP_NO_CACHE_DIR="off")
            ):
                yield

    def reset_requests(self) -> None:
        """Resets the recorded requests."""
        self._requests.clear()

    def count_requests(self) -> int:
        """Returns the number of requests made in total."""
        return len(self._requests)

    def count_package_requests(self, package: str, version: str) -> int:
        """Returns the number of requests made for a specific package version."""
        return self._requests.count(f"/{package}/{package}-{version}.tar.gz")
