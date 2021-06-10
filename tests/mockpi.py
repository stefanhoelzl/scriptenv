"""Mocks a pypi server"""

import os
from pathlib import Path
from typing import Optional, List, Generator
from unittest.mock import patch
from contextlib import contextmanager
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
from threading import Thread

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


@contextmanager
def _serve_directory(path: Path) -> Generator[str, None, None]:
    host, port = "localhost", 9000

    handler_class = partial(SimpleHTTPRequestHandler, directory=path.absolute())
    with ThreadingHTTPServer((host, port), handler_class) as httpd:
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

    def add(
        self, pkg: str, version: str = "0.0.1", dependencies: Optional[List[str]] = None
    ) -> None:
        """Adds a dummy package to the pypi server"""
        package_path = self._build_path / pkg
        package_path.mkdir(parents=True)

        setup_py = package_path / "setup.py"
        setup_py.write_text(
            SetupPyTemplate.format(
                package=pkg, version=version, install_requires=str(dependencies)
            )
        )
        (package_path / f"{pkg}.py").write_text("")

        sandbox.run_setup(str(setup_py.absolute()), ["sdist"])

        tar_name = f"{pkg}-{version}.tar.gz"
        dist_path = package_path / "dist" / tar_name
        serve_path = self._serve_path / pkg
        serve_path.mkdir(parents=True, exist_ok=True)
        (serve_path / tar_name).write_bytes(dist_path.read_bytes())

    @contextmanager
    def server(self) -> Generator[None, None, None]:
        """Starts the pypi server"""
        with _serve_directory(self._serve_path) as url:
            with patch.dict(os.environ, dict(PIP_INDEX_URL=url)):
                yield
