# pylint: disable=missing-module-docstring,missing-function-docstring,unused-argument,redefined-outer-name

import os
from pathlib import Path
from typing import Callable, Generator, List, cast
from uuid import uuid4 as uuid

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_git import GitRepo

from release import changelog, check_commit_messages

CommitFactory = Callable[[List[str]], List[str]]


@pytest.fixture(autouse=True)
def in_git_repo(
    request: FixtureRequest, git_repo: GitRepo
) -> Generator[GitRepo, None, None]:
    os.chdir(git_repo.workspace)
    yield git_repo
    os.chdir(request.config.invocation_dir)


@pytest.fixture(autouse=True)
def setup_git_repo(in_git_repo: GitRepo) -> None:
    in_git_repo.run("git config user.name pytest")
    in_git_repo.run("git config user.email pytest@example.com")


@pytest.fixture
def commit_factory(git_repo: GitRepo) -> CommitFactory:
    def _commit_factory(commits: List[str]) -> List[str]:
        for commit in commits:
            new_file_name = uuid().hex
            Path(git_repo.workspace, new_file_name).write_text("")
            git_repo.run(f"git add {new_file_name}", capture=True)
            git_repo.run(f'git commit -m"{commit}"', capture=True)
        return (
            cast(
                str,
                git_repo.run(f'git log --pretty="%H" -n{len(commits)}', capture=True),
            )
            .strip()
            .split("\n")
        )

    return _commit_factory


@pytest.mark.parametrize(
    "allowed_keyword", ["internal", "bugfix", "feature", "internal", "tooling"]
)
def test_check_valid_commit_message(
    allowed_keyword: str, commit_factory: CommitFactory
) -> None:
    commit_factory([f"[{allowed_keyword}] message"])
    assert list(check_commit_messages()) == []


@pytest.mark.parametrize("message", ["no prefix"])
def test_check_invalid_commit_message(
    message: str, commit_factory: CommitFactory
) -> None:
    commit_factory([message])
    error_messages = check_commit_messages()
    assert next(error_messages) == f"Invalid commit message: {message}"
    with pytest.raises(SystemExit):
        next(error_messages)


def test_changelog(commit_factory: CommitFactory) -> None:
    commit_factory(
        [
            "[internal] internal",
            "[bugfix] bugfix",
            "[feature] feature",
            "[tooling] hidden",
        ]
    )
    assert list(changelog()) == [
        "* Features",
        "  * feature",
        "* Bugfixes",
        "  * bugfix",
        "* Internal",
        "  * internal",
    ]


def test_changelog_omit_empty_categories(commit_factory: CommitFactory) -> None:
    commit_factory(["[feature] feature"])
    assert list(changelog()) == [
        "* Features",
        "  * feature",
    ]
