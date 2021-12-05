"""Script to update the requirements"""
from pathlib import Path
from typing import Generator, NamedTuple, Optional, Tuple

import fire
import requests


class Requirement(NamedTuple):
    """container for requirement informations."""

    name: str
    version: str
    source: Path

    def __str__(self) -> str:
        return f"{self.name}=={self.version} ({str(self.source)})"


def update() -> Generator[str, None, None]:
    """Updates all requirements to its latest versions."""
    for requirement, latest_version in get_updates():
        yield f"{requirement.name}: {requirement.version} => {latest_version}"
        requirement.source.write_text(
            requirement.source.read_text().replace(
                f"{requirement.name}=={requirement.version}",
                f"{requirement.name}=={latest_version}",
            )
        )


def get_updates() -> Generator[Tuple[Requirement, str], None, None]:
    """Gets all available updates."""
    for requirement in get():
        package_info = requests.get(
            f"https://www.pypi.org/pypi/{requirement.name}/json"
        ).json()
        latest_version = package_info["info"]["version"]
        if latest_version != requirement.version:
            yield requirement, latest_version


def get(requirements_txt: Optional[Path] = None) -> Generator[Requirement, None, None]:
    """Gets all defined requirements."""
    requirements_txt = requirements_txt or Path("requirements.txt")
    for requirement in _read_non_empty_lines(requirements_txt):
        if requirement.startswith("-r"):
            _, link = requirement.split(" ")
            yield from get(requirements_txt.parent / link)
        else:
            name, version = requirement.split("==", 1)
            yield Requirement(name, version, requirements_txt)


def _read_non_empty_lines(filepath: Path) -> Generator[str, None, None]:
    with open(str(filepath), mode="r", encoding="utf-8") as filehandle:
        for line in filehandle.readlines():
            line = line.strip()
            if line:
                yield line


if __name__ == "__main__":
    fire.Fire()
