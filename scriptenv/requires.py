"""Implementation of scriptenv.requires"""
import hashlib
import json
import sys
from pathlib import Path

import appdirs

from . import pip


def requires(*requirements: str) -> None:
    """Makes each requirements available to import.

    Installs each requirement and dependency to a seperate directory
    and adds each directory to the front of sys.path

    Arguments:
        requirements: List of pip requirements required to be installed.
    """
    base_path = Path(appdirs.user_cache_dir(__name__)).absolute()
    download_path = base_path / "download"
    install_path = base_path / "install"
    dependencies_path = base_path / "dependencies"
    dependencies_path.mkdir(parents=True, exist_ok=True)

    requirements_hash = hashlib.md5(
        "\n".join(sorted(requirements)).encode("utf-8")
    ).hexdigest()
    requirements_list_path = dependencies_path / requirements_hash

    if not requirements_list_path.exists():
        packages = pip.download(requirements, download_path)
        requirements_list_path.write_text(json.dumps(list(packages)))
    else:
        packages = set(json.loads(requirements_list_path.read_text()))

    for package in packages:
        package_install_path = install_path / package
        if not package_install_path.exists():
            pip.install(download_path / package, package_install_path)
        sys.path[0:0] = [str(package_install_path)]
