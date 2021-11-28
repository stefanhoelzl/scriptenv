"""Handles Pipfile.lock"""

import json
from pathlib import Path
from typing import Generator


def parse_pipfile_lock(pipfile_lock: Path) -> Generator[str, None, None]:
    """Parses a Pipfile.lock into requirements."""
    if pipfile_lock.is_dir():
        pipfile_lock /= "Pipfile.lock"

    yield from (
        f"{package_name}{package_spec['version']}"
        for section, packages in json.loads(pipfile_lock.read_bytes()).items()
        if section != "_meta"
        for package_name, package_spec in packages.items()
    )
