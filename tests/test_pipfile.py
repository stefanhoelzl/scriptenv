# pylint: disable=missing-module-docstring,missing-function-docstring,disable=redefined-outer-name,unused-argument
import json
from pathlib import Path

from scriptenv import pipfile


def test_parse_pipfile_lock(tmp_path: Path) -> None:
    pipfile_lock = tmp_path / "Pipfile.lock"
    pipfile_lock.write_text(
        json.dumps(
            {
                "default": {"default_package": {"version": "==1.0.0"}},
                "develop": {"develop_package": {"version": "==0.1.0"}},
            }
        )
    )

    assert list(pipfile.parse_pipfile_lock(pipfile_lock)) == [
        "default_package==1.0.0",
        "develop_package==0.1.0",
    ]


def test_parse_pipfile_lock_from_folder(tmp_path: Path) -> None:
    pipfile_lock = tmp_path / "Pipfile.lock"
    pipfile_lock.write_text(json.dumps({}))

    assert list(pipfile.parse_pipfile_lock(tmp_path)) == []


def test_skip_meta_section(tmp_path: Path) -> None:
    pipfile_lock = tmp_path / "Pipfile.lock"
    pipfile_lock.write_text(json.dumps({"_meta": {"pipfile-spec": 6}}))

    assert list(pipfile.parse_pipfile_lock(pipfile_lock)) == []
